import glob
import random
import os

class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Processes the file content of 'path.'"

	def run_atomic(self, pargs, kwargs, context):
		if "_bypass_if" in kwargs:
			if self.Unprompted.parse_advanced(kwargs["_bypass_if"],context): return ""

		file_string = self.Unprompted.parse_alt_tags(pargs[0],context)
		this_encoding = self.Unprompted.parse_advanced(kwargs["_encoding"],context) if "_encoding" in kwargs else "utf-8"
		
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

		with open(file, "r", encoding=this_encoding) as f: file_contents = f.read()
		f.close()

		# Use [set] with keyword arguments
		for key, value in kwargs.items():
			if (key[0] == "_"): continue # Skips system arguments
			self.Unprompted.shortcode_objects["set"].run_block([key],{},context,value)

		self.Unprompted.shortcode_objects["else"].do_else = False
		return(self.Unprompted.process_string(file_contents,path))

	def ui(self,gr):
		gr.Textbox(label="Filepath 🡢 str",max_lines=1)
		gr.Textbox(label="Expected encoding 🡢 _encoding",max_lines=1,value="utf-8")
		pass