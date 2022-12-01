class Shortcode():
	"""Updates a string using the arguments for replacement logic."""

	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_block(self, pargs, kwargs, context, content):

		for key, value in kwargs.items():
			if (key == "_from"):
				from_value = self.Unprompted.parse_alt_tags(value,context)
				to_value = self.Unprompted.parse_alt_tags(kwargs["_to"],context)
			elif (key[0] != "_"):
				from_value = key
				to_value = self.Unprompted.parse_alt_tags(value,context)
			else: continue

			content = content.replace(from_value,to_value)

		return(content)