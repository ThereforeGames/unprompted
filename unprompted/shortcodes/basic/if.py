class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_block(self, pargs, kwargs, context, content):
		is_true = True
		_not = "_not" in pargs
		
		for key, value in kwargs.items():
			this_value = self.Unprompted.parse_alt_tags(value,context)
			if (self.Unprompted.is_float(this_value)): this_value = float(this_value)
			if (str(self.Unprompted.shortcode_user_vars[key]) != str(this_value)):
				is_true = False
				break

		if ((is_true and not _not) or (_not and not is_true)):
			self.Unprompted.shortcode_objects["else"].do_else = False
			return(self.Unprompted.parse_alt_tags(content,context))
		else:
			self.Unprompted.shortcode_objects["else"].do_else = True
			return("")