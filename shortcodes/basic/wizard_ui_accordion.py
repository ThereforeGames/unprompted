class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Used to construct an accordion menu with the Wizard UI; the main parser simply returns the content."
	def run_block(self, pargs, kwargs, context, content):
		return(self.Unprompted.parse_alt_tags(content))
	def ui(self,gr):
		pass