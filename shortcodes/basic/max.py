class Shortcode():
	"""Returns the maximum value among the given arguments."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_atomic(self, pargs, kwargs, context):
		max_value = None
		for key in pargs:
			this_value = self.Unprompted.parse_advanced(key)
			if max_value is None or this_value > max_value: max_value = this_value
		return(max_value)