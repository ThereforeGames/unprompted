import random

class Shortcode():
	"""Returns the content if the number you passed is greater than or equal to a random number between 1 and 100."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		
	def run_block(self, pargs, kwargs, context, content):
		if ("_probability" in kwargs): this_number = self.Unprompted.parse_alt_tags(kwargs["_probability"],context)
		else: this_number = pargs[0]
		
		if (int(float(this_number)) >= random.randint(1, 100)):
			self.Unprompted.shortcode_objects["else"].do_else = False
			return(self.Unprompted.parse_alt_tags(content,context))
		else:
			self.Unprompted.shortcode_objects["else"].do_else = True
			return("")