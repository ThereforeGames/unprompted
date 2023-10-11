class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Use within [switch] to run different logic blocks depending on the value of a var."

	def preprocess_block(self,pargs,kwargs,context): return True

	def run_block(self, pargs, kwargs, context, content):
		import lib_unprompted.helpers as helpers
		
		_var = self.Unprompted.shortcode_objects["switch"].switch_var
		
		# Default case
		if len(pargs) == 0:
			if _var != "": return(self.Unprompted.parse_alt_tags(content,context))
		# Matching case
		elif helpers.is_equal(_var,self.Unprompted.parse_advanced(pargs[0],context)):
			self.Unprompted.shortcode_objects["switch"].switch_var = ""
			return(self.Unprompted.parse_alt_tags(content,context))
		
		return("")

	def ui(self,gr):
		gr.Textbox(label="Matching value 🡢 str",max_lines=1)