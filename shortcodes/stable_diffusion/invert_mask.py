class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Inverts the mask (great in combination with multiple txt2masks)"

	def run_atomic(self, pargs, kwargs, context):
		from PIL import Image, ImageOps

		if "image_mask" in self.Unprompted.shortcode_user_vars:
			mask = self.Unprompted.shortcode_user_vars["image_mask"]
			mask = mask.convert("L")
			mask = ImageOps.invert(mask)
			self.Unprompted.shortcode_user_vars["image_mask"] = mask

		return ""
			
	def ui(self,gr):
		pass