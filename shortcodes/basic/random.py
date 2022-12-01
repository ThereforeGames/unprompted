import random

class Shortcode():
	"""Returns a random number between 0 and a given max value (inclusive)"""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_atomic(self, pargs, kwargs, context):
		_min = 0
		if ("_min" in kwargs):
			_min = self.Unprompted.parse_alt_tags(kwargs["_min"],context)
			_max = self.Unprompted.parse_alt_tags(kwargs["_max"],context)
		else:
			_max = pargs[0]

		if ("_float" in pargs): return(random.uniform(float(_min),float(_max)))
		else: return(random.randint(int(_min), int(_max)))