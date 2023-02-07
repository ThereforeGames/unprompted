class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Converts the content into plural form."
	def run_block(self, pargs, kwargs, context, content):
		from pattern.en import pluralize

		this_pos = kwargs["pos"] if "pos" in kwargs else "noun"

		return(pluralize(content,pos=this_pos))

	def ui(self,gr):
		pass