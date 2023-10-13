class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Shorthand 'else-if.'"

	def preprocess_block(self, pargs, kwargs, context):
		return True

	def run_block(self, pargs, kwargs, context, content):
		to_return = ""
		else_id = kwargs["_else_id"] if "_else_id" in kwargs else str(self.Unprompted.conditional_depth)
		if (self.Unprompted.shortcode_objects["else"].do_else[else_id]):
			self.Unprompted.prevent_else(else_id)
			# Calls 'if' directly
			to_return = self.Unprompted.shortcode_objects["if"].run_block(pargs, kwargs, context, content)

		# self.Unprompted.conditional_depth = max(0, self.Unprompted.conditional_depth -1)
		return (to_return)

	def ui(self, gr):
		pass