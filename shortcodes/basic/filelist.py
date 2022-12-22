import glob
import random
import os

class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted

	def run_atomic(self, pargs, kwargs, context):
		file_string = self.Unprompted.parse_alt_tags(pargs[0],context)
		_delimiter = self.Unprompted.parse_advanced(kwargs["_delimiter"],context) if "_delimiter" in kwargs else self.Unprompted.Config.syntax.delimiter
		
		# Relative path
		if (file_string[0] == "."):
			path = os.path.dirname(context) + "/" + file_string
		
		files = glob.glob(file_string)
		if (len(files) == 0):
			self.Unprompted.log(f"No files found at this location: {path}",True,"ERROR")
			return("")

		files = _delimiter.join(files)

		return(files)