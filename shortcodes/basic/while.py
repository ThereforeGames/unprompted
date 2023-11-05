import operator


class Shortcode():
	def __init__(self, Unprompted):
		import lib_unprompted.helpers as helpers
		self.Unprompted = Unprompted
		self.ops = {"==": helpers.is_equal, "!=": helpers.is_not_equal, "<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}
		self.description = "Loops content until the condition returns false."

	def preprocess_block(self, pargs, kwargs, context):
		return True

	def run_block(self, pargs, kwargs, context, content):
		final_string = ""

		_not = "_not" in pargs
		_any = "_any" in pargs

		is_true = not _any

		_is = kwargs["_is"] if "_is" in kwargs else "=="

		do_advanced_expression = False

		while True:
			for key in pargs:
				if (key[0] == "_"): continue  # Skips system arguments
				do_advanced_expression = True
				if (self.Unprompted.parse_advanced(key, context)):
					if _any:
						is_true = True
						break
				elif not _any:
					is_true = False
				break

			if not do_advanced_expression:
				for key, value in kwargs.items():
					if (key[0] == "_"): continue  # Skips system arguments

					this_value = self.Unprompted.parse_advanced(value, context)

					# Fix data type
					if (_is != "=="):
						self.Unprompted.shortcode_user_vars[key] = float(self.Unprompted.shortcode_user_vars[key])
						this_value = float(this_value)

					if (self.ops[_is](self.Unprompted.shortcode_user_vars[key], this_value)):
						if _any:
							is_true = True
							break
					elif not _any:
						is_true = False
					break

			if ((is_true and not _not) or (_not and not is_true)):
				if "_raw" in pargs: final_string += self.Unprompted.process_string(content, context)
				else: final_string += self.Unprompted.process_string(self.Unprompted.sanitize_pre(content, self.Unprompted.Config.syntax.sanitize_block, True), context, False)
			else:
				break

		return (final_string)

	def ui(self, gr):
		gr.Textbox(label="Arbitrary conditional statement(s) to test against 🡢 verbatim", max_lines=1)
		gr.Dropdown(label="Evaluation method 🡢 _is", choices=["==", "!=", "<", "<=", ">", ">="], value="==")
		gr.Checkbox(label="Invert evaluation such that a false condition will end the loop 🡢 _not")
		gr.Checkbox(label="Return true if any one of multiple conditions are true 🡢 _any")
		gr.Checkbox(label="Print content without sanitizing 🡢 _raw")