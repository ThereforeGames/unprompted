class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Stores a value into a given variable."

	def preprocess_block(self, pargs, kwargs, context):
		return True

	def run_block(self, pargs, kwargs, context, content):
		import lib_unprompted.helpers as helpers
		overrides = self.Unprompted.shortcode_objects["overrides"]
		can_set = True

		if (content is None or len(content) < 1): return ""

		self.Unprompted.is_var_deprecated(pargs[0])

		# Prep content with override support
		if (pargs[0] in overrides.shortcode_overrides):
			content = overrides.shortcode_overrides[pargs[0]]
		elif "_defer" not in pargs:
			if "_raw" in pargs:
				content = self.Unprompted.process_string(content, context)
			else:
				content = self.Unprompted.process_string(self.Unprompted.sanitize_pre(content, self.Unprompted.Config.syntax.sanitize_block, True), context, False)
			content = helpers.autocast(content)

		if "_new" in pargs:
			if pargs[0] in self.Unprompted.shortcode_user_vars:
				# Check if this var already holds a valid value, if not we will set it
				if "_choices" in kwargs:
					if self.Unprompted.shortcode_user_vars[pargs[0]] in self.Unprompted.parse_advanced(kwargs["_choices"], context).split(self.Unprompted.Config.syntax.delimiter): can_set = False
				else: can_set = False
		elif "_choices" in kwargs:
			if str(content) not in self.Unprompted.parse_advanced(kwargs["_choices"], context).split(self.Unprompted.Config.syntax.delimiter): can_set = False

		if can_set:
			if ("_append" in pargs): self.Unprompted.shortcode_user_vars[pargs[0]] += content
			elif ("_prepend" in pargs): self.Unprompted.shortcode_user_vars[pargs[0]] = content + self.Unprompted.shortcode_user_vars[pargs[0]]
			else: self.Unprompted.shortcode_user_vars[pargs[0]] = content

			self.log.debug(f"Setting {pargs[0]} to {self.Unprompted.shortcode_user_vars[pargs[0]]}")

		if "_remember" in pargs:
			if pargs[0] not in self.Unprompted.shortcode_objects["remember"].globals:
				self.Unprompted.shortcode_objects["remember"].globals.append(pargs[0])

		if "_external" in kwargs:
			import json
			filepath = self.Unprompted.parse_filepath(helpers.str_with_ext(kwargs["_external"]),root=self.Unprompted.base_dir,must_exist=False)

			# We load the file twice so that we can prepare the full data to send with json.dump
			json_obj = helpers.create_load_json(filepath, encoding=self.Unprompted.Config.formats.default_encoding)
			json_obj[pargs[0]] = self.Unprompted.shortcode_user_vars[pargs[0]]

			with open(filepath, "w", encoding=self.Unprompted.Config.formats.default_encoding) as f:
				json.dump(json_obj, f, ensure_ascii=False)

		if ("_out" in pargs): return (self.Unprompted.shortcode_user_vars[pargs[0]])
		else: return ("")

	def ui(self, gr):
		gr.Textbox(label="Variable name 🡢 verbatim", max_lines=1)
		gr.Checkbox(label="Only set this variable if it doesn't already exist 🡢 _new")
		gr.Textbox(label="Array of valid values (used in conjunction with _new) 🡢 _choices")
		gr.Checkbox(label="Append the content to the variable's current value 🡢 _append")
		gr.Checkbox(label="Prepend the content to the variable's current value 🡢 _prepend")
		gr.Checkbox(label="Store content without sanitizing 🡢 _raw")
		gr.Checkbox(label="Print the variable's value 🡢 _out")