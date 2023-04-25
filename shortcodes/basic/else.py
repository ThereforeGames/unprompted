class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.do_else = False
		self.description = "Returns content if a previous conditional shortcode failed its check, otherwise discards content."

	def preprocess_block(self,pargs,kwargs,context): return True

	def run_block(self, pargs, kwargs, context, content):
		if (self.do_else):
			self.do_else = False
			return(self.Unprompted.process_string(self.Unprompted.sanitize_pre(content,self.Unprompted.Config.syntax.sanitize_block,True),context,False))
		else:
			return("")
	
	def cleanup(self):
		self.do_else = False

	def ui(self,gr):
		pass