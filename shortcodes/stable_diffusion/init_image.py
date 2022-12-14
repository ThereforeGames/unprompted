import glob
import random
import os

class Shortcode():
	'''Loads an image from the given path and sets it as the initial image for use with img2img.'''
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted

	def run_atomic(self, pargs, kwargs, context):
		from PIL import Image

		path = self.Unprompted.parse_alt_tags(pargs[0],context)

		files = glob.glob(path)
		if (len(files) == 0):
			self.Unprompted.log(f"No files found at this location: {path}",True,"ERROR")
			return("")
		file = random.choice(files)

		self.Unprompted.log(f"Loading file: {file}")

		if not os.path.exists(file):
			self.Unprompted.log(f"File does not exist: {file}",True,"ERROR")
			return("")

		self.Unprompted.shortcode_user_vars["init_images"] = [Image.open(file)]

		return ""