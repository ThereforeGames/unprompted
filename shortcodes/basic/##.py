class Shortcode():
	"""Houses a multiline comment that will not affect the final output."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_block(self, pargs, kwargs, context, content):
		return("")