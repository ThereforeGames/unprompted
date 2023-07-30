class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.after_content = []
		self.description = "Processes arbitrary text following the main output."
		self.last_index = -1
		self.allow_unsafe_scripts = False

	def preprocess_block(self, pargs, kwargs, context):
		return True

	def run_block(self, pargs, kwargs, context, content):
		index = int(self.Unprompted.parse_advanced(pargs[0])) if len(pargs) > 0 else 0
		if self.last_index != index or "allow_dupe_index" in pargs:
			self.log.debug(f"Queueing up content ({index}): {content}")
			self.after_content.insert(index, content)
			self.last_index = index
		else:
			self.log.info("Duplicate [after] content detected, skipping - include allow_dupe_index to bypass this check")

		if "allow_unsafe_scripts" in pargs: self.allow_unsafe_scripts = True
		return ("")

	def after(self, p=None, processed=None):
		self.last_index = -1

		if self.after_content:

			# Disable or unload other extensions that cause trouble with [after] processing
			if not self.allow_unsafe_scripts:
				i = 0
				while i < len(self.Unprompted.p_copy.scripts.alwayson_scripts):
					script = self.Unprompted.p_copy.scripts.alwayson_scripts[i]
					script_title = script.title().lower()
					try:
						if script_title == "regional prompter" and script.active:
							rp_path = self.Unprompted.extension_path("sd-webui-regional-prompter")
							rp_mod = self.Unprompted.import_file(f"sd-webui-regional-prompter.scripts.rp", f"{rp_path}/scripts/rp.py")
							rp_mod.unloader(script, self.Unprompted.p_copy)
							self.log.debug("Successfully unloaded Regional Prompter")
					except Exception as e:
						self.Unprompted.log_error(e, f"An error ocurred while trying to bypass an extension: {script_title}")
					i += 1

			if processed:
				# Share variable with other shortcodes
				self.Unprompted.after_processed = processed
				# Fix init_images for other functions that may expect it (e.g. txt2mask)
				self.Unprompted.shortcode_user_vars["init_images"] = self.Unprompted.after_processed.images

			# Set up system var support - copy relevant p attributes into shortcode var object
			for att in dir(p):
				if not att.startswith("__"):
					self.Unprompted.shortcode_user_vars[att] = getattr(p, att)

			for idx, content in enumerate(self.after_content):
				self.Unprompted.shortcode_user_vars["after_index"] = idx
				self.Unprompted.process_string(content, "after")

			self.after_content = []
			return (self.Unprompted.after_processed)
		return processed

	def ui(self, gr):
		gr.Number(label="Order compared to other [after] blocks 🡢 int", value=0, interactive=True)
