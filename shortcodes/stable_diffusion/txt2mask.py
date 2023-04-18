
class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.image_mask = None
		self.show = False
		self.description = "Creates an image mask from the content for use with inpainting."
		self.cached_model = -1
		self.cached_transform = -1

	def run_block(self, pargs, kwargs, context, content):
		from PIL import ImageChops, Image, ImageOps
		import os.path
		import torch
		from torchvision import transforms
		from matplotlib import pyplot as plt
		import cv2
		import numpy
		from modules.images import flatten
		from modules.shared import opts
		from torchvision.transforms.functional import pil_to_tensor, to_pil_image

		if "txt2mask_init_image" in kwargs:
			self.init_image = kwargs["txt2mask_init_image"]
		elif "init_images" not in self.Unprompted.shortcode_user_vars:
			self.Unprompted.log("No init_images found...")
			return
		else: self.init_image = self.Unprompted.shortcode_user_vars["init_images"][0]

		method = self.Unprompted.parse_advanced(kwargs["method"],context) if "method" in kwargs else "clipseg"

		if method == "clipseg":
			mask_width = 512
			mask_height = 512
		elif method == "sam":
			import launch
			if not launch.is_installed("groundingdino"):
				self.Unprompted.log("Attempting to install GroundingDINO library. Buckle up bro")
				try:
					launch.run_pip("install git+https://github.com/IDEA-Research/GroundingDINO","requirements for Unprompted - txt2mask SAM method")
				except Exception as e:
					self.Unprompted.log(f"GroundingDINO problem: {e}",context="ERROR")
					self.Unprompted.log(f"Please open an issue on their repo, not mine.",context="ERROR")
					return ""

			mask_width = self.Unprompted.shortcode_user_vars["width"]
			mask_height = self.Unprompted.shortcode_user_vars["height"]

		device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

		brush_mask_mode = self.Unprompted.parse_advanced(kwargs["mode"],context) if "mode" in kwargs else "add"
		self.show = True if "show" in pargs else False


		box_thresh = float(self.Unprompted.parse_advanced(kwargs["box_threshold"],context)) if "box_threshold" in kwargs else 0.3
		text_thresh = float(self.Unprompted.parse_advanced(kwargs["text_threshold"],context)) if "text_threshold" in kwargs else 0.25

		self.legacy_weights = True if "legacy_weights" in pargs else False
		smoothing = int(self.Unprompted.parse_advanced(kwargs["smoothing"],context)) if "smoothing" in kwargs else 20
		smoothing_kernel = None
		if smoothing > 0:
			smoothing_kernel = numpy.ones((smoothing,smoothing),numpy.float32)/(smoothing*smoothing)

		neg_smoothing = int(self.Unprompted.parse_advanced(kwargs["neg_smoothing"],context)) if "neg_smoothing" in kwargs else 20
		neg_smoothing_kernel = None
		if neg_smoothing > 0:
			neg_smoothing_kernel = numpy.ones((neg_smoothing,neg_smoothing),numpy.float32)/(neg_smoothing*neg_smoothing)

		# Pad the mask by applying a dilation or erosion
		mask_padding = int(self.Unprompted.parse_advanced(kwargs["padding"],context) if "padding" in kwargs else 0)
		neg_mask_padding = int(self.Unprompted.parse_advanced(kwargs["neg_padding"],context) if "neg_padding" in kwargs else 0)
		padding_dilation_kernel = None
		if (mask_padding != 0):
			padding_dilation_kernel = numpy.ones((abs(mask_padding), abs(mask_padding)), numpy.uint8)

		neg_padding_dilation_kernel = None
		if (neg_mask_padding != 0):
			neg_padding_dilation_kernel = numpy.ones((abs(neg_mask_padding), abs(neg_mask_padding)), numpy.uint8)

		prompts = content.split(self.Unprompted.Config.syntax.delimiter)
		prompt_parts = len(prompts)

		if "negative_mask" in kwargs:
			neg_parsed = self.Unprompted.parse_advanced(kwargs["negative_mask"],context)
			if len(neg_parsed) < 1: negative_prompts = None
			else:
				negative_prompts = neg_parsed.split(self.Unprompted.Config.syntax.delimiter)
				negative_prompt_parts = len(negative_prompts)
		else: negative_prompts = None

		mask_precision = min(255,int(self.Unprompted.parse_advanced(kwargs["precision"],context) if "precision" in kwargs else 100))
		neg_mask_precision = min(255,int(self.Unprompted.parse_advanced(kwargs["neg_precision"],context) if "neg_precision" in kwargs else 100))

		def overlay_mask_part(img_a,img_b,mode):
			if (mode == "discard"): img_a = ImageChops.darker(img_a, img_b)
			else: img_a = ImageChops.lighter(img_a, img_b)
			return(img_a)

		def gray_to_pil(img):
			return (Image.fromarray(cv2.cvtColor(img,cv2.COLOR_GRAY2RGBA)))

		def process_mask_parts(masks, mode, final_img = None, mask_precision=100, mask_padding=0, padding_dilation_kernel=None, smoothing_kernel=None):
			for i, mask in enumerate(masks):
				
				filename = f"mask_{mode}_{i}.png"
				if method == "clipseg":
					plt.imsave(filename,torch.sigmoid(mask[0]))
					img = cv2.imread(filename)
				# TODO: Figure out how to convert the plot above to numpy instead of re-loading image
				else:
					plt.imsave(filename,mask)
					img = cv2.imread(filename)
					img = cv2.resize(img,(mask_width,mask_height))
					


				if padding_dilation_kernel is not None:
					if (mask_padding > 0): img = cv2.dilate(img,padding_dilation_kernel,iterations=1)
					else: img = cv2.erode(img,padding_dilation_kernel,iterations=1)
				if smoothing_kernel is not None: img = cv2.filter2D(img,-1,smoothing_kernel)

				gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
				(thresh, bw_image) = cv2.threshold(gray_image, mask_precision, 255, cv2.THRESH_BINARY)

				if (mode == "discard"): bw_image = numpy.invert(bw_image)

				# overlay mask parts
				bw_image = gray_to_pil(bw_image)
				if (i > 0 or final_img is not None): bw_image = overlay_mask_part(bw_image,final_img,mode)

				final_img = bw_image
			return(final_img)
			
		def get_mask():
			image_pil = flatten(self.init_image, opts.img2img_background_color)

			if method == "sam":
				# Grounding DINO
				import groundingdino.datasets.transforms as T
				from groundingdino.models import build_model
				from groundingdino.util import box_ops
				from groundingdino.util.slconfig import SLConfig
				from groundingdino.util.utils import clean_state_dict, get_phrases_from_posmap

				# segment anything
				from segment_anything import build_sam, SamPredictor 
				import cv2
				import numpy as np
				import matplotlib.pyplot as plt

				def get_grounding_output(model, image, caption, box_threshold, text_threshold, with_logits=True, device="cpu"):
					caption = caption.lower()
					caption = caption.strip()
					if not caption.endswith("."):
						caption = caption + "."
					model = model.to(device)
					image = image.to(device)
					with torch.no_grad():
						outputs = model(image[None], captions=[caption])
					logits = outputs["pred_logits"].cpu().sigmoid()[0]  # (nq, 256)
					boxes = outputs["pred_boxes"].cpu()[0]  # (nq, 4)
					logits.shape[0]

					# filter output
					logits_filt = logits.clone()
					boxes_filt = boxes.clone()
					filt_mask = logits_filt.max(dim=1)[0] > box_threshold
					logits_filt = logits_filt[filt_mask]  # num_filt, 256
					boxes_filt = boxes_filt[filt_mask]  # num_filt, 4
					logits_filt.shape[0]

					# get phrase
					tokenlizer = model.tokenizer
					tokenized = tokenlizer(caption)
					# build pred
					pred_phrases = []
					for logit, box in zip(logits_filt, boxes_filt):
						pred_phrase = get_phrases_from_posmap(logit > text_threshold, tokenized, tokenlizer)
						if with_logits:
							pred_phrases.append(pred_phrase + f"({str(logit.max().item())[:4]})")
						else:
							pred_phrases.append(pred_phrase)

					return boxes_filt, pred_phrases

				sam_model_dir = f"{self.Unprompted.base_dir}/models/segment_anything"
				os.makedirs(sam_model_dir, exist_ok=True)
				sam_filename = "sam_vit_h_4b8939.pth"
				sam_file = f"{sam_model_dir}/{sam_filename}"

				# Download model weights if we don't have them yet
				if not os.path.exists(sam_file):
					print("Downloading SAM model weights...")
					self.Unprompted.download_file(sam_file,f"https://dl.fbaipublicfiles.com/segment_anything/{sam_filename}")
				
				dino_model_dir = f"{self.Unprompted.base_dir}/models/groundingdino"
				os.makedirs(dino_model_dir, exist_ok=True)
				dino_filename = "groundingdino_swint_ogc.pth"
				dino_file = f"{dino_model_dir}/{dino_filename}"

				if not os.path.exists(dino_file):
					print("Downloading GroundingDINO model weights...")
					self.Unprompted.download_file(dino_file,f"https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/{dino_filename}")

				model_config_path = f"{self.Unprompted.base_dir}/lib_unprompted/groundingdino/config/GroundingDINO_SwinT_OGC.py"

				# load model
				if self.cached_model == -1:
					args = SLConfig.fromfile(model_config_path)
					args.device = device
					model = build_model(args)
					checkpoint = torch.load(dino_file, map_location="cpu")
					load_res = model.load_state_dict(clean_state_dict(checkpoint["model"]), strict=False)
					print(load_res)
					_ = model.eval()

					transform = T.Compose(
						[
							T.RandomResize([800], max_size=1333),
							T.ToTensor(),
							T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
						]
					)
					self.cached_model = model
					self.cached_transform = transform

				else:
					self.Unprompted.log("Using cached GroundingDINO model.")
					model = self.cached_model
					transform = self.cached_transform


				def sam_infer(boxes_filt):
					for i in range(boxes_filt.size(0)):
						boxes_filt[i] = boxes_filt[i] * torch.Tensor([W, H, W, H])
						boxes_filt[i][:2] -= boxes_filt[i][2:] / 2
						boxes_filt[i][2:] += boxes_filt[i][:2]

					boxes_filt = boxes_filt.cpu()
					transformed_boxes = predictor.transform.apply_boxes_torch(boxes_filt, img.shape[:2]).to(device)

					masks, _, _ = predictor.predict_torch(
						point_coords = None,
						point_labels = None,
						boxes = transformed_boxes.to(device),
						multimask_output = False,
					)
					
					preds = []
					value = 0
					mask_img = torch.zeros(masks.shape[-2:])
					for idx, mask in enumerate(masks):
						mask_img[mask.cpu().numpy()[0] == True] = value + idx + 1
					preds.append(mask_img.numpy())

					return(preds)

				# run grounding dino model
				img, _ = transform(image_pil,None)
				boxes_filt, pred_phrases = get_grounding_output(model, img, prompts[0], box_thresh, text_thresh, device=device)
				if (negative_prompts):
					neg_boxes_filt, pred_phrases = get_grounding_output(model, img, negative_prompts[0], box_thresh, text_thresh, device=device)

				# initialize SAM
				predictor = SamPredictor(build_sam(checkpoint=sam_file).to(device))
				img = numpy.array(image_pil) # cv2.imread(image_path)
				img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
				predictor.set_image(img)

				size = image_pil.size
				H, W = size[0], size[1]

				preds = sam_infer(boxes_filt)
				if (negative_prompts): negative_preds = sam_infer(neg_boxes_filt)		

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
					print("Downloading clipseg model weights...")
					self.Unprompted.download_file(d64_file,f"https://owncloud.gwdg.de/index.php/s/ioHbRzFx6th32hn/download?path=%2F&files={d64_filename}")
					self.Unprompted.download_file(d16_file,"https://owncloud.gwdg.de/index.php/s/ioHbRzFx6th32hn/download?path=%2F&files=rd16-uni.pth")


				# load model
				if self.cached_model == -1:
					self.Unprompted.log("Loading clipseg model...")
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
				else:
					self.Unprompted.log("Using cached clipseg model.")
					model = self.cached_model
					transform = self.cached_transform

				img = transform(image_pil).unsqueeze(0)

				# predict
				with torch.no_grad():
					preds = model(img.repeat(prompt_parts,1,1,1).to(device=device), prompts)[0].cpu()
					if (negative_prompts): negative_preds = model(img.repeat(negative_prompt_parts,1,1,1).to(device=device), negative_prompts)[0].cpu()

			# All of the below logic applies to both clipseg and sam

			if "image_mask" not in self.Unprompted.shortcode_user_vars: self.Unprompted.shortcode_user_vars["image_mask"] = None
				
			if (brush_mask_mode == "add" and self.Unprompted.shortcode_user_vars["image_mask"] is not None):
				final_img = self.Unprompted.shortcode_user_vars["image_mask"].convert("RGBA").resize((mask_width,mask_height))
			else: final_img = None

			# process masking
			final_img = process_mask_parts(preds,"add",final_img, mask_precision, mask_padding, padding_dilation_kernel, smoothing_kernel)

			# process negative masking
			if (brush_mask_mode == "subtract" and self.Unprompted.shortcode_user_vars["image_mask"] is not None):
				self.Unprompted.shortcode_user_vars["image_mask"] = ImageOps.invert(self.Unprompted.shortcode_user_vars["image_mask"])
				self.Unprompted.shortcode_user_vars["image_mask"] = self.Unprompted.shortcode_user_vars["image_mask"].convert("RGBA").resize((mask_width,mask_height))
				final_img = overlay_mask_part(final_img,self.Unprompted.shortcode_user_vars["image_mask"],"discard")
			if (negative_prompts): final_img = process_mask_parts(negative_preds,"discard",final_img, neg_mask_precision,neg_mask_padding, neg_padding_dilation_kernel, neg_smoothing_kernel)

			if "size_var" in kwargs:
				img_data = final_img.load()
				# Count number of transparent pixels
				black_pixels = 0
				total_pixels = mask_width * mask_height
				for y in range(mask_height):
					for x in range(mask_width):
						pixel_data = img_data[x,y]
						if (pixel_data[0] == 0 and pixel_data[1] == 0 and pixel_data[2] == 0): black_pixels += 1
				subject_size = 1 - black_pixels / total_pixels
				self.Unprompted.shortcode_user_vars[kwargs["size_var"]] = subject_size

			# Inpaint sketch compatibility
			if "sketch_color" in kwargs:
				self.Unprompted.shortcode_user_vars["mode"] = 3

				this_color = kwargs["sketch_color"]
				# Convert to tuple for use with colorize
				if this_color[0].isdigit(): this_color = tuple(map(int,this_color.split(',')))
				paste_mask  = ImageOps.colorize(final_img.convert("L"),black="black",white=this_color)

				# Convert black pixels to transparent
				paste_mask = paste_mask.convert('RGBA')
				mask_data = paste_mask.load()
				width, height = paste_mask.size
				for y in range(height):
					for x in range(width):
						if mask_data[x, y] == (0, 0, 0, 255): mask_data[x, y] = (0, 0, 0, 0)

				# Match size just in case
				paste_mask = paste_mask.resize((image_pil.size[0],image_pil.size[1]))

				# Workaround for A1111 not including mask_alpha in p object
				if "sketch_alpha" in kwargs:
					alpha_channel = paste_mask.getchannel('A')
					new_alpha = alpha_channel.point(lambda i: int(float(kwargs["sketch_alpha"])) if i>0 else 0)
					paste_mask.putalpha(new_alpha)

				# Workaround for A1111 bug, not accepting inpaint_color_sketch param w/ blur
				if (self.Unprompted.shortcode_user_vars["mask_blur"] > 0):
					from PIL import ImageFilter
					blur = ImageFilter.GaussianBlur(self.Unprompted.shortcode_user_vars["mask_blur"])
					paste_mask = paste_mask.filter(blur)
					self.Unprompted.shortcode_user_vars["mask_blur"] = 0

				# Paste mask on
				image_pil.paste(paste_mask,box=None,mask=paste_mask)
				
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
				self.Unprompted.shortcode_user_vars["mode"] = 4 # "mask upload" mode to avoid unnecessary processing
				if ("mask_blur" in self.Unprompted.shortcode_user_vars and self.Unprompted.shortcode_user_vars["mask_blur"] > 0):
					from PIL import ImageFilter
					blur = ImageFilter.GaussianBlur(self.Unprompted.shortcode_user_vars["mask_blur"])
					final_img = final_img.filter(blur)
					self.Unprompted.shortcode_user_vars["mask_blur"] = 0


			if "unload_model" in pargs:
				self.model = -1
				self.cached_model = -1

			return final_img

		# Set up processor parameters correctly
		self.image_mask = get_mask().resize((self.init_image.width,self.init_image.height))
		
		if "return_image" in pargs: return(self.image_mask)
		
		self.Unprompted.shortcode_user_vars["mode"] = max(4,self.Unprompted.shortcode_user_vars["mode"])
		self.Unprompted.shortcode_user_vars["image_mask"] =self.image_mask
		self.Unprompted.shortcode_user_vars["mask"]=self.image_mask
		self.Unprompted.shortcode_user_vars["mask_for_overlay"] = self.image_mask
		self.Unprompted.shortcode_user_vars["latent_mask"] = None # fixes inpainting full resolution
		arr = {}
		arr["image"] = self.init_image
		arr["mask"] = self.image_mask
		self.Unprompted.shortcode_user_vars["init_img_with_mask"] = arr
		self.Unprompted.shortcode_user_vars["init_mask"] = self.image_mask

		if "save" in kwargs: self.image_mask.save(f"{self.Unprompted.parse_advanced(kwargs['save'],context)}.png")

		return ""
	
	def after(self,p=None,processed=None):
		from torchvision.transforms.functional import pil_to_tensor, to_pil_image
		from torchvision.utils import draw_segmentation_masks
		
		if self.image_mask and self.show:
			if self.Unprompted.shortcode_user_vars["mode"] == 4: processed.images.append(self.image_mask)
			else: processed.images.append(self.Unprompted.shortcode_user_vars["colorized_mask"])
			
			overlayed_init_img = draw_segmentation_masks(pil_to_tensor(self.Unprompted.shortcode_user_vars["init_images"][0]), pil_to_tensor(self.image_mask.convert("L")) > 0)
			processed.images.append(to_pil_image(overlayed_init_img))
			self.image_mask = None
			self.show = False
			return processed
	
	def ui(self,gr):
		gr.Radio(label="Mask blend mode 🡢 mode",choices=["add","subtract","discard"],value="add",interactive=True)
		gr.Radio(label="Masking tech method 🡢 method",choices=["sam","clipseg"],value="sam",interactive=True)
		gr.Checkbox(label="Show mask in output 🡢 show")
		gr.Checkbox(label="Use clipseg legacy weights 🡢 legacy_weights")
		gr.Number(label="Precision of selected area 🡢 precision",value=100,interactive=True)
		gr.Number(label="Padding radius in pixels 🡢 padding",value=0,interactive=True)
		gr.Number(label="Smoothing radius in pixels 🡢 smoothing",value=20,interactive=True)
		gr.Textbox(label="Negative mask prompt 🡢 negative_mask",max_lines=1)
		gr.Number(label="Negative mask precision of selected area 🡢 neg_precision",value=100,interactive=True)
		gr.Number(label="Negative mask padding radius in pixels 🡢 neg_padding",value=0,interactive=True)
		gr.Number(label="Negative mask smoothing radius in pixels 🡢 neg_smoothing",value=20,interactive=True)
		gr.Textbox(label="Mask color, enables Inpaint Sketch mode 🡢 sketch_color",max_lines=1,placeholder="e.g. tan or 127,127,127")
		gr.Number(label="Mask alpha, must be used in conjunction with mask color 🡢 sketch_alpha",value=0,interactive=True)
		gr.Textbox(label="Save the mask size to the following variable 🡢 size_var",max_lines=1)
		gr.Checkbox(label="Unload model after inference (for low memory devices) 🡢 unload_model")