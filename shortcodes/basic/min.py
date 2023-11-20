class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns the minimum value among the given arguments."
	def run_atomic(self, pargs, kwargs, context):
		min_value = None
		for key in pargs:
			this_value = self.Unprompted.parse_advanced(key)
			if min_value is None or float(this_value) < min_value: min_value = this_value
		return(min_value)

	def ui(self,gr):
		pass