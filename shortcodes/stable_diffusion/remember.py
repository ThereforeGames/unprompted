class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Allows certain vars to persist throughout a batch run."
		self.globals = []

	def run_atomic(self, pargs, kwargs, context):
		for parg in pargs:
			if parg not in self.globals:
				self.globals.append(parg)
		return ""

	def cleanup(self):
		self.globals = []

	def ui(self, gr):
		gr.Textbox(label="Arbitrary variable names to remember 🡢 verbatim", max_lines=1, placeholder="var_a var_b var_c")