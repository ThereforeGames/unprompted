class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Runs an img2img task inside of an [after] block."
		
		# using a counter to keep track of the current image index as something isn't working quite 
		# right with getting the image index from the shortcode_user_vars
		# this also helps with grid detection as well
		self.counter = -1	# start at -1 so that the first image is 0 when we iterate
		self.image_array = []

	def run_atomic(self, pargs, kwargs, context):
		import modules.img2img
		from modules import sd_samplers
		from modules import scripts
		
		# this counter is what we are using to track the current image index
		self.counter += 1
		
		did_error = False

		# temporary bypass alwayson scripts to ensure vanilla img2img task
		temp_alwayson = None
		self.Unprompted.is_enabled = False
		try:
			temp_alwayson = self.Unprompted.shortcode_user_vars["scripts"].alwayson_scripts.copy()
			self.Unprompted.shortcode_user_vars["scripts"].alwayson_scripts.clear()
		except:
			pass

		# Synchronize any changes from user vars
		if "no_sync" not in pargs:
			self.Unprompted.update_stable_diffusion_vars(self.Unprompted.main_p)

		if "mask_mode" not in self.Unprompted.shortcode_user_vars: self.Unprompted.shortcode_user_vars["mask_mode"] = 0
		init_mask = None
		if "init_mask" in self.Unprompted.shortcode_user_vars: init_mask = self.Unprompted.shortcode_user_vars["init_mask"]
		elif "init_mask_inpaint" in self.Unprompted.shortcode_user_vars: init_mask = self.Unprompted.shortcode_user_vars["init_mask_inpaint"]

		if "img2img_init_image" in self.Unprompted.shortcode_user_vars:
			init_imgs = [self.Unprompted.shortcode_user_vars["img2img_init_image"]]
		else:
			init_imgs = self.Unprompted.shortcode_user_vars["init_images"]  # [len(self.Unprompted.shortcode_user_vars["init_images"]) - 1]

		init_img_with_mask = self.Unprompted.shortcode_user_vars["init_img_with_mask"] if "init_img_with_mask" in self.Unprompted.shortcode_user_vars else None

		for att in self.Unprompted.shortcode_user_vars:
			if att.startswith("controlnet_") or att.startswith("cn_"): self.Unprompted.update_controlnet_var(self.Unprompted.main_p, att)

		# this just sets up the starting image for the img2img operation
		# storing a copy of the image array into this class instance as it seems the order of the images
		# change once the processing starts and we end up getting the images in the wrong order
		# compared to the prompt array
		if self.image_array == []:
			try:				
				self.image_array = self.Unprompted.main_p.init_images.copy()
			except:
				self.image_array = self.Unprompted.after_processed.images.copy()

		
		batch_count = self.Unprompted.shortcode_user_vars["n_iter"] if "n_iter" in self.Unprompted.shortcode_user_vars else 1
		batch_size = self.Unprompted.shortcode_user_vars["batch_size"]
		total_images_expected = batch_count * batch_size
		
		if len(self.image_array) != total_images_expected:			
			# when the processed image array contains the grid image, we then will have the batch_count*batch_size + 1 images
			# when there is a grid image it is always the first image, so we can safely remove it from the image array
			self.image_array.pop(0)
		
		try:
			img2img_images = []
			temp_gr_request = lambda: None
			temp_gr_request.username = "unprompted"
			
			# subtract the real_first_image_index to get the correct zero based index of the prompt for the first image
			prompt = self.Unprompted.after_processed.all_prompts[self.counter]			
			negative_prompt = self.Unprompted.after_processed.all_negative_prompts[self.counter]
						
			image = self.image_array[self.counter]

			# if the ratio is set to 0 then use the width and height, otherwise use the ratio
			ratio = self.Unprompted.parse_arg("ratio",0.0)

			current_width = image.width
			current_height = image.height

			if ratio != 0 and ratio != 1:
				current_width = int(current_width * ratio)
				current_height = int(current_height * ratio)

			img2img_result = modules.img2img.img2img(
				"unprompted_img2img",  #id_task
				int(self.Unprompted.shortcode_user_vars["mode"]) if "mode" in self.Unprompted.shortcode_user_vars else 0,  #p.mode
				prompt, 
				negative_prompt, 
				[],  # prompt_styles
				image,
				None,  # sketch
				init_img_with_mask,  # p.init_img_with_mask
				None,  # inpaint_color_sketch
				None,  # inpaint_color_sketch_orig
				image,  # p.init_img_inpaint
				init_mask,  # p.init_mask_inpaint
				self.Unprompted.shortcode_user_vars["steps"],
				self.Unprompted.shortcode_user_vars["sampler_name"],
				self.Unprompted.shortcode_user_vars["mask_blur"] if "mask_blur" in self.Unprompted.shortcode_user_vars else 0,  # p.mask_blur
				0.0,  #p.mask_alpha
				0,  # p.inpainting_fill
				1, 
				1, 
				self.Unprompted.shortcode_user_vars["cfg_scale"],
				self.Unprompted.shortcode_user_vars["image_cfg_scale"] if "image_cfg_scale" in self.Unprompted.shortcode_user_vars else None,
				self.Unprompted.shortcode_user_vars["denoising_strength"] if self.Unprompted.shortcode_user_vars["denoising_strength"] is not None else 1.0,
				0,  #selected_scale_tab
				current_height, #self.Unprompted.shortcode_user_vars["height"],
				current_width, #self.Unprompted.shortcode_user_vars["width"],
				1.0,  #scale_by
				self.Unprompted.shortcode_user_vars["resize_mode"] if "resize_mode" in self.Unprompted.shortcode_user_vars else 1,
				self.Unprompted.shortcode_user_vars["inpaint_full_res"] if "inpaint_full_res" in self.Unprompted.shortcode_user_vars else True,  # p.inpaint_full_res
				self.Unprompted.shortcode_user_vars["inpaint_full_res_padding"] if "inpaint_full_res_padding" in self.Unprompted.shortcode_user_vars else 1,  # p.inpaint_full_res_padding
				0,  # p.inpainting_mask_invert
				"",  #p.batch_input_directory
				"",  #p.batch_output_directory
				"",  #p.img2img_batch_inpaint_mask_dir
				"",  # override_settings_texts
				self.Unprompted.shortcode_user_vars["img2img_batch_use_png_info"] if "img2img_batch_use_png_info" in self.Unprompted.shortcode_user_vars else 0,  # img2img_batch_use_png_info
				None,  # img2img_batch_png_info_props,
				"",  # img2img_batch_png_info_dir
				temp_gr_request,
				*self.Unprompted.main_p.script_args)

			# Get the image stored in the first index
			img2img_images.append(img2img_result[0][0])

		except Exception as e:
			self.log.exception("Exception while running the img2img task")
			did_error = True

		# Re-enable alwayson scripts
		if temp_alwayson:
			self.Unprompted.shortcode_user_vars["scripts"].alwayson_scripts = temp_alwayson
		self.Unprompted.is_enabled = True

		try:
			if len(img2img_images) < 1:
				self.log.error(f"The returned object does not appear to contain an image: {img2img_images}")
				return ""
		except Exception as e:
			self.log.error("Could not check length of img2img_images")
			pass

		# Add the new image(s) to our main output
		if did_error: 
			return False
		elif "return_image" in pargs:
			return img2img_images[0]
		else:
			self.Unprompted.after_processed.images.extend(img2img_images)
			self.Unprompted.shortcode_user_vars["init_images"] = self.Unprompted.after_processed.images
		return ""
	
	def after(self, p=None, processed=None):
		self.counter = -1	# reset the counter for the next run
		self.image_array = []  # this array holds the whole images, make sure to clear it after the run
		return ""

	def ui(self, gr):
		gr.Slider(label="Img2Img Ratio (if value is other than 1, it is used over the height and width supplied) 🡢 ratio", value=1.0, maximum=3, minimum=0.25, interactive=True, step=0.01)