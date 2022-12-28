class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Houses a comment that does not affect your final prompt."
	def run_atomic(self, pargs, kwargs, context):
		return("")
	def ui(self,gr):
		gr.Textbox(label="Comment 🡢 str",max_lines=1)
		pass