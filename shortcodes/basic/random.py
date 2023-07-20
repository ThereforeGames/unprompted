import random


class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns a random number between 0 and a given max value (inclusive)"

	def run_atomic(self, pargs, kwargs, context):
		_min = 0
		if ("_min" in kwargs):
			_min = self.Unprompted.parse_advanced(kwargs["_min"], context)
			_max = self.Unprompted.parse_advanced(kwargs["_max"], context)
		else:
			_max = pargs[0]

		if ("_float" in pargs): return (random.uniform(float(_min), float(_max)))
		else: return (random.randint(int(_min), int(_max)))

	def ui(self, gr):
		gr.Number(label="Minimum number 🡢 _min", value=0, interactive=True)
		gr.Number(label="Maximum number 🡢 _max", value=10, interactive=True)
		gr.Checkbox(label="Evaluate as floats instead of integers 🡢 _float")