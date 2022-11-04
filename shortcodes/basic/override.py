class Shortcode():
	"""Force variable(s) to hold a pre-determined value the rest of the run."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.shortcode_overrides = {}

	def run_atomic(self, pargs, kwargs, context):
		self.shortcode_overrides.update(kwargs)
		return("")

	def cleanup(self):
		self.shortcode_overrides.clear()