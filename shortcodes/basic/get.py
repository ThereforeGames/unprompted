class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns the value of a variable."
	def run_atomic(self, pargs, kwargs, context):
		_default = self.Unprompted.parse_advanced(kwargs["_default"],context) if "_default" in kwargs else ""
		_sep = str(self.Unprompted.parse_advanced(kwargs["_sep"],context)) if "_sep" in kwargs else " "

		return_string = ""
		for idx,parg in enumerate(pargs):
			if idx == 0:
				if "_var" in kwargs: parg = self.Unprompted.parse_alt_tags(kwargs["_var"],context)
			else: return_string += _sep
			if ("_before" in kwargs):
				self.Unprompted.shortcode_user_vars[parg] = kwargs["_before"] + str(self.Unprompted.shortcode_user_vars[parg])
			if ("_after" in kwargs):
				self.Unprompted.shortcode_user_vars[parg] = str(self.Unprompted.shortcode_user_vars[parg] + kwargs["_after"])
			if (parg in self.Unprompted.shortcode_user_vars):
				this_var = self.Unprompted.shortcode_user_vars[parg]
				if (isinstance(this_var,list)): return_string += _sep.join(str(x) for x in this_var)
				else: return_string += str(this_var)
			else: return_string += _default

		return(return_string)

	def ui(self,gr):
		gr.Textbox(label="Variable to get 🡢 str",max_lines=1,placeholder="my_var")
		gr.Textbox(label="Default value if the variable doesn't exist 🡢 _default",max_lines=1)
		gr.Textbox(label="Separator string when returning multiple variables 🡢 _sep",max_lines=1)
		gr.Textbox(label="String to prepend to the variable 🡢 _before",max_lines=1)
		gr.Textbox(label="String to append to the variable 🡢 _after",max_lines=1)