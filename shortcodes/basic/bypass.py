class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.bypassed = {}
		self.description = "Turn off specific shortcodes for the duration of a run."

	# We need to run this in the preprocess step so that handler changes will propagate to other shortcodes in the same routine
	def run_preprocess(self,pargs,kwargs,context):
		for parg in pargs:
			if self.Unprompted.is_system_arg(parg): continue
			if parg in self.Unprompted.shortcode_parser.keywords:
				if parg not in self.bypassed:
					self.bypassed[parg] = self.Unprompted.shortcode_parser.keywords[parg]
					# We temporarily replace the run function of this shortcode with an empty lambda
					self.Unprompted.shortcode_parser.keywords[parg] = (lambda *x:"",self.Unprompted.shortcode_parser.keywords[parg][1],None)
				elif "_toggle" in pargs:
					# Un-bypass
					self.Unprompted.shortcode_parser.keywords[parg] = self.bypassed[parg]
					del self.bypassed[parg]
		return True

	def run_atomic(self, pargs, kwargs, context):
		return("")

	def cleanup(self):
		for shortcode in self.bypassed:
			self.Unprompted.shortcode_parser.keywords[shortcode] = self.bypassed[shortcode]
		self.bypassed.clear()

	def ui(self,gr):
		gr.Textbox(label="Shortcode names separated by space 🡢 verbatim",max_lines=1,placeholder='txt2mask after repeat')
		gr.Checkbox(label="Enable Toggle mode to re-activate shortcodes that were previously bypassed 🡢 _toggle")