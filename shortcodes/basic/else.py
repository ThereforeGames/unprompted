class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.do_else = {}
		self.description = "Returns content if a previous conditional shortcode failed its check, otherwise discards content."

	def preprocess_block(self, pargs, kwargs, context):
		return True

	def run_block(self, pargs, kwargs, context, content):
		to_return = ""
		else_id = kwargs["id"] if "id" in kwargs else str(self.Unprompted.conditional_depth)
		if (self.do_else[else_id]):
			self.Unprompted.prevent_else(else_id)

			to_return = self.Unprompted.process_string(self.Unprompted.sanitize_pre(content, self.Unprompted.Config.syntax.sanitize_block, True), context, False)

			self.Unprompted.conditional_depth = 0
		return (to_return)

	def cleanup(self):
		self.do_else.clear()

	def ui(self, gr):
		pass