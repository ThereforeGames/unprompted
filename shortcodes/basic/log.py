class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Prints a message to the console."

	def run_block(self, pargs, kwargs, context, content):
		log_func = getattr(self.log, pargs[0].lower() if len(pargs) > 0 else self.Unprompted.Config.logging.level.lower())
		log_func(content)
		return ("")

	def ui(self, gr):
		pass