class Shortcode():
	'''Processes arbitrary text following the main output.'''
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.after_content = []

	def run_block(self, pargs, kwargs, context, content):
		index = pargs[0] if len(pargs) > 0 else 0
		self.after_content.insert(index,content)
		return("")
	
	def after(self,p=None,processed=None):
		if self.after_content:
			if processed:
				# Share variable with other shortcodes
				self.Unprompted.after_processed = processed
				# Fix init_images for other functions that may expect it (e.g. txt2mask)
				self.Unprompted.shortcode_user_vars["init_images"] = self.Unprompted.after_processed.images

			# Set up system var support - copy relevant p attributes into shortcode var object
			for att in dir(p):
				if not att.startswith("__"):
					self.Unprompted.shortcode_user_vars[att] = getattr(p,att)

			for content in self.after_content:
				self.Unprompted.process_string(self.Unprompted.parse_alt_tags(content,"after"))

			self.after_content = []
			return(self.Unprompted.after_processed)