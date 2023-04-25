class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "It's a do-until loop."

	def preprocess_block(self,pargs,kwargs,context): return True

	def run_block(self, pargs, kwargs, context, content):
		final_string = ""

		while True:
			if "_raw" in pargs: final_string += self.Unprompted.process_string(content,context)
			else: final_string += self.Unprompted.process_string(self.Unprompted.sanitize_pre(content,self.Unprompted.Config.syntax.sanitize_block,True),context,False)
			
			if (self.Unprompted.parse_advanced(kwargs["until"],context)): return(final_string)

	def ui(self,gr):
		gr.Textbox(label="Until condition 🡢 until",max_lines=1)
		gr.Checkbox(label="Print content without sanitizing 🡢 _raw")
		pass