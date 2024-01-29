# NOTE: This img2img_enhanced tag is not as well developed as the original img2img tag. This was created for the purpose
# of allowing img2img to be used in a batch mode. The original img2img tag did not work well in batch
# I have choosen to go with a new tag as updated the existing one may create breaking changes for all people who have already 
# hacked together some other solution or use it in their own unique way. 

try:
	from modules.processing import process_images_inner	
	from modules import sd_samplers
except:
	pass  # for unprompted_dry

def process_images_inner_(this_p):
	return (process_images_inner(this_p))

class Shortcode():

	def __init__(self, Unprompted):
		import lib_unprompted.helpers as helpers
		self.Unprompted = Unprompted
		self.description = "img2img enhanced edition. This will allow you to run img2img either on a single image or on a batch of images. "
		self.description += "If you are running a batch of images inside of an [after] block. I believe the [after] block is required for this. "
		self.description += "The img2img_enhanced task requires that you have have the Automatic1111 setting: User Interface -> Infotext -> Write Infotext to metadata of the generated image, turned on."

	def run_atomic(self, pargs, kwargs, context):
		import modules.img2img
		
		try:
			self.is_processing = True
			self.Unprompted.update_user_vars(self.Unprompted.main_p)
			
			batch_idx = self.Unprompted.shortcode_user_vars["batch_real_index"] if "batch_real_index" in self.Unprompted.shortcode_user_vars else 0
			if batch_idx > 0:
				return ""

			# this just sets up the starting image for the img2img operation
			image_array = []
			try:
				image_array = self.Unprompted.main_p.init_images.copy()
			except:
				image_array = self.Unprompted.after_processed.images.copy()

			all_prompts = self.Unprompted.after_processed.all_prompts.copy()
			all_negative_prompts = self.Unprompted.after_processed.all_negative_prompts.copy()

			temp_gr_request = lambda: None
			temp_gr_request.username = "unprompted"

			# this is setting up the img2img settings so that i can be processed one at a time
			self.Unprompted.main_p.mode = 0
			self.Unprompted.main_p.image_mask = None
			self.Unprompted.main_p.mask = None
			self.Unprompted.main_p.init_img_with_mask = None
			self.Unprompted.main_p.init_mask = None
			self.Unprompted.main_p.mask_mode = 0
			self.Unprompted.main_p.init_mask_inpaint = None
			self.Unprompted.main_p.latent_mask = None
			self.Unprompted.main_p.batch_size = 1
			self.Unprompted.main_p.n_iter = 1

			if "mask_mode" not in self.Unprompted.shortcode_user_vars: self.Unprompted.shortcode_user_vars["mask_mode"] = 0
			init_mask = None
			if "init_mask" in self.Unprompted.shortcode_user_vars: init_mask = self.Unprompted.shortcode_user_vars["init_mask"]
			elif "init_mask_inpaint" in self.Unprompted.shortcode_user_vars: init_mask = self.Unprompted.shortcode_user_vars["init_mask_inpaint"]
			init_img_with_mask = self.Unprompted.shortcode_user_vars["init_img_with_mask"] if "init_img_with_mask" in self.Unprompted.shortcode_user_vars else None
			
			ux_width = self.Unprompted.shortcode_user_vars["width"]
			ux_height = self.Unprompted.shortcode_user_vars["height"]

			# There are only prompts in the prompt array for the non-grid images
			# count the number of grid images that are skipped so that we can index the prompts correctly
			image_skip_count = 0
			batch_idx = 0

			for batch_idx in range(len(image_array)):
				image = image_array[batch_idx]
				current_width = image.width
				current_height = image.height

				# check if we have a grid image, as its width or height is always different than the other images
				# with the exception of if the user generates a grid image even for 1 image batches
				if (ux_width != current_width or ux_height != current_height):
					image_skip_count += 1
					continue

				batch_idx_fixed = batch_idx - image_skip_count
				current_positive_prompt = all_prompts[batch_idx_fixed]
				current_negative_prompt = all_negative_prompts[batch_idx_fixed]

				denoising_strength = self.Unprompted.parse_arg("denoising_strength",-1.0,float)			
					
				if (denoising_strength == -1):
					denoising_strength = float(self.Unprompted.shortcode_user_vars["denoising_strength"] if self.Unprompted.shortcode_user_vars["denoising_strength"] is not None else 1.0)

				config_scale = self.Unprompted.parse_arg("config_scale",-1.0, float)
				if (config_scale == -1):
					config_scale = self.Unprompted.shortcode_user_vars["image_cfg_scale"] if "image_cfg_scale" in self.Unprompted.shortcode_user_vars else None,

				# if the ratio is set to 0 then use the width and height, otherwise use the ratio
				ratio = self.Unprompted.parse_arg("ratio",0.0)

				if ratio != 0 and ratio != 1:
					current_width = int(current_width * ratio)
					current_height = int(current_height * ratio)

				sampler_name = self.Unprompted.parse_arg("sampler_name","")

				if sampler_name == "":
					sampler_name = self.Unprompted.shortcode_user_vars["sampler_name"]

				steps = self.Unprompted.parse_arg("steps",0)
				if steps == 0:
					steps = self.Unprompted.shortcode_user_vars["steps"]
					
				print(f"################# running img2img for img [{batch_idx_fixed+1}/{len(image_array)-image_skip_count})] prompt {current_positive_prompt} #################")
				img2img_result = modules.img2img.img2img(
					"unprompted_img2img",  #id_task
					int(self.Unprompted.shortcode_user_vars["mode"]) if "mode" in self.Unprompted.shortcode_user_vars else 0,  #p.mode
					current_positive_prompt,
					current_negative_prompt,
					[],  # prompt_styles
					image, # actual image to use for the img2img
					None,  # sketch
					init_img_with_mask,  # p.init_img_with_mask
					None,  # inpaint_color_sketch
					None,  # inpaint_color_sketch_orig
					image, #init image
					init_mask,  # p.init_mask_inpaint
					steps,
					sampler_name,
					self.Unprompted.shortcode_user_vars["mask_blur"] if "mask_blur" in self.Unprompted.shortcode_user_vars else 0,  # p.mask_blur
					0.0,  #p.mask_alpha
					0,  # p.inpainting_fill
					1, #forcing 1 for num iterations as we are doing one by one   #self.Unprompted.shortcode_user_vars["n_iter"] if "n_iter" in self.Unprompted.shortcode_user_vars else 1,  #p.n_iter - batch count
					1, #forcing 1 for batch size as we are doing 1 by 1  #self.Unprompted.shortcode_user_vars["batch_size"] if "batch_size" in self.Unprompted.shortcode_user_vars else 1,  #p.batch_size
					config_scale,
					self.Unprompted.shortcode_user_vars["image_cfg_scale"] if "image_cfg_scale" in self.Unprompted.shortcode_user_vars else None,
					denoising_strength,
					0,  #selected_scale_tab
					current_height,
					current_width,
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

		except Exception:
			self.log.exception("Exception while running the img2img_enhanced task")
			image_array = []
			return ""
		image_array = []
		return ""

	def ui(self, gr):
		gr.Slider(label="Img2Img Ratio (if value is other than 1, it is used over the height and width supplied) 🡢 ratio", value=1.0, maximum=3, minimum=0.25, interactive=True, step=0.01)
		gr.Dropdown(label="Img2Img Sampler Name 🡢 sampler_name",choices=[upscaler.name for upscaler in sd_samplers.samplers_for_img2img],multiselect=False)
		gr.Number(label="Img2Img Steps 🡢 steps", value=20, interactive=True)
		gr.Slider(label="Img2Img Config Scale 🡢 config_scale", value=7.0, maximum=20, minimum=0, interactive=True, step=0.1)
		gr.Slider(label="Img2Img Denoising Strength 🡢 denoising_strength", value=1.0, maximum=256.0, minimum=0.0, interactive=True, step=0.01) # not sure what the actual maximum is for this