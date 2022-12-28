class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.image_mask = None
		self.show = False
		self.description = "Modify or replace your img2img mask with arbitrary files."
	def run_atomic(self, pargs, kwargs, context):
		import os.path
		from PIL import ImageChops, Image, ImageOps
		import cv2
		import numpy

		brush_mask_mode = self.Unprompted.parse_advanced(kwargs["mode"],context) if "mode" in kwargs else "add"
		self.show = True if "_show" in pargs else False

		def overlay_mask_part(img_a,img_b,mode):
			if (mode == "discard"): img_a = ImageChops.darker(img_a, img_b)
			else: img_a = ImageChops.lighter(img_a, img_b)
			return(img_a)

		def gray_to_pil(img): return (Image.fromarray(cv2.cvtColor(img,cv2.COLOR_GRAY2RGBA)))

		def process_mask_parts(final_img = None):
			for idx,parg in enumerate(pargs):
				if (parg[0] == "_"): continue # Skips system arguments
				filename = self.Unprompted.parse_alt_tags(parg,context)

				try:
					img = cv2.imread(filename)
				except:
					self.Unprompted.log(f"Could not load file: {filename}",True,"ERROR")
					quit()
				gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

				# overlay mask parts
				gray_image = gray_to_pil(gray_image)
				if (idx > 0 or final_img is not None): gray_image = overlay_mask_part(gray_image,final_img,"add")

				final_img = gray_image
			return(final_img)

		def get_mask():
			if "image_mask" not in self.Unprompted.shortcode_user_vars: self.Unprompted.shortcode_user_vars["image_mask"] = None
			
			if (brush_mask_mode == "add" and self.Unprompted.shortcode_user_vars["image_mask"] is not None):
				final_img = self.Unprompted.shortcode_user_vars["image_mask"].convert("RGBA")
			else: final_img = None

			# process masking
			final_img = process_mask_parts(final_img)

			# process negative masking
			if (brush_mask_mode == "subtract" and self.Unprompted.shortcode_user_vars["image_mask"] is not None):
				self.Unprompted.shortcode_user_vars["image_mask"] = ImageOps.invert(self.Unprompted.shortcode_user_vars["image_mask"])
				self.Unprompted.shortcode_user_vars["image_mask"] = self.Unprompted.shortcode_user_vars["image_mask"].convert("RGBA")
				final_img = overlay_mask_part(final_img,self.Unprompted.shortcode_user_vars["image_mask"],"discard")

			return final_img

		# Set up processor parameters correctly
		self.image_mask = get_mask().resize((self.Unprompted.shortcode_user_vars["init_images"][0].width,self.Unprompted.shortcode_user_vars["init_images"][0].height))
		self.Unprompted.shortcode_user_vars["mode"] = 1
		self.Unprompted.shortcode_user_vars["mask_mode"] = 1
		self.Unprompted.shortcode_user_vars["image_mask"] =self.image_mask
		self.Unprompted.shortcode_user_vars["mask_for_overlay"] = self.image_mask
		self.Unprompted.shortcode_user_vars["latent_mask"] = None # fixes inpainting full resolution

		return ""
	
	def after(self,p=None,processed=None):
		if self.image_mask and self.show:
			processed.images.append(self.image_mask)
			self.image_mask = None
			self.show = False
			return processed

	def ui(self,gr):
		gr.Textbox(label="Path to image file 🡢 str",max_lines=1)
		gr.Radio(label="Mask blend mode 🡢 mode",choices=["add","subtract","discard"],value="add",interactive=True)
		gr.Checkbox(label="Show mask in output 🡢 show")