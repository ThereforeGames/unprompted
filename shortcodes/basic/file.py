import glob
import random
import os

class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted

	def run_atomic(self, pargs, kwargs, context):
		file_string = pargs[0]
		# Relative path
		if (file_string[0] == "."):
			path = os.path.dirname(context) + "/" + file_string + self.Unprompted.Config.txt_format
		# Absolute path
		else: path = self.Unprompted.base_dir + "/" + self.Unprompted.Config.template_directory + "/" + file_string + self.Unprompted.Config.txt_format
		
		files = glob.glob(path)
		file = random.choice(files)

		self.Unprompted.log(f"Loading file: {file}")

		file_contents = open(file).read()

		self.Unprompted.shortcode_objects["else"].do_else = False
		return(self.Unprompted.process_string(file_contents,path))