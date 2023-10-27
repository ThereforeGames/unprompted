class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Force a variable to hold a pre-determined value the rest of the run."

	def run_block(self, pargs, kwargs, context,content):
		# self.shortcode_overrides.update(kwargs)
		self.Unprompted.shortcode_objects["overrides"].shortcode_overrides[pargs[0]] = self.Unprompted.parse_advanced(content,context)
		return("")

	def ui(self,gr):
		gr.Textbox(label="Variable name 🡢 str",max_lines=1,placeholder="my_var")