class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Houses arbitrary code that you can [call]."
		self.functions = {}
		self.function_default_args = {}
		self.function_required_args = {}

	def preprocess_block(self, pargs, kwargs, context):
		return True

	def run_block(self, pargs, kwargs, context, content):
		func_name = self.Unprompted.parse_advanced(pargs[0], context)
		if "_const" not in pargs or func_name not in self.functions:
			self.functions[func_name] = content
			self.function_default_args[func_name] = {}
			self.function_required_args[func_name] = []

			# Define the required arguments for this function
			for parg in pargs:
				if parg == pargs[0] or self.Unprompted.is_system_arg(parg): continue
				self.function_default_args[func_name][parg] = 1
			for kwarg, val in kwargs.items():
				if (self.Unprompted.is_system_arg(kwarg)): continue
				self.function_default_args[func_name][kwarg] = val

			if "_required" in kwargs:
				self.function_required_args[func_name] = self.Unprompted.parse_advanced(kwargs["_required"], context).split(self.Unprompted.Config.syntax.delimiter)
		else:
			self.log.warning(f"The function {func_name} was already declared as a constant and cannot be changed.")
		self.log.debug(f"Successfully added {func_name} as a function.")
		return ""

	def cleanup(self):
		self.functions.clear()
		self.function_default_args.clear()
		self.function_required_args.clear()

	def ui(self, gr):
		gr.Textbox(label="Function name 🡢 str", max_lines=1)
		gr.Textbox(label="Delimited list of required arguments 🡢 _required", max_lines=1)
		gr.Checkbox(label="Make this a constant function that cannot be overwritten 🡢 _const")