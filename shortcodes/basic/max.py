class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns the maximum value among the given arguments."
	def run_atomic(self, pargs, kwargs, context):
		max_value = None
		for key in pargs:
			this_value = self.Unprompted.parse_advanced(key)
			if max_value is None or float(this_value) > max_value: max_value = this_value
		return(max_value)

	def ui(self,gr):
		pass