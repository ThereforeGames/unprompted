import random

class Shortcode():
	"""Returns the content an arbitrary number of times."""
	
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_block(self, pargs, kwargs, context, content):
		final_string = ""
		_sep = kwargs["_sep"] if "_sep" in kwargs else ""

		_times = self.Unprompted.parse_advanced(pargs[0],context)

		# Support floats
		_times = self.Unprompted.autocast(_times)
		if isinstance(_times,float):
			probability = (_times % 1)
			_times = int(_times)
			if (probability >= random.uniform(0,1)): _times += 1

		for x in range(0, _times):
			final_string += self.Unprompted.parse_alt_tags(content,context) + _sep

		return(final_string.rstrip(_sep))