class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Prints one or more messages to the console."

	def run_atomic(self, pargs, kwargs, context):
		_level = self.Unprompted.parse_arg("_level",self.Unprompted.Config.logging.level.lower())
		log_func = getattr(self.log,_level.lower())
		for parg in pargs:
			log_func(self.Unprompted.parse_advanced(parg,context))

		return ("")

	def ui(self, gr):
		gr.Textbox(label="Arbitrary messages as pargs 🡢 verbatim",max_lines=1,placeholder='"message one" "message two goes here"')
		gr.Dropdown(label="Log level 🡢 _level",choices=["debug","info","warning","error","critical"],value="info")