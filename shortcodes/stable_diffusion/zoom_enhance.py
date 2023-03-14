class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Upscales a selected portion of the image. ENHANCE!"
		self.is_fixing = False
		self.wizard_prepend = Unprompted.Config.syntax.tag_start + "after" + Unprompted.Config.syntax.tag_end + Unprompted.Config.syntax.tag_start_alt + "zoom_enhance"
		self.wizard_append = Unprompted.Config.syntax.tag_end_alt + Unprompted.Config.syntax.tag_start + Unprompted.Config.syntax.tag_close + "after" + Unprompted.Config.syntax.tag_end

	def run_atomic(self, pargs, kwargs, context):
		import cv2
		import numpy
		from PIL import Image, ImageFilter
		import math

		def sigmoid(x):
			return 1 / (1 + math.exp(-x))

		blur_radius_orig = float(self.Unprompted.parse_advanced(kwargs["blur_size"],context)) if "blur_size" in kwargs else 0.03
		upscale_width = int(float(self.Unprompted.parse_advanced(kwargs["upscale_width"],context))) if "upscale_width" in kwargs else 512
		upscale_height = int(float(self.Unprompted.parse_advanced(kwargs["upscale_height"],context))) if "upscale_height" in kwargs else 512
		save = True if "save" in pargs else False
		use_workaround = True if "use_workaround" in pargs else False
		mask_sort_method = self.Unprompted.parse_alt_tags(kwargs["mask_sort_method"],context) if "mask_sort_method" in kwargs else "left-to-right"

		all_replacements = (self.Unprompted.parse_alt_tags(kwargs["replacement"],context) if "replacement" in kwargs else "face").split(self.Unprompted.Config.syntax.delimiter)
		all_negative_replacements = (self.Unprompted.parse_alt_tags(kwargs["negative_replacement"],context) if "negative_replacement" in kwargs else "").split(self.Unprompted.Config.syntax.delimiter)
		
		self.Unprompted.shortcode_user_vars["width"] = upscale_width
		self.Unprompted.shortcode_user_vars["height"] = upscale_height
		# Ensure standard img2img mode
		self.Unprompted.shortcode_user_vars["mode"] = 0
		# Prevent batch from breaking
		batch_size_orig = self.Unprompted.shortcode_user_vars["batch_size"]
		n_iter_orig = self.Unprompted.shortcode_user_vars["n_iter"]
		self.Unprompted.shortcode_user_vars["batch_size"] = 1
		self.Unprompted.shortcode_user_vars["n_iter"] = 1
		
		if "denoising_strength" in kwargs: self.Unprompted.shortcode_user_vars["denoising_strength"] = float(self.Unprompted.parse_advanced(kwargs["denoising_strength"],context))
		if "cfg_scale" in kwargs: self.Unprompted.shortcode_user_vars["cfg_scale"] = float(self.Unprompted.parse_advanced(kwargs["cfg_scale"],context))

		# vars for dynamic settings
		denoising_max = float(self.Unprompted.parse_advanced(kwargs["denoising_max"],context)) if "denoising_max" in kwargs else 0.65
		cfg_min = float(self.Unprompted.parse_advanced(kwargs["cfg_scale_min"],context)) if "cfg_scale_min" in kwargs else 6.0
		target_size_max = float(self.Unprompted.parse_advanced(kwargs["mask_size_max"],context)) if "mask_size_max" in kwargs else 0.3	
		cfg_max = self.Unprompted.shortcode_user_vars["cfg_scale"] - cfg_min

		padding_original = int(float(self.Unprompted.parse_advanced(kwargs["contour_padding"],context))) if "contour_padding" in kwargs else 0
		min_area = int(float(self.Unprompted.parse_advanced(kwargs["min_area"],context))) if "min_area" in kwargs else 50
		target_mask = self.Unprompted.parse_alt_tags(kwargs["mask"],context) if "mask" in kwargs else "face"

		set_pargs = pargs
		set_kwargs = kwargs
		set_pargs.insert(0,"return_image")

		if context == "after":
			all_images = self.Unprompted.after_processed.images
		else: all_images = self.Unprompted.shortcode_user_vars["init_images"]

		append_originals = []
		
		# Batch support yo
		for image_idx, image_pil in enumerate(all_images):
			# Workaround for compatibility between [after] block and batch processing
			if "width" not in self.Unprompted.shortcode_user_vars: return ""

			image = numpy.array(image_pil)

			if save: image_pil.save("zoom_enhance_0.png")

			if "include_original" in pargs:
				append_originals.append(image_pil.copy())

			set_kwargs["txt2mask_init_image"] = image_pil
			
			mask_image = self.Unprompted.shortcode_objects["txt2mask"].run_block(set_pargs,set_kwargs,None,target_mask)
			if save: mask_image.save("zoom_enhance_1.png")
			# Make it grayscale
			mask_image = cv2.cvtColor(numpy.array(mask_image),cv2.COLOR_BGR2GRAY)

			thresh = cv2.threshold(mask_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

			# Two pass dilate with horizontal and vertical kernel
			horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,5))
			dilate = cv2.dilate(thresh, horizontal_kernel, iterations=2)
			vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,9))
			dilate = cv2.dilate(dilate, vertical_kernel, iterations=2)

			# Find contours, filter using contour threshold area
			cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			cnts = cnts[0] if len(cnts) == 2 else cnts[1]

			if mask_sort_method is not "unsorted":
				if mask_sort_method=="small-to-big":
					cnts = sorted(cnts, key=cv2.contourArea, reverse=False)[:5]
				elif mask_sort_method=="big-to-small":
					cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
				else:
					# initialize the reverse flag and sort index
					reverse = False
					i = 0
					# handle if we need to sort in reverse
					if mask_sort_method == "right-to-left" or mask_sort_method == "bottom-to-top": reverse = True
					# handle if we are sorting against the y-coordinate rather than
					# the x-coordinate of the bounding box
					if mask_sort_method == "top-to-bottom" or mask_sort_method == "bottom-to-top": i = 1
					# construct the list of bounding boxes and sort them from top to
					# bottom
					boundingBoxes = [cv2.boundingRect(c) for c in cnts]
					(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
						key=lambda b:b[1][i], reverse=reverse))

			for c_idx,c in enumerate(cnts):
				self.Unprompted.log(f"Processing contour #{c_idx+1}...")
				area = cv2.contourArea(c)
				if area >= min_area:
					x,y,w,h = cv2.boundingRect(c)
					self.Unprompted.log(f"Contour properties: {x} {y} {w} {h}")
					
					# Make sure it's a square, 1:1 AR for stable diffusion
					size = max(w,h)
					w = size
					h = size
					# Padding may be constrained by the mask region position
					padding = min(padding_original,x,y) 

					if "denoising_strength" not in kwargs or "cfg_scale" not in kwargs:
						target_size = (w * h) / (self.Unprompted.shortcode_user_vars["width"] * self.Unprompted.shortcode_user_vars["height"])
						self.Unprompted.log(f"Masked region size is {target_size}")
						if target_size < target_size_max:
							sig = sigmoid(-6 + (target_size / target_size_max) * 12) # * -1 # (12 * (target_size / target_size_max) - 6))
							self.Unprompted.log(f"Sigmoid value: {sig}")
							if "denoising_strength" not in kwargs:
								self.Unprompted.shortcode_user_vars["denoising_strength"] = (1 - sig) * denoising_max
								self.Unprompted.log(f"Denoising strength is {self.Unprompted.shortcode_user_vars['denoising_strength']}")
							if "cfg_scale" not in kwargs:
								self.Unprompted.shortcode_user_vars["cfg_scale"] = cfg_min + sig * cfg_max
								self.Unprompted.log(f"CFG Scale is {self.Unprompted.shortcode_user_vars['cfg_scale']} (min {cfg_min}, max {cfg_min+cfg_max})")									
						else:
							self.Unprompted.log("Humongous target detected. Skipping zoom_enhance...")
							continue

					# Set prompt with multi-subject support
					self.Unprompted.shortcode_user_vars["prompt"] = all_replacements[min(c_idx,len(all_replacements)-1)]
					self.Unprompted.shortcode_user_vars["negative_prompt"] = all_negative_replacements[min(c_idx,len(all_negative_replacements)-1)]

					y1 = max(0,y-padding)
					y2 = min(image.shape[0],y+h+padding)
					# In case the target appears close to the bottom of the picture, we push the mask up to get the right 1:1 size
					if (y2 - y1 < size): y1 -= size - (y2 - y1)

					x1 = max(0,x-padding)
					x2 = min(image.shape[1],x+w+padding)
					if (x2 - x1 < size): x1 -= size - (x2 - x1)

					sub_img=Image.fromarray(image[y1:y2,x1:x2])
					sub_mask=Image.fromarray(mask_image[y1:y2,x1:x2])
					sub_img_big = sub_img.resize((upscale_width,upscale_height))
					if save: sub_img_big.save("zoom_enhance_2.png")

					# blur radius is relative to canvas size, should be odd integer
					blur_radius = math.ceil(w * blur_radius_orig) // 2 * 2 + 1
					if blur_radius > 0:
						sub_mask = sub_mask.filter(ImageFilter.GaussianBlur(radius = blur_radius))
					
					if save: sub_mask.save("zoom_enhance_3.png")

					self.Unprompted.shortcode_user_vars["img2img_init_image"] = sub_img_big
					fixed_image = self.Unprompted.shortcode_objects["img2img"].run_atomic(set_pargs,None,None)
					# self.Unprompted.shortcode_user_vars["init_images"].append(fixed_image)
					if save: fixed_image.save("zoom_enhance_4.png")
					# Downscale fixed image back to original size
					fixed_image = fixed_image.resize((w + padding*2,h + padding*2))
					
					# Slap our new image back onto the original
					image_pil.paste(fixed_image, (x - padding, y - padding),sub_mask)

					# self.Unprompted.shortcode_user_vars["init_images"].append(image_pil)
					if use_workaround: append_originals.append(image_pil.copy())

					# test outside after block, WIP pls don't use
					if context != "after":
						self.Unprompted.shortcode_user_vars["init_images"] = image_pil

					# Remove temp image key in case [img2img] is used later
					if "img2img_init_image" in self.Unprompted.shortcode_user_vars: del self.Unprompted.shortcode_user_vars["img2img_init_image"]

				else: self.Unprompted.log(f"Countour area ({area}) is less than the minimum ({min_area}) - skipping")
		
		# Add original images
		for appended_image in append_originals:
			self.Unprompted.after_processed.images.append(appended_image)
		

		self.Unprompted.shortcode_user_vars["batch_size"] = batch_size_orig
		self.Unprompted.shortcode_user_vars["n_iter"] = n_iter_orig


		return ""

	def ui(self,gr):
		gr.Checkbox(label="Final image not showing up? Try using this workaround 🡢 use_workaround")
		gr.Text(label="Mask to find 🡢 mask",value="face")
		gr.Text(label="Replacement 🡢 replacement",value="face")
		gr.Text(label="Negative replacement 🡢 negative_replacement",value="")
		gr.Dropdown(label="Mask sorting method 🡢 mask_sort_method",value="left-to-right",choices=["left-to-right","right-to-left","top-to-bottom","bottom-to-top","big-to-small","small-to-big","unsorted"])
		gr.Slider(label="Blur edges size 🡢 blur_size",value=0.03,maximum=1.0,minimum=0.0,interactive=True,step=0.01)
		gr.Slider(label="Minimum CFG scale 🡢 cfg_scale_min",value=3.0,maximum=15.0,minimum=0.0,interactive=True,step=0.5)
		gr.Slider(label="Maximum denoising strength 🡢 denoising_max",value=0.65,maximum=1.0,minimum=0.0,interactive=True,step=0.01)
		gr.Slider(label="Maximum mask size (if a bigger mask is found, it will bypass the shortcode) 🡢 mask_size_max",value=0.3,maximum=1.0,minimum=0.0,interactive=True,step=0.01)
		gr.Text(label="Force denoising strength to this value 🡢 denoising_strength")
		gr.Text(label="Force CFG scale to this value 🡢 cfg_scale")
		gr.Number(label="Mask minimum number of pixels 🡢 min_area",value=50,interactive=True)
		gr.Number(label="Contour padding in pixels 🡢 contour_padding",value=0,interactive=True)
		gr.Number(label="Upscale width 🡢 upscale_width",value=512,interactive=True)
		gr.Number(label="Upscale height 🡢 upscale_height",value=512,interactive=True)
		gr.Checkbox(label="Include original image in output window 🡢 include_original")
		gr.Checkbox(label="Save debug images to WebUI folder 🡢 save")