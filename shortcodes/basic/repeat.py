import random

class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns the content an arbitrary number of times."

	def preprocess_block(self,pargs,kwargs,context): return True	

	def run_block(self, pargs, kwargs, context, content):
		import lib_unprompted.helpers as helpers
		final_string = ""
		_sep = kwargs["_sep"] if "_sep" in kwargs else ""

		_times = self.Unprompted.parse_advanced(pargs[0],context)

		# Support floats
		_times = helpers.autocast(_times)
		if isinstance(_times,float):
			probability = (_times % 1)
			_times = int(_times)
			if (probability >= random.uniform(0,1)): _times += 1

		for x in range(0, _times):
			final_string += self.Unprompted.process_string(content,context) + _sep

		return(final_string.rstrip(_sep))

	def ui(self,gr):
		gr.Number(label="Number of times to repeat the content 🡢 int",max_lines=1,value=2)
		gr.Textbox(label="Delimiter string between outputs 🡢 _sep",max_lines=1)