class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_atomic(self, pargs, kwargs, context):
		for key in pargs:
			del self.Unprompted.shortcode_user_vars[key]
		return("")