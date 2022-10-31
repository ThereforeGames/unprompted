class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_atomic(self, pargs, kwargs, context):
		if ("_var" in kwargs): parg = self.Unprompted.parse_alt_tags(kwargs["_var"],context)
		else: parg = pargs[0]

		if (parg in self.Unprompted.shortcode_user_vars):
			if ("after" in kwargs):
				self.Unprompted.shortcode_user_vars[parg] = str(self.Unprompted.shortcode_user_vars[parg]) + kwargs["after"]
			return(str(self.Unprompted.shortcode_user_vars[parg]))
		else:
			return("")