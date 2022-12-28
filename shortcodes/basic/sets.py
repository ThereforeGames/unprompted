class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "The atomic version of [set] that lets you set multiple variables at once."
	def run_atomic(self, pargs, kwargs, context):
		for key,value in kwargs.items():
			if key not in self.Unprompted.shortcode_user_vars or "_new" not in pargs:
				self.Unprompted.shortcode_user_vars[key] = self.Unprompted.parse_advanced(value,context)
				self.Unprompted.log(f"Setting {key} to {value}")
		return("")

	def ui(self,gr):
		gr.Textbox(label="Arbitrary arguments in variable=value format 🡢 verbatim",max_lines=1,placeholder='my_var="something" another_var=56')
		gr.Checkbox(label="Only set this variable if it doesn't already exist 🡢 _new")