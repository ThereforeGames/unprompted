class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns the minimum value among the given arguments."
	def run_atomic(self, pargs, kwargs, context):
		min_value = None
		return_key = self.Unprompted.parse_arg("_key", False)
		to_return = ""

		for key in pargs:
			# Array support:
			key_split = self.Unprompted.parse_alt_tags(key).split(self.Unprompted.Config.syntax.delimiter)
			for this_key in key_split:
				if self.Unprompted.is_system_arg(this_key): continue

				this_value = self.Unprompted.parse_advanced(key)
				try:
					if min_value is None or float(this_value) < min_value:
						min_value = this_value
						
						if return_key: to_return = this_key
						else: to_return = min_value				
				except:
					pass

		return(to_return)

	def ui(self,gr):
		pass