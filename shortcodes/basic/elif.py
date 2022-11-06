class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted

	def run_block(self, pargs, kwargs, context, content):
		if (self.Unprompted.shortcode_objects["else"].do_else):
			# Calls 'if' directly
			if_result = self.Unprompted.shortcode_objects["if"].run_block(pargs,kwargs,context,content)
			return(if_result) # alt tags were already processed by 'if'
		else:
			return("")