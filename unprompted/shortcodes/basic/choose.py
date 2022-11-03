import random

class Shortcode():
	"""Returns one of multiple options, delimited by newline or vertical pipe"""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted

	def run_block(self, pargs, kwargs, context, content):
		parts = content.replace(self.Unprompted.Config.syntax.n_temp,"|").split("|")
		# Remove empty lines
		parts = list(filter(None, parts))
		# self.Unprompted.log(f"List of options: {parts}")
		selected = self.Unprompted.parse_alt_tags(random.choice(parts),context)
		return selected