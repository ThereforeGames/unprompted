class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "changes the filename of the image."
	def run_atomic(self, pargs, kwargs, context):
		from modules.shared import opts, cmd_opts

		opts.samples_filename_pattern = self.Unprompted.parse_advanced(pargs[0],context)
		# #remove the original images from the output

		return("")

	def ui(self,gr):
		pass