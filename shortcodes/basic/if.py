import operator


class Shortcode():
	def __init__(self, Unprompted):
		import lib_unprompted.helpers as helpers
		self.Unprompted = Unprompted
		self.ops = {"==": helpers.is_equal, "!=": helpers.is_not_equal, "<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}
		self.description = "Checks whether a variable is equal to a given value."

	def preprocess_block(self, pargs, kwargs, context):
		return True

	def run_block(self, pargs, kwargs, context, content):
		_not = "_not" in pargs
		_any = "_any" in pargs

		is_true = not _any

		# Normal expressions
		_is = kwargs["_is"] if "_is" in kwargs else "=="
		for key, value in kwargs.items():
			if self.Unprompted.is_system_arg(key): continue  # Skips system arguments

			this_value = self.Unprompted.parse_advanced(value, context)

			# Fix data type
			if (_is != "==" and _is != "!="):
				self.Unprompted.shortcode_user_vars[key] = float(self.Unprompted.shortcode_user_vars[key])
				this_value = float(this_value)

			if (key in self.Unprompted.shortcode_user_vars and self.ops[_is](self.Unprompted.shortcode_user_vars[key], this_value)):
				if _any:
					is_true = True
					break
			elif not _any:
				is_true = False
				break

		# Support truthy checks
		for key in pargs:
			if self.Unprompted.is_system_arg(key): continue
			if (self.Unprompted.parse_advanced(key, context)):  #  == 1
				if _any:
					is_true = True
					break
			elif not _any:
				is_true = False
				break

		to_return = ""
		else_id = kwargs["_else_id"] if "_else_id" in kwargs else str(self.Unprompted.conditional_depth)
		if ((is_true and not _not) or (_not and not is_true)):
			self.Unprompted.prevent_else(else_id)
			to_return = self.Unprompted.process_string(content, context)
		else:
			self.Unprompted.shortcode_objects["else"].do_else[else_id] = True

		return (to_return)

	def ui(self, gr):
		gr.Textbox(label="Conditional statement 🡢 my_var", max_lines=1)
		gr.Dropdown(label="Evaluation method 🡢 _is", choices=["==", "!=", "<", "<=", ">", ">="], value="==")
		gr.Checkbox(label="Invert evaluation such that a true statement will return false 🡢 _not")
		gr.Checkbox(label="Return true if any one of multiple conditions are true 🡢 _any")