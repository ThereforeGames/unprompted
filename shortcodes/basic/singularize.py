class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Converts the content into singular form."
	def run_block(self, pargs, kwargs, context, content):
		from pattern.en import singularize

		this_pos = kwargs["pos"] if "pos" in kwargs else "noun"

		return(singularize(content,pos=this_pos))

	def ui(self,gr):
		pass