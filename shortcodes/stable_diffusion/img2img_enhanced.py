try:
	from modules.processing import process_images_inner, StableDiffusionProcessingImg2Img, StableDiffusionProcessing
	from modules import shared
	from modules import sd_samplers
except:
	pass  # for unprompted_dry

# NOTE: This img2img_enhanced tag is not as well developed as the original img2img tag. This was created for the purpose
# of allowing img2img to be used in a batch mode. The original img2img tag did not work well in batch
# I have choosen to go with a new tag as updated the existing one may create breaking changes for all people who have already 
# hacked together some other solution or use it in their own unique way. 

def process_images_inner_(this_p):
	return (process_images_inner(this_p))

class Shortcode():

	def __init__(self, Unprompted):
		import lib_unprompted.helpers as helpers
		self.Unprompted = Unprompted
		self.description = "img2img enhanced edition. This will allow you to run img2img either on a single image or on a batch of images. If you are running a batch of images inside of an [after] block. I believe the [after] block is required for this"

		# the isFirstPass is being used to detect when we have the array of processed images from the previous operation
		# the first batch that comes through in the after def has the original images as well as an additional
		# image representing the image grid if you are doing batch. The image grid is always the first image.
		# this is essentially what fixes the batch processing issue that the original img2img has
		self.isFirstPass = True

	def run_atomic(self, pargs, kwargs, context):
		# this sets the variable multiple times, but it doesn't matter. It makes sure that the isFirstPass is true
		# as the state does not reset after the last operation is complete
		self.isFirstPass = True
		return ""

	def after(self, p=None, processed=None):
		import modules.img2img

		try:  	
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

			self.Unprompted.update_user_vars(self.Unprompted.main_p)
   
			if "mask_mode" not in self.Unprompted.shortcode_user_vars: self.Unprompted.shortcode_user_vars["mask_mode"] = 0
			init_mask = None
			if "init_mask" in self.Unprompted.shortcode_user_vars: init_mask = self.Unprompted.shortcode_user_vars["init_mask"]
			elif "init_mask_inpaint" in self.Unprompted.shortcode_user_vars: init_mask = self.Unprompted.shortcode_user_vars["init_mask_inpaint"]

			init_img_with_mask = self.Unprompted.shortcode_user_vars["init_img_with_mask"] if "init_img_with_mask" in self.Unprompted.shortcode_user_vars else None

			# batch processing hack, process the first time we come through and skip all the other passes
			# this way its easier to determine which of the images is the grid image, in the first pass
			# if you try to allow the other passes through, for some reason the after tag calls into here more times than is
			# expected, so this was the most reliable way I could get the batch processing to work
			if self.isFirstPass == True:
				
				# the first image is the grid image, so we are going to remove it as we don't want to process it
				if (len(processed.images) > 1):
					processed.images.pop(0)
     	
				self.isFirstPass = False
			else:
				# we do not need to process further as the first time in here, all of the images from the txt2img operation are available
				return ""

			for image in processed.images:

				current_width = self.Unprompted.parse_arg("width",0)
				current_height = self.Unprompted.parse_arg("height",0)
		
				if current_width == 0 or current_height == 0:
					current_width = image.width
					current_height = image.height
								
				# if the ratio is set to 0 then use the width and height, otherwise use the ratio
				ratio = self.Unprompted.parse_arg("ratio",1.0)

				if ratio != 0 and ratio != 1:
					current_width = int(current_width * ratio)
					current_height = int(current_height * ratio)

				sampler_name =  self.Unprompted.parse_arg("sampler_name","")

				if sampler_name == "":
					sampler_name = self.Unprompted.shortcode_user_vars["sampler_name"]

				steps = self.Unprompted.parse_arg("steps",0)
				if steps == 0:
					steps = self.Unprompted.shortcode_user_vars["steps"]

				config_scale = self.Unprompted.parse_arg("config_scale",0)
				if config_scale == 0:
					config_scale = self.Unprompted.shortcode_user_vars["config_scale"]

				img2img_result = modules.img2img.img2img(
					"unprompted_img2img",  #id_task
					int(self.Unprompted.shortcode_user_vars["mode"]) if "mode" in self.Unprompted.shortcode_user_vars else 0,  #p.mode
					self.Unprompted.shortcode_user_vars["prompt"],
					self.Unprompted.shortcode_user_vars["negative_prompt"],
					[],  # prompt_styles
					image,
					None,  # sketch
					init_img_with_mask,  # p.init_img_with_mask
					None,  # inpaint_color_sketch
					None,  # inpaint_color_sketch_orig
					image, #seeing if image can simply be passed as the init image    #init_img,  # p.init_img_inpaint
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
					self.Unprompted.shortcode_user_vars["denoising_strength"] if self.Unprompted.shortcode_user_vars["denoising_strength"] is not None else 1.0,
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
			return ""
   
		except Exception as e:
			self.log.exception("Exception while running the img2img task")
			return ""

	def ui(self, gr):
		gr.Slider(label="Img2Img Ratio (if value is other than 1, it is used over the height and width supplied) 🡢 ratio", value=1.0, maximum=3, minimum=0.25, interactive=True, step=0.01)
		gr.Number(label="Img2Img Width 🡢 width", value=512, interactive=True)
		gr.Number(label="Img2Img Height 🡢 height", value=512, interactive=True)		
		gr.Dropdown(label="Img2Img Sampler Name 🡢 sampler_name",choices=[upscaler.name for upscaler in sd_samplers.samplers_for_img2img],multiselect=False)
		gr.Number(label="Img2Img Steps 🡢 steps", value=20, interactive=True)
		gr.Number(label="Img2Img Config Scale 🡢 config_scale", value=7, interactive=True)