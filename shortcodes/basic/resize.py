import random

class Shortcode():
	def __init__(self,Unprompted):
		import lib_unprompted.helpers as helpers
		self.Unprompted = Unprompted
		self.description = "Adjusts the dimensions of a given image with scaling or cropping."
		self.resample_methods = helpers.pil_resampling_dict

	def run_atomic(self, pargs, kwargs, context):
		from PIL import Image

		image_orig = self.Unprompted.parse_alt_tags(pargs[0],context) if len(pargs) else self.Unprompted.current_image()
		width = self.Unprompted.parse_arg("width",0)
		height = self.Unprompted.parse_arg("height",0)
		# TODO: Figure out why this isn't working with the parse_arg function
		min_width = int(float(kwargs["min_width"]) if "min_width" in kwargs else 0)# self.Unprompted.parse_arg("min_width",-1)
		min_height = int(float(kwargs["min_height"]) if "min_height" in kwargs else 0)# self.Unprompted.parse_arg("min_height",-1)
		unit = self.Unprompted.parse_arg("unit","px")
		keep_ratio = self.Unprompted.parse_arg("keep_ratio",True)
		technique = self.Unprompted.parse_arg("technique","scale")
		resample_method = self.resample_methods[self.Unprompted.parse_arg("resample_method","Lanczos")]
		origin = self.Unprompted.parse_arg("origin","middle_center")
		save_out = self.Unprompted.parse_arg("save_out","")

		if isinstance(image_orig,str):
			image = Image.open(image_orig)
		else: image = image_orig

		if unit == "%":
			width = int(image.width * width)
			height = int(image.height * height)
			min_width = int(image.width * min_width)
			min_height = int(image.height * min_height)

		new_width = image.width
		new_height = image.height

		# If width and height are both specified, resize to those dimensions
		if width and height:
			new_width = width
			new_height = height
		# If only width is specified, resize to that width
		elif width:
			new_width = width
			if keep_ratio:
				new_height = int(image.height * width / image.width)
		# If only height is specified, resize to that height
		elif height:
			new_height = height
			if keep_ratio:
				new_width = int(image.width * height / image.height)

		# Enforce minimum width and height
		if new_height < min_height:
			new_height = min_height
			if keep_ratio:
				new_width = int(image.width * min_height / image.height)
		if new_width < min_width:
			new_width = min_width
			if keep_ratio:
				new_height = int(image.height * min_width / image.width)

		# Resize image if dimensions have changed
		if new_width != image.width or new_height != image.height:
			if technique == "scale":
				image = image.resize((new_width,new_height),resample=resample_method)
			elif technique == "crop":
				# Verify that image is larger than new dimensions
				if image.width < new_width or image.height < new_height:
					self.log.error(f"Image dimensions ({image.width}x{image.height}) are smaller than new dimensions ({new_width}x{new_height}). Skipping crop.")
					return ""

				# Determine bounding box based on `origin`
				if origin == "top_left":
					bbox = (0,0,new_width,new_height)
				elif origin == "top_center":
					bbox = (int((image.width - new_width) / 2),0,int((image.width - new_width) / 2) + new_width,new_height)
				elif origin == "top_right":
					bbox = (image.width - new_width,0,image.width,new_height)
				elif origin == "middle_left":
					bbox = (0,int((image.height - new_height) / 2),new_width,int((image.height - new_height) / 2) + new_height)
				elif origin == "middle_center":
					bbox = (int((image.width - new_width) / 2),int((image.height - new_height) / 2),int((image.width - new_width) / 2) + new_width,int((image.height - new_height) / 2) + new_height)
				elif origin == "middle_right":
					bbox = (image.width - new_width,int((image.height - new_height) / 2),image.width,int((image.height - new_height) / 2) + new_height)
				elif origin == "bottom_left":
					bbox = (0,image.height - new_height,new_width,image.height)
				elif origin == "bottom_center":
					bbox = (int((image.width - new_width) / 2),image.height - new_height,int((image.width - new_width) / 2) + new_width,image.height)
				elif origin == "bottom_right":
					bbox = (image.width - new_width,image.height - new_height,image.width,image.height)
				else:
					self.log.error(f"Invalid origin `{origin}`. Skipping crop.")
					return ""

				# Crop image
				image = image.crop(bbox)

			if not len(pargs):
				# Update current image
				self.Unprompted.current_image(image)
			if isinstance(image_orig,str) or save_out:
				# Save image to file
				if save_out: image.save(save_out)
				else: image.save(image_orig)
		else:
			self.log.info("Image dimensions unchanged. Skipping resize.")

		return ""

	def ui(self,gr):
		gr.Textbox(label="Path to image (uses SD image by default) 🡢 str")
		gr.Textbox(label="Save result to a different path (optional) 🡢 save_out")
		with gr.Row():
			gr.Number(label="New width 🡢 width")
			gr.Number(label="New height 🡢 height")
			gr.Dropdown(label="Unit 🡢 unit",choices=["px","%"],value="px")
		gr.Dropdown(label="Technique 🡢 technique", value="scale", choices=["scale","crop"], interactive=True)
		gr.Dropdown(label="Resample Method 🡢 resample_method", value="Lanczos", choices=list(self.resample_methods.keys()), interactive=True)
		gr.Dropdown(label="Crop Origin 🡢 origin", value="middle_center", choices=["top_left","top_center","top_right","middle_left","middle_center","middle_right","bottom_left","bottom_center","bottom_right"], interactive=True)
		gr.Checkbox(label="Maintain aspect ratio 🡢 keep_ratio",value=True)
		with gr.Row():
			gr.Number(label="Minimum width of resulting image 🡢 min_width",value=0)
			gr.Number(label="Minimum height of resulting image 🡢 min_height",value=0)