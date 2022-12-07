class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_atomic(self, pargs, kwargs, context):
		parg = self.Unprompted.parse_alt_tags(kwargs["_var"],context) if "_var" in kwargs else pargs[0]
		_default = self.Unprompted.parse_advanced(kwargs["_default"],context) if "_default" in kwargs else ""

		if (parg in self.Unprompted.shortcode_user_vars):
			if ("_before" in kwargs):
				self.Unprompted.shortcode_user_vars[parg] = kwargs["_before"] + str(self.Unprompted.shortcode_user_vars[parg])
			if ("_after" in kwargs):
				self.Unprompted.shortcode_user_vars[parg] = str(self.Unprompted.shortcode_user_vars[parg] + kwargs["_after"])
				
			return(str(self.Unprompted.shortcode_user_vars[parg]))
		else:
			return(_default)