class Shortcode():
	"""Returns the content an arbitrary number of times."""

class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_block(self, pargs, kwargs, context, content):
		final_string = ""

		if ("_times" in kwargs): _times = self.Unprompted.parse_alt_tags(kwargs["_times"],context)
		else: _times = pargs[0]

		for x in range(0, int(_times) + 1):
			final_string += self.Unprompted.parse_alt_tags(content,context)

		return(final_string)