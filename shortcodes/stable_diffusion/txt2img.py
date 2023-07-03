try:
	from modules.processing import process_images_inner
except: pass # for unprompted_dry

def process_images_inner_(p):
	return(process_images_inner(p))

class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Runs a txt2img task inside of an [after] block."
		self.wizard_prepend = f"{Unprompted.Config.syntax.tag_start}after{Unprompted.Config.syntax.tag_end}{Unprompted.Config.syntax.tag_start}txt2img"
		self.wizard_append = Unprompted.Config.syntax.tag_end + Unprompted.Config.syntax.tag_start + Unprompted.Config.syntax.tag_close + "after" + Unprompted.Config.syntax.tag_end
	def run_atomic(self, pargs, kwargs, context):
		# Temporarily bypass other scripts
		temp_alwayson = self.Unprompted.shortcode_user_vars["scripts"].alwayson_scripts.copy()
		self.Unprompted.shortcode_user_vars["scripts"].alwayson_scripts.clear()

		if hasattr(self.Unprompted.p_copy,"init_images"):
			# We're in img2img mode, so we need to prepare a different p object
			from modules.processing import StableDiffusionProcessingTxt2Img
			from modules.shared import opts
			import modules.shared as shared

			this_p = StableDiffusionProcessingTxt2Img(
				sd_model=shared.sd_model,
				outpath_samples=opts.outdir_samples or opts.outdir_txt2img_samples,
				outpath_grids=opts.outdir_grids or opts.outdir_txt2img_grids,
				prompt=self.Unprompted.shortcode_user_vars["prompt"],
				styles=[],
				negative_prompt=self.Unprompted.shortcode_user_vars["negative_prompt"],
				seed=self.Unprompted.shortcode_user_vars["seed"],
				subseed=self.Unprompted.shortcode_user_vars["subseed"],
				subseed_strength=self.Unprompted.shortcode_user_vars["subseed_strength"],
				seed_resize_from_h=self.Unprompted.shortcode_user_vars["seed_resize_from_h"],
				seed_resize_from_w=self.Unprompted.shortcode_user_vars["seed_resize_from_w"],
				seed_enable_extras=self.Unprompted.shortcode_user_vars["seed_enable_extras"] if "seed_enable_extras" in self.Unprompted.shortcode_user_vars else 0,
				sampler_name=self.Unprompted.shortcode_user_vars["sampler_name"] if "sampler_name" in self.Unprompted.shortcode_user_vars else "euler a",
				batch_size=self.Unprompted.shortcode_user_vars["batch_size"],
				n_iter=self.Unprompted.shortcode_user_vars["n_iter"],
				steps=self.Unprompted.shortcode_user_vars["steps"],
				cfg_scale=self.Unprompted.shortcode_user_vars["cfg_scale"],
				width=self.Unprompted.shortcode_user_vars["width"],
				height=self.Unprompted.shortcode_user_vars["height"],
				restore_faces=self.Unprompted.shortcode_user_vars["restore_faces"],
				tiling=self.Unprompted.shortcode_user_vars["tiling"],
				enable_hr=self.Unprompted.shortcode_user_vars["enable_hr"] if "enable_hr" in self.Unprompted.shortcode_user_vars else 0,
				denoising_strength=self.Unprompted.shortcode_user_vars["denoising_strength"] if "enable_hr" in self.Unprompted.shortcode_user_vars else None,
				hr_scale=self.Unprompted.shortcode_user_vars["hr_scale"] if "hr_scale" in self.Unprompted.shortcode_user_vars else 1.0,
				hr_upscaler=self.Unprompted.shortcode_user_vars["hr_upscaler"] if "hr_upscaler" in self.Unprompted.shortcode_user_vars else "latent",
				hr_second_pass_steps=self.Unprompted.shortcode_user_vars["hr_second_pass_steps"] if "hr_second_pass_steps" in self.Unprompted.shortcode_user_vars else 10,
				hr_resize_x=self.Unprompted.shortcode_user_vars["hr_resize_x"] if "hr_resize_x" in self.Unprompted.shortcode_user_vars else 512,
				hr_resize_y=self.Unprompted.shortcode_user_vars["hr_resize_y"] if "hr_resize_y" in self.Unprompted.shortcode_user_vars else 512,
				override_settings="",
				)
		else:
			# We're already in txt2img mode, so we should be able to use the same p object
			self.Unprompted.update_stable_diffusion_vars(self.Unprompted.main_p)
			this_p = self.Unprompted.main_p
			print(this_p.prompt)
		
		processed = process_images_inner_(this_p)

		self.Unprompted.after_processed.images.extend(processed.images)
		self.Unprompted.shortcode_user_vars["init_images"] = self.Unprompted.after_processed.images

		# Re-enable alwayson scripts
		self.Unprompted.shortcode_user_vars["scripts"].alwayson_scripts = temp_alwayson

		return ""

	def ui(self,gr):
		pass