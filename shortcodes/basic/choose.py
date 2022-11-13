import random

class Shortcode():
	"""Returns one of multiple options, delimited by newline or vertical pipe"""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted

	def run_block(self, pargs, kwargs, context, content):
		parts = content.replace(self.Unprompted.Config.syntax.n_temp,self.Unprompted.Config.shortcodes.choose_delimiter).split(self.Unprompted.Config.shortcodes.choose_delimiter)
		# Remove empty lines
		parts = list(filter(None, parts))

		if ("_case" in kwargs):
			part_idx = max(min(len(parts)-1, int(self.Unprompted.parse_alt_tags(kwargs["_case"],context))), 0)
			selected = self.Unprompted.parse_alt_tags(parts[part_idx],context)
		else: selected = self.Unprompted.parse_alt_tags(random.choice(parts),context)

		return selected