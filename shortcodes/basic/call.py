import glob
import random
import os


class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Processes the function or filepath content of the first parg."

	def run_atomic(self, pargs, kwargs, context):
		import lib_unprompted.helpers as helpers

		contents = "ok"
		else_id = kwargs["_else_id"] if "_else_id" in kwargs else str(self.Unprompted.conditional_depth)

		if "_bypass_if" in kwargs and self.Unprompted.parse_advanced(kwargs["_bypass_if"], context):
			contents = ""
		else:
			name = self.Unprompted.parse_alt_tags(pargs[0], context)
			next_context = ""
			this_encoding = self.Unprompted.parse_advanced(kwargs["_encoding"], context) if "_encoding" in kwargs else "utf-8"

			if name in self.Unprompted.shortcode_objects["function"].functions:
				self.log.debug(f"{name} was detected as a function")

				if len(self.Unprompted.shortcode_objects["function"].function_required_args[name]):
					for arg in self.Unprompted.shortcode_objects["function"].function_required_args:
						if arg not in pargs and arg not in kwargs and arg not in self.Unprompted.shortcode_user_vars:
							self.log.debug(f"Required arg `{arg}` not met. Bypassing function {name}.")
							contents = ""
							break

				if contents == "ok":
					if len(self.Unprompted.shortcode_objects["function"].function_default_args[name]):
						self.log.debug("Parsing default args...")
						for arg, val in self.Unprompted.shortcode_objects["function"].function_default_args[name].items():
							if arg not in pargs and arg not in kwargs:
								self.Unprompted.shortcode_objects["set"].run_block([arg], {}, context, val)

					contents = self.Unprompted.shortcode_objects["function"].functions[name]
					next_context = name
			else:
				# self.log.debug(f"{name} is assumed to be a filepath")

				file = self.Unprompted.parse_filepath(helpers.str_with_ext(name, self.Unprompted.Config.txt_format), context=context, must_exist=False)

				if not os.path.exists(file):
					if "_suppress_errors" not in pargs: self.log.error(f"File does not exist: {file}")
					contents = ""
				else:
					next_context = file  # os.path.dirname(file)
					with open(file, "r", encoding=this_encoding) as f:
						contents = f.read()
					f.close()

		# Return logic
		if not contents:
			self.Unprompted.shortcode_objects["else"].do_else[else_id] = True
		else:
			# Use [set] with keyword arguments
			for key, value in kwargs.items():
				if (self.Unprompted.is_system_arg(key)): continue
				self.Unprompted.shortcode_objects["set"].run_block([key], {}, context, self.Unprompted.parse_alt_tags(value))

			contents = self.Unprompted.process_string(contents, next_context)

			if contents == "_false":
				contents = ""
				self.Unprompted.shortcode_objects["else"].do_else[else_id] = True
			else:
				self.Unprompted.prevent_else(else_id)

		# self.Unprompted.conditional_depth = max(0, self.Unprompted.conditional_depth -1)
		return contents

	def ui(self, gr):
		gr.Textbox(label="Function name or filepath 🡢 str", max_lines=1)
		gr.Textbox(label="Expected encoding 🡢 _encoding", max_lines=1, value="utf-8")
		pass