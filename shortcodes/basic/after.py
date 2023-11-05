import lib_unprompted.helpers as helpers


class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.after_content = []
		self.description = "Processes arbitrary text following the main output."
		self.allow_unsafe_scripts = False

	def preprocess_block(self, pargs, kwargs, context):
		return True

	def run_block(self, pargs, kwargs, context, content):
		# if "batch_indexing" in kwargs: self.batch_indexing = bool(self.Unprompted.parse_advanced(kwargs["batch_indexing"]))

		batch_real_index = self.Unprompted.shortcode_user_vars["batch_real_index"] if "batch_real_index" in self.Unprompted.shortcode_user_vars else 0
		dupe_index_mode = self.Unprompted.parse_arg("dupe_index_mode","concat")

		# Create list inside of list to house [after] content for this batch number
		while batch_real_index >= len(self.after_content):
			self.after_content.append([])

		index = int(self.Unprompted.parse_advanced(pargs[0])) if len(pargs) > 0 else 0

		is_new_index = index >= len(self.after_content[batch_real_index])
		if is_new_index or dupe_index_mode != "skip":
			self.log.debug(f"Queueing up content (Batch #{batch_real_index}, After {index}): {content}")
			
			if is_new_index or dupe_index_mode == "replace":
				self.log.debug(f"Replacing content in After routine (index {index})")
				helpers.list_set(self.after_content[batch_real_index],index,content,"")
			elif not is_new_index:
				if dupe_index_mode == "concat":
					self.log.debug(f"Concatenating content to After routine (index {index})")
					self.after_content[batch_real_index][index] += str(content)
				elif dupe_index_mode == "append":
					self.log.debug(f"Appending to After routine content")
					self.after_content[batch_real_index].append(str(content))
		else:
			self.log.info(f"Duplicate [after] content detected (index {index}), skipping per dupe_index_mode")

		if "allow_unsafe_scripts" in pargs: self.allow_unsafe_scripts = True
		return ("")

	def after(self, p=None, processed=None):
		# Disable or unload other extensions that cause trouble with [after] processing
		if self.after_content:
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
							rp_mod = helpers.import_file(f"sd-webui-regional-prompter.scripts.rp", f"{rp_path}/scripts/rp.py")
							rp_mod.unloader(script, self.Unprompted.main_p)
							self.log.debug(f"{success_string} Regional Prompter")
						elif script_title == "controlnet":
							# Update the controlnet script args with a list of 0 units
							cn_path = self.Unprompted.extension_path(self.Unprompted.Config.stable_diffusion.controlnet.extension)
							if cn_path:
								cn_module = helpers.import_file(f"{self.Unprompted.Config.stable_diffusion.controlnet.extension}.internal_controlnet.external_code", f"{cn_path}/internal_controlnet/external_code.py")
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

			# Main processing loop
			for batch_idx, this_after_content in enumerate(self.after_content):
				if self.Unprompted.batch_test_bypass(batch_idx): continue

				self.Unprompted.shortcode_user_vars["batch_real_index"] = batch_idx

				for idx, content in enumerate(this_after_content):
					self.log.info(f"Processing After content for batch {batch_idx}, block {idx}...")
					self.log.debug(f"After content: {content}")
					self.Unprompted.shortcode_user_vars["after_index"] = idx
					
					self.Unprompted.process_string(content, "after")

			self.after_content = []
			
			return (self.Unprompted.after_processed)
		return processed

	def ui(self, gr):
		gr.Number(label="Order compared to other [after] blocks 🡢 int", value=0, interactive=True)
