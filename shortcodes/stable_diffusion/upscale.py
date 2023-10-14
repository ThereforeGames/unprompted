try:
	from modules import shared
except:
	pass  # for unprompted_dry


class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Enhances a given image using the WebUI's built-in upscaler methods."

	def run_atomic(self, pargs, kwargs, context):
		from PIL import Image
		import lib_unprompted.helpers as helpers

		image = self.Unprompted.parse_arg("image",False)
		if not image: image = self.Unprompted.current_image()
		if isinstance(image,str):
			image = Image.open(image)
		orig_image = image.copy()

		scale = self.Unprompted.parse_arg("scale",1)
		visibility = self.Unprompted.parse_arg("visibility",1.0)
		limit = self.Unprompted.parse_arg("limit",100)
		keep_res = self.Unprompted.parse_arg("keep_res",False)

		_models = helpers.ensure(self.Unprompted.parse_arg("models","None"),list)
		models = []
		for model in _models:
			for upscaler in shared.sd_upscalers:
				if upscaler.name == model:
					models.append(upscaler)
					break
			if len(models) >= limit:
				self.log.info(f"Upscale model limit satisfied ({limit}). Proceeding...")
				break

		for model in models:
			self.log.info(f"Upscaling {scale}x with {model.name}...")
			image = model.scaler.upscale(image, scale, model.data_path)
			if keep_res:
				image = image.resize(orig_image.size, Image.ANTIALIAS)

		# Append to output window
		try:
			if not keep_res:
				orig_image = orig_image.resize(image.size, Image.ANTIALIAS)
			self.Unprompted.current_image(Image.blend(orig_image, image, visibility))
		except:
			pass

		return ""

	def ui(self, gr):
		gr.Image(label="Image to perform upscaling on (defaults to SD output) 🡢 image",type="filepath",interactive=True)
		gr.Dropdown(label="Upscaler Model(s) 🡢 models",choices=[upscaler.name for upscaler in shared.sd_upscalers],multiselect=True)
		gr.Slider(label="Upscale Factor 🡢 scale", value=1, maximum=16, minimum=1, interactive=True, step=1)
		gr.Slider(label="Upscale Visibility 🡢 visibility", value=1.0, maximum=1.0, minimum=0.0, interactive=True, step=0.01)
		gr.Checkbox(label="Keep original resolution 🡢 keep_res", value=False, interactive=True)