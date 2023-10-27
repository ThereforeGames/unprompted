import random, copy


class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns one of multiple options, delimited by newline or vertical pipe"
		# self.sanitize_original = copy.copy(self.Unprompted.Config.syntax.sanitize_after)

	def preprocess_block(self, pargs, kwargs, context):
		return True

	def run_block(self, pargs, kwargs, context, content):
		import lib_unprompted.helpers as helpers
		# import copy
		temp_syntax_after = copy.copy(self.Unprompted.Config.syntax.sanitize_after)
		if "_sanitize" in kwargs:
			if len(_sanitize) > 0:
				import json
				_sanitize = json.load(self.Unprompted.parse_advanced(kwargs["_sanitize"], context))
				self.Unprompted.Config.syntax.sanitize_after = _sanitize
		elif "_raw" not in pargs:
			setattr(self.Unprompted.Config.syntax.sanitize_after, "\\n", self.Unprompted.Config.syntax.delimiter)

		# Allow inner [file] to return linebreaks
		if "_raw" not in pargs:
			content = self.Unprompted.shortcode_parser.parse(content, context)

		final_string = ""
		parts = content.replace(getattr(self.Unprompted.Config.syntax.sanitize_before, "\n", "\\n"), self.Unprompted.Config.syntax.delimiter).split(self.Unprompted.Config.syntax.delimiter)

		# Remove empty lines
		parts = list(filter(None, parts))

		try:
			if ("_weighted" in pargs):
				weighted_list = []
				checking_weight = True
				this_weight = 1

				for idx, part in enumerate(parts):
					if checking_weight:
						this_weight = helpers.autocast(part)

						if (isinstance(this_weight, str)):
							this_weight = 1
							checking_weight = False
						elif isinstance(this_weight, float):
							probability = (this_weight % 1)
							this_weight = int(this_weight)
							if (probability >= random.uniform(0, 1)): this_weight += 1

					if not checking_weight:
						for x in range(0, this_weight):
							weighted_list.append(part)

					checking_weight = not checking_weight

				parts = weighted_list

			times = 1
			for parg in pargs:
				if self.Unprompted.is_system_arg(parg): continue
				times = self.Unprompted.parse_advanced(parg, context)
				break

			_sep = self.Unprompted.parse_advanced(kwargs["_sep"], context) if "_sep" in kwargs else ", "
			_case = max(min(len(parts) - 1, int(self.Unprompted.parse_advanced(kwargs["_case"], context))), 0) if "_case" in kwargs else -1

			for x in range(0, times):
				part_index = random.choice(range(len(parts))) if _case == -1 else _case
				final_string += self.Unprompted.process_string(self.Unprompted.sanitize_pre(parts[part_index], self.Unprompted.Config.syntax.sanitize_block, True), context, False)

				if (times > 1 and x != times - 1):
					del parts[part_index]  # Prevent the same choice from being made again
					final_string += _sep
		except Exception as e:
			self.log.exception(f"Exception while parsing the list of choices. The partially assembled final string was: {final_string}")
			pass

		# Reset to original value
		self.Unprompted.Config.syntax.sanitize_after = copy.copy(temp_syntax_after)

		return self.Unprompted.parse_alt_tags(final_string, context)

	def ui(self, gr):
		gr.Number(label="Number of times to choose 🡢 int", value=1, interactive=True)
		gr.Textbox(label="String delimiter when returning more than one choice 🡢 _sep", max_lines=1, placeholder=", ")
		gr.Checkbox(label="Custom weight per option 🡢 _weighted")
		gr.Checkbox(label="Do not process inner shortcodes except the selected one 🡢 _raw")
		gr.Number(label="Override random nature of shortcode with predetermined outcome 🡢 _case", value=-1, interactive=True)
