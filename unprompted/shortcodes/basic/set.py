class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_block(self, pargs, kwargs, context, content):
		overrides = self.Unprompted.shortcode_objects["override"]

		if (pargs[0] in overrides.shortcode_overrides):
			content = overrides.shortcode_overrides[pargs[0]]

		if (self.Unprompted.is_float(content)): content = float(content)
		elif (self.Unprompted.is_int(content)): content = int(content)
		
		if ("_append" in pargs): self.Unprompted.shortcode_user_vars[pargs[0]] += content
		elif ("_prepend" in pargs): self.Unprompted.shortcode_user_vars[pargs[0]] = content + self.Unprompted.shortcode_user_vars[pargs[0]]
		else: self.Unprompted.shortcode_user_vars[pargs[0]] = content
		
		self.Unprompted.log(f"Setting {pargs[0]} to {content}")

		if ("_out" in pargs): return(content)
		else: return("")