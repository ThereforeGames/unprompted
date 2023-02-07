class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns the content with prefixed with a definite or indefinite article."
	def run_block(self, pargs, kwargs, context, content):
		from pattern.en import referenced, inflect
		
		form = inflect.DEFINITE if "definite" in pargs else inflect.INDEFINITE

		return(referenced(content,article=form))

	def ui(self,gr):
		pass