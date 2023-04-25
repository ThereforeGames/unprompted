class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.switch_var = ""
		self.description = "Use in conjunction with [case] to run different logic blocks depending on the value of a var."

	def preprocess_block(self,pargs,kwargs,context): return True

	def run_block(self, pargs, kwargs, context,content):
		self.switch_var = self.Unprompted.parse_advanced(pargs[0],context)
		return(self.Unprompted.process_string(content,context))

	def cleanup(self):
		self.switch_var = ""

	def ui(self,gr):
		gr.Textbox(label="Variable to test against 🡢 verbatim",max_lines=1,placeholder='my_var')