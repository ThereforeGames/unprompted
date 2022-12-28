class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Parses the content using the simpleeval library, returning the result. Particularly useful for arithmetic."
	def run_block(self, pargs, kwargs, context, content):
		# Note: You can uncomment the following line to use this shortcode with Python's stock eval function. NOT SAFE OVER THE NETWORK - be careful dude!
		# return str(eval(content))
		return(str(self.Unprompted.parse_advanced(content,context)))

	def ui(self,gr):
		pass