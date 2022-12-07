class Shortcode():
	"""The atomic version of [set] that lets you set multiple variables at once."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_atomic(self, pargs, kwargs, context):
		for key,value in kwargs.items():
			if key not in self.Unprompted.shortcode_user_vars or "_new" not in pargs:
				self.Unprompted.shortcode_user_vars[key] = self.Unprompted.parse_advanced(value,context)
				self.Unprompted.log(f"Setting {key} to {value}")
		return("")