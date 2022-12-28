class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Removes one or more variables from memory. Generally not needed."
	def run_atomic(self, pargs, kwargs, context):
		for key in pargs:
			del self.Unprompted.shortcode_user_vars[key]
		return("")

	def ui(self,gr):
		gr.Textbox(label="Arbitrary variable names to free from memory 🡢 verbatim",max_lines=1,placeholder='my_var another_var')