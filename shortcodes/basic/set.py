class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Stores a value into a given variable."
	def run_block(self, pargs, kwargs, context, content):
		overrides = self.Unprompted.shortcode_objects["override"]
		can_set = True

		if (content is None or len(content) < 1): return ""

		# Prep content with override support
		if (pargs[0] in overrides.shortcode_overrides):
			content = overrides.shortcode_overrides[pargs[0]]
		elif "_raw" in pargs: content = self.Unprompted.process_string(content,context)
		else:
			content = self.Unprompted.process_string(self.Unprompted.sanitize_pre(content,self.Unprompted.Config.syntax.sanitize_block,True),context,False)
		content = self.Unprompted.autocast(content)

		if "_new" in pargs:
			if pargs[0] in self.Unprompted.shortcode_user_vars:
				# Check if this var already holds a valid value, if not we will set it
				if "_choices" in kwargs:
					if self.Unprompted.shortcode_user_vars[pargs[0]] in kwargs["_choices"].split(self.Unprompted.Config.syntax.delimiter): can_set = False
				else: can_set = False
		elif "_choices" in kwargs:
			if str(content) not in kwargs["_choices"].split(self.Unprompted.Config.syntax.delimiter): can_set = False
		
		if can_set:
			if ("_append" in pargs): self.Unprompted.shortcode_user_vars[pargs[0]] += content
			elif ("_prepend" in pargs): self.Unprompted.shortcode_user_vars[pargs[0]] = content + self.Unprompted.shortcode_user_vars[pargs[0]]
			else: self.Unprompted.shortcode_user_vars[pargs[0]] = content
		
			self.Unprompted.log(f"Setting {pargs[0]} to {self.Unprompted.shortcode_user_vars[pargs[0]]}")

		if ("_out" in pargs): return(self.Unprompted.shortcode_user_vars[pargs[0]])
		else: return("")

	def ui(self,gr):
		gr.Textbox(label="Variable name 🡢 verbatim",max_lines=1)
		gr.Checkbox(label="Only set this variable if it doesn't already exist 🡢 _new")
		gr.Textbox(label="Array of valid values (used in conjunction with _new) 🡢 _choices")
		gr.Checkbox(label="Append the content to the variable's current value 🡢 _append")
		gr.Checkbox(label="Prepend the content to the variable's current value 🡢 _prepend")
		gr.Checkbox(label="Store content without sanitizing 🡢 _raw")
		gr.Checkbox(label="Print the variable's value 🡢 _out")