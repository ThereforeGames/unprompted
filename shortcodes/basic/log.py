class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Prints a message to the console."

	def run_block(self, pargs, kwargs, context, content):
		import os
		import inspect
		log_func = getattr(self.log, pargs[0].lower() if len(pargs) > 0 else "debug")
		log_func(content)
		# self.Unprompted.log_old(content, context=pargs[0] if len(pargs) > 0 else "DEBUG", caller=" [" + os.path.relpath(inspect.stack()[1].filename, __file__).replace("..\\", "") + "]")
		return ("")

	def ui(self, gr):
		pass