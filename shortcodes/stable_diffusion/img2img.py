class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Runs an img2img task inside of an [after] block."
	def run_atomic(self, pargs, kwargs, context):
		import modules.img2img
		from modules import sd_samplers
		from modules import scripts

		did_error = False

		# Temporarily bypass alwayson scripts because I am not sure how to call modules.img2img.img2img with arbitrary extension args
		temp_alwayson = self.Unprompted.shortcode_user_vars["scripts"].alwayson_scripts.copy()
		self.Unprompted.shortcode_user_vars["scripts"].alwayson_scripts.clear()

		if "mask_mode" not in self.Unprompted.shortcode_user_vars: self.Unprompted.shortcode_user_vars["mask_mode"] = 0
		init_mask = None
		if "init_mask" in self.Unprompted.shortcode_user_vars: init_mask = self.Unprompted.shortcode_user_vars["init_mask"]
		elif "init_mask_inpaint" in self.Unprompted.shortcode_user_vars: init_mask = self.Unprompted.shortcode_user_vars["init_mask_inpaint"]

		# TODO: There might be a function to retrieve sampler index from its name, if so use that instead
		sampler_index = 0
		for i in range(len(sd_samplers.samplers_for_img2img)):
			if sd_samplers.samplers_for_img2img[i].name == self.Unprompted.shortcode_user_vars["sampler_name"]:
				sampler_index = i
				print(sd_samplers.samplers_for_img2img[i].name) #break

		if "img2img_init_image" in self.Unprompted.shortcode_user_vars:
			init_img = self.Unprompted.shortcode_user_vars["img2img_init_image"]
		else:
			init_img = self.Unprompted.shortcode_user_vars["init_images"][len(self.Unprompted.shortcode_user_vars["init_images"]) - 1]			
		init_img_with_mask = self.Unprompted.shortcode_user_vars["init_img_with_mask"] if "init_img_with_mask" in self.Unprompted.shortcode_user_vars else None
		
		try:
			img2img_result = modules.img2img.img2img(
				"unprompted_img2img", #id_task
				self.Unprompted.shortcode_user_vars["mode"] if "mode" in self.Unprompted.shortcode_user_vars else 0, #p.mode
				self.Unprompted.shortcode_user_vars["prompt"],
				self.Unprompted.shortcode_user_vars["negative_prompt"],
				[], # prompt_styles
				init_img,
				None, # sketch
				init_img_with_mask, # p.init_img_with_mask
				None, # inpaint_color_sketch
				None, # inpaint_color_sketch_orig
				init_img, # p.init_img_inpaint
				init_mask, # p.init_mask_inpaint
				self.Unprompted.shortcode_user_vars["steps"],
				sampler_index,
				self.Unprompted.shortcode_user_vars["mask_blur"] if "mask_blur" in self.Unprompted.shortcode_user_vars else 0, # p.mask_blur
				0.0, #p.mask_alpha
				0, # p.inpainting_fill
				self.Unprompted.shortcode_user_vars["restore_faces"],
				self.Unprompted.shortcode_user_vars["tiling"],
				self.Unprompted.shortcode_user_vars["n_iter"] if "n_iter" in self.Unprompted.shortcode_user_vars else 1, #p.n_iter - batch count
				self.Unprompted.shortcode_user_vars["batch_size"] if "batch_size" in self.Unprompted.shortcode_user_vars else 1, #p.batch_size
				self.Unprompted.shortcode_user_vars["cfg_scale"],
				self.Unprompted.shortcode_user_vars["image_cfg_scale"] if "image_cfg_scale" in self.Unprompted.shortcode_user_vars else None,
				self.Unprompted.shortcode_user_vars["denoising_strength"] if self.Unprompted.shortcode_user_vars["denoising_strength"] is not None else 1.0,
				self.Unprompted.shortcode_user_vars["seed"],
				self.Unprompted.shortcode_user_vars["subseed"],
				self.Unprompted.shortcode_user_vars["subseed_strength"],
				self.Unprompted.shortcode_user_vars["seed_resize_from_h"],
				self.Unprompted.shortcode_user_vars["seed_resize_from_w"],
				0, # seed_enable_extras
				self.Unprompted.shortcode_user_vars["height"],
				self.Unprompted.shortcode_user_vars["width"],
				self.Unprompted.shortcode_user_vars["resize_mode"] if "resize_mode" in self.Unprompted.shortcode_user_vars else 1,
				self.Unprompted.shortcode_user_vars["inpaint_full_res"] if "inpaint_full_res" in self.Unprompted.shortcode_user_vars else True, # p.inpaint_full_res
				self.Unprompted.shortcode_user_vars["inpaint_full_res_padding"] if "inpaint_full_res_padding" in self.Unprompted.shortcode_user_vars else 1, # p.inpaint_full_res_padding
				0, # p.inpainting_mask_invert
				"", #p.batch_input_directory
				"", #p.batch_output_directory
				"", #p.img2img_batch_inpaint_mask_dir
				"", # override_settings_texts
				0, # this is the *args tuple, 0 prevents additional scripts from running here
				0, # Prevents endless loop
				0,
				-1
			)

			# Get the image stored in the first index
			img2img_images = img2img_result[0]
		except:
			self.Unprompted.log("An error occurred while generating the image! Perhaps it was interrupted by the user?")	
			did_error = True

		# Re-enable alwayson scripts
		self.Unprompted.shortcode_user_vars["scripts"].alwayson_scripts = temp_alwayson

		if len(img2img_images) < 1:
			self.Unprompted.log(f"The returned object does not appear to contain an image: {img2img_images}",context="ERROR")
			return("")

		# Add the new image(s) to our main output
		if did_error: return False
		elif "return_image" in pargs:
			return img2img_images[0]
		else:
			self.Unprompted.after_processed.images.append(img2img_images[0])
			self.Unprompted.shortcode_user_vars["init_images"] = self.Unprompted.after_processed.images

		return("")

	def ui(self,gr):
		pass