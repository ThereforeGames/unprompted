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
			if not self.allow_unsafe_scripts and self.Unprompted.main_p.scripts:
				self.log.debug("Unloading incompatible scripts...")
				i = 0
				success_string = "Sucessfully unloaded"
				while i < len(self.Unprompted.main_p.scripts.alwayson_scripts):
					script = self.Unprompted.main_p.scripts.alwayson_scripts[i]
					script_title = script.title().lower()
					try:
						if script_title == "regional prompter" and script.active:
							rp_path = self.Unprompted.extension_path("sd-webui-regional-prompter")
							rp_mod = self.Unprompted.import_file(f"sd-webui-regional-prompter.scripts.rp", f"{rp_path}/scripts/rp.py")
							rp_mod.unloader(script, self.Unprompted.main_p)
							self.log.debug(f"{success_string} Regional Prompter")
						elif script_title == "controlnet":
							# Update the controlnet script args with a list of 0 units
							cn_path = self.Unprompted.extension_path(self.Unprompted.Config.stable_diffusion.controlnet_name)
							if cn_path:
								cn_module = self.Unprompted.import_file(f"{self.Unprompted.Config.stable_diffusion.controlnet_name}.internal_controlnet.external_code", f"{cn_path}/internal_controlnet/external_code.py")
								cn_module.update_cn_script_in_processing(self.Unprompted.main_p, [])
								self.log.debug(f"{success_string} ControlNet")
							else:
								self.log.error("Could not communicate with ControlNet.")

							pass
					except Exception as e:
						self.log.exception(f"Exception while trying to bypass an extension: {script_title}")
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

			# self.Unprompted.shortcode_objects["bypass"].run_atomic({"after"}, {}, "")

			for idx, content in enumerate(self.after_content):
				self.Unprompted.shortcode_user_vars["after_index"] = idx
				self.Unprompted.process_string(content, "after")

			self.after_content = []
			return (self.Unprompted.after_processed)
		return processed

	def ui(self, gr):
		gr.Number(label="Order compared to other [after] blocks 🡢 int", value=0, interactive=True)
