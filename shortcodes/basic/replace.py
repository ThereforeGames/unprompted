class Shortcode():
	"""Updates a string using the arguments for replacement logic."""

	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_block(self, pargs, kwargs, context, content):

		for key, value in kwargs.items():
			if (key == "_from"):
				from_value = self.Unprompted.parse_advanced(value,context)
				to_value = self.Unprompted.parse_advanced(kwargs["_to"],context)
			elif (key[0] != "_"):
				from_value = key
				to_value = self.Unprompted.parse_advanced(value,context)
			else: continue

			if ("_count" in kwargs): content = content.replace(from_value,to_value,self.Unprompted.parse_advanced(kwargs["_count"]))
			else: content = content.replace(from_value,to_value)

		return(content)