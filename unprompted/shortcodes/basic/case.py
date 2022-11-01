class Shortcode():
	"""Use within [switch] to run different logic blocks depending on the value of a var."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted

	def run_block(self, pargs, kwargs, context, content):
		_var = self.Unprompted.shortcode_objects["switch"].switch_var
		
		# self.Unprompted.log(pargs[0])

		if (_var in self.Unprompted.shortcode_user_vars):
			# Default case
			if len(pargs) == 0:
				return(self.Unprompted.parse_alt_tags(content,context))
			# Matching case
			elif self.Unprompted.is_equal(self.Unprompted.shortcode_user_vars[_var],pargs[0]):
				self.Unprompted.shortcode_objects["switch"].switch_var = ""
				return(self.Unprompted.parse_alt_tags(content,context))
		
		return("")
	