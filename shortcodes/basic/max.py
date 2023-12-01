class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns the maximum value among the given arguments."
	def run_atomic(self, pargs, kwargs, context):
		max_value = None
		return_key = self.Unprompted.parse_arg("_key", False)
		to_return = ""

		for key in pargs:
			# Array support:
			key_split = self.Unprompted.parse_alt_tags(key).split(self.Unprompted.Config.syntax.delimiter)
			for this_key in key_split:
				if self.Unprompted.is_system_arg(this_key): continue

				this_value = self.Unprompted.parse_advanced(this_key)
				try:
					if max_value is None or float(this_value) > max_value:
						max_value = this_value
						
						if return_key: to_return = this_key
						else: to_return = max_value
				except:
					pass
		
		return(to_return)

	def ui(self,gr):
		pass