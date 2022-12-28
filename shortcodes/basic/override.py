class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.shortcode_overrides = {}
		self.description = "Force variable(s) to hold a pre-determined value the rest of the run."

	def run_atomic(self, pargs, kwargs, context):
		self.shortcode_overrides.update(kwargs)
		return("")

	def cleanup(self):
		self.shortcode_overrides.clear()

	def ui(self,gr):
		gr.Textbox(label="Arguments in variable=value format 🡢 verbatim",max_lines=1,placeholder='my_var=6 another_var="300"')