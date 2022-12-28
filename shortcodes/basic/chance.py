import random

class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns the content if the number you passed is greater than or equal to a random number between 1 and 100."
		
	def run_block(self, pargs, kwargs, context, content):
		this_number = self.Unprompted.parse_advanced(pargs[0],context)
		
		_sides = self.Unprompted.parse_advanced(kwargs["_sides"],context) if "_sides" in kwargs else 100

		if (int(float(this_number)) >= random.randint(1, int(_sides))):
			self.Unprompted.shortcode_objects["else"].do_else = False
			return(self.Unprompted.parse_alt_tags(content,context))
		else:
			self.Unprompted.shortcode_objects["else"].do_else = True
			return("")

	def ui(self,gr):
		gr.Number(label="Highest possible roll 🡢 _sides",value=100,interactive=True)