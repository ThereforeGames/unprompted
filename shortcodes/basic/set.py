class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_block(self, pargs, kwargs, context, content):
		overrides = self.Unprompted.shortcode_objects["override"]

		if (pargs[0] in overrides.shortcode_overrides):
			content = overrides.shortcode_overrides[pargs[0]]
		else:
			content = self.Unprompted.parse_alt_tags(content,context)

		content = self.Unprompted.autocast(content)
		
		if pargs[0] not in self.Unprompted.shortcode_user_vars or "_new" not in pargs:
			if ("_append" in pargs): self.Unprompted.shortcode_user_vars[pargs[0]] += content
			elif ("_prepend" in pargs): self.Unprompted.shortcode_user_vars[pargs[0]] = content + self.Unprompted.shortcode_user_vars[pargs[0]]
			else: self.Unprompted.shortcode_user_vars[pargs[0]] = content
		
			self.Unprompted.log(f"Setting {pargs[0]} to {self.Unprompted.shortcode_user_vars[pargs[0]]}")

		if ("_out" in pargs): return(self.Unprompted.shortcode_user_vars[pargs[0]])
		else: return("")