class Shortcode():
	"""Creates an image mask from the content for use with inpainting."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.image_mask = None
		self.show = False
	def run_block(self, pargs, kwargs, context, content):
		from lib.stable_diffusion.clipseg.models.clipseg import CLIPDensePredT

		from PIL import ImageChops, Image, ImageOps
		import os.path
		import torch
		from torchvision import transforms
		from matplotlib import pyplot as plt
		import cv2
		import numpy

		brush_mask_mode = self.Unprompted.parse_advanced(kwargs["mode"],context) if "mode" in kwargs else "add"
		self.show = True if "show" in pargs else False

		prompts = content.split(self.Unprompted.Config.syntax.delimiter)
		prompt_parts = len(prompts)

		if "negative_mask" in kwargs:
			negative_prompts = (self.Unprompted.parse_advanced(kwargs["negative_mask"],context)).split(self.Unprompted.Config.syntax.delimiter)
			negative_prompt_parts = len(negative_prompts)
		else: negative_prompts = None

		mask_precision = min(255,int(self.Unprompted.parse_advanced(kwargs["precision"],context) if "precision" in kwargs else 100))
		mask_padding = int(self.Unprompted.parse_advanced(kwargs["padding"],context) if "padding" in kwargs else 0)

		def overlay_mask_part(img_a,img_b,mode):
			if (mode == "discard"): img_a = ImageChops.darker(img_a, img_b)
			else: img_a = ImageChops.lighter(img_a, img_b)
			return(img_a)

		def gray_to_pil(img):
			return (Image.fromarray(cv2.cvtColor(img,cv2.COLOR_GRAY2RGBA)))

		def center_crop(img,new_width,new_height):
			width, height = img.size   # Get dimensions
			left = (width - new_width)/2
			top = (height - new_height)/2
			right = (width + new_width)/2
			bottom = (height + new_height)/2
			# Crop the center of the image
			return(img.crop((left, top, right, bottom)))

		def process_mask_parts(these_preds,these_prompt_parts,mode,final_img = None):
			for i in range(these_prompt_parts):
				filename = f"mask_{mode}_{i}.png"
				plt.imsave(filename,torch.sigmoid(these_preds[i][0]))

				# TODO: Figure out how to convert the plot above to numpy instead of re-loading image
				img = cv2.imread(filename)
				gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
				(thresh, bw_image) = cv2.threshold(gray_image, mask_precision, 255, cv2.THRESH_BINARY)

				if (mode == "discard"): bw_image = numpy.invert(bw_image)

				# overlay mask parts
				bw_image = gray_to_pil(bw_image)
				if (i > 0 or final_img is not None): bw_image = overlay_mask_part(bw_image,final_img,mode)

				final_img = bw_image
			return(final_img)

		def get_mask():
			# load model
			model = CLIPDensePredT(version='ViT-B/16', reduce_dim=64)
			model.eval()
			model_dir = f"{self.Unprompted.base_dir}/lib/stable_diffusion/clipseg/weights"
			os.makedirs(model_dir, exist_ok=True)
			d64_file = f"{model_dir}/rd64-uni.pth"
			d16_file = f"{model_dir}/rd16-uni.pth"

			# Download model weights if we don't have them yet
			if not os.path.exists(d64_file):
				print("Downloading clipseg model weights...")
				self.Unprompted.download_file(d64_file,"https://owncloud.gwdg.de/index.php/s/ioHbRzFx6th32hn/download?path=%2F&files=rd64-uni.pth")
				self.Unprompted.download_file(d16_file,"https://owncloud.gwdg.de/index.php/s/ioHbRzFx6th32hn/download?path=%2F&files=rd16-uni.pth")

			# non-strict, because we only stored decoder weights (not CLIP weights)
			model.load_state_dict(torch.load(d64_file, map_location=torch.device('cuda')), strict=False);	

			transform = transforms.Compose([
				transforms.ToTensor(),
				transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
				transforms.Resize((512, 512)),
			])
			img = transform(self.Unprompted.shortcode_user_vars["init_images"][0]).unsqueeze(0)

			# predict
			with torch.no_grad():
				preds = model(img.repeat(prompt_parts,1,1,1), prompts)[0]
				if (negative_prompts): negative_preds = model(img.repeat(negative_prompt_parts,1,1,1), negative_prompts)[0]

			if "image_mask" not in self.Unprompted.shortcode_user_vars: self.Unprompted.shortcode_user_vars["image_mask"] = None
			
			if (brush_mask_mode == "add" and self.Unprompted.shortcode_user_vars["image_mask"] is not None):
				final_img = self.Unprompted.shortcode_user_vars["image_mask"].convert("RGBA").resize((512,512))
			else: final_img = None

			# process masking
			final_img = process_mask_parts(preds,prompt_parts,"add",final_img)

			# process negative masking
			if (brush_mask_mode == "subtract" and self.Unprompted.shortcode_user_vars["image_mask"] is not None):
				self.Unprompted.shortcode_user_vars["image_mask"] = ImageOps.invert(self.Unprompted.shortcode_user_vars["image_mask"])
				self.Unprompted.shortcode_user_vars["image_mask"] = self.Unprompted.shortcode_user_vars["image_mask"].convert("RGBA").resize((512,512))
				final_img = overlay_mask_part(final_img,self.Unprompted.shortcode_user_vars["image_mask"],"discard")
			if (negative_prompts): final_img = process_mask_parts(negative_preds,negative_prompt_parts,"discard",final_img)

			# Increase mask size with padding
			if (mask_padding > 0):
				aspect_ratio = self.Unprompted.shortcode_user_vars["init_images"][0].width / self.Unprompted.shortcode_user_vars["init_images"][0].height
				new_width = self.Unprompted.shortcode_user_vars["init_images"][0].width+mask_padding*2
				new_height = round(new_width / aspect_ratio)
				final_img = final_img.resize((new_width,new_height))
				final_img = center_crop(final_img,self.Unprompted.shortcode_user_vars["init_images"][0].width,self.Unprompted.shortcode_user_vars["init_images"][0].height)

			return final_img

		# Set up processor parameters correctly
		self.image_mask = get_mask().resize((self.Unprompted.shortcode_user_vars["init_images"][0].width,self.Unprompted.shortcode_user_vars["init_images"][0].height))
		self.Unprompted.shortcode_user_vars["mode"] = 1
		self.Unprompted.shortcode_user_vars["mask_mode"] = 1
		self.Unprompted.shortcode_user_vars["image_mask"] =self.image_mask
		self.Unprompted.shortcode_user_vars["mask_for_overlay"] = self.image_mask
		self.Unprompted.shortcode_user_vars["latent_mask"] = None # fixes inpainting full resolution

		if "save" in kwargs: self.image_mask.save(f"{self.Unprompted.parse_advanced(kwargs['save'],context)}.png")

		return ""
	
	def after(self,p=None,processed=None):
		if self.image_mask and self.show:
			processed.images.append(self.image_mask)
			self.image_mask = None
			self.show = False
			return processed