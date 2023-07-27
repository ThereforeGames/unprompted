import glob
import random
import os


class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns a list of files at a given location using glob."

	def run_atomic(self, pargs, kwargs, context):
		file_string = self.Unprompted.parse_alt_tags(pargs[0], context)
		_delimiter = self.Unprompted.parse_advanced(kwargs["_delimiter"], context) if "_delimiter" in kwargs else self.Unprompted.Config.syntax.delimiter
		_basename = self.Unprompted.shortcode_var_is_true("_basename", pargs, kwargs)
		_hide_ext = self.Unprompted.shortcode_var_is_true("_hide_ext", pargs, kwargs)

		# Relative path
		if (file_string[0] == "."):
			path = os.path.dirname(context) + "/" + file_string
		else:
			file_string = file_string.replace("%BASE_DIR%", self.Unprompted.base_dir)

		files = glob.glob(file_string)
		if (len(files) == 0):
			self.log.error(f"No files found at this location: {file_string}")
			return ("")

		if _hide_ext:
			for idx, file in enumerate(files):
				files[idx] = os.path.splitext(file)[0]

		if _basename:
			for idx, file in enumerate(files):
				files[idx] = os.path.basename(file)

		files = _delimiter.join(files)

		return (files)

	def ui(self, gr):
		gr.Textbox(label="Filepath 🡢 str", max_lines=1)
		gr.Textbox(label="Result delimiter 🡢 _delimiter", max_lines=1, value=self.Unprompted.Config.syntax.delimiter)
