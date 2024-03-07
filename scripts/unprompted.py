# Unprompted by Therefore Games. All Rights Reserved.

# This script is intended to be used as an extension for Automatic1111's Stable Diffusion WebUI.

# You may support the project here:
# https://github.com/ThereforeGames/unprompted
# https://patreon.com/thereforegames

import gradio as gr

import modules.scripts as scripts
from modules.processing import process_images, fix_seed, Processed
from modules.shared import opts, cmd_opts, state
from modules.ui_components import ToolButton
from modules import sd_models
import lib_unprompted.shortcodes as shortcodes
import lib_unprompted.helpers as helpers
from pathlib import Path
from enum import IntEnum, auto
import sys, os, html, random

base_dir = scripts.basedir()
unprompted_dir = str(Path(*Path(base_dir).parts[-2:])).replace("\\", "/")

sys.path.append(base_dir)
# Main object
from lib_unprompted.shared import Unprompted, parse_config

Unprompted = Unprompted(base_dir)

Unprompted.log.debug(f"The `base_dir` is: {base_dir}")
ext_dir = os.path.split(os.path.normpath(base_dir))[1]
if ext_dir == "unprompted":
	Unprompted.log.warning("The extension folder must be renamed from unprompted to _unprompted in order to ensure compatibility with other extensions. Please see this A1111 WebUI issue for more details: https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/8011")

WizardModes = IntEnum("WizardModes", ["TEMPLATES", "SHORTCODES"], start=0)

Unprompted.wizard_groups = [[{}, {}] for _ in range(len(WizardModes))]  # Two subdictionaries for txt2img and img2img
# shortcodes_dropdown = None
Unprompted.main_p = None
Unprompted.is_enabled = True
Unprompted.original_prompt = None
Unprompted.original_negative_prompt = ""

if os.path.exists(f"./modules_forge"):
	Unprompted.webui = "forge"
else:
	Unprompted.webui = "auto1111"

Unprompted.log.debug(f"WebUI type: {Unprompted.webui}")

Unprompted.wizard_template_files = []
Unprompted.wizard_template_names = []
Unprompted.wizard_template_kwargs = []


def do_dry_run(string):
	Unprompted.log.debug(string)
	# Reset vars
	Unprompted.shortcode_user_vars = {}
	unp_result = Unprompted.start(string)
	Unprompted.cleanup()
	return f"<strong>RESULT:</strong> {unp_result}"


def wizard_select_item(option, is_img2img, mode=WizardModes.SHORTCODES):
	# self.shortcodes_dropdown.value = option

	this_list = Unprompted.wizard_groups[mode][int(is_img2img)]

	# Retrieve corresponding template filepath
	try:
		if (mode == WizardModes.TEMPLATES): option = Unprompted.wizard_template_files[option]
	except Exception as e:
		Unprompted.log.debug("Unexpected wizard_select_item error")
		pass

	results = [gr.update(visible=(option == key)) for key in this_list.keys()]
	return results


def block_is_container(block_name):
	if (block_name == "form" or block_name == "accordion" or block_name == "row"): return True
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


def wizard_generate_template(option, is_img2img, html_safe=True, prepend="", append=""):
	filepath = os.path.relpath(Unprompted.wizard_template_files[option], f"{base_dir}/{Unprompted.Config.template_directory}")
	# Remove file extension
	filepath = os.path.splitext(filepath)[0]
	result = f"{Unprompted.Config.syntax.tag_start}call \"{filepath}\""
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
					if block_name == "file":
						this_val = f"{Unprompted.Config.syntax.delimiter}".join([str(e.name) for e in gr_obj.value])
					else:
						this_val = gr_obj.value
					if (arg_name == "prompt"): continue

					this_val = str(helpers.autocast(this_val)).replace("\"", "\'")
					if html_safe: this_val = html.escape(this_val, quote=False)
					this_val = Unprompted.make_alt_tags(this_val)

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


def wizard_generate_shortcode(option, is_img2img, html_safe=True, prepend="", append=""):
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
					block_content += results[0]
					result = results[1]
				elif gr_obj.label == "Content":
					block_content += gr_obj.value
				else:
					if block_name == "label" or block_name == "markdown" or gr_obj.value is None or gr_obj.value == "": continue  # Skip empty fields

					# Enable support for multiselect dropdowns
					if type(gr_obj.value) == list:
						this_val = f"{Unprompted.Config.syntax.delimiter}".join([str(e) for e in gr_obj.value])
					else:
						this_val = gr_obj.value

					arg_name = gr_obj.label.split(" ")[-1]  # Get everything after the last space

					# Rules
					if (arg_name == "prompt"): continue
					elif (arg_name == "str"):
						result += " \"" + str(this_val) + "\""
					elif (arg_name == "int"):
						result += " " + str(int(this_val))
					elif (arg_name == "verbatim"):
						result += " " + str(this_val)
					elif (block_name == "checkbox"):
						if this_val: result += " " + arg_name
					elif (block_name == "number" or block_name == "slider"): result += f" {arg_name}={helpers.autocast(gr_obj.value)}"
					elif (block_name == "textbox"):
						if len(this_val) > 0: result += f" {arg_name}=\"{this_val}\""
					else:
						if html_safe: this_val = html.escape(this_val, quote=False)
						result += f" {arg_name}=\"{this_val}\""

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
								result += f"{prefix}{html.escape(str(att_val))}"

			if include_inference != "none" or include_model: result += f"{Unprompted.Config.syntax.tag_end}"
			if include_prompt != "none": result += prompt
			if include_neg_prompt != "none" and len(neg_prompt) > 0: result += f"{Unprompted.Config.syntax.tag_start}set negative_prompt{Unprompted.Config.syntax.tag_end}{neg_prompt}{Unprompted.Config.syntax.tag_start}{Unprompted.Config.syntax.tag_close}set{Unprompted.Config.syntax.tag_end}"

		else: result = "<strong>ERROR:</strong> Could not detect your inference settings. Try generating an image first."
	except Exception as e:
		Unprompted.log.exception("Exception caught during Wizard Capture generation")
		result = f"<strong>ERROR:</strong> {e}"

	return result


def get_local_file_dir(filename=None):
	# unp_dir = os.path.basename(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

	if filename: filepath = "/" + str(Path(os.path.relpath(filename, f"{base_dir}")).parent)
	else: filepath = ""

	return (f"file/{unprompted_dir}{filepath}")


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

	# Lists with two positions - one for txt2img, one for img2img
	templates_region = [None] * 2
	templates_dropdown = [None] * 2
	shortcodes_region = [None] * 2
	shortcodes_dropdown = [None] * 2

	def title(self):
		return "Unprompted"

	def show(self, is_img2img):
		return scripts.AlwaysVisible

	def ui(self, is_img2img):
		mode_string = "img2img" if is_img2img else "txt2img"
		with gr.Group():
			with gr.Accordion("Unprompted", open=Unprompted.Config.ui.open, elem_classes=["unprompted-accordion", mode_string]):
				with gr.Row(equal_height=True):
					is_enabled = gr.Checkbox(label="Enabled", value=gradio_enabled_checkbox_workaround)

					match_main_seed = gr.Checkbox(label="Synchronize with main seed", value=True)
					setattr(match_main_seed, "do_not_save_to_config", True)

				unprompted_seed = gr.Number(label="Unprompted Seed", value=-1)
				setattr(unprompted_seed, "do_not_save_to_config", True)

				if (os.path.exists(f"{base_dir}/{Unprompted.Config.template_directory}/pro/beautiful_soul_v0.1.0/main{Unprompted.Config.formats.txt}")): is_open = False
				else: is_open = True

				promos = []
				promos.append(f'<a href="https://payhip.com/b/L1uNF" target="_blank"><img src="{get_local_file_dir()}/images/promo_box_beautiful_soul.png" class="thumbnail"></a><h1><strong>Beautiful Soul</strong>: Bring your characters to life.</h1><p>A highly expressive character generator for the A1111 WebUI. With thousands of wildcards and direct ControlNet integration, this is by far our most powerful Unprompted template to date.</p><a href="https://payhip.com/b/L1uNF" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View premium assets for Unprompted">Download Now ➜</button></a>')
				promos.append(f'<a href="https://payhip.com/b/qLUX9" target="_blank"><img src="{get_local_file_dir()}/images/promo_box_demoncrawl_avatar_generator.png" class="thumbnail"></a><h1>The <strong>DemonCrawl</strong> Pixel Art Avatar Generator</h1><p>Create pixel art portraits in the style of the popular roguelite, <a href="https://demoncrawl.com" _target=blank>DemonCrawl</a>. Includes a custom Stable Diffusion model trained by the game\'s developer, as well as a custom GUI and the ability to randomize your prompts.</p><a href="https://payhip.com/b/qLUX9" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View premium assets for Unprompted">Download Now ➜</button></a>')
				promos.append(f'<a href="https://payhip.com/b/hdgNR" target="_blank"><img src="{get_local_file_dir()}/images/promo_box_fantasy.png" class="thumbnail"></a><h1>Create beautiful art for your <strong>Fantasy Card Game</strong></h1><p>Generate a wide variety of creatures and characters in the style of a fantasy card game. Perfect for heroes, animals, monsters, and even crazy hybrids.</p><a href="https://payhip.com/b/hdgNR" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View premium assets for Unprompted">Download Now ➜</button></a>')
				promos.append(f'<a href="https://github.com/ThereforeGames/unprompted" target="_blank"><img src="{get_local_file_dir()}/images/promo_github_star.png" class="thumbnail"></a><h1>Give Unprompted a <strong>star</strong> for visibility</h1><p>Most WebUI users have never heard of Unprompted. You can help more people discover it by giving the repo a ⭐ on Github. Thank you for your support!</p><a href="https://github.com/ThereforeGames/unprompted" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View the Unprompted repo">Visit Github ➜</button></a>')
				promos.append(f'<a href="https://github.com/sponsors/ThereforeGames" target="_blank"><img src="{get_local_file_dir()}/images/promo_github_sponsor.png" class="thumbnail"></a><h1>Become a Sponsor</h1><p>One of the best ways to support Unprompted is by becoming our Sponsor on Github - sponsors receive access to a private repo containing all of our premium add-ons. <em>(Still setting that up... should be ready soon!)</em></p><a href="https://github.com/sponsors/ThereforeGames" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View the Unprompted repo">Visit Github ➜</button></a>')
				promos.append(f'<a href="https://github.com/ThereforeGames/sd-webui-breadcrumbs" target="_blank"><img src="{get_local_file_dir()}/images/promo_breadcrumbs.png" class="thumbnail"></a><h1>Try our new Breadcrumbs extension</h1><p>From the developer of Unprompted comes <strong>sd-webui-breadcrumbs</strong>, an extension designed to improve the WebUI\'s navigation flow. Tedious "menu diving" is a thing of the past!</p><a href="https://github.com/ThereforeGames/sd-webui-breadcrumbs" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View the sd-webui-breadcrumbs repo">Visit Github ➜</button></a>')

				with gr.Accordion("🎉 Promo", open=is_open):
					plug = gr.HTML(label="plug", elem_id="promo", value=random.choice(promos))

				with gr.Accordion("🧙 Wizard", open=Unprompted.Config.ui.wizard_open):
					if Unprompted.Config.ui.wizard_enabled:

						self.wizard_template_template = ""
						self.wizard_template_elements = []

						# Wizard UI shortcode parser for templates
						wizard_shortcode_parser = shortcodes.Parser(start=Unprompted.Config.syntax.tag_start, end=Unprompted.Config.syntax.tag_end, esc=Unprompted.Config.syntax.tag_escape, ignore_unknown=True, inherit_globals=False)

						def handler(keyword, pargs, kwargs, context, content):
							if "_new" in pargs and ("_ui" not in kwargs or kwargs["_ui"] != "none"):
								import lib_unprompted.casefy as casefy

								friendly_name = kwargs["_label"] if "_label" in kwargs else casefy.titlecase(pargs[0])
								block_name = kwargs["_ui"] if "_ui" in kwargs else "textbox"
								_info = kwargs["_info"] if "_info" in kwargs else ""
								_multiselect = bool(int(kwargs["_multiselect"])) if "_multiselect" in kwargs else False
								_show_label = bool(int(kwargs["_show_label"])) if "_show_label" in kwargs else True

								this_label = f"{friendly_name} {Unprompted.Config.syntax.wizard_delimiter} {pargs[0]}"

								# Produce UI based on type
								if (block_name == "textbox"):
									if "_placeholder" in kwargs: this_placeholder = kwargs["_placeholder"]
									else: this_placeholder = str(content)
									obj = gr.Textbox(label=this_label, lines=int(kwargs["_lines"]) if "_lines" in kwargs else 1, max_lines=int(kwargs["_max_lines"]) if "_max_lines" in kwargs else 1, placeholder=this_placeholder, info=_info, show_label=_show_label)
								elif (block_name == "checkbox"):
									obj = gr.Checkbox(label=this_label, value=bool(int(content)), info=_info, show_label=_show_label)
								elif (block_name == "number"):
									obj = gr.Number(label=this_label, value=int(content), interactive=True, info=_info, minimum=kwargs["_minimum"] if "_minimum" in kwargs else None, maximum=kwargs["_maximum"] if "_maximum" in kwargs else None, show_label=_show_label)
								elif (block_name == "dropdown"):
									_choices = Unprompted.parse_advanced(kwargs["_choices"], "wizard").split(Unprompted.Config.syntax.delimiter)
									obj = gr.Dropdown(label=this_label, value=content, choices=_choices, info=_info, multiselect=_multiselect, show_label=_show_label)
								elif (block_name == "radio"):
									obj = gr.Radio(label=this_label, choices=kwargs["_choices"].split(Unprompted.Config.syntax.delimiter), interactive=True, value=content, show_label=_show_label)
								elif (block_name == "slider"):
									obj = gr.Slider(label=this_label, value=int(content), minimum=kwargs["_minimum"] if "_minimum" in kwargs else 1, maximum=kwargs["_maximum"] if "_maximum" in kwargs else 10, step=kwargs["_step"] if "_step" in kwargs else 1, info=_info, show_label=_show_label)
								elif (block_name == "image"):
									if len(content) < 1: content = None
									obj = gr.Image(label=this_label, value=content, type="filepath", interactive=True, info=_info, show_label=_show_label)
								elif (block_name == "file"):
									if len(content) < 1: content = None
									file_types = helpers.ensure(kwargs["_file_types"].split(Unprompted.Config.syntax.delimiter), list) if "_file_types" in kwargs else None

									obj = gr.File(label=this_label, value=content, interactive=True, info=_info, show_label=_show_label, file_count=kwargs["_file_count"] if "_file_count" in kwargs else "single", file_types=file_types)

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

						def handler(keyword, pargs, kwargs, context, content):
							if pargs[0] == "accordion":
								block = gr.Accordion(kwargs["_label"] if "_label" in kwargs else "More", open=True if "_open" in pargs else False)
							elif pargs[0] == "row":
								block = gr.Row(equal_height=pargs["_equal_height"] if "_equal_height" in pargs else False)
							elif pargs[0] == "column":
								block = gr.Column(scale=int(pargs["_scale"]) if "_scale" in pargs else 1)

							with block:
								# Unprompted.parse_alt_tags(content, None, wizard_shortcode_parser)
								# Unprompted.process_string(content,parser=wizard_shortcode_parser)
								wizard_shortcode_parser.parse(content)
							return ("")

						def preprocess(keyword, pargs, kwargs, context):
							return True

						wizard_shortcode_parser.register(handler, "wizard", f"{Unprompted.Config.syntax.tag_close}wizard", preprocess)

						def handler(keyword, pargs, kwargs, context):
							if self.dropdown_item_name:
								return get_local_file_dir(self.dropdown_item_name)
							return get_local_file_dir()  # filename

						wizard_shortcode_parser.register(handler, "base_dir")

						with gr.Tabs():

							self.filtered_templates = Unprompted.wizard_groups[WizardModes.TEMPLATES][int(is_img2img)]
							self.filtered_shortcodes = Unprompted.wizard_groups[WizardModes.SHORTCODES][int(is_img2img)]

							def wizard_populate_templates(region, first_load=False):
								import glob

								self.filtered_templates = Unprompted.wizard_groups[WizardModes.TEMPLATES][int(is_img2img)]

								def wizard_add_template(show_me=False):
									self.dropdown_item_name = filename
									with gr.Group(visible=show_me) as self.filtered_templates[filename]:
										# Render the text file's UI with special parser object
										wizard_shortcode_parser.parse(file.read())
										# Auto-include is always the last element
										gr.Checkbox(label=f"🪄 Auto-include {self.dropdown_item_name} in prompt", value=False, elem_classes=["wizard-autoinclude", mode_string])
										# Add event listeners
										wizard_prep_event_listeners(self.filtered_templates[filename])
									Unprompted.log.debug(f"Added {'img2img' if is_img2img else 'txt2img'} Wizard Template: {self.dropdown_item_name}")

								txt_files = glob.glob(f"{base_dir}/{Unprompted.Config.template_directory}/**/*.txt", recursive=True) if (not is_img2img) else Unprompted.wizard_template_files
								is_first = True

								with region:
									for filename in txt_files:
										with open(filename, encoding=Unprompted.Config.formats.default_encoding) as file:
											if is_img2img and first_load: wizard_add_template()
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
														self.templates_dropdown[int(is_img2img)].value = self.dropdown_item_name
														is_first = False

									if (len(self.filtered_templates) > 1):
										self.templates_dropdown[int(is_img2img)].change(fn=wizard_select_item, inputs=[self.templates_dropdown[int(is_img2img)], gr.Variable(value=is_img2img), gr.Variable(value=WizardModes.TEMPLATES)], outputs=list(self.filtered_templates.values()))

								Unprompted.log.debug(f"Finished populating {'img2img' if is_img2img else 'txt2img'} templates.")
								return gr.Dropdown.update(choices=Unprompted.wizard_template_names)

							def wizard_populate_shortcodes(region, first_load=False):
								if not first_load:
									Unprompted.load_shortcodes()
									Unprompted.log.warning("Sorry, Gradio is presently incapable of dynamically creating UI elements. You must restart the WebUI to see new shortcodes in the Wizard. This is expected to change in a future release: https://github.com/gradio-app/gradio/issues/4689")
									return ""

								with region:
									for key in shortcode_list:
										if (hasattr(Unprompted.shortcode_objects[key], "ui")):
											with gr.Group(visible=(key == self.shortcodes_dropdown[int(is_img2img)].value)) as self.filtered_shortcodes[key]:
												gr.Label(label="Options", value=f"{key}: {Unprompted.shortcode_objects[key].description}")
												if hasattr(Unprompted.shortcode_objects[key], "run_block"): gr.Textbox(label="Content", max_lines=2, min_lines=2)
												# Run the shortcode's UI template to populate
												Unprompted.shortcode_objects[key].ui(gr)
												# Auto-include is always the last element
												gr.Checkbox(label=f"🪄 Auto-include [{key}] in prompt", value=False, elem_classes=["wizard-autoinclude", mode_string])
												# Add event listeners
												wizard_prep_event_listeners(self.filtered_shortcodes[key])

									self.shortcodes_dropdown[int(is_img2img)].change(fn=wizard_select_item, inputs=[self.shortcodes_dropdown[int(is_img2img)], gr.Variable(value=is_img2img)], outputs=list(self.filtered_shortcodes.values()))

								return gr.Dropdown.update(choices=list(Unprompted.shortcode_objects.keys()))

							def wizard_refresh_templates():
								Unprompted.log.debug("Refreshing the Wizard Templates...")
								Unprompted.log.warning("Sorry, Gradio is presently incapable of dynamically creating UI elements. You must restart the WebUI to update Wizard templates. This is expected to change in a future release: https://github.com/gradio-app/gradio/issues/4689")
								return ""
								if Unprompted.Config.ui.wizard_templates:
									Unprompted.wizard_template_names.clear()
									Unprompted.wizard_template_files.clear()
									Unprompted.wizard_template_kwargs.clear()
									return wizard_populate_templates(self.templates_region[int(is_img2img)])
								return ""

							def wizard_refresh_shortcodes():
								Unprompted.log.debug("Refreshing the Wizard Shortcodes...")
								return wizard_populate_shortcodes(self.shortcodes_region[int(is_img2img)])

							if Unprompted.Config.ui.wizard_templates:
								with gr.Tab("Templates"):
									with gr.Row():
										self.templates_dropdown[int(is_img2img)] = gr.Dropdown(choices=[], label="Select template:", type="index", info="These are your GUI templates - you can think of them like custom scripts, except you can run an unlimited number of them at the same time.")
										templates_refresh = ToolButton(value='\U0001f504', elem_id=f"templates-refresh")
										templates_refresh.click(fn=wizard_refresh_templates)  # , outputs=self.templates_dropdown[int(is_img2img)]

									self.templates_region[int(is_img2img)] = gr.Blocks()
									wizard_populate_templates(self.templates_region[int(is_img2img)], True)

									self.templates_dropdown[int(is_img2img)].choices = Unprompted.wizard_template_names

									wizard_template_btn = gr.Button(value="🧠 Generate Shortcode")

							if Unprompted.Config.ui.wizard_shortcodes:
								with gr.Tab("Shortcodes"):
									shortcode_list = list(Unprompted.shortcode_objects.keys())
									with gr.Row():
										self.shortcodes_dropdown[int(is_img2img)] = gr.Dropdown(choices=shortcode_list, label="Select shortcode:", value=Unprompted.Config.ui.wizard_default_shortcode, info="GUI for setting up any shortcode in Unprompted. More engaging than reading the manual!")
										shortcodes_refresh = ToolButton(value='\U0001f504', elemn_id=f"shortcodes-refresh")
										shortcodes_refresh.click(fn=wizard_refresh_shortcodes)  # , outputs=self.shortcodes_dropdown[int(is_img2img)]

									self.shortcodes_region[int(is_img2img)] = gr.Blocks()
									wizard_populate_shortcodes(self.shortcodes_region[int(is_img2img)], True)

									wizard_shortcode_btn = gr.Button(value="🧠 Generate Shortcode")

							if Unprompted.Config.ui.wizard_capture:
								with gr.Tab("Capture"):
									gr.Markdown(value="This assembles Unprompted code with the WebUI settings for the last image you generated. You can save the code to your `templates` folder and `[call]` it later, or send it to someone as 'preset' for foolproof image reproduction.<br><br>**⚠️ Important:** <em>When you change your inference settings, you must generate an image before Unprompted can detect the changes. This is due to a limitation in the WebUI extension framework.</em>")
									# wizard_capture_include_inference = gr.Checkbox(label="Include inference settings",value=True)
									wizard_capture_include_inference = gr.Radio(label="Include inference settings:", choices=["none", "simple", "verbose"], value="simple", interactive=True)
									wizard_capture_include_prompt = gr.Radio(label="Include prompt:", choices=["none", "original", "postprocessed"], value="original", interactive=True)
									wizard_capture_include_neg_prompt = gr.Radio(label="Include negative prompt:", choices=["none", "original", "postprocessed"], value="original", interactive=True)
									wizard_capture_include_model = gr.Checkbox(label="Include model", value=False)
									wizard_capture_add_template_block = gr.Checkbox(label="Add [template] block", value=False)
									wizard_capture_btn = gr.Button(value="Generate code for my last image")

							wizard_result = gr.HTML(label="wizard_result", value="", elem_id="unprompted_result")
							if Unprompted.Config.ui.wizard_templates: wizard_template_btn.click(fn=wizard_generate_template, inputs=[self.templates_dropdown[int(is_img2img)], gr.Variable(value=is_img2img), gr.Variable(value="<strong>RESULT:</strong> ")], outputs=wizard_result)
							if Unprompted.Config.ui.wizard_shortcodes: wizard_shortcode_btn.click(fn=wizard_generate_shortcode, inputs=[self.shortcodes_dropdown[int(is_img2img)], gr.Variable(value=is_img2img), gr.Variable(value="<strong>RESULT:</strong> ")], outputs=wizard_result)
							if Unprompted.Config.ui.wizard_capture: wizard_capture_btn.click(fn=wizard_generate_capture, inputs=[wizard_capture_include_inference, wizard_capture_include_prompt, wizard_capture_include_neg_prompt, wizard_capture_include_model, wizard_capture_add_template_block], outputs=wizard_result)

					else:
						gr.HTML(label="wizard_debug", value="You have disabled the Wizard in your config.")

				with gr.Accordion("📝 Dry Run", open=Unprompted.Config.ui.dry_run_open):
					dry_run_prompt = gr.Textbox(lines=2, placeholder="Test prompt", show_label=False, info="Run arbitrary text through Unprompted to check for syntax problems. Note: Stable Diffusion shortcodes are not well-supported here.")
					dry_run = gr.Button(value="Process Text")
					dry_run_result = gr.HTML(label="dry_run_result", value="", elem_id="unprompted_result")
					dry_run.click(fn=do_dry_run, inputs=dry_run_prompt, outputs=dry_run_result)

				with gr.Accordion("🛠️ Resources", open=Unprompted.Config.ui.resources_open):
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

					with gr.Tab("📣 Announcements"):
						announcements = gr.Markdown(value=get_markdown("docs/ANNOUNCEMENTS.md"))

					with gr.Tab("⏱ Changelog"):
						changelog = gr.Markdown(value=get_markdown("docs/CHANGELOG.md"))

					with gr.Tab("📘 Manual"):
						manual = gr.Markdown(value=get_markdown("docs/MANUAL.md"))

					with gr.Tab("🎓 Guides"):
						guide = gr.Markdown(value=get_markdown("docs/GUIDE.md"))

				def reload_unprompted():
					Unprompted.log.debug("Reloading Unprompted...")
					Unprompted.log.debug("Reloading `config.json`...")
					Unprompted.cfg_dict, Unprompted.Config = parse_config(base_dir)
					Unprompted.load_shortcodes()
					# self.shortcodes_dropdown[int(is_img2img)].update(choices=wizard_refresh_shortcodes())
					# self.templates_dropdown[int(is_img2img)].update(choices=wizard_refresh_templates())
					Unprompted.log.debug("Reload completed!")

				with gr.Row():
					open_templates = gr.Button(value="📂 Open templates folder")
					open_templates.click(fn=lambda: open_folder(f"{base_dir}/{Unprompted.Config.template_directory}"), inputs=[], outputs=[])

					reload_config = gr.Button(value="\U0001f504 Reload Unprompted")
					reload_config.click(fn=reload_unprompted, inputs=[], outputs=[])

		return [is_enabled, unprompted_seed, match_main_seed]

	def process(self, p, is_enabled=True, unprompted_seed=-1, match_main_seed=True, *args):
		if not is_enabled or not Unprompted.is_enabled:
			return p

		# test compatibility with controlnet
		Unprompted.main_p = p

		Unprompted.log.debug(f"Directory of the p object: {dir(p)}")

		# as of webui 1.5.1, creating a shallow copy of the p object no longer seems to work.
		# deepcopy throws errors as well.
		# Unprompted.p_copy = copy.copy(p)

		if match_main_seed:
			if p.seed == -1:
				from modules.processing import get_fixed_seed
				p.seed = get_fixed_seed(-1)
			Unprompted.log.debug(f"Synchronizing seed with WebUI: {p.seed}")
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
				Unprompted.log.exception("Exception while trying to read hires variables from p object")
				pass

		# Reset vars
		if hasattr(p, "unprompted_original_prompt"):
			Unprompted.log.debug(f"Resetting to initial prompt for batch processing: {Unprompted.original_prompt}")
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
						if mode == WizardModes.SHORTCODES: Unprompted.original_prompt = wizard_generate_shortcode(key, is_img2img, False, "", Unprompted.original_prompt)
						elif mode == WizardModes.TEMPLATES: Unprompted.original_prompt = wizard_generate_template(idx, is_img2img, False, "", Unprompted.original_prompt)
						p.all_prompts[0] = Unprompted.original_prompt  # test
						p.unprompted_original_prompt = Unprompted.original_prompt

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

		# Instantiate special vars
		Unprompted.shortcode_user_vars["batch_index"] = 0  # legacy name for batch_count_index
		Unprompted.shortcode_user_vars["batch_count_index"] = 0
		Unprompted.shortcode_user_vars["batch_size_index"] = 0
		Unprompted.shortcode_user_vars["batch_real_index"] = 0
		Unprompted.shortcode_user_vars["batch_test"] = None
		Unprompted.original_model = opts.data["sd_model_checkpoint"]
		Unprompted.shortcode_user_vars["sd_model"] = opts.data["sd_model_checkpoint"]
		Unprompted.shortcode_user_vars["sd_base"] = "none"
		if sd_models.model_data.sd_model:
			try:  # temporary workaround for sd.next lacking these variables
				if sd_models.model_data.sd_model.is_sdxl: Unprompted.shortcode_user_vars["sd_base"] = "sdxl"
				elif sd_models.model_data.sd_model.is_sd2: Unprompted.shortcode_user_vars["sd_base"] = "sd2"
				elif sd_models.model_data.sd_model.is_sd1: Unprompted.shortcode_user_vars["sd_base"] = "sd1"
			except:
				pass

		if p.seed is not None and p.seed != -1.0:
			if (helpers.is_int(p.seed)): p.seed = int(p.seed)
			p.all_seeds[0] = p.seed
		else:
			p.seed = -1
			p.seed = fix_seed(p)

		# Legacy processing support
		if (Unprompted.Config.stable_diffusion.batch_count_method != "standard"):
			# Set up system var support - copy relevant p attributes into shortcode var object
			Unprompted.update_user_vars(p)

			Unprompted.shortcode_user_vars["prompt"] = Unprompted.start(apply_prompt_template(Unprompted.original_prompt, Unprompted.Config.templates.default))
			Unprompted.shortcode_user_vars["negative_prompt"] = Unprompted.start(apply_prompt_template(Unprompted.shortcode_user_vars["negative_prompt"] if "negative_prompt" in Unprompted.shortcode_user_vars else Unprompted.original_negative_prompt, Unprompted.Config.templates.default_negative))

			# Apply any updates to system vars
			Unprompted.update_stable_diffusion_vars(p)

			if (Unprompted.Config.stable_diffusion.batch_count_method == "safe"):
				Unprompted.log.warning("Engaging Safe batch_count processing mode per the config")

				for i, val in enumerate(p.all_prompts):
					if "single_seed" in Unprompted.shortcode_user_vars: p.all_seeds[i] = Unprompted.shortcode_user_vars["single_seed"]
					if (i == 0):
						Unprompted.shortcode_user_vars["batch_count_index"] = i
						p.all_prompts[0] = Unprompted.shortcode_user_vars["prompt"]
						p.all_negative_prompts[0] = Unprompted.shortcode_user_vars["negative_prompt"]
					else:
						for key in list(Unprompted.shortcode_user_vars):  # create a copy obj to avoid error during iteration
							if key not in Unprompted.shortcode_objects["remember"].globals:
								del Unprompted.shortcode_user_vars[key]

						Unprompted.shortcode_user_vars["batch_count_index"] = i
						p.all_prompts[i] = Unprompted.start(apply_prompt_template(p.unprompted_original_prompt, Unprompted.Config.templates.default))
						p.all_negative_prompts[i] = Unprompted.start(apply_prompt_template(Unprompted.shortcode_user_vars["negative_prompt"] if "negative_prompt" in Unprompted.shortcode_user_vars else p.unprompted_original_negative_prompt, Unprompted.Config.templates.default_negative))

					Unprompted.log.debug(f"Result {i}: {p.all_prompts[i]}")
			# Keep the same prompt between runs
			elif (Unprompted.Config.stable_diffusion.batch_count_method == "unify"):
				Unprompted.log.warning("Batch processing mode disabled per the config - all images will share the same prompt")

				for i, val in enumerate(p.all_prompts):
					p.all_prompts[i] = Unprompted.shortcode_user_vars["prompt"]
					p.all_negative_prompts[i] = Unprompted.shortcode_user_vars["negative_prompt"]

			# Cleanup routines
			Unprompted.log.debug("Entering Cleanup routine...")
			for i in Unprompted.cleanup_routines:
				Unprompted.shortcode_objects[i].cleanup()

			if unprompted_seed != -1: random.seed()
		# In standard mode, it is essential to evaluate the prompt here at least once to set up our Extra Networks correctly.
		else:
			# TODO: Think about ways of reducing code duplication between this and process_batch()

			Unprompted.update_user_vars(p)

			batch_size_index = 0
			while batch_size_index < p.batch_size:
				neg_now = Unprompted.shortcode_user_vars["negative_prompt"] if "negative_prompt" in Unprompted.shortcode_user_vars else Unprompted.original_negative_prompt
				prompt_result = Unprompted.start(apply_prompt_template(Unprompted.original_prompt, Unprompted.Config.templates.default))
				negative_prompt_result = Unprompted.start(apply_prompt_template(Unprompted.shortcode_user_vars["negative_prompt"] if "negative_prompt" in Unprompted.shortcode_user_vars and Unprompted.shortcode_user_vars["negative_prompt"] != neg_now else neg_now, Unprompted.Config.templates.default_negative))

				Unprompted.shortcode_user_vars["prompt"] = prompt_result
				Unprompted.shortcode_user_vars["negative_prompt"] = negative_prompt_result

				if "single_seed" in Unprompted.shortcode_user_vars and batch_size_index == 0:
					p.seed = Unprompted.shortcode_user_vars["single_seed"]
					p.all_seeds = [Unprompted.shortcode_user_vars["single_seed"]] * len(p.all_seeds)
					Unprompted.shortcode_user_vars["seed"] = Unprompted.shortcode_user_vars["single_seed"]
					Unprompted.shortcode_user_vars["all_seeds"] = [Unprompted.shortcode_user_vars["single_seed"]] * len(p.all_seeds)

				# Instantiate vars for batch processing
				if batch_size_index == 0:
					total_images = len(p.all_seeds)

					Unprompted.shortcode_user_vars["all_prompts"] = [prompt_result] * total_images
					Unprompted.shortcode_user_vars["all_negative_prompts"] = [negative_prompt_result] * total_images
					Unprompted.shortcode_user_vars["prompts"] = [prompt_result] * p.batch_size
					Unprompted.shortcode_user_vars["negative_prompts"] = [negative_prompt_result] * p.batch_size

				# Fill all prompts with the same value in unify mode
				if Unprompted.Config.stable_diffusion.batch_size_method == "unify":
					Unprompted.shortcode_user_vars["all_prompts"] = [prompt_result] * total_images
					Unprompted.shortcode_user_vars["all_negative_prompts"] = [negative_prompt_result] * total_images
				else:
					Unprompted.shortcode_user_vars["all_prompts"][batch_size_index] = prompt_result
					Unprompted.shortcode_user_vars["all_negative_prompts"][batch_size_index] = negative_prompt_result

					Unprompted.shortcode_user_vars["prompts"][batch_size_index] = prompt_result
					Unprompted.shortcode_user_vars["negative_prompts"][batch_size_index] = negative_prompt_result

				Unprompted.update_stable_diffusion_vars(p)
				batch_size_index += 1
				Unprompted.shortcode_user_vars["batch_size_index"] += 1
				Unprompted.shortcode_user_vars["batch_real_index"] += 1

				if Unprompted.fix_hires_prompts:
					Unprompted.log.debug("Synchronizing prompt vars with hr_prompt vars")
					p.hr_prompt = prompt_result
					p.hr_negative_prompt = negative_prompt_result
					p.all_hr_prompts = p.all_prompts
					p.all_negative_prompts = p.all_negative_prompts
					p.hr_prompts = p.prompts
					p.hr_negative_prompts = p.negative_prompts

	def process_batch(self, p, is_enabled=True, unprompted_seed=-1, match_main_seed=True, *args, **kwargs):
		if (is_enabled and Unprompted.is_enabled and Unprompted.Config.stable_diffusion.batch_count_method == "standard"):
			from modules.processing import extra_networks

			batch_count_index = Unprompted.shortcode_user_vars["batch_count_index"]

			Unprompted.log.debug(f"Starting process_batch() routine for batch_count_index #{batch_count_index}/{p.n_iter - 1}...")

			batch_size_index = 0
			while batch_size_index < p.batch_size:
				Unprompted.log.debug(f"Starting subroutine for batch_size_index #{batch_size_index}/{p.batch_size - 1}...")
				batch_real_index = batch_count_index * p.batch_size + batch_size_index

				Unprompted.log.debug(f"Current value of batch_real_index: {batch_real_index}")

				if batch_count_index > 0:
					try:
						Unprompted.log.debug("Attempting to deactivate extra networks...")
						if hasattr(p, "hasattr"): extra_networks.deactivate(p, p.extra_network_data)
					except Exception as e:
						Unprompted.log.exception("Exception while deactiating extra networks")

					for key in list(Unprompted.shortcode_user_vars):  # create a copy obj to avoid error during iteration
						if key not in Unprompted.shortcode_objects["remember"].globals:
							del Unprompted.shortcode_user_vars[key]

					# Update special vars
					Unprompted.shortcode_user_vars["batch_index"] = batch_count_index
					Unprompted.shortcode_user_vars["batch_count_index"] = batch_count_index
					Unprompted.shortcode_user_vars["batch_size_index"] = batch_size_index
					Unprompted.shortcode_user_vars["batch_real_index"] = batch_real_index

					Unprompted.update_user_vars(p)

					# Main string process
					neg_now = Unprompted.shortcode_user_vars["negative_prompt"] if "negative_prompt" in Unprompted.shortcode_user_vars else p.unprompted_original_negative_prompt
					prompt_result = Unprompted.start(apply_prompt_template(p.unprompted_original_prompt, Unprompted.Config.templates.default))
					negative_prompt_result = Unprompted.start(apply_prompt_template(Unprompted.shortcode_user_vars["negative_prompt"] if "negative_prompt" in Unprompted.shortcode_user_vars and Unprompted.shortcode_user_vars["negative_prompt"] != neg_now else neg_now, Unprompted.Config.templates.default_negative))
				# On the first image, we have already evaluted the prompt in the process() function
				else:
					Unprompted.log.debug("Inheriting prompt vars for batch_count_index 0 from process() routine")

					prompt_result = Unprompted.shortcode_user_vars["all_prompts"][batch_size_index]
					negative_prompt_result = Unprompted.shortcode_user_vars["all_negative_prompts"][batch_size_index]

					p.prompt = prompt_result
					p.negative_prompt = negative_prompt_result

				Unprompted.shortcode_user_vars["prompt"] = prompt_result
				Unprompted.shortcode_user_vars["negative_prompt"] = negative_prompt_result

				if batch_count_index > 0 and Unprompted.Config.stable_diffusion.batch_size_method == "standard":
					# Unprompted.shortcode_user_vars["prompts"][batch_real_index] = prompt_result
					# Unprompted.shortcode_user_vars["negative_prompts"][batch_real_index] = negative_prompt_result
					Unprompted.shortcode_user_vars["all_prompts"][batch_real_index] = prompt_result
					Unprompted.shortcode_user_vars["all_negative_prompts"][batch_real_index] = negative_prompt_result

				p.all_prompts = Unprompted.shortcode_user_vars["all_prompts"]
				p.all_negative_prompts = Unprompted.shortcode_user_vars["all_negative_prompts"]

				Unprompted.shortcode_user_vars["prompts"][batch_size_index] = prompt_result
				Unprompted.shortcode_user_vars["negative_prompts"][batch_size_index] = negative_prompt_result

				batch_size_index += 1

			if (batch_count_index > 0): Unprompted.update_stable_diffusion_vars(p)

			p.all_prompts[batch_real_index] = prompt_result
			p.all_negative_prompts[batch_real_index] = negative_prompt_result

			if Unprompted.fix_hires_prompts:
				Unprompted.log.debug("Synchronizing prompt vars with hr_prompt vars")
				p.hr_prompt = prompt_result
				p.hr_negative_prompt = negative_prompt_result
				p.all_hr_prompts = p.all_prompts
				p.all_negative_prompts = p.all_negative_prompts
				p.hr_prompts = p.prompts
				p.hr_negative_prompts = p.negative_prompts

			if (batch_count_index > 0):
				try:
					Unprompted.log.debug("Attempting to re-parse and re-activate extra networks...")
					_, p.extra_network_data = extra_networks.parse_prompts([prompt_result, negative_prompt_result])
					extra_networks.activate(p, p.extra_network_data)
				except Exception as e:
					Unprompted.log.exception("Exception while trying to activate extra networks")

			# Check for final iteration
			if (batch_real_index == len(p.all_seeds) - 1):
				Unprompted.cleanup()

				if unprompted_seed != -1:
					import random
					random.seed()
			else:
				Unprompted.log.debug("Proceeding to next batch_count batch")
				# Increment batch index
				batch_count_index += 1
				# Will retrieve this var with the next process_batch() routine
				Unprompted.shortcode_user_vars["batch_count_index"] = batch_count_index
				Unprompted.shortcode_user_vars["batch_index"] = batch_count_index  # TODO: this is for legacy support, remove eventually?

	# After routines
	def postprocess(self, p, processed, is_enabled=True, unprompted_seed=-1, match_main_seed=True):
		if not is_enabled or not Unprompted.is_enabled: return False

		if not self.allow_postprocess:
			Unprompted.log.debug("Bypassing After routine to avoid infinite loop.")
			self.allow_postprocess = True
			return False  # Prevents endless loop with some shortcodes

		self.allow_postprocess = False
		processed = Unprompted.after(p, processed)

		self.allow_postprocess = True

		return processed
