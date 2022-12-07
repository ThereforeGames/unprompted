import glob
import random
import os

class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted

	def run_atomic(self, pargs, kwargs, context):
		file_string = self.Unprompted.parse_alt_tags(pargs[0],context)
		
		# Relative path
		if (file_string[0] == "."):
			path = os.path.dirname(context) + "/" + file_string + self.Unprompted.Config.txt_format
		# Absolute path
		else: path = self.Unprompted.base_dir + "/" + self.Unprompted.Config.template_directory + "/" + file_string + self.Unprompted.Config.txt_format
		
		files = glob.glob(path)
		if (len(files) == 0):
			self.Unprompted.log(f"No files found at this location: {path}",True,"ERROR")
			return("")
		file = random.choice(files)

		self.Unprompted.log(f"Loading file: {file}")

		if not os.path.exists(file):
			self.Unprompted.log(f"File does not exist: {file}",True,"ERROR")
			return("")

		file_contents = open(file).read()

		# Use [set] with keyword arguments
		for key, value in kwargs.items():
			self.Unprompted.shortcode_objects["set"].run_block([key],None,context,value)

		self.Unprompted.shortcode_objects["else"].do_else = False
		return(self.Unprompted.process_string(file_contents,path))