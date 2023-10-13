import random


class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns the content if the number you passed is greater than or equal to a random number between 1 and 100."

	def preprocess_block(self, pargs, kwargs, context):
		return True

	def run_block(self, pargs, kwargs, context, content):
		_number = self.Unprompted.parse_advanced(pargs[0], context)
		_sides = self.Unprompted.parse_advanced(kwargs["_sides"], context) if "_sides" in kwargs else 100
		else_id = kwargs["_else_id"] if "_else_id" in kwargs else str(self.Unprompted.conditional_depth)

		to_return = ""
		if (int(float(_number)) >= random.randint(1, int(_sides))):
			self.Unprompted.prevent_else(else_id)
			if "_raw" in pargs: to_return = self.Unprompted.process_string(content, context)
			else: to_return = self.Unprompted.process_string(self.Unprompted.sanitize_pre(content, self.Unprompted.Config.syntax.sanitize_block, True), context, False)
		else:
			self.Unprompted.shortcode_objects["else"].do_else[else_id] = True

		# self.Unprompted.conditional_depth = max(0, self.Unprompted.conditional_depth -1)
		return to_return

	def ui(self, gr):
		gr.Number(label="Highest possible roll 🡢 _sides", value=100, interactive=True)
		gr.Checkbox(label="Print content without sanitizing 🡢 _raw")