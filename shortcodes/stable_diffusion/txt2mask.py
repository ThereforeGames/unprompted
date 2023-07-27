class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.image_mask = None
		self.show = False
		self.description = "Creates an image mask from the content for use with inpainting."
		try:
			del self.cached_model
			del self.cached_transform
			del self.cached_model_method
			del self.cached_predictor
		except:
			pass
		self.cached_model = -1
		self.cached_transform = -1
		self.cached_model_method = ""
		self.cached_predictor = -1

	def run_block(self, pargs, kwargs, context, content):
		from PIL import ImageChops, Image, ImageOps
		import os.path
		import torch
		from torchvision import transforms
		from matplotlib import pyplot as plt
		import cv2
		import numpy
		# import gc
		from modules.images import flatten
		from modules.shared import opts
		from torchvision.transforms.functional import pil_to_tensor, to_pil_image

		# gc.collect()

		if "txt2mask_init_image" in kwargs:
			self.init_image = kwargs["txt2mask_init_image"].copy()
		elif "init_images" not in self.Unprompted.shortcode_user_vars:
			self.log.error("No init_images found...")
			return
		else:
			self.init_image = self.Unprompted.shortcode_user_vars["init_images"][0].copy()

		method = self.Unprompted.parse_advanced(kwargs["method"], context) if "method" in kwargs else "clipseg"

		if method == "clipseg":
			mask_width = 512
			mask_height = 512
		else:
			mask_width = self.init_image.size[0]
			mask_height = self.init_image.size[1]

		device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
		if device == "cuda": torch.cuda.empty_cache()

		if "stamp" in kwargs:
			stamps = (self.Unprompted.parse_advanced(kwargs["stamp"], context)).split(self.Unprompted.Config.syntax.delimiter)

			stamp_x = int(float(self.Unprompted.parse_advanced(kwargs["stamp_x"], context))) if "stamp_x" in kwargs else 0
			stamp_y = int(float(self.Unprompted.parse_advanced(kwargs["stamp_y"], context))) if "stamp_y" in kwargs else 0
			stamp_x_orig = stamp_x
			stamp_y_orig = stamp_y
			stamp_method = self.Unprompted.parse_advanced(kwargs["stamp_method"], context) if "stamp_method" in kwargs else "stretch"

			for stamp in stamps:
				# Checks for file in images/stamps, otherwise assumes absolute path
				stamp_path = f"{self.Unprompted.base_dir}/images/stamps/{stamp}.png"
				if not os.path.exists(stamp_path): stamp_path = stamp
				if not os.path.exists(stamp_path):
					self.log.error(f"Stamp not found: {stamp_path}")
					continue

				stamp_img = Image.open(stamp_path).convert("RGBA")

				if stamp_method == "stretch":
					stamp_img = stamp_img.resize((self.init_image.size[0], self.init_image.size[1]))
				elif stamp_method == "center":
					stamp_x = stamp_x_orig + int((mask_width - stamp_img.size[0]) / 2)
					stamp_y = stamp_y_orig + int((mask_height - stamp_img.size[1]) / 2)

				stamp_blur = int(float(self.Unprompted.parse_advanced(kwargs["stamp_blur"], context))) if "stamp_blur" in kwargs else 0
				if stamp_blur:
					from PIL import ImageFilter
					blur = ImageFilter.GaussianBlur(stamp_blur)
					stamp_img = stamp_img.filter(blur)

				self.init_image.paste(stamp_img, (stamp_x, stamp_y), stamp_img)

		brush_mask_mode = self.Unprompted.parse_advanced(kwargs["mode"], context) if "mode" in kwargs else "add"
		self.show = True if "show" in pargs else False

		self.legacy_weights = True if "legacy_weights" in pargs else False
		smoothing = int(self.Unprompted.parse_advanced(kwargs["smoothing"], context)) if "smoothing" in kwargs else 20
		smoothing_kernel = None
		if smoothing > 0:
			smoothing_kernel = numpy.ones((smoothing, smoothing), numpy.float32) / (smoothing * smoothing)

		neg_smoothing = int(self.Unprompted.parse_advanced(kwargs["neg_smoothing"], context)) if "neg_smoothing" in kwargs else 20
		neg_smoothing_kernel = None
		if neg_smoothing > 0:
			neg_smoothing_kernel = numpy.ones((neg_smoothing, neg_smoothing), numpy.float32) / (neg_smoothing * neg_smoothing)

		# Pad the mask by applying a dilation or erosion
		mask_padding = int(self.Unprompted.parse_advanced(kwargs["padding"], context) if "padding" in kwargs else 0)
		neg_mask_padding = int(self.Unprompted.parse_advanced(kwargs["neg_padding"], context) if "neg_padding" in kwargs else 0)
		padding_dilation_kernel = None
		if (mask_padding != 0):
			padding_dilation_kernel = numpy.ones((abs(mask_padding), abs(mask_padding)), numpy.uint8)

		neg_padding_dilation_kernel = None
		if (neg_mask_padding != 0):
			neg_padding_dilation_kernel = numpy.ones((abs(neg_mask_padding), abs(neg_mask_padding)), numpy.uint8)

		prompts = content.split(self.Unprompted.Config.syntax.delimiter)
		prompt_parts = len(prompts)

		if "negative_mask" in kwargs:
			neg_parsed = self.Unprompted.parse_advanced(kwargs["negative_mask"], context)
			if len(neg_parsed) < 1: negative_prompts = None
			else:
				negative_prompts = neg_parsed.split(self.Unprompted.Config.syntax.delimiter)
				negative_prompt_parts = len(negative_prompts)
		else:
			negative_prompts = None

		mask_precision = min(255, int(self.Unprompted.parse_advanced(kwargs["precision"], context) if "precision" in kwargs else 100))
		neg_mask_precision = min(255, int(self.Unprompted.parse_advanced(kwargs["neg_precision"], context) if "neg_precision" in kwargs else 100))

		def overlay_mask_part(img_a, img_b, mode):
			if (mode == "discard"): img_a = ImageChops.darker(img_a, img_b)
			else: img_a = ImageChops.lighter(img_a, img_b)
			return (img_a)

		def gray_to_pil(img):
			return (Image.fromarray(cv2.cvtColor(img, cv2.COLOR_GRAY2RGBA)))

		def process_mask_parts(masks, mode, final_img=None, mask_precision=100, mask_padding=0, padding_dilation_kernel=None, smoothing_kernel=None):
			for i, mask in enumerate(masks):

				filename = f"mask_{mode}_{i}.png"

				if method == "clipseg":
					plt.imsave(filename, torch.sigmoid(mask[0]))
					img = cv2.imread(filename)
				# TODO: Figure out how to convert the plot above to numpy instead of re-loading image
				else:
					plt.imsave(filename, mask)
					img = cv2.imread(filename)
					img = cv2.resize(img, (mask_width, mask_height))

				if padding_dilation_kernel is not None:
					if (mask_padding > 0): img = cv2.dilate(img, padding_dilation_kernel, iterations=1)
					else: img = cv2.erode(img, padding_dilation_kernel, iterations=1)
				if smoothing_kernel is not None: img = cv2.filter2D(img, -1, smoothing_kernel)

				gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
				Image.fromarray(gray_image).save("mask_gray_test.png")
				(thresh, bw_image) = cv2.threshold(gray_image, mask_precision, 255, cv2.THRESH_BINARY)

				if (mode == "discard"): bw_image = numpy.invert(bw_image)

				# overlay mask parts
				bw_image = gray_to_pil(bw_image)
				if (i > 0 or final_img is not None): bw_image = overlay_mask_part(bw_image, final_img, mode)

				final_img = bw_image
			return (final_img)

		def get_mask():
			preds = []
			negative_preds = []
			image_pil = flatten(self.init_image, opts.img2img_background_color)

			if method == "fastsam":
				from ultralytics import YOLO
				from lib_unprompted.fastsam.utils import tools
				import clip
				import numpy as np
				import cv2

				fastsam_better_quality = bool(self.Unprompted.parse_advanced(kwargs["fastsam_better_quality"], context)) if "fastsam_better_quality" in kwargs else True
				fastsam_retina = bool(self.Unprompted.parse_advanced(kwargs["fastsam_retina"], context)) if "fastsam_retina" in kwargs else True
				fastsam_model_type = "YOLOv8s"
				fastsam_iou = float(self.Unprompted.parse_advanced(kwargs["fastsam_iou"], context)) if "fastsam_iou" in kwargs else 0.9
				fastsam_conf = float(self.Unprompted.parse_advanced(kwargs["fastsam_conf"], context)) if "fastsam_conf" in kwargs else 0.4
				fastsam_max_det = int(self.Unprompted.parse_advanced(kwargs["fastsam_max_det"], context)) if "fastsam_max_det" in kwargs else 100
				fastsam_size = int(self.Unprompted.parse_advanced(kwargs["fastsam_size"], context)) if "fastsam_size" in kwargs else 1024

				def fast_show_mask(
				    annotation,
				    random_color=False,
				    retinamask=True,
				    target_height=960,
				    target_width=960,
				):
					msak_sum = annotation.shape[0]
					height = annotation.shape[1]
					weight = annotation.shape[2]
					if device != "cpu":
						areas = torch.sum(annotation, dim=(1, 2))
						sorted_indices = torch.argsort(areas, descending=False)
						annotation = annotation[sorted_indices]
						# 找每个位置第一个非零值下标
						index = (annotation != 0).to(torch.long).argmax(dim=0)
						if random_color == True:
							color = torch.rand((msak_sum, 1, 1, 3)).to(annotation.device)
						else:
							color = torch.ones((msak_sum, 1, 1, 3)).to(annotation.device) * torch.tensor([30 / 255, 144 / 255, 255 / 255]).to(annotation.device)
						transparency = torch.ones((msak_sum, 1, 1, 1)).to(annotation.device) * 0.6
						visual = torch.cat([color, transparency], dim=-1)
						mask_image = torch.unsqueeze(annotation, -1) * visual
						# 按index取数，index指每个位置选哪个batch的数，把mask_image转成一个batch的形式
						show = torch.zeros((height, weight, 4)).to(annotation.device)
						h_indices, w_indices = torch.meshgrid(torch.arange(height), torch.arange(weight), indexing="ij")
					else:
						# 将annotation 按照面积 排序
						areas = np.sum(annotation, axis=(1, 2))
						sorted_indices = np.argsort(areas)
						annotation = annotation[sorted_indices]
						index = (annotation != 0).argmax(axis=0)
						if random_color == True:
							color = np.random.random((msak_sum, 1, 1, 3))
						else:
							color = np.ones((msak_sum, 1, 1, 3)) * np.array([30 / 255, 144 / 255, 255 / 255])
						transparency = np.ones((msak_sum, 1, 1, 1)) * 0.6
						visual = np.concatenate([color, transparency], axis=-1)
						mask_image = np.expand_dims(annotation, -1) * visual
						show = np.zeros((height, weight, 4))
						h_indices, w_indices = np.meshgrid(np.arange(height), np.arange(weight), indexing="ij")
					indices = (index[h_indices, w_indices], h_indices, w_indices, slice(None))
					# 使用向量化索引更新show的值
					show[h_indices, w_indices, :] = mask_image[indices]
					show_cpu = show.cpu().numpy()
					if retinamask == False:
						show_cpu = cv2.resize(show_cpu, (target_width, target_height), interpolation=cv2.INTER_NEAREST)
					return show_cpu

				sam_model_dir = f"{self.Unprompted.base_dir}/models/fastsam"
				os.makedirs(sam_model_dir, exist_ok=True)
				if fastsam_model_type == "YOLOv8x": sam_filename = "FastSAM-x.pt"
				else: sam_filename = "FastSAM-s.pt"
				sam_file = f"{sam_model_dir}/{sam_filename}"

				# Download model weights if we don't have them yet
				if not os.path.exists(sam_file):
					self.log.info("Downloading FastSAM model weights...")
					# TODO: The YOLOv8x model is too big to download directly from Gdrive, find another host that supports it. Not particularly urgent as the difference in quality between the two models seems negligible...
					if fastsam_model_type == "YOLOv8x": self.Unprompted.download_file(sam_file, "https://drive.google.com/uc?export=download&id=1m1sjY4ihXBU1fZXdQ-Xdj-mDltW-2Rqv")
					else: self.Unprompted.download_file(sam_file, f"https://drive.google.com/uc?export=download&id=10XmSj6mmpmRb8NhXbtiuO9cTTBwR_9SV")

				if self.cached_model == -1 or self.cached_model_method != method:
					model = YOLO(sam_file)
					clip_model, preprocess = clip.load("ViT-B/32", device=device)

					# Cache for future runs
					self.cached_model = model
					self.cached_clip_model = clip_model
					self.cached_preprocess = preprocess
					self.cached_model_method = method
				else:
					self.log.info("Using cached FastSAM model.")
					model = self.cached_model
					preprocess = self.cached_preprocess
					clip_model = self.cached_clip_model

				results = model(image_pil, imgsz=fastsam_size, device=device, retina_masks=fastsam_retina, iou=fastsam_iou, conf=fastsam_conf, max_det=fastsam_max_det)
				results = tools.format_results(results[0], 0)
				cropped_boxes, cropped_images, not_crop, filter_id, annot = tools.crop_image(results, image_pil)

				image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_BGR2RGB)
				original_h = image.shape[0]
				original_w = image.shape[1]

				def run_fastsam(text_prompts):
					scores = tools.retriev(clip_model, preprocess, cropped_boxes, text_prompts, device=device)
					max_idx = scores.argsort()
					max_idx = max_idx[-1]
					max_idx += sum(np.array(filter_id) <= int(max_idx))
					annotations = annot[max_idx]["segmentation"]
					annotations = np.array([annotations])

					if isinstance(annotations[0], dict):
						annotations = [annotation["segmentation"] for annotation in annotations]

					if fastsam_better_quality == True:
						if isinstance(annotations[0], torch.Tensor):
							annotations = np.array(annotations.cpu())
						for i, mask in enumerate(annotations):
							mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
							annotations[i] = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, np.ones((8, 8), np.uint8))
					# from PIL import Image
					# preds = Image.fromarray((preds * 255).astype(np.uint8))
					if device == "cpu": annotations = np.array(annotations)
					else:
						if isinstance(annotations[0], np.ndarray):
							annotations = torch.from_numpy(annotations)

					return fast_show_mask(
					    annotations,
					    random_color=False,
					    retinamask=fastsam_retina,
					    target_height=original_h,
					    target_width=original_w,
					)

				preds.append(run_fastsam(prompts))
				if negative_prompts: negative_preds.append(run_fastsam(negative_prompts))

			elif method == "clip_surgery":
				from lib_unprompted import clip_surgery as clip
				import cv2
				import numpy as np
				from PIL import Image
				from matplotlib import pyplot as plt
				from torchvision.transforms import Compose, Resize, ToTensor, Normalize
				from torchvision.transforms import InterpolationMode
				BICUBIC = InterpolationMode.BICUBIC
				from segment_anything import sam_model_registry, SamPredictor

				# default imagenet redundant features
				redundants = [
				    'a bad photo of a {}.', 'a photo of many {}.', 'a sculpture of a {}.', 'a photo of the hard to see {}.', 'a low resolution photo of the {}.', 'a rendering of a {}.', 'graffiti of a {}.', 'a bad photo of the {}.', 'a cropped photo of the {}.', 'a tattoo of a {}.', 'the embroidered {}.', 'a photo of a hard to see {}.', 'a bright photo of a {}.', 'a photo of a clean {}.', 'a photo of a dirty {}.', 'a dark photo of the {}.', 'a drawing of a {}.', 'a photo of my {}.', 'the plastic {}.', 'a photo of the cool {}.', 'a close-up photo of a {}.', 'a black and white photo of the {}.', 'a painting of the {}.', 'a painting of a {}.', 'a pixelated photo of the {}.', 'a sculpture of the {}.', 'a bright photo of the {}.', 'a cropped photo of a {}.', 'a plastic {}.', 'a photo of the dirty {}.', 'a jpeg corrupted photo of a {}.', 'a blurry photo of the {}.', 'a photo of the {}.', 'a good photo of the {}.', 'a rendering of the {}.', 'a {} in a video game.', 'a photo of one {}.',
				    'a doodle of a {}.', 'a close-up photo of the {}.', 'a photo of a {}.', 'the origami {}.', 'the {} in a video game.', 'a sketch of a {}.', 'a doodle of the {}.', 'a origami {}.', 'a low resolution photo of a {}.', 'the toy {}.', 'a rendition of the {}.', 'a photo of the clean {}.', 'a photo of a large {}.', 'a rendition of a {}.', 'a photo of a nice {}.', 'a photo of a weird {}.', 'a blurry photo of a {}.', 'a cartoon {}.', 'art of a {}.', 'a sketch of the {}.', 'a embroidered {}.', 'a pixelated photo of a {}.', 'itap of the {}.', 'a jpeg corrupted photo of the {}.', 'a good photo of a {}.', 'a plushie {}.', 'a photo of the nice {}.', 'a photo of the small {}.', 'a photo of the weird {}.', 'the cartoon {}.', 'art of the {}.', 'a drawing of the {}.', 'a photo of the large {}.', 'a black and white photo of a {}.', 'the plushie {}.', 'a dark photo of a {}.', 'itap of a {}.', 'graffiti of the {}.', 'a toy {}.', 'itap of my {}.', 'a photo of a cool {}.',
				    'a photo of a small {}.', 'a tattoo of the {}.', 'there is a {} in the scene.', 'there is the {} in the scene.', 'this is a {} in the scene.', 'this is the {} in the scene.', 'this is one {} in the scene.'
				]

				if "redundant_features" in kwargs: redundants.extend(kwargs["redundant_features"].split(self.Unprompted.Config.syntax.delimiter))
				self.bypass_sam = True if "bypass_sam" in pargs else False

				### Init CLIP and data
				if self.cached_model == -1 or self.cached_model_method != method:
					model, preprocess = clip.load("CS-ViT-B/16", device=device)
					model.eval()
					# Cache for future runs
					self.cached_model = model
					self.cached_transform = preprocess
				else:
					self.log.info("Using cached model(s) for CLIP_Surgery method")
					model = self.cached_model
					preprocess = self.cached_transform

				image = preprocess(image_pil).unsqueeze(0).to(device)
				cv2_img = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

				### CLIP Surgery for a single text, without fixed label sets
				with torch.no_grad():
					# CLIP architecture surgery acts on the image encoder
					image_features = model.encode_image(image)
					image_features = image_features / image_features.norm(dim=1, keepdim=True)

					# Prompt ensemble for text features with normalization
					text_features = clip.encode_text_with_prompt_ensemble(model, prompts, device)

					if (negative_prompts):
						negative_text_features = clip.encode_text_with_prompt_ensemble(model, negative_prompts, device)

					# Extract redundant features from an empty string
					redundant_features = clip.encode_text_with_prompt_ensemble(model, [""], device, redundants)

					# no sam
					if self.bypass_sam:

						def reg_inference(text_features):
							preds = []
							# Apply feature surgery for single text
							similarity = clip.clip_feature_surgery(image_features, text_features, redundant_features)
							similarity_map = clip.get_similarity_map(similarity[:, 1:, :], cv2_img.shape[:2])

							# Draw similarity map
							for b in range(similarity_map.shape[0]):
								for n in range(similarity_map.shape[-1]):
									vis = (similarity_map[b, :, :, n].cpu().numpy() * 255).astype('uint8')
									preds.append(vis)
							return (preds)

						preds = reg_inference(text_features)
						if (negative_prompts): negative_preds = reg_inference(negative_text_features)
					else:
						point_thresh = float(self.Unprompted.parse_advanced(kwargs["point_threshold"], context)) if "point_threshold" in kwargs else 0.98
						multimask_output = True if "multimask_output" in pargs else False

						# Init SAM
						if self.cached_predictor == -1 or self.cached_model_method != method:
							sam_model_dir = f"{self.Unprompted.base_dir}/models/segment_anything"
							os.makedirs(sam_model_dir, exist_ok=True)
							sam_filename = "sam_vit_h_4b8939.pth"
							sam_file = f"{sam_model_dir}/{sam_filename}"
							# Download model weights if we don't have them yet
							if not os.path.exists(sam_file):
								self.log.info("Downloading SAM model weights...")
								self.Unprompted.download_file(sam_file, f"https://dl.fbaipublicfiles.com/segment_anything/{sam_filename}")

							model_type = "vit_h"
							sam = sam_model_registry[model_type](checkpoint=sam_file)
							sam.to(device=device)
							predictor = SamPredictor(sam)

							self.cached_predictor = predictor
						else:
							predictor = self.cached_predictor

						predictor.set_image(np.array(image_pil))
						self.cached_model_method = method

						def sam_inference(text_features):
							preds = []

							# Combine features after removing redundant features and min-max norm
							sm = clip.clip_feature_surgery(image_features, text_features, redundant_features)[0, 1:, :]
							sm_norm = (sm - sm.min(0, keepdim=True)[0]) / (sm.max(0, keepdim=True)[0] - sm.min(0, keepdim=True)[0])
							sm_mean = sm_norm.mean(-1, keepdim=True)
							# get positive points from individual maps, and negative points from the mean map
							p, l = clip.similarity_map_to_points(sm_mean, cv2_img.shape[:2], t=point_thresh)
							num = len(p) // 2
							points = p[num:]  # negatives in the second half
							labels = [l[num:]]
							for i in range(sm.shape[-1]):
								p, l = clip.similarity_map_to_points(sm[:, i], cv2_img.shape[:2], t=point_thresh)
								num = len(p) // 2
								points = points + p[:num]  # positive in first half
								labels.append(l[:num])
							labels = np.concatenate(labels, 0)

							# Inference SAM with points from CLIP Surgery
							masks, scores, logits = predictor.predict(point_labels=labels, point_coords=np.array(points), multimask_output=multimask_output)
							mask = masks[np.argmax(scores)]
							mask = mask.astype('uint8')

							vis = cv2_img.copy()
							vis[mask > 0] = np.array([255, 255, 255], dtype=np.uint8)
							vis[mask == 0] = np.array([0, 0, 0], dtype=np.uint8)
							preds.append(vis)
							if self.show:
								for idx, mask in enumerate(masks):
									plt.imsave(f"mask{idx}.png", mask)

							return (preds)

						preds = sam_inference(text_features)
						if negative_prompts: negative_preds = sam_inference(negative_text_features)
			# clipseg method
			else:
				from lib_unprompted.stable_diffusion.clipseg.models.clipseg import CLIPDensePredT

				model_dir = f"{self.Unprompted.base_dir}/models/clipseg"

				os.makedirs(model_dir, exist_ok=True)

				d64_filename = "rd64-uni.pth" if self.legacy_weights else "rd64-uni-refined.pth"
				d64_file = f"{model_dir}/{d64_filename}"
				d16_file = f"{model_dir}/rd16-uni.pth"

				# Download model weights if we don't have them yet
				if not os.path.exists(d64_file):
					self.log.info("Downloading clipseg model weights...")
					self.Unprompted.download_file(d64_file, f"https://owncloud.gwdg.de/index.php/s/ioHbRzFx6th32hn/download?path=%2F&files={d64_filename}")
					self.Unprompted.download_file(d16_file, "https://owncloud.gwdg.de/index.php/s/ioHbRzFx6th32hn/download?path=%2F&files=rd16-uni.pth")

				# load model
				if self.cached_model == -1 or self.cached_model_method != method:
					self.log.debug("Loading clipseg model...")
					model = CLIPDensePredT(version='ViT-B/16', reduce_dim=64, complex_trans_conv=not self.legacy_weights)

					# non-strict, because we only stored decoder weights (not CLIP weights)
					model.load_state_dict(torch.load(d64_file, map_location=device), strict=False)
					model = model.eval().to(device=device)

					transform = transforms.Compose([
					    transforms.ToTensor(),
					    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
					    transforms.Resize((512, 512)),
					])

					# Cache for future runs
					self.cached_model = model
					self.cached_transform = transform
					self.cached_model_method = method
				else:
					self.log.info("Using cached clipseg model.")
					model = self.cached_model
					transform = self.cached_transform

				img = transform(image_pil).unsqueeze(0)

				# predict
				with torch.no_grad():
					if "image_prompt" in kwargs:
						from PIL import Image
						img_mask = flatten(Image.open(r"A:/inbox/test_mask.png"), opts.img2img_background_color)
						img_mask = transform(img_mask).unsqueeze(0)
						preds = model(img.to(device=device), img_mask.to(device=device))[0].cpu()
					else:
						preds = model(img.repeat(prompt_parts, 1, 1, 1).to(device=device), prompts)[0].cpu()

					if (negative_prompts): negative_preds = model(img.repeat(negative_prompt_parts, 1, 1, 1).to(device=device), negative_prompts)[0].cpu()

			# The below logic applies to all masking methods

			if "image_mask" not in self.Unprompted.shortcode_user_vars: self.Unprompted.shortcode_user_vars["image_mask"] = None

			if (brush_mask_mode == "add" and self.Unprompted.shortcode_user_vars["image_mask"] is not None):
				final_img = self.Unprompted.shortcode_user_vars["image_mask"].convert("RGBA").resize((mask_width, mask_height))
			else:
				final_img = None

			# process masking
			final_img = process_mask_parts(preds, "add", final_img, mask_precision, mask_padding, padding_dilation_kernel, smoothing_kernel)

			# process negative masking
			if (brush_mask_mode == "subtract" and self.Unprompted.shortcode_user_vars["image_mask"] is not None):
				self.Unprompted.shortcode_user_vars["image_mask"] = ImageOps.invert(self.Unprompted.shortcode_user_vars["image_mask"])
				self.Unprompted.shortcode_user_vars["image_mask"] = self.Unprompted.shortcode_user_vars["image_mask"].convert("RGBA").resize((mask_width, mask_height))
				final_img = overlay_mask_part(final_img, self.Unprompted.shortcode_user_vars["image_mask"], "discard")
			if (negative_prompts): final_img = process_mask_parts(negative_preds, "discard", final_img, neg_mask_precision, neg_mask_padding, neg_padding_dilation_kernel, neg_smoothing_kernel)

			if "size_var" in kwargs:
				img_data = final_img.load()
				# Count number of transparent pixels
				black_pixels = 0
				total_pixels = mask_width * mask_height
				for y in range(mask_height):
					for x in range(mask_width):
						pixel_data = img_data[x, y]
						if (pixel_data[0] == 0 and pixel_data[1] == 0 and pixel_data[2] == 0): black_pixels += 1
				subject_size = 1 - black_pixels / total_pixels
				self.Unprompted.shortcode_user_vars[kwargs["size_var"]] = subject_size

			# Inpaint sketch compatibility
			if "sketch_color" in kwargs:
				self.Unprompted.shortcode_user_vars["mode"] = 3

				this_color = kwargs["sketch_color"]
				# Convert to tuple for use with colorize
				if this_color[0].isdigit(): this_color = tuple(map(int, this_color.split(',')))
				paste_mask = ImageOps.colorize(final_img.convert("L"), black="black", white=this_color)

				# Convert black pixels to transparent
				paste_mask = paste_mask.convert('RGBA')
				mask_data = paste_mask.load()
				width, height = paste_mask.size
				for y in range(height):
					for x in range(width):
						if mask_data[x, y] == (0, 0, 0, 255): mask_data[x, y] = (0, 0, 0, 0)

				# Match size just in case
				paste_mask = paste_mask.resize((image_pil.size[0], image_pil.size[1]))

				# Workaround for A1111 not including mask_alpha in p object
				if "sketch_alpha" in kwargs:
					alpha_channel = paste_mask.getchannel('A')
					new_alpha = alpha_channel.point(lambda i: int(float(kwargs["sketch_alpha"])) if i > 0 else 0)
					paste_mask.putalpha(new_alpha)

				# Workaround for A1111 bug, not accepting inpaint_color_sketch param w/ blur
				if (self.Unprompted.shortcode_user_vars["mask_blur"] > 0):
					from PIL import ImageFilter
					blur = ImageFilter.GaussianBlur(self.Unprompted.shortcode_user_vars["mask_blur"])
					paste_mask = paste_mask.filter(blur)
					self.Unprompted.shortcode_user_vars["mask_blur"] = 0

				# Paste mask on
				image_pil.paste(paste_mask, box=None, mask=paste_mask)

				self.Unprompted.shortcode_user_vars["init_images"][0] = image_pil
				# not used by SD, just used to append to our GUI later
				self.Unprompted.shortcode_user_vars["colorized_mask"] = paste_mask

				# Assign webui vars, note - I think it should work this way but A1111 doesn't appear to store some of these in p obj
				# note: inpaint_color_sketch = flattened image with mask on top
				# self.Unprompted.shortcode_user_vars["inpaint_color_sketch"] = image_pil
				# note: inpaint_color_sketch_orig = the init image
				# self.Unprompted.shortcode_user_vars["inpaint_color_sketch_orig"] = self.Unprompted.shortcode_user_vars["init_images"][0]
				# return image_pil

			else:
				if ("mode" in self.Unprompted.shortcode_user_vars and self.Unprompted.shortcode_user_vars["mode"] != 5):  # 5 =  batch processing
					self.Unprompted.shortcode_user_vars["mode"] = 4  # "mask upload" mode to avoid unnecessary processing
				if ("mask_blur" in self.Unprompted.shortcode_user_vars and self.Unprompted.shortcode_user_vars["mask_blur"] > 0):
					from PIL import ImageFilter
					blur = ImageFilter.GaussianBlur(self.Unprompted.shortcode_user_vars["mask_blur"])
					final_img = final_img.filter(blur)
					self.Unprompted.shortcode_user_vars["mask_blur"] = 0

			# Free up memory
			if "unload_model" in pargs:
				self.model = -1
				self.cached_model = -1
				self.cached_model_method = ""
				self.cached_predictor = -1
				self.cached_preprocess = -1
				self.cached_clip_model = -1

			return final_img

		# Set up processor parameters correctly
		self.image_mask = get_mask().resize((self.init_image.width, self.init_image.height))

		if "return_image" in pargs: return (self.image_mask)

		if "mode" in self.Unprompted.shortcode_user_vars:
			self.Unprompted.shortcode_user_vars["mode"] = max(5, self.Unprompted.shortcode_user_vars["mode"])
		self.Unprompted.shortcode_user_vars["image_mask"] = self.image_mask

		# Copy code from modules/processing.py, necessary for batch processing
		if "mask" in self.Unprompted.shortcode_user_vars and self.Unprompted.shortcode_user_vars["mask"] is not None:
			self.log.warning("Detected batch tab tensor mask, attempting to update it...")
			latmask = self.image_mask.convert('RGB').resize((self.Unprompted.shortcode_user_vars["init_latent"].shape[3], self.Unprompted.shortcode_user_vars["init_latent"].shape[2]))
			latmask = numpy.moveaxis(numpy.array(latmask, dtype=numpy.float32), 2, 0) / 255
			latmask = latmask[0]
			latmask = numpy.around(latmask)
			latmask = numpy.tile(latmask[None], (4, 1, 1))
			self.Unprompted.shortcode_user_vars["mask"] = torch.asarray(1.0 - latmask).to(device).type(self.Unprompted.main_p.sd_model.dtype)
			self.Unprompted.shortcode_user_vars["nmask"] = torch.asarray(latmask).to(device).type(self.Unprompted.main_p.sd_model.dtype)

		# self.Unprompted.shortcode_user_vars["mmask"]=self.Unprompted.shortcode_user_vars["mask"]
		self.Unprompted.shortcode_user_vars["mask_for_overlay"] = self.image_mask
		self.Unprompted.shortcode_user_vars["latent_mask"] = None  # fixes inpainting full resolution
		arr = {}
		arr["image"] = self.init_image
		arr["mask"] = self.image_mask
		self.Unprompted.shortcode_user_vars["init_img_with_mask"] = arr
		self.Unprompted.shortcode_user_vars["init_mask"] = self.image_mask  # TODO: Not sure if used anymore

		if "save" in kwargs: self.image_mask.save(f"{self.Unprompted.parse_advanced(kwargs['save'],context)}.png")

		return ""

	def after(self, p=None, processed=None):
		from torchvision.transforms.functional import pil_to_tensor, to_pil_image
		from torchvision.utils import draw_segmentation_masks

		if self.image_mask and self.show:
			if "mode" not in self.Unprompted.shortcode_user_vars or self.Unprompted.shortcode_user_vars["mode"] >= 4: processed.images.append(self.image_mask)
			else: processed.images.append(self.Unprompted.shortcode_user_vars["colorized_mask"])

			overlayed_init_img = draw_segmentation_masks(pil_to_tensor(self.Unprompted.shortcode_user_vars["init_images"][0]), pil_to_tensor(self.image_mask.convert("L")) > 0)
			processed.images.append(to_pil_image(overlayed_init_img))
			self.image_mask = None
			self.show = False
			return processed

	def ui(self, gr):
		with gr.Accordion("⚙️ General Settings", open=False):
			gr.Radio(label="Masking tech method (clipseg is most accurate) 🡢 method", choices=["clipseg", "clip_surgery", "fastsam"], value="clipseg", interactive=True)
			gr.Radio(label="Mask blend mode 🡢 mode", choices=["add", "subtract", "discard"], value="add", interactive=True)
			gr.Textbox(label="Mask color, enables Inpaint Sketch mode 🡢 sketch_color", max_lines=1, placeholder="e.g. tan or 127,127,127")
			gr.Number(label="Mask alpha, must be used in conjunction with mask color 🡢 sketch_alpha", value=0, interactive=True)
			gr.Textbox(label="Save the mask size to the following variable 🡢 size_var", max_lines=1)
			gr.Checkbox(label="Show mask in output 🡢 show")
			gr.Checkbox(label="Debug mode (saves mask images to root WebUI folder) 🡢 debug")
			gr.Checkbox(label="Unload model after inference (for low memory devices) 🡢 unload_model")
			gr.Checkbox(label="Use clipseg legacy weights 🡢 legacy_weights")
		with gr.Accordion("➕ Positive Mask", open=False):
			gr.Number(label="Precision of selected area 🡢 precision", value=100, interactive=True)
			gr.Number(label="Padding radius in pixels 🡢 padding", value=0, interactive=True)
			gr.Number(label="Smoothing radius in pixels 🡢 smoothing", value=20, interactive=True)
		with gr.Accordion("➖ Negative Mask", open=False):
			gr.Textbox(label="Negative mask prompt 🡢 negative_mask", max_lines=1)
			gr.Number(label="Negative mask precision of selected area 🡢 neg_precision", value=100, interactive=True)
			gr.Number(label="Negative mask padding radius in pixels 🡢 neg_padding", value=0, interactive=True)
			gr.Number(label="Negative mask smoothing radius in pixels 🡢 neg_smoothing", value=20, interactive=True)
		with gr.Accordion("🖼️ Stamp", open=False):
			gr.Textbox(label="Stamp file(s) 🡢 stamp", max_lines=1, placeholder="Looks for PNG file in unprompted/images/stamps OR absolute path")
			gr.Dropdown(label="Stamp method 🡢 stamp_method", choices=["stretch", "center"], value="stretch", interactive=True)
			gr.Number(label="Stamp X 🡢 stamp_x", value=0, interactive=True)
			gr.Number(label="Stamp Y 🡢 stamp_y", value=0, interactive=True)
