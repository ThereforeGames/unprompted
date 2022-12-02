from lib.simpleeval import simple_eval
class Shortcode():
	"""It's a for loop."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted

	def run_block(self, pargs, kwargs, context, content):
		final_string = ""
		this_var = ""

		for key, value in kwargs.items():
			if (key[0] == "_"): continue # Skips system arguments
			this_var = key
			self.Unprompted.shortcode_objects["set"].run_block([key],None,context,value) # run [set]

		while True:
			if (simple_eval(pargs[0],names=self.Unprompted.shortcode_user_vars)):
				final_string += self.Unprompted.parse_alt_tags(content,context)
				self.Unprompted.shortcode_user_vars[this_var] = simple_eval(pargs[1],names=self.Unprompted.shortcode_user_vars)
			else: return(final_string)