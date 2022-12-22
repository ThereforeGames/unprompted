class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_atomic(self, pargs, kwargs, context):
		_default = self.Unprompted.parse_advanced(kwargs["_default"],context) if "_default" in kwargs else ""
		_sep = str(self.Unprompted.parse_advanced(kwargs["_sep"],context)) if "_sep" in kwargs else " "

		return_string = ""
		for idx,parg in enumerate(pargs):
			if idx == 0:
				if "_var" in kwargs: parg = self.Unprompted.parse_alt_tags(kwargs["_var"],context)
			else: return_string += _sep
			if ("_before" in kwargs):
				self.Unprompted.shortcode_user_vars[parg] = kwargs["_before"] + str(self.Unprompted.shortcode_user_vars[parg])
			if ("_after" in kwargs):
				self.Unprompted.shortcode_user_vars[parg] = str(self.Unprompted.shortcode_user_vars[parg] + kwargs["_after"])
			if (parg in self.Unprompted.shortcode_user_vars): return_string += str(self.Unprompted.shortcode_user_vars[parg])
			else: return_string += _default

		return(return_string)