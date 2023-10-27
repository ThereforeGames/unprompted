class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.shortcode_overrides = {}
		self.description = "Tags for filtering content inside of [tags] blocks."
		self.parg_tags = []
		self.kwarg_tags = {}
		self.once = False
		self.debug = False
		self.clear = False
		self.must_match = "any"

	def run_atomic(self, pargs, kwargs, context):
		_extend = self.Unprompted.parse_arg("_extend",False)
		self.debug = self.Unprompted.parse_arg("_debug",False)
		self.once = self.Unprompted.parse_arg("_once",False)
		self.clear = self.Unprompted.parse_arg("_clear",False)
		self.must_match = self.Unprompted.parse_arg("_must_match","any")

		if _extend:
			self.parg_tags.extend(pargs)
			self.kwarg_tags.update(kwargs)
		else:
			self.parg_tags = pargs
			self.kwarg_tags = kwargs
		
		if self.debug:
			self.log.info(f"Parg tags: {self.parg_tags}")
			self.log.info(f"Kwarg tags: {self.kwarg_tags}")

		return("")

	def cleanup(self):
		self.parg_tags = []
		self.kwarg_tags = {}
		self.once = False
		self.clear = False
		self.must_match = "any"
		self.debug = False

	def ui(self,gr):
		gr.Textbox(label="Arbitrary tag filters 🡢 verbatim",max_lines=1,placeholder='location=outdoors nature')
		gr.Checkbox(label="Clear all filters after first matching tag block 🡢 _clear",value=False)
		gr.Checkbox(label="Match each tag only once 🡢 _once",value=False)
		gr.Radio(label="Rules for what is considered a matching block 🡢 _must_match",choices=["any","all","selective"])
		gr.Checkbox(label="Debug 🡢 _debug",value=False)
