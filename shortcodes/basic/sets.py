class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "The atomic version of [set] that lets you set multiple variables at once."
	def run_atomic(self, pargs, kwargs, context):
		system_kwargs = {}

		# Populate a dict of system args to pass off to [set]
		for key,value in kwargs.items():
			if (self.Unprompted.is_system_arg(key)): system_kwargs[key] = value	

		if "_load" in kwargs:
			jsons = self.Unprompted.load_jsons(self.Unprompted.parse_advanced(kwargs["_load"],context),context)
			kwargs.update(jsons)
		
		# Traverse our kwargs again, firing the [set] call with all the right data
		for key,value in kwargs.items():
			if not self.Unprompted.is_system_arg(key):
				# We create a copy of the pargs list because we need to add 'key' to the start for [set] processing
				set_pargs = pargs
				set_pargs.insert(0,key)
				self.Unprompted.shortcode_objects["set"].run_block(set_pargs,system_kwargs,context,str(self.Unprompted.parse_advanced(value,context)))
		
		return("")

	def ui(self,gr):
		gr.Textbox(label="Arbitrary arguments in variable=value format 🡢 verbatim",max_lines=1,placeholder='my_var="something" another_var=56')