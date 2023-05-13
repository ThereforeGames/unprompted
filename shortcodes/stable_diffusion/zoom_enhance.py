try:
	from modules.processing import process_images_inner, StableDiffusionProcessingImg2Img, StableDiffusionProcessing
except: pass # for unprompted_dry

def process_images_inner_(p):
	return(process_images_inner(p))

class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Upscales a selected portion of the image. ENHANCE!"
		self.is_fixing = False
		self.wizard_prepend = f"{Unprompted.Config.syntax.tag_start}if batch_index=0{Unprompted.Config.syntax.tag_end}{Unprompted.Config.syntax.tag_start}after{Unprompted.Config.syntax.tag_end}{Unprompted.Config.syntax.tag_start}zoom_enhance"

		self.wizard_append = Unprompted.Config.syntax.tag_end + Unprompted.Config.syntax.tag_start + Unprompted.Config.syntax.tag_close + "after" + Unprompted.Config.syntax.tag_end + Unprompted.Config.syntax.tag_start + Unprompted.Config.syntax.tag_close  + "if" + Unprompted.Config.syntax.tag_end
		self.resample_methods = {}
		self.resample_methods["Nearest Neighbor"] = 0
		self.resample_methods["Box"] = 4
		self.resample_methods["Bilinear"] = 2
		self.resample_methods["Hamming"] = 5
		self.resample_methods["Bicubic"] = 3
		self.resample_methods["Lanczos"] = 1


	def run_atomic(self, pargs, kwargs, context):
		import gc
		from modules import devices
		import cv2
		from scipy import mean, interp, ravel, array
		import numpy
		from PIL import Image, ImageFilter, ImageChops, ImageOps
		from blendmodes.blend import blendLayers, BlendType
		import math
		from modules import shared

		def sigmoid(x):
			return 1 / (1 + math.exp(-x))

		def unsharp_mask(image, amount=1.0, kernel_size=(5, 5), sigma=1.0, threshold=0):
			"""Return a sharpened version of the image, using an unsharp mask."""
			image = numpy.array(image).astype(numpy.uint8)
			blurred = cv2.GaussianBlur(image, kernel_size, sigma)
			sharpened = float(amount + 1) * image - float(amount) * blurred
			sharpened = numpy.maximum(sharpened, numpy.zeros(sharpened.shape))
			sharpened = numpy.minimum(sharpened, 255 * numpy.ones(sharpened.shape))
			sharpened = sharpened.round().astype(numpy.uint8)
			if threshold > 0:
				low_contrast_mask = numpy.absolute(image - blurred) < threshold
				numpy.copyto(sharpened, image, where=low_contrast_mask)
			return Image.fromarray(sharpened)


		test = int(float(self.Unprompted.parse_advanced(kwargs["test"],context))) if "test" in kwargs else 0
		blur_radius_orig = float(self.Unprompted.parse_advanced(kwargs["blur_size"],context)) if "blur_size" in kwargs else 0.03
		upscale_width = int(float(self.Unprompted.parse_advanced(kwargs["upscale_width"],context))) if "upscale_width" in kwargs else 512
		upscale_height = int(float(self.Unprompted.parse_advanced(kwargs["upscale_height"],context))) if "upscale_height" in kwargs else 512
		hires_size_max = int(float(self.Unprompted.parse_advanced(kwargs["hires_size_max"],context))) if "hires_size_max" in kwargs else 1024

		sharpen_amount = int(float(self.Unprompted.parse_advanced(kwargs["sharpen_amount"],context))) if "sharpen_amount" in kwargs else 1.0

		debug = self.Unprompted.shortcode_var_is_true("debug", pargs, kwargs, context)
		show_original = self.Unprompted.shortcode_var_is_true("show_original", pargs, kwargs, context)
		controlnet_preset = self.Unprompted.parse_alt_tags(kwargs["controlnet_preset"],context) if "controlnet_preset" in kwargs else "none"
		color_correct_method = self.Unprompted.parse_alt_tags(kwargs["color_correct_method"],context) if "color_correct_method" in kwargs else "none"
		color_correct_timing = self.Unprompted.parse_alt_tags(kwargs["color_correct_timing"],context) if "color_correct_timing" in kwargs else "pre"
		color_correct_strength = int(float(self.Unprompted.parse_advanced(kwargs["color_correct_strength"],context))) if "color_correct_strength" in kwargs else 1
		manual_mask_mode = self.Unprompted.parse_alt_tags(kwargs["mode"],context) if "mode" in kwargs else "subtract"
		mask_sort_method = self.Unprompted.parse_alt_tags(kwargs["mask_sort_method"],context) if "mask_sort_method" in kwargs else "left-to-right"
		downscale_method = self.Unprompted.parse_alt_tags(kwargs["downscale_method"],context) if "downscale_method" in kwargs else "Lanczos"
		downscale_method = self.resample_methods[downscale_method]
		upscale_method = self.Unprompted.parse_alt_tags(kwargs["upscale_method"],context) if "downscale_method" in kwargs else "Nearest Neighbor"
		upscale_method = self.resample_methods[upscale_method]

		all_replacements = (self.Unprompted.parse_alt_tags(kwargs["replacement"],context) if "replacement" in kwargs else "face").split(self.Unprompted.Config.syntax.delimiter)
		all_negative_replacements = (self.Unprompted.parse_alt_tags(kwargs["negative_replacement"],context) if "negative_replacement" in kwargs else "").split(self.Unprompted.Config.syntax.delimiter)

		# Ensure standard img2img mode
		if (hasattr(self.Unprompted.p_copy,"image_mask")):
			image_mask_orig = self.Unprompted.p_copy.image_mask
		else: image_mask_orig = None
		self.Unprompted.p_copy.mode = 0
		self.Unprompted.p_copy.image_mask = None
		self.Unprompted.p_copy.mask = None
		self.Unprompted.p_copy.init_img_with_mask = None
		self.Unprompted.p_copy.init_mask = None
		self.Unprompted.p_copy.mask_mode = 0
		self.Unprompted.p_copy.init_mask_inpaint = None
		self.Unprompted.p_copy.batch_size = 1
		self.Unprompted.p_copy.n_iter = 1
		self.Unprompted.p_copy.mask_for_overlay = None

		try:
			starting_image = self.Unprompted.p_copy.init_images[0]
			is_img2img = True
		except:
			starting_image = self.Unprompted.after_processed.images[0]
			is_img2img = False

		# for [txt2mask]
		self.Unprompted.shortcode_user_vars["mode"] = 0

		if "image_mask" in self.Unprompted.shortcode_user_vars:
			current_mask = self.Unprompted.shortcode_user_vars["image_mask"]
			self.Unprompted.shortcode_user_vars["image_mask"] = None
		else: current_mask = None
		
		if "denoising_strength" in kwargs:
			self.Unprompted.p_copy.denoising_strength = float(self.Unprompted.parse_advanced(kwargs["denoising_strength"],context))
			self.Unprompted.log(f"Manually setting denoise strength to {self.Unprompted.p_copy.denoising_strength}")
		if "cfg_scale" in kwargs:
			self.Unprompted.p_copy.cfg_scale = float(self.Unprompted.parse_advanced(kwargs["cfg_scale"],context))
			self.Unprompted.log(f"Manually setting CFG scale to {self.Unprompted.p_copy.cfg_scale}")

		# vars for dynamic settings
		denoising_max = float(self.Unprompted.parse_advanced(kwargs["denoising_max"],context)) if "denoising_max" in kwargs else 0.3
		cfg_min = float(self.Unprompted.parse_advanced(kwargs["cfg_scale_min"],context)) if "cfg_scale_min" in kwargs else 7.0
		cfg_max = float(self.Unprompted.parse_advanced(kwargs["cfg_scale_max"],context)) if "cfg_scale_max" in kwargs else 14.0
		target_size_max = float(self.Unprompted.parse_advanced(kwargs["mask_size_max"],context)) if "mask_size_max" in kwargs else 0.5	
		target_size_max_orig = target_size_max
		cfg_max = max(cfg_min,cfg_max)

		padding_original = int(float(self.Unprompted.parse_advanced(kwargs["contour_padding"],context))) if "contour_padding" in kwargs else 0
		min_area = int(float(self.Unprompted.parse_advanced(kwargs["min_area"],context))) if "min_area" in kwargs else 50
		target_mask = self.Unprompted.parse_alt_tags(kwargs["mask"],context) if "mask" in kwargs else "face"

		set_pargs = pargs
		set_kwargs = kwargs
		set_pargs.insert(0,"return_image") # for [txt2mask]

		if context == "after":
			all_images = self.Unprompted.after_processed.images
		else: 
			all_images = self.Unprompted.shortcode_user_vars["init_images"]

		append_originals = []
		
		# Batch support yo
		for image_idx, image_pil in enumerate(all_images):
			if show_original: append_originals.append(all_images[image_idx].copy())
			# Workaround for compatibility between [after] block and batch processing
			if "width" not in self.Unprompted.shortcode_user_vars:
				self.Unprompted.log("Width variable not set - bypassing shortcode")
				return ""
			
			if not self.Unprompted.shortcode_var_is_true("bypass_adaptive_hires",pargs,kwargs):
				total_pixels = image_pil.size[0] * image_pil.size[1]
				
				self.Unprompted.log(f"Image size: {image_pil.size[0]}x{image_pil.size[1]} ({total_pixels}px)")
				target_multiplier = max(image_pil.size[0],image_pil.size[1]) / max(self.Unprompted.shortcode_user_vars["width"],self.Unprompted.shortcode_user_vars["height"])
				self.Unprompted.log(f"Target multiplier is {target_multiplier}")
				# target_size_max = target_size_max_orig * target_multiplier
				sd_unit = 64

				# Adaptive scaling algo
				denoise_unit = (denoising_max / 8) * 0.125
				cfg_min_unit = (cfg_min / 2) * 0.125
				cfg_max_unit = (cfg_max / 2) * 0.125
				# step_unit = math.ceil(self.Unprompted.p_copy.steps * 0.125)
				upscale_size_test = upscale_width * target_multiplier
				while (upscale_width < min(upscale_size_test,hires_size_max)):
					upscale_width += sd_unit
					upscale_height += sd_unit
					denoising_max = min(1.0,denoising_max-denoise_unit)
					cfg_min += cfg_min_unit
					cfg_max += cfg_max_unit
					sharpen_amount += 0.125 # TODO: Calculate blurriness of original image to determine sharpen amount
					denoising_max -= denoise_unit
					# self.Unprompted.p_copy.steps += step_unit
					
				upscale_width = min(hires_size_max,upscale_width)
				upscale_height = min(hires_size_max,upscale_height)

				self.Unprompted.log(f"Target size max scaled for image size: {target_size_max}")
				self.Unprompted.log(f"Upscale size, accounting for original image: {upscale_width}")


			image = numpy.array(image_pil)
			if starting_image: starting_image = starting_image.resize((image_pil.size[0],image_pil.size[1]))

			if debug: image_pil.save("zoom_enhance_0.png")

			#if "include_original" in pargs:
			#	append_originals.append(image_pil.copy())
			if "mask_method" in kwargs: set_kwargs["method"] = self.Unprompted.parse_alt_tags(kwargs["mask_method"],context)

			set_kwargs["txt2mask_init_image"] = image_pil
			mask_image = self.Unprompted.shortcode_objects["txt2mask"].run_block(set_pargs,set_kwargs,None,target_mask)
			
			if debug: mask_image.save(f"zoom_enhance_1_{image_idx}.png")
			if (image_mask_orig):
				self.Unprompted.log("Original image mask detected")
				prep_orig = image_mask_orig.resize((mask_image.size[0],mask_image.size[1])).convert("L")
				fg_color = 255
				if (manual_mask_mode == "subtract"):
					prep_orig = ImageOps.invert(prep_orig)
					fg_color = 0

				prep_orig = prep_orig.convert("RGBA")
			
				# Make background of original mask transparent
				mask_data = prep_orig.load()
				width, height = prep_orig.size
				for y in range(height):
					for x in range(width):
						if mask_data[x, y] != (fg_color, fg_color, fg_color,255): mask_data[x, y] = (0, 0, 0, 0)

				prep_orig.convert("RGBA") # just in case

				# Overlay mask
				mask_image.paste(prep_orig, (0, 0), prep_orig)

						
			if debug: mask_image.save(f"zoom_enhance_2_{image_idx}.png")
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

			if len(cnts) > 0 and mask_sort_method != "unsorted":
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
					# handle if we are sorting against the y-coordinate rather than the x-coordinate of the bounding box
					if mask_sort_method == "top-to-bottom" or mask_sort_method == "bottom-to-top": i = 1
					# construct the list of bounding boxes and sort them from top to bottom
					boundingBoxes = [cv2.boundingRect(c) for c in cnts]
					(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
						key=lambda b:b[1][i], reverse=reverse))

			for c_idx,c in enumerate(cnts):
				self.Unprompted.log(f"Processing contour #{c_idx+1}...")
				area = cv2.contourArea(c)
				if area >= min_area:
					x,y,w,h = cv2.boundingRect(c)
					
					self.Unprompted.log(f"Contour properties: {x} {y} {w} {h}")
					target_size = (w * h) / (512 * 512 * target_multiplier)
					self.Unprompted.log(f"Masked region size is {target_size}")
					if target_size > 1 or target_size < 0.03:
						self.Unprompted.log(f"This mask is either too large or too small for processing - skipping")
						continue					
					
					# Make sure it's a square, 1:1 AR for stable diffusion
					size = max(w,h)
					w = size
					h = size
					# Padding may be constrained by the mask region position
					padding = min(padding_original,x,y) 

					if "denoising_strength" not in kwargs or "cfg_scale" not in kwargs:
						# target_size = (w * h) / (image_pil.size[0] * image_pil.size[1] * target_multiplier)


						# sig = 0 # sigmoid(-6 + target_size * 12) # * -1 # (12 * (target_size / target_size_max) - 6))
						# self.Unprompted.log(f"Sigmoid value: {sig}")
						if "denoising_strength" not in kwargs:
							self.Unprompted.p_copy.denoising_strength = (1 - min(1,target_size)) * denoising_max
							self.Unprompted.log(f"Denoising strength is {self.Unprompted.p_copy.denoising_strength}")
						if "cfg_scale" not in kwargs:
							self.Unprompted.p_copy.cfg_scale = cfg_min + min(1,target_size) * (cfg_max - cfg_min)
							self.Unprompted.log(f"CFG Scale is {self.Unprompted.p_copy.cfg_scale} (min {cfg_min}, max {cfg_min+cfg_max})")									


					# Set prompt with multi-subject support
					self.Unprompted.p_copy.prompt = all_replacements[min(c_idx,len(all_replacements)-1)]
					self.Unprompted.p_copy.negative_prompt = all_negative_replacements[min(c_idx,len(all_negative_replacements)-1)]

					y1 = max(0,y-padding)
					y2 = min(image.shape[0],y+h+padding)
					# In case the target appears close to the bottom of the picture, we push the mask up to get the right 1:1 size
					if (y2 - y1 < size): y1 -= size - (y2 - y1)

					x1 = max(0,x-padding)
					x2 = min(image.shape[1],x+w+padding)
					if (x2 - x1 < size): x1 -= size - (x2 - x1)

					sub_img=Image.fromarray(image[y1:y2,x1:x2])
					if starting_image:
						if debug: starting_image.save("zoom_enhance_2b_this is the starting image.png")
						starting_image_face=Image.fromarray(numpy.array(starting_image)[y1:y2,x1:x2])
						starting_image_face_big=starting_image_face.resize((upscale_width,upscale_height),resample=upscale_method)
					sub_mask=Image.fromarray(mask_image[y1:y2,x1:x2])
					sub_img_big = sub_img.resize((upscale_width,upscale_height),resample=upscale_method)
					if debug: sub_img_big.save("zoom_enhance_3.png")

					# blur radius is relative to canvas size, should be odd integer
					blur_radius = math.ceil(w * blur_radius_orig) // 2 * 2 + 1
					if blur_radius > 0:
						sub_mask = sub_mask.filter(ImageFilter.GaussianBlur(radius = blur_radius))
					
					if debug: sub_mask.save("zoom_enhance_4.png")

					if color_correct_timing == "pre" and color_correct_method != "none" and starting_image:
						sub_img_big = self.Unprompted.color_match(starting_image_face_big,sub_img_big,color_correct_method,color_correct_strength)

					self.Unprompted.p_copy.init_images = [sub_img_big]
					self.Unprompted.p_copy.width = upscale_width
					self.Unprompted.p_copy.height = upscale_height

					# Ensure standard img2img mode again... JUST IN CASE
					self.Unprompted.p_copy.mode = 0
					self.Unprompted.p_copy.image_mask = None
					self.Unprompted.p_copy.mask = None
					self.Unprompted.p_copy.init_img_with_mask = None
					self.Unprompted.p_copy.init_mask = None
					self.Unprompted.p_copy.mask_mode = 0
					self.Unprompted.p_copy.init_mask_inpaint = None
					self.Unprompted.p_copy.latent_mask = None
					self.Unprompted.p_copy.batch_size = 1
					self.Unprompted.p_copy.n_iter = 1

					if controlnet_preset != "none" and len(controlnet_preset) > 0:
						set_pargs = [f"common/presets/controlnet/{controlnet_preset}"]
						set_kwargs = {}
						file_contents = self.Unprompted.shortcode_objects["file"].run_atomic(set_pargs,set_kwargs,context)						
						# temporarily disable user vars to avoid applying old controlnet values
						temp_user_vars = self.Unprompted.shortcode_user_vars
						self.Unprompted.shortcode_user_vars.clear()
						self.Unprompted.process_string(file_contents,context)
						for att in self.Unprompted.shortcode_user_vars:
							if att.startswith("controlnet_") or att.startswith("cn_"): self.Unprompted.update_controlnet_var(self.Unprompted.p_copy,att)
						
						# restore user vars
						self.Unprompted.shortcode_user_vars = temp_user_vars
						# print(self.Unprompted.shortcode_user_vars)	

					if self.Unprompted.shortcode_var_is_true("use_starting_face",pargs,kwargs):
						self.Unprompted.p_copy.init_images = [starting_image_face_big]
						color_correct_timing = "post"					

					# run img2img now to improve face
					try:
						if is_img2img:
							#print(self.Unprompted.p_copy.all_prompts)
							# temp_alwayson = self.Unprompted.p_copy.scripts.alwayson_scripts.copy()
							# self.Unprompted.p_copy.scripts.alwayson_scripts.clear()
							# Remove Unprompted from the copied object

							for idx,script in enumerate(self.Unprompted.p_copy.scripts.alwayson_scripts):
								if script.title().lower() == 'unprompted':
									unp_idx = idx
									temp_script = self.Unprompted.p_copy.scripts.alwayson_scripts[idx]
									self.Unprompted.p_copy.scripts.alwayson_scripts.pop(idx)
									self.Unprompted.log("Successfully disabled Unprompted from p_copy scripts")
									break

							fixed_image = process_images_inner_(self.Unprompted.p_copy)
							fixed_image = fixed_image.images[0]

							self.Unprompted.p_copy.scripts.alwayson_scripts.insert(unp_idx,temp_script)
						else:
							# workaround for txt2img, not sure if compatible with controlnet
							for att in dir(self.Unprompted.p_copy):
								if not att.startswith("__") and att != "sd_model":
									self.Unprompted.shortcode_user_vars[att] = getattr(self.Unprompted.p_copy,att)							
							fixed_image = self.Unprompted.shortcode_objects["img2img"].run_atomic(set_pargs,None,None)
						if debug: fixed_image.save("zoom_enhance_4after.png")
					except Exception as e:
						self.Unprompted.log_error(e)
						return ""


					
					if color_correct_method != "none" and starting_image:						
						try:
							if color_correct_timing == "post":
								self.Unprompted.log("Color correcting the face...")
								if debug:
									fixed_image.save("zoom_enhance_5a_pre_color_correct.png")
									starting_image_face_big.save("zoom_enhance_5b_using_this_face_mask.png")
									starting_image.save("zoom_enhance_5c_main_starting_image.png")
								
								fixed_image = self.Unprompted.color_match(sub_img_big,fixed_image,color_correct_method,color_correct_strength) # starting_image_face_big
							
							self.Unprompted.log("Color correcting the main image to the init image...")
							corrected_main_img  = self.Unprompted.color_match(starting_image,image_pil,color_correct_method,color_correct_strength)
							width, height = image_pil.size
							corrected_main_img = corrected_main_img.resize((width,height))
							# prevent changes to background
							if current_mask:
								current_mask.convert("RGBA")
								mask_data = current_mask.load()
								width, height = current_mask.size
								for y in range(height):
									for x in range(width):
										if mask_data[x, y] != (255, 255, 255, 255): mask_data[x, y] = (0, 0, 0, 0)
								if blur_radius > 0:
									current_mask = current_mask.filter(ImageFilter.GaussianBlur(radius = blur_radius))
								width, height = corrected_main_img.size
								current_mask = current_mask.resize((width,height))
								if debug: current_mask.save("zoom_enhance_5d_current_main_mask.png")
								image_pil.paste(corrected_main_img,(0,0),current_mask)
								if debug: image_pil.save("zoom_enhance_5e_corrected_main_image.png")
						except Exception as e:
							self.Unprompted.log_error(e)

					# self.Unprompted.shortcode_user_vars["init_images"].append(fixed_image)
					if debug: fixed_image.save("zoom_enhance_5f.png")

					if sharpen_amount > 0:
						self.Unprompted.log(f"Sharpening the fixed image by {sharpen_amount}")
						fixed_image = unsharp_mask(fixed_image,sharpen_amount)

					try:
						# Downscale fixed image back to original size
						fixed_image = fixed_image.resize((w + padding*2,h + padding*2),resample=downscale_method)
						
						# Slap our new image back onto the original
						if test == 1: image_pil = image_pil.paste(fixed_image, (x1 - padding, y1 - padding),sub_mask)
						elif test == 2: image_pil = image_pil.paste(fixed_image, (x1 - padding, y1 - padding),sub_mask).copy()
						else: image_pil.paste(fixed_image, (x1 - padding, y1 - padding),sub_mask)

						if debug: image_pil.save("zoom_enhance_final_result.png")

						self.Unprompted.log(f"Adding zoom_enhance result for image_idx {image_idx}")
						if context != "after":
							self.Unprompted.log("Attempting to use zoom_enhance outside of an after block... good luck")
							self.Unprompted.shortcode_user_vars["init_images"] = image_pil
						# main return
						else:
							if test == 3: self.Unprompted.after_processed.images[image_idx] = image_pil.copy()
							elif test == 4: self.Unprompted.after_processed.images[0] = image_pil.copy()
							elif test == 5: append_originals.append(image_pil.copy())
							else: self.Unprompted.after_processed.images[image_idx] = image_pil
					except Exception as e:
							self.Unprompted.log(f"Could not append zoom_enhance result: {e}",context="ERROR")
							return""

					# Remove temp image key in case [img2img] is used later
					if "img2img_init_image" in self.Unprompted.shortcode_user_vars: del self.Unprompted.shortcode_user_vars["img2img_init_image"]

				else: self.Unprompted.log(f"Countour area ({area}) is less than the minimum ({min_area}) - skipping")
		
		# Add original image to output window
		for appended_image in append_originals:
			self.Unprompted.after_processed.images.append(appended_image)
			# TODO: Find a way to fix the save button

		self.Unprompted.shortcode_user_vars["init_images"] = self.Unprompted.after_processed.images

		return ""

	def ui(self,gr):
		gr.Checkbox(label="Include original, unenhanced image in output window? 🡢 show_original")
		gr.Text(label="Mask to find 🡢 mask",value="face")
		gr.Text(label="Replacement 🡢 replacement",value="face")
		gr.Text(label="Negative mask 🡢 negative_mask",value="")
		gr.Text(label="Negative replacement 🡢 negative_replacement",value="")
		gr.Dropdown(label="Mask sorting method 🡢 mask_sort_method",value="left-to-right",choices=["left-to-right","right-to-left","top-to-bottom","bottom-to-top","big-to-small","small-to-big","unsorted"])
		gr.Checkbox(label="Save debug images to WebUI folder 🡢 debug")
		gr.Checkbox(label="Unload txt2mask model after inference (for low memory devices) 🡢 unload_model")
		with gr.Accordion("⚙️ Advanced Options", open=False):
			gr.Dropdown(label="Upscale method 🡢 upscale_method",value="Nearest Neighbor",choices=list(self.resample_methods.keys()),interactive=True)
			gr.Dropdown(label="Downscale method 🡢 downscale_method",value="Lanczos",choices=list(self.resample_methods.keys()),interactive=True)
			gr.Slider(label="Blur edges size 🡢 blur_size",value=0.03,maximum=1.0,minimum=0.0,interactive=True,step=0.01)
			gr.Slider(label="Minimum CFG scale 🡢 cfg_scale_min",value=7.0,maximum=15.0,minimum=0.0,interactive=True,step=0.5)
			gr.Slider(label="Maximum denoising strength 🡢 denoising_max",value=0.65,maximum=1.0,minimum=0.0,interactive=True,step=0.01)
			gr.Slider(label="Maximum mask size (if a bigger mask is found, it will bypass the shortcode) 🡢 mask_size_max",value=0.5,maximum=1.0,minimum=0.0,interactive=True,step=0.01)
			gr.Radio(label="Masking tech method 🡢 mask_method",choices=["clipseg","clip_surgery","grounded_sam"],value="clipseg",interactive=True) # Passed to txt2mask as "method"
			gr.Number(label="Sharpen amount 🡢 sharpen_amount",value=1.0,interactive=True)
			gr.Dropdown(label="Color correct method 🡢 color_correct_method",choices=["hm","mvgd","mkl","hm-mvgd-hm","hm-mkl-hms"],value="none",interactive=True)
			gr.Radio(label="Color correct timing 🡢 color_correct_timing",choices=["pre","post"],value="pre",interactive=True)
			gr.Slider(label="Color correct strength 🡢 color_correct_strength",value=1.0,maximum=5.0,minimum=1.0,interactive=True,step=1.0)
			gr.Text(label="Force denoising strength to this value 🡢 denoising_strength")
			gr.Text(label="Force CFG scale to this value 🡢 cfg_scale")
			gr.Number(label="Mask minimum number of pixels 🡢 min_area",value=50,interactive=True)
			gr.Number(label="Contour padding in pixels 🡢 contour_padding",value=0,interactive=True)
			gr.Number(label="Upscale width 🡢 upscale_width",value=512,interactive=True)
			gr.Number(label="Upscale height 🡢 upscale_height",value=512,interactive=True)
			gr.Number(label="Hires size max 🡢 hires_size_max",value=1024,interactive=True)
			gr.Checkbox(label="Bypass adaptive hires 🡢 bypass_adaptive_hires")