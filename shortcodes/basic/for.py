class Shortcode():
	"""It's a for loop."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted

	def run_block(self, pargs, kwargs, context, content):
		final_string = ""
		this_var = ""

		for key, value in kwargs.items():
			if (key[0] == "_"): continue # Skips system arguments
			this_var = key
			self.Unprompted.shortcode_objects["set"].run_block([key],None,context,value)

		while True:
			if (self.Unprompted.parse_advanced(pargs[0],context)):
				final_string += self.Unprompted.parse_alt_tags(content,context)
				self.Unprompted.shortcode_user_vars[this_var] = self.Unprompted.parse_advanced(pargs[1],context)
			else: return(final_string)