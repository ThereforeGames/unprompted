# Unprompted by Therefore Games. All Rights Reserved.
# https://patreon.com/thereforegames
# https://github.com/ThereforeGames/unprompted

# This script is intended to be used as an extension for Automatic1111's Stable Diffusion WebUI.

import gradio as gr

import modules.scripts as scripts
from modules.processing import process_images, fix_seed, Processed
from modules.shared import opts, cmd_opts, state, Options
from modules import sd_models
import lib_unprompted.shortcodes as shortcodes
from pathlib import Path
from enum import IntEnum, auto

# from ui import settings

import sys
import os

# settings.initialize()

base_dir = scripts.basedir()
sys.path.append(base_dir)
# Main object
from lib_unprompted.shared import Unprompted

Unprompted = Unprompted(base_dir)

WizardModes = IntEnum("WizardModes", ["TEMPLATES", "SHORTCODES"], start=0)

Unprompted.wizard_groups = [[{}, {}] for _ in range(len(WizardModes))]  # Two subdictionaries for txt2img and img2img
Unprompted.wizard_dropdown = None
Unprompted.main_p = None
Unprompted.original_prompt = None
Unprompted.original_negative_prompt = ""

Unprompted.wizard_template_files = []
Unprompted.wizard_template_names = []
Unprompted.wizard_template_kwargs = []


def do_dry_run(string):
	Unprompted.log(string)
	# Reset vars
	Unprompted.shortcode_user_vars = {}
	unp_result = Unprompted.process_string(string)
	# Cleanup routines
	Unprompted.log("Entering cleanup routine...", False)
	for i in Unprompted.cleanup_routines:
		Unprompted.shortcode_objects[i].cleanup()
	return f"<strong>RESULT:</strong> {unp_result}"


def wizard_select_item(option, is_img2img, mode=WizardModes.SHORTCODES):
	Unprompted.wizard_dropdown.value = option

	this_list = Unprompted.wizard_groups[mode][int(is_img2img)]

	# Retrieve corresponding template filepath
	if (mode == WizardModes.TEMPLATES): option = Unprompted.wizard_template_files[option]

	results = [gr.update(visible=(option == key)) for key in this_list.keys()]
	return results


def block_is_container(block_name):
	if (block_name == "form" or block_name == "accordion"): return True
	else: return False


def wizard_set_event_listener(obj):
	obj.change(fn=lambda val: wizard_update_value(obj, val), inputs=obj)
	if ("blur" in dir(obj)): obj.blur(fn=lambda val: wizard_update_value(obj, val), inputs=obj)


def wizard_update_value(obj, val):
	obj.value = val  # TODO: Rewrite this with Gradio update template if possible


def wizard_prep_event_listeners(obj):
	for child in obj.children:
		block_name = child.get_block_name()

		if (block_is_container(block_name)):
			wizard_prep_event_listeners(child)
		elif (block_name != "label" and "change" in dir(child)):
			# use template to pass obj by reference
			wizard_set_event_listener(child)


def wizard_generate_template(option, is_img2img, prepend="", append=""):
	filepath = os.path.relpath(Unprompted.wizard_template_files[option], f"{base_dir}/{Unprompted.Config.template_directory}")
	# Remove file extension
	filepath = os.path.splitext(filepath)[0]
	result = f"{Unprompted.Config.syntax.tag_start}file \"{filepath}\""
	filtered_templates = Unprompted.wizard_groups[WizardModes.TEMPLATES][int(is_img2img)]
	group = filtered_templates[Unprompted.wizard_template_files[option]]

	def parse_children(obj, result):
		try:
			for gr_obj in obj.children:
				block_name = gr_obj.get_block_name()

				if block_is_container(block_name):
					result = parse_children(gr_obj, result)
				else:
					if block_name == "label" or block_name == "markdown" or gr_obj.value is None or gr_obj.value == "": continue  # Skip empty fields
					arg_name = gr_obj.label.split(" ")[-1]  # Get everything after the last space
					# Skip special fields
					if (arg_name == "prompt"): continue

					this_val = str(Unprompted.autocast(gr_obj.value))

					if " " in this_val: this_val = f"\"{this_val}\""  # Enclose in quotes if necessary
					result += f" {arg_name}={this_val}"
		except:
			pass
		return (result)

	result = parse_children(group, result)

	for kwarg in Unprompted.wizard_template_kwargs[option]:
		result += f" {kwarg}='{Unprompted.wizard_template_kwargs[option][kwarg]}'"

	# Closing bracket
	result += Unprompted.Config.syntax.tag_end

	return (prepend + result + append)


def wizard_generate_shortcode(option, is_img2img, prepend="", append=""):
	if hasattr(Unprompted.shortcode_objects[option], "wizard_prepend"): result = Unprompted.shortcode_objects[option].wizard_prepend
	else: result = Unprompted.Config.syntax.tag_start + option
	filtered_shortcodes = Unprompted.wizard_groups[WizardModes.SHORTCODES][int(is_img2img)]
	group = filtered_shortcodes[option]
	block_content = ""

	def parse_children(obj, result):
		block_content = ""
		try:
			for gr_obj in obj.children:
				block_name = gr_obj.get_block_name()

				if block_is_container(block_name):
					results = parse_children(gr_obj, result)
					block_content = results[0]
					result = results[1]
				elif gr_obj.label == "Content":
					block_content = gr_obj.value
				else:
					if block_name == "label" or block_name == "markdown" or gr_obj.value is None or gr_obj.value == "": continue  # Skip empty fields

					arg_name = gr_obj.label.split(" ")[-1]  # Get everything after the last space

					# Rules
					if (arg_name == "prompt"): continue
					elif (arg_name == "str"):
						result += " \"" + str(gr_obj.value) + "\""
					elif (arg_name == "int"):
						result += " " + str(int(gr_obj.value))
					elif (arg_name == "verbatim"):
						result += " " + str(gr_obj.value)
					elif (block_name == "checkbox"):
						if gr_obj.value: result += " " + arg_name
					elif (block_name == "number" or block_name == "slider"): result += f" {arg_name}={Unprompted.autocast(gr_obj.value)}"
					elif (block_name == "textbox"):
						if len(gr_obj.value) > 0: result += f" {arg_name}=\"{gr_obj.value}\""
					else: result += f" {arg_name}=\"{gr_obj.value}\""

		except:
			pass
		return ([block_content, result])

	results = parse_children(group, result)
	block_content = results[0]
	result = results[1]

	# Closing bracket
	if hasattr(Unprompted.shortcode_objects[option], "wizard_append"): result += Unprompted.shortcode_objects[option].wizard_append
	else: result += Unprompted.Config.syntax.tag_end

	if hasattr(Unprompted.shortcode_objects[option], "run_block"):
		if (append and not block_content):
			block_content = append
			append = ""
			prepend = ""
		result += block_content + Unprompted.Config.syntax.tag_start + Unprompted.Config.syntax.tag_close + option + Unprompted.Config.syntax.tag_end

	return (prepend + result + append)


def wizard_generate_capture(include_inference, include_prompt, include_neg_prompt, include_model, include_template_block):
	try:
		if Unprompted.main_p:
			result = f"<strong>RESULT:</strong> "
			prompt = ""
			neg_prompt = ""

			if include_template_block:
				result += f"{Unprompted.Config.syntax.tag_start}template name='Untitled'{Unprompted.Config.syntax.tag_end}Your template description goes here.{Unprompted.Config.syntax.tag_start}{Unprompted.Config.syntax.tag_close}template{Unprompted.Config.syntax.tag_end}"

			if include_inference != "none" or include_model:
				result += f"{Unprompted.Config.syntax.tag_start}sets"
				if include_model: result += f" sd_model='{opts.data['sd_model_checkpoint']}'"

			for att in dir(Unprompted.main_p):
				if not att.startswith("__"):
					att_val = getattr(Unprompted.main_p, att)
					if (att.startswith("unprompted_")): continue  # Skip special extension attributes
					elif att == "prompt":
						if include_prompt == "postprocessed": prompt = att_val
						else: prompt = Unprompted.original_prompt
					elif att == "negative_prompt":
						if include_neg_prompt == "postprocessed": neg_prompt = att_val
						else: neg_prompt = Unprompted.original_negative_prompt
					elif include_inference != "none":
						if (isinstance(att_val, int) or isinstance(att_val, float) or isinstance(att_val, str)):
							prefix = f" {att}="

							if isinstance(att_val, str):
								if (len(att_val) > 0 or include_inference == "verbose"):
									result += f"{prefix}'{att_val}'"
							else:
								if isinstance(att_val, bool): att_val = int(att_val == True)  # convert bool to 0 or 1
								if att_val == 0 and include_inference != "verbose": continue
								elif (att_val == float("inf") or att_val == float("-inf")) and include_inference != "verbose": continue
								result += f"{prefix}{att_val}"

			if include_inference != "none" or include_model: result += f"{Unprompted.Config.syntax.tag_end}"
			if include_prompt != "none": result += prompt
			if include_neg_prompt != "none" and len(neg_prompt) > 0: result += f"{Unprompted.Config.syntax.tag_start}set negative_prompt{Unprompted.Config.syntax.tag_end}{neg_prompt}{Unprompted.Config.syntax.tag_start}{Unprompted.Config.syntax.tag_close}set{Unprompted.Config.syntax.tag_end}"

		else: result = "<strong>ERROR:</strong> Could not detect your inference settings. Try generating an image first."
	except Exception as e:
		Unprompted.log_error(e)
		result = f"<strong>ERROR:</strong> {e}"

	return result


def get_local_file_dir(filename=None):
	unp_dir = os.path.basename(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
	if filename: filepath = "/" + str(Path(os.path.relpath(filename, f"{base_dir}")).parent)
	else: filepath = ""
	return (f"file/extensions/{unp_dir}{filepath}")


def get_markdown(file):
	file = Path(base_dir) / file
	lines = file.open(mode='r', encoding='utf-8').readlines()
	final_string = ""
	for line in lines:
		# Skip h1 elements
		if not line.startswith("# "): final_string += line
	final_string = final_string.replace("[base_dir]", get_local_file_dir())
	return final_string


# Workaround for Gradio checkbox label+value bug https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/6109
def gradio_enabled_checkbox_workaround():
	return (Unprompted.Config.ui.enabled)


def apply_prompt_template(string, template):
	return template.replace("*", string)


class Scripts(scripts.Script):
	allow_postprocess = True

	# infotext_fields = []
	# paste_field_names = []

	def title(self):
		return "Unprompted"

	def show(self, is_img2img):
		return scripts.AlwaysVisible

	def ui(self, is_img2img):
		with gr.Group():
			with gr.Accordion("Unprompted", open=Unprompted.Config.ui.open):
				is_enabled = gr.Checkbox(label="Enabled", value=gradio_enabled_checkbox_workaround)
				# self.infotext_fields.append((is_enabled,"Unprompted Enabled"))
				# self.paste_field_names.append("Unprompted Enabled")

				match_main_seed = gr.Checkbox(label="Synchronize with main seed", value=True)
				setattr(match_main_seed, "do_not_save_to_config", True)

				unprompted_seed = gr.Number(label="Unprompted Seed", value=-1)
				setattr(unprompted_seed, "do_not_save_to_config", True)

				if (os.path.exists(f"{base_dir}/{Unprompted.Config.template_directory}/pro/demoncrawl_avatar_generator_v0.0.2/main{Unprompted.Config.txt_format}")): is_open = False
				else: is_open = True

				with gr.Accordion("🎉 Promo", open=is_open):
					plug = gr.HTML(label="plug", elem_id="promo", value=f'<a href="https://payhip.com/b/qLUX9" target="_blank"><img src="{get_local_file_dir()}/images/promo_box_demoncrawl_avatar_generator.png" style="float: left;width: 150px;margin-bottom:10px;"></a><h1 style="font-size: 20px;letter-spacing:0.015em;margin-top:10px;">NEW! The <strong>DemonCrawl Avatar Generator</strong> is out now.</h1><p style="margin:1em 0;">Create pixel art portraits in the style of the popular roguelite, DemonCrawl. Includes a custom Stable Diffusion model trained by the game\'s developer, as well as a custom GUI and the ability to randomize your prompts.</p><a href="https://payhip.com/b/qLUX9" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View premium assets for Unprompted">Learn More ➜</button></a>')

				with gr.Accordion("🧙 Wizard", open=Unprompted.Config.ui.wizard_open):
					if Unprompted.Config.ui.wizard_enabled:

						self.wizard_template_template = ""
						self.wizard_template_elements = []

						# Wizard UI shortcode parser for templates
						wizard_shortcode_parser = shortcodes.Parser(start=Unprompted.Config.syntax.tag_start, end=Unprompted.Config.syntax.tag_end, esc=Unprompted.Config.syntax.tag_escape, ignore_unknown=True, inherit_globals=False)

						def handler(keyword, pargs, kwargs, context, content):
							if "_new" in pargs:
								friendly_name = kwargs["_label"] if "_label" in kwargs else "Setting"
								block_name = kwargs["_ui"] if "_ui" in kwargs else "textbox"
								_info = kwargs["_info"] if "_info" in kwargs else ""

								this_label = f"{friendly_name} {Unprompted.Config.syntax.wizard_delimiter} {pargs[0]}"

								# Produce UI based on type
								if (block_name == "textbox"):
									if "_placeholder" in kwargs: this_placeholder = kwargs["_placeholder"]
									else: this_placeholder = str(content)
									obj = gr.Textbox(label=this_label, max_lines=1, placeholder=this_placeholder, info=_info)
								elif (block_name == "checkbox"):
									obj = gr.Checkbox(label=this_label, value=bool(int(content)), info=_info)
								elif (block_name == "number"):
									obj = gr.Number(label=this_label, value=int(content), interactive=True, info=_info, minimum=kwargs["_minimum"] if "_minimum" in kwargs else None, maximum=kwargs["_maximum"] if "_maximum" in kwargs else None)

								elif (block_name == "dropdown"):
									_choices = Unprompted.parse_advanced(kwargs["_choices"], "wizard").split(Unprompted.Config.syntax.delimiter)
									obj = gr.Dropdown(label=this_label, value=content, choices=_choices, info=_info)
								elif (block_name == "radio"):
									obj = gr.Radio(label=this_label, choices=kwargs["_choices"].split(Unprompted.Config.syntax.delimiter), interactive=True, value=content)
								elif (block_name == "slider"):
									obj = gr.Slider(label=this_label, value=int(content), minimum=kwargs["_minimum"] if "_minimum" in kwargs else 1, maximum=kwargs["_maximum"] if "_maximum" in kwargs else 10, step=kwargs["_step"] if "_step" in kwargs else 1, info=_info)

								setattr(obj, "do_not_save_to_config", True)
							return ("")

						wizard_shortcode_parser.register(handler, "set", f"{Unprompted.Config.syntax.tag_close}set")

						def handler(keyword, pargs, kwargs, context, content):
							if "name" in kwargs: self.dropdown_item_name = kwargs["name"]
							# Fix content formatting for markdown
							content = content.replace("\\r\\n", "<br>") + "<br><br>"
							gr.Label(label="Options", value=f"{self.dropdown_item_name}")
							gr.Markdown(value=content)
							self.wizard_template_kwargs = kwargs
							return ("")

						wizard_shortcode_parser.register(handler, "template", f"{Unprompted.Config.syntax.tag_close}template")

						def handler(keyword, pargs, kwargs, context):
							return get_local_file_dir(filename)

						wizard_shortcode_parser.register(handler, "base_dir")

						def handler(keyword, pargs, kwargs, context, content):
							with gr.Accordion(kwargs["_label"] if "_label" in kwargs else "More", open=True if "_open" in pargs else False):
								Unprompted.parse_alt_tags(content, None, wizard_shortcode_parser)
							return ("")

						def preprocess(keyword, pargs, kwargs, context):
							return True

						wizard_shortcode_parser.register(handler, "wizard_ui_accordion", f"{Unprompted.Config.syntax.tag_close}wizard_ui_accordion", preprocess)

						with gr.Tabs():
							filtered_templates = Unprompted.wizard_groups[WizardModes.TEMPLATES][int(is_img2img)]
							filtered_shortcodes = Unprompted.wizard_groups[WizardModes.SHORTCODES][int(is_img2img)]

							def wizard_add_template(show_me=False):
								self.dropdown_item_name = filename
								with gr.Group(visible=show_me) as filtered_templates[filename]:
									# Render the text file's UI with special parser object
									wizard_shortcode_parser.parse(file.read())
									# Auto-include is always the last element
									gr.Checkbox(label="🪄 Auto-include this in prompt", value=False, elem_classes=["wizard-autoinclude"])
									# Add event listeners
									wizard_prep_event_listeners(filtered_templates[filename])

							with gr.Tab("Templates"):
								import glob
								txt_files = glob.glob(f"{base_dir}/{Unprompted.Config.template_directory}/**/*.txt", recursive=True) if not is_img2img else Unprompted.wizard_template_files
								is_first = True

								templates_dropdown = gr.Dropdown(choices=[], label="Select template:", type="index", info="These are your GUI templates - you can think of them like custom scripts, except you can run an unlimited number of them at the same time.")

								for filename in txt_files:
									with open(filename, encoding="utf8") as file:
										if is_img2img: wizard_add_template()
										else:
											first_line = file.readline()
											# Make sure this text file starts with the [template] tag - this identifies it as a valid template
											if first_line.startswith(f"{Unprompted.Config.syntax.tag_start}template"):
												file.seek(0)  # Go back to start of file
												wizard_add_template(is_first)
												Unprompted.wizard_template_names.append(self.dropdown_item_name)
												Unprompted.wizard_template_files.append(filename)
												Unprompted.wizard_template_kwargs.append(self.wizard_template_kwargs)
												if (is_first):
													templates_dropdown.value = self.dropdown_item_name
													is_first = False

								# Refresh dropdown list
								templates_dropdown.choices = Unprompted.wizard_template_names

								if (len(filtered_templates) > 1):
									templates_dropdown.change(fn=wizard_select_item, inputs=[templates_dropdown, gr.Variable(value=is_img2img), gr.Variable(value=WizardModes.TEMPLATES)], outputs=list(filtered_templates.values()))

								wizard_template_btn = gr.Button(value="Generate Shortcode")

							with gr.Tab("Shortcodes"):
								shortcode_list = list(Unprompted.shortcode_objects.keys())
								Unprompted.wizard_dropdown = gr.Dropdown(choices=shortcode_list, label="Select shortcode:", value=Unprompted.Config.ui.wizard_default_shortcode, info="GUI for setting up any shortcode in Unprompted. More engaging than reading the manual!")

								for key in shortcode_list:
									if (hasattr(Unprompted.shortcode_objects[key], "ui")):
										with gr.Group(visible=(key == Unprompted.wizard_dropdown.value)) as filtered_shortcodes[key]:
											gr.Label(label="Options", value=f"{key}: {Unprompted.shortcode_objects[key].description}")
											if hasattr(Unprompted.shortcode_objects[key], "run_block"): gr.Textbox(label="Content", max_lines=2, min_lines=2)
											# Run the shortcode's UI template to populate
											Unprompted.shortcode_objects[key].ui(gr)
											# Auto-include is always the last element
											gr.Checkbox(label="🪄 Auto-include this in prompt", value=False, elem_classes=["wizard-autoinclude"])
											# Add event listeners
											wizard_prep_event_listeners(filtered_shortcodes[key])

								Unprompted.wizard_dropdown.change(fn=wizard_select_item, inputs=[Unprompted.wizard_dropdown, gr.Variable(value=is_img2img)], outputs=list(filtered_shortcodes.values()))

								wizard_shortcode_btn = gr.Button(value="Generate Shortcode")

							with gr.Tab("Capture"):
								gr.Markdown(value="This assembles Unprompted code with the WebUI settings for the last image you generated. You can save the code to your `templates` folder and call it later using `[file]`, or send it to someone as 'preset' for foolproof image reproduction.<br><br>**⚠️ Important:** <em>When you change your inference settings, you must generate an image before Unprompted can detect the changes. This is due to a limitation in the WebUI extension framework.</em>")
								# wizard_capture_include_inference = gr.Checkbox(label="Include inference settings",value=True)
								wizard_capture_include_inference = gr.Radio(label="Include inference settings:", choices=["none", "simple", "verbose"], value="simple", interactive=True)
								wizard_capture_include_prompt = gr.Radio(label="Include prompt:", choices=["none", "original", "postprocessed"], value="original", interactive=True)
								wizard_capture_include_neg_prompt = gr.Radio(label="Include negative prompt:", choices=["none", "original", "postprocessed"], value="original", interactive=True)
								wizard_capture_include_model = gr.Checkbox(label="Include model", value=False)
								wizard_capture_add_template_block = gr.Checkbox(label="Add [template] block", value=False)
								wizard_capture_btn = gr.Button(value="Generate code for my last image")

							wizard_result = gr.HTML(label="wizard_result", value="", elem_id="unprompted_result")
							wizard_shortcode_btn.click(fn=wizard_generate_shortcode, inputs=[Unprompted.wizard_dropdown, gr.Variable(value=is_img2img), gr.Variable(value="<strong>RESULT:</strong> ")], outputs=wizard_result)
							wizard_template_btn.click(fn=wizard_generate_template, inputs=[templates_dropdown, gr.Variable(value=is_img2img), gr.Variable(value="<strong>RESULT:</strong> ")], outputs=wizard_result)
							wizard_capture_btn.click(fn=wizard_generate_capture, inputs=[wizard_capture_include_inference, wizard_capture_include_prompt, wizard_capture_include_neg_prompt, wizard_capture_include_model, wizard_capture_add_template_block], outputs=wizard_result)

					else:
						gr.HTML(label="wizard_debug", value="You have disabled the Wizard in your config.")

				with gr.Accordion("📝 Dry Run", open=Unprompted.Config.ui.dry_run_open):
					dry_run_prompt = gr.Textbox(lines=2, placeholder="Test prompt", show_label=False, info="Run arbitrary text through Unprompted to check for syntax problems. Note: Stable Diffusion shortcodes are not well-supported here.")
					dry_run = gr.Button(value="Process Text")
					dry_run_result = gr.HTML(label="dry_run_result", value="", elem_id="unprompted_result")
					dry_run.click(fn=do_dry_run, inputs=dry_run_prompt, outputs=dry_run_result)

				with gr.Tab("💡 About"):
					about = gr.Markdown(value=get_markdown("docs/ABOUT.md").replace("$VERSION", Unprompted.VERSION))

					def open_folder(path):
						import platform
						import subprocess as sp
						path = os.path.normpath(path)
						if platform.system() == "Windows":
							os.startfile(path)
						elif platform.system() == "Darwin":
							sp.Popen(["open", path])
						else:
							sp.Popen(["xdg-open", path])

					open_templates = gr.Button(value="📂 Open templates folder")
					open_templates.click(fn=lambda: open_folder(f"{base_dir}/{Unprompted.Config.template_directory}"), inputs=[], outputs=[])

				with gr.Tab("📣 Announcements"):
					announcements = gr.Markdown(value=get_markdown("docs/ANNOUNCEMENTS.md"))

				with gr.Tab("⏱ Changelog"):
					changelog = gr.Markdown(value=get_markdown("docs/CHANGELOG.md"))

				with gr.Tab("📘 Manual"):
					manual = gr.Markdown(value=get_markdown("docs/MANUAL.md"))

				with gr.Tab("🎓 Guides"):
					guide = gr.Markdown(value=get_markdown("docs/GUIDE.md"))

		return [is_enabled, unprompted_seed, match_main_seed]

	def process(self, p, is_enabled=True, unprompted_seed=-1, match_main_seed=True, *args):
		if not is_enabled:
			return p

		# test compatibility with controlnet
		import copy
		Unprompted.main_p = p
		Unprompted.p_copy = copy.copy(p)

		# Update the controlnet script args with a list of 0 units
		# TODO: Check if CN is installed and enabled
		try:
			import importlib
			external_code = importlib.import_module("extensions.sd-webui-controlnet.scripts.external_code", "external_code")
			external_code.update_cn_script_in_processing(Unprompted.p_copy, [], is_ui=False)
		except Exception as e:
			# Unprompted.log_error(e)
			Unprompted.log("Could not communicate with ControlNet; proceeding without it.", context="WARNING")
			pass

		if match_main_seed:
			if p.seed == -1:
				from modules.processing import get_fixed_seed
				p.seed = get_fixed_seed(-1)
			Unprompted.log(f"Synchronizing seed with WebUI: {p.seed}")
			unprompted_seed = p.seed

		if unprompted_seed != -1:
			import random
			random.seed(unprompted_seed)

		Unprompted.fix_hires_prompts = False
		if hasattr(p, "hr_prompt"):
			try:
				if p.hr_prompt == p.prompt and p.hr_negative_prompt == p.negative_prompt:
					Unprompted.fix_hires_prompts = True
			except Exception as e:
				Unprompted.log_error(e, "Could not read hires variables from p object")
				pass

		# Reset vars
		if hasattr(p, "unprompted_original_prompt"):
			Unprompted.log(f"Resetting to initial prompt for batch processing: {Unprompted.original_prompt}")
			p.all_prompts[0] = Unprompted.original_prompt
			p.all_negative_prompts[0] = Unprompted.original_negative_prompt
		else:
			Unprompted.original_prompt = p.all_prompts[0]
			# This var is necessary for batch processing
			p.unprompted_original_prompt = Unprompted.original_prompt

		# Process Wizard auto-includes
		if Unprompted.Config.ui.wizard_enabled and self.allow_postprocess:
			is_img2img = hasattr(p, "init_images")

			for mode in range(len(WizardModes)):
				groups = Unprompted.wizard_groups[mode][int(is_img2img)]
				for idx, key in enumerate(groups):
					group = groups[key]
					autoinclude_obj = group

					# In theory, this should always select the "autoinclude" checkbox at the bottom of the UI
					while hasattr(autoinclude_obj, "children"):
						autoinclude_obj = autoinclude_obj.children[-1]

					if (autoinclude_obj.value):
						if mode == WizardModes.SHORTCODES: Unprompted.original_prompt = wizard_generate_shortcode(key, is_img2img, "", Unprompted.original_prompt)
						elif mode == WizardModes.TEMPLATES: Unprompted.original_prompt = wizard_generate_template(idx, is_img2img, "", Unprompted.original_prompt)

		Unprompted.original_negative_prompt = p.all_negative_prompts[0]
		if not hasattr(p, "unprompted_original_negative_prompt"): p.unprompted_original_negative_prompt = Unprompted.original_negative_prompt
		Unprompted.shortcode_user_vars = {}

		if Unprompted.Config.stable_diffusion.show_extra_generation_params:
			p.extra_generation_params.update({
			    "Unprompted Enabled": True,
			    "Unprompted Prompt": Unprompted.original_prompt.replace("\"", "'"),  # Must use single quotes or output will have backslashes
			    "Unprompted Negative Prompt": Unprompted.original_negative_prompt.replace("\"", "'"),
			    "Unprompted Seed": unprompted_seed
			})

		# Extra vars
		Unprompted.shortcode_user_vars["batch_index"] = 0
		Unprompted.shortcode_user_vars["batch_test"] = None
		Unprompted.original_model = opts.data["sd_model_checkpoint"]  # opts.sd_model_checkpoint
		Unprompted.shortcode_user_vars["sd_model"] = opts.data["sd_model_checkpoint"]  # opts.sd_model_checkpoint

		# Set up system var support - copy relevant p attributes into shortcode var object
		# for att in dir(p):
		# 	if not att.startswith("__") and att != "sd_model":
		# 		Unprompted.shortcode_user_vars[att] = getattr(p, att)

		#Unprompted.shortcode_user_vars["prompt"] = Unprompted.process_string(apply_prompt_template(Unprompted.original_prompt, Unprompted.Config.templates.default))
		#Unprompted.shortcode_user_vars["negative_prompt"] = Unprompted.process_string(apply_prompt_template(Unprompted.shortcode_user_vars["negative_prompt"] if "negative_prompt" in Unprompted.shortcode_user_vars else Unprompted.original_negative_prompt, Unprompted.Config.templates.default_negative))

		#Unprompted.update_stable_diffusion_vars(p)

		if p.seed is not None and p.seed != -1.0:
			if (Unprompted.is_int(p.seed)): p.seed = int(p.seed)
			p.all_seeds[0] = p.seed
		else:
			p.seed = -1
			p.seed = fix_seed(p)

		# Legacy processing support
		if (Unprompted.Config.stable_diffusion.batch_method != "standard"):
			# Set up system var support - copy relevant p attributes into shortcode var object
			for att in dir(p):
				if not att.startswith("__") and att != "sd_model":
					Unprompted.shortcode_user_vars[att] = getattr(p, att)

			Unprompted.shortcode_user_vars["prompt"] = Unprompted.process_string(apply_prompt_template(Unprompted.original_prompt, Unprompted.Config.templates.default))
			Unprompted.shortcode_user_vars["negative_prompt"] = Unprompted.process_string(apply_prompt_template(Unprompted.shortcode_user_vars["negative_prompt"] if "negative_prompt" in Unprompted.shortcode_user_vars else Unprompted.original_negative_prompt, Unprompted.Config.templates.default_negative))

			# Apply any updates to system vars
			Unprompted.update_stable_diffusion_vars(p)

			if (Unprompted.Config.stable_diffusion.batch_method == "legacy"):
				for i, val in enumerate(p.all_prompts):
					if "single_seed" in Unprompted.shortcode_user_vars: p.all_seeds[i] = Unprompted.shortcode_user_vars["single_seed"]
					if (i == 0):
						Unprompted.shortcode_user_vars["batch_index"] = i
						p.all_prompts[0] = Unprompted.shortcode_user_vars["prompt"]
						p.all_negative_prompts[0] = Unprompted.shortcode_user_vars["negative_prompt"]
					else:
						for key in list(Unprompted.shortcode_user_vars):  # create a copy obj to avoid error during iteration
							if key not in Unprompted.shortcode_objects["remember"].globals:
								del Unprompted.shortcode_user_vars[key]

						Unprompted.shortcode_user_vars["batch_index"] = i
						p.all_prompts[i] = Unprompted.process_string(apply_prompt_template(p.unprompted_original_prompt, Unprompted.Config.templates.default))
						p.all_negative_prompts[i] = Unprompted.process_string(apply_prompt_template(Unprompted.shortcode_user_vars["negative_prompt"] if "negative_prompt" in Unprompted.shortcode_user_vars else p.unprompted_original_negative_prompt, Unprompted.Config.templates.default_negative))

					Unprompted.log(f"Result {i}: {p.all_prompts[i]}", False)
			# Keep the same prompt between runs
			elif (Unprompted.Config.stable_diffusion.batch_method == "none"):
				for i, val in enumerate(p.all_prompts):
					p.all_prompts[i] = Unprompted.shortcode_user_vars["prompt"]
					p.all_negative_prompts[i] = Unprompted.shortcode_user_vars["negative_prompt"]

			# Cleanup routines
			Unprompted.log("Entering Cleanup routine...", False)
			for i in Unprompted.cleanup_routines:
				Unprompted.shortcode_objects[i].cleanup()

			if unprompted_seed != -1: random.seed()

	def process_batch(self, p, is_enabled=True, unprompted_seed=-1, match_main_seed=True, *args, **kwargs):
		if (is_enabled and Unprompted.Config.stable_diffusion.batch_method == "standard"):
			Unprompted.log("Engaging new process_batch() implementation - if it gives you any trouble, please set batch_method to 'legacy' in your config. This message will be removed in a future update.", context="WARNING")

			batch_index = Unprompted.shortcode_user_vars["batch_index"]

			Unprompted.log(f"Starting process_batch() for batch_index #{batch_index}...")

			if batch_index > 0:
				if "single_seed" in Unprompted.shortcode_user_vars: p.all_seeds[batch_index] = Unprompted.shortcode_user_vars["single_seed"]

				for key in list(Unprompted.shortcode_user_vars):  # create a copy obj to avoid error during iteration
					if key not in Unprompted.shortcode_objects["remember"].globals and key != "batch_index":
						del Unprompted.shortcode_user_vars[key]

			# Set up system var support - copy relevant p attributes into shortcode var object
			for att in dir(p):
				if not att.startswith("__") and att != "sd_model":
					# Unprompted.log(f"Setting {att} to {getattr(p, att)}")
					Unprompted.shortcode_user_vars[att] = getattr(p, att)

			prompt_result = Unprompted.process_string(apply_prompt_template(p.unprompted_original_prompt, Unprompted.Config.templates.default))
			negative_prompt_result = Unprompted.process_string(apply_prompt_template(Unprompted.shortcode_user_vars["negative_prompt"] if "negative_prompt" in Unprompted.shortcode_user_vars else p.unprompted_original_negative_prompt, Unprompted.Config.templates.default_negative))

			Unprompted.shortcode_user_vars["prompt"] = prompt_result
			Unprompted.shortcode_user_vars["negative_prompt"] = negative_prompt_result
			# TODO: Determine if Unprompted should handle batch_size in a more sophisticated fashion than simply filling the prompts list with one result
			Unprompted.shortcode_user_vars["prompts"] = [prompt_result] * Unprompted.shortcode_user_vars["batch_size"]
			Unprompted.shortcode_user_vars["negative_prompts"] = [negative_prompt_result] * Unprompted.shortcode_user_vars["batch_size"]

			Unprompted.update_stable_diffusion_vars(p)

			p.all_prompts[batch_index] = prompt_result
			p.all_negative_prompts[batch_index] = negative_prompt_result

			# Increment batch index
			batch_index += 1

			# Check for final iteration
			if (batch_index == len(p.all_prompts)):

				# Cleanup routines
				Unprompted.log("Entering Cleanup routine...", False)
				for i in Unprompted.cleanup_routines:
					Unprompted.shortcode_objects[i].cleanup()

				if unprompted_seed != -1:
					import random
					random.seed()
			else:
				Unprompted.shortcode_user_vars["batch_index"] = batch_index

	# After routines
	def postprocess(self, p, processed, is_enabled=True, unprompted_seed=-1, match_main_seed=True):
		if not self.allow_postprocess or not is_enabled:
			Unprompted.log("Bypassing After routine to avoid infinite loop.")
			self.allow_postprocess = True
			return False  # Prevents endless loop with some shortcodes

		if Unprompted.fix_hires_prompts:
			Unprompted.log("Synchronizing prompt vars with hr_prompt vars")
			p.hr_prompt = Unprompted.shortcode_user_vars["prompt"]
			p.hr_negative_prompt = Unprompted.shortcode_user_vars["negative_prompt"]
			p.all_hr_prompts = p.all_prompts
			p.all_hr_negative_prompts = p.all_negative_prompts

		self.allow_postprocess = False
		Unprompted.log("Entering After routine...")

		for i in Unprompted.after_routines:
			val = Unprompted.shortcode_objects[i].after(p, processed)
			if val: processed = val

		self.allow_postprocess = True

		return processed