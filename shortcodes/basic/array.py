class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Manages a group or list of values."

	def run_atomic(self, pargs, kwargs, context):
		import random
		import lib_unprompted.helpers as helpers
		result_list = []
		delimiter = kwargs["_delimiter"] if "_delimiter" in kwargs else self.Unprompted.Config.syntax.delimiter

		for idx, parg in enumerate(pargs):
			if (self.Unprompted.is_system_arg(parg)): continue
			# Get array name
			if (idx == 0):
				# Define the array if it doesn't exist
				if not parg in self.Unprompted.shortcode_user_vars: self.Unprompted.shortcode_user_vars[parg] = []
				continue
			# Print remaining pargs
			# self.log.debug(f"What is pargs[0]? {pargs[0]}")
			# self.log.debug(f"What is the second array index? {int(self.Unprompted.parse_advanced(parg, context))}")
			result_list.append(str(self.Unprompted.shortcode_user_vars[pargs[0]][int(self.Unprompted.parse_advanced(parg, context))]))

		# Set new array values
		for kwarg, val in kwargs.items():
			if (self.Unprompted.is_system_arg(kwarg)): continue
			if (helpers.is_int(kwarg)):
				this_kwarg = int(kwarg)
			else:
				try:
					this_kwarg = int(self.Unprompted.shortcode_user_vars[kwarg])
				except Exception as e:
					self.log.exception(f"Exception while trying to parse the following kwarg as an array index: {kwarg}")
					continue
			# Initialize null values if we're outside the array's length
			while (len(self.Unprompted.shortcode_user_vars[parg]) <= this_kwarg):
				self.Unprompted.shortcode_user_vars[parg].append("")
			self.Unprompted.shortcode_user_vars[parg][this_kwarg] = self.Unprompted.parse_advanced(val, context)

		if "_append" in kwargs:
			split_append = self.Unprompted.parse_advanced(kwargs["_append"], context).split(delimiter)
			for idx, item in enumerate(split_append):
				split_append[idx] = self.Unprompted.parse_advanced(item, context)
			self.Unprompted.shortcode_user_vars[pargs[0]].extend(split_append)
		if "_prepend" in kwargs:
			split_prepend = kwargs["_prepend"].split(delimiter)
			for idx, item in enumerate(split_prepend):
				split_prepend[idx] = self.Unprompted.parse_advanced(item, context)
			self.Unprompted.shortcode_user_vars[pargs[0]] = split_prepend.extend(self.Unprompted.shortcode_user_vars[parg])
		if "_del" in kwargs:
			for item in kwargs["_del"].split(delimiter):
				del self.Unprompted.shortcode_user_vars[pargs[0]][int(self.Unprompted.parse_advanced(item, context))]
		if "_remove" in kwargs:
			for item in kwargs["_remove"].split(delimiter):
				self.Unprompted.shortcode_user_vars[pargs[0]].remove(self.Unprompted.parse_advanced(item, context))
		if "_find" in kwargs:
			for item in kwargs["_find"].split(delimiter):
				result_list.append(self.Unprompted.shortcode_user_vars[pargs[0]].index(self.Unprompted.parse_advanced(item, context)))
		if "_shuffle" in pargs:
			random.shuffle(self.Unprompted.shortcode_user_vars[pargs[0]])
		if "_fill" in kwargs:
			fill_val = self.Unprompted.parse_advanced(kwargs["_fill"], context)
			for i in range(len(self.Unprompted.shortcode_user_vars[pargs[0]])):
				self.Unprompted.shortcode_user_vars[pargs[0]][i] = fill_val

		return (delimiter.join(str(x) for x in result_list))

	def ui(self, gr):
		gr.Textbox(label="Name of array variable 🡢 str", max_lines=1, placeholder="my_array")
		gr.Textbox(label="Get or set index statements 🡢 verbatim", max_lines=1)
		gr.Textbox(label="Custom delimiter string 🡢 _delimiter", max_lines=1, placeholder=self.Unprompted.Config.syntax.delimiter)
		gr.Checkbox(label="Shuffle the array 🡢 _shuffle")
		gr.Textbox(label="Prepend value(s) to the array 🡢 _prepend", max_lines=1)
		gr.Textbox(label="Append value(s) to the array 🡢 _append", max_lines=1)
		gr.Textbox(label="Delete value(s) from the array by index 🡢 _del", max_lines=1)
		gr.Textbox(label="Removed specified value(s) from the array 🡢 _remove", max_lines=1)
		gr.Textbox(label="Find the first index of the following value(s) 🡢 _find", max_lines=1)
