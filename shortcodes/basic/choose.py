import random

class Shortcode():
	"""Returns one of multiple options, delimited by newline or vertical pipe"""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted

	def run_block(self, pargs, kwargs, context, content):
		final_string = ""
		parts = content.replace(getattr(self.Unprompted.Config.syntax.sanitize_before,"\n","\\n"),self.Unprompted.Config.syntax.delimiter).split(self.Unprompted.Config.syntax.delimiter)
		# Remove empty lines
		parts = list(filter(None, parts))

		times = self.Unprompted.parse_advanced(pargs[0],context) if len(pargs)>0 else 1

		_sep = self.Unprompted.parse_advanced(kwargs["_sep"],context) if "_sep" in kwargs else ", "
		_case = max(min(len(parts)-1, int(self.Unprompted.parse_advanced(kwargs["_case"],context))), 0) if "_case" in kwargs else -1

		for x in range(0, times):
			if (_case == -1):
				part_index = random.choice(range(len(parts)))
				final_string += self.Unprompted.parse_alt_tags(parts[part_index],context)
			else:
				part_index = _case
				final_string += self.Unprompted.parse_alt_tags(parts[part_index],context)
			
			if (times > 1 and x != times - 1):
				del parts[part_index]
				final_string += _sep

		return final_string