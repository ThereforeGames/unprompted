class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Automatically adjusts the width and height parameters in img2img mode based on the proportions of the input image."
	def run_atomic(self, pargs, kwargs, context):
		if "init_images" in self.Unprompted.shortcode_user_vars:
			sd_unit = 64
			target_size = self.Unprompted.parse_advanced(kwargs["target"],context) if "target" in kwargs else 512
			only_full_res = self.Unprompted.parse_advanced(kwargs["only_full_res"],context) if "only_full_res" in kwargs else False

			if not only_full_res or "inpaint_full_res" not in self.Unprompted.shortcode_user_vars or not self.Unprompted.shortcode_user_vars["inpaint_full_res"]:
			
				self.Unprompted.shortcode_user_vars["width"] = self.Unprompted.shortcode_user_vars["init_images"][0].width
				self.Unprompted.shortcode_user_vars["height"] = self.Unprompted.shortcode_user_vars["init_images"][0].height

				smaller_dimension = min(self.Unprompted.shortcode_user_vars["width"],self.Unprompted.shortcode_user_vars["height"])
				larger_dimension = max(self.Unprompted.shortcode_user_vars["width"],self.Unprompted.shortcode_user_vars["height"])

				if (smaller_dimension > target_size):
					multiplier = target_size / smaller_dimension
					self.Unprompted.shortcode_user_vars["width"] *= multiplier
					self.Unprompted.shortcode_user_vars["height"] *= multiplier
				if (larger_dimension < target_size):
					multiplier = target_size / larger_dimension
					self.Unprompted.shortcode_user_vars["width"] *= multiplier
					self.Unprompted.shortcode_user_vars["height"] *= multiplier

				self.Unprompted.shortcode_user_vars["width"] = round(self.Unprompted.shortcode_user_vars["width"] / sd_unit) * sd_unit
				self.Unprompted.shortcode_user_vars["height"] = round(self.Unprompted.shortcode_user_vars["height"] / sd_unit) * sd_unit

				self.Unprompted.log(f"Output image size: {self.Unprompted.shortcode_user_vars['width']}x{self.Unprompted.shortcode_user_vars['height']}")
	
		return("")

	def ui(self,gr):
		gr.Number(label="Minimum pixels of at least one dimension 🡢 target",value=512,interactive=True)
		gr.Checkbox(label="Only run this shortcode if using full resolution inpainting mode 🡢 only_full_res")