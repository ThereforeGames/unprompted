class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.do_else = False

	def run_block(self, pargs, kwargs, context, content):
		if (self.do_else):
			self.do_else = False
			return(self.Unprompted.parse_alt_tags(content,context))
		else:
			return("")
	
	def cleanup(self):
		self.do_else = False