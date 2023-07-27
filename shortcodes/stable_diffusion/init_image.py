import glob
import random
import os


class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Loads an image from the given path and sets it as the initial image for use with img2img."

	def run_atomic(self, pargs, kwargs, context):
		from PIL import Image

		path = self.Unprompted.parse_alt_tags(pargs[0], context)

		files = glob.glob(path)
		if (len(files) == 0):
			self.log.error(f"No files found at this location: {path}")
			return ("")
		file = random.choice(files)

		self.log.debug(f"Loading file: {file}")

		if not os.path.exists(file):
			self.log.error(f"File does not exist: {file}")
			return ("")

		self.Unprompted.shortcode_user_vars["init_images"] = [Image.open(file)]

		return ""

	def ui(self, gr):
		gr.File(label="Image path", file_type="image")
