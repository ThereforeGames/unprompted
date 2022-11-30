class Shortcode():
	"""Updates a string using the arguments for replacement logic."""

	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_block(self, pargs, kwargs, context, content):

		for key, value in kwargs.items():
			if (key[0] == "_"): continue # Skips system arguments

			content = content.replace(key,value)

		return(content)