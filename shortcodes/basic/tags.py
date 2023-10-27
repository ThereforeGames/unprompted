class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Applies one or more metatags to be evaluated with [filter_tags] for bypassing the content."

	def preprocess_block(self, pargs, kwargs, context):
		return True

	def run_block(self, pargs, kwargs, context,content):
		# self.shortcode_overrides.update(kwargs)
		filter_obj = self.Unprompted.shortcode_objects["filter_tags"]
		failed_test = False
		matched_one = False

		for orig_parg_tag in filter_obj.parg_tags:
			parg_tag = orig_parg_tag
			if self.Unprompted.is_system_arg(parg_tag): continue
			# Check if the tag begins with a hyphen for "negative" matching
			elif parg_tag.startswith(self.Unprompted.Config.syntax.not_operator):
				is_not = True
				parg_tag = parg_tag[1:]
			else: is_not = False

			if parg_tag not in pargs:
				if is_not:
					if filter_obj.once: filter_obj.parg_tags.remove(orig_parg_tag)
					matched_one = True				
					continue
				if filter_obj.must_match == "any": continue
				else:
					failed_test = True
					break
			else:
				if is_not:
					if filter_obj.must_match != "any":
						failed_test = True
						break
				else:
					if filter_obj.once: filter_obj.parg_tags.remove(parg_tag)
					matched_one = True

		for orig_kwarg_tag in filter_obj.kwarg_tags:
			kwarg_tag = orig_kwarg_tag

			if self.Unprompted.is_system_arg(kwarg_tag): continue
			elif kwarg_tag.startswith(self.Unprompted.Config.syntax.not_operator):
				key_is_not = True
				kwarg_tag = kwarg_tag[1:]
			else: key_is_not = False

			# Support "not" operator for kwarg value:
			if isinstance(filter_obj.kwarg_tags[orig_kwarg_tag], str) and filter_obj.kwarg_tags[orig_kwarg_tag].startswith(self.Unprompted.Config.syntax.not_operator):
				val_is_not = True
				kwarg_val = filter_obj.kwarg_tags[orig_kwarg_tag][1:]
			else:
				val_is_not = False
				kwarg_val = filter_obj.kwarg_tags[orig_kwarg_tag]

			if kwarg_tag not in kwargs:
				if key_is_not:
					if filter_obj.once: filter_obj.kwarg_tags.pop(orig_kwarg_tag)
					matched_one = True
					continue
				if filter_obj.must_match != "all": continue
				else:
					failed_test = True
					break
			
			if kwargs[kwarg_tag] != kwarg_val:
				if val_is_not:
					if filter_obj.once: filter_obj.kwarg_tags.pop(orig_kwarg_tag)
					matched_one = True
					continue
				elif filter_obj.must_match == "any": continue
				else:
					failed_test = True
					break
			else:
				if val_is_not:
					if filter_obj.must_match != "any":
						failed_test = True
						break
				else:
					if filter_obj.once: filter_obj.kwarg_tags.pop(kwarg_tag)
					matched_one = True
		
		# Return content in the event of success or no filters
		if (matched_one and not failed_test) or (not filter_obj.parg_tags and not filter_obj.kwarg_tags):
			if filter_obj.debug: self.log.info(f"Matched tags block: {pargs} {kwargs}")
			
			# Reset filter tags
			if filter_obj.clear:
				filter_obj.cleanup()

			return self.Unprompted.parse_alt_tags(content, context)

		if filter_obj.debug: self.log.info(f"Failed tags block: {pargs} {kwargs}")
		return ""

	def ui(self,gr):
		gr.Textbox(label="Arbitrary tags 🡢 verbatim",max_lines=1,placeholder="nature")