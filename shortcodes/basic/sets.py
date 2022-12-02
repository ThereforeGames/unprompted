class Shortcode():
	"""The atomic version of [set] that lets you set multiple variables at once."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_atomic(self, pargs, kwargs, context):
		for key,value in kwargs.items():
			self.Unprompted.shortcode_user_vars[key] = value
			self.Unprompted.log(f"Setting {key} to {value}")
		return("")