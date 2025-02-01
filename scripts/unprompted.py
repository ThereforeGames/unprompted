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
Unprompted.wizard_template_ids = []
Unprompted.wizard_template_kwargs = []
Unprompted.last_cached_images = []

# This is necessary for updating arbitrary wizard fields in the UI via function output event listeners.
Unprompted.all_wizard_objects = [[{}, {}] for _ in range(len(WizardModes))]

# Example of structure:
# Unprompted.all_wizard_objects[WizardModes.TEMPLATES][is_img2img][template/shortcode_name][block_name] = gradio object


def do_dry_run(string):
	Unprompted.log.debug(string)
	# Reset vars
	Unprompted.shortcode_user_vars = {}
	unp_result = Unprompted.start(string)
	Unprompted.cleanup()
	return f"<strong>RESULT:</strong> {unp_result}"


def wizard_select_item(option, is_img2img, mode=WizardModes.SHORTCODES):
	# Unprompted.log.debug(f"Selecting item `{option}` in mode `{mode}` for {'img2img' if is_img2img else 'txt2img'}")

	this_list = Unprompted.wizard_groups[mode][int(is_img2img)]

	# Retrieve corresponding template filepath
	try:
		if (mode == WizardModes.TEMPLATES):
			option = Unprompted.wizard_template_files[option]
	except Exception as e:
		Unprompted.log.debug("Unexpected wizard_select_item error")
		pass

	results = [gr.update(visible=(option == key)) for key in this_list.keys()]
	return results


def wizard_prep_destination(autoinclude_mode, order=0):
	prefix = ""
	affix = ""
	# Support variable encapsulation
	if autoinclude_mode != "prompt":
		if autoinclude_mode == "after":
			prefix = f"{Unprompted.Config.syntax.tag_start}after {order}{Unprompted.Config.syntax.tag_end}"
			affix = f"{Unprompted.Config.syntax.tag_start}{Unprompted.Config.syntax.tag_close}after{Unprompted.Config.syntax.tag_end}"
		else:
			prefix = f"{Unprompted.Config.syntax.tag_start}set {autoinclude_mode} _append{Unprompted.Config.syntax.tag_end}"
			affix = f"{Unprompted.Config.syntax.tag_start}{Unprompted.Config.syntax.tag_close}set{Unprompted.Config.syntax.tag_end}"
	return [prefix, affix]


# TODO: Deprecated
def wizard_skip_object(obj):
	block_name = obj.get_block_name()
	try:
		if not hasattr(obj, "value") or block_name == "label" or block_name == "markdown" or obj.value is None or obj.label is None or obj.value == "" or (obj.label != "Content" and Unprompted.Config.syntax.wizard_delimiter not in obj.label):
			return True
	except:
		Unprompted.log.exception(f"Error while parsing attributes of block `{block_name}`, skipping.")
		return True

	return False


def get_wizard_objects(mode, is_img2img):
	return [value for inner_dict in Unprompted.all_wizard_objects[mode][is_img2img].values() for value in inner_dict.values()]


def get_all_wizard_objects(operation=[False, True]):
	# Returns a complete list of wizard objects, including both modes and txt2img types
	results = []
	for mode in WizardModes:
		for is_img2img in operation:
			results += get_wizard_objects(mode, is_img2img)
	return results


# An absurd workaround for the way Gradio handles event listeners
# TODO: If anyone knows a cleaner way to do this, please open a PR! x.x
def wizard_parse_gradio_inputs(tabs, is_img2img, option, remove_special, values):

	# Check if values is a dict, or contains a dict
	if type(values) == dict:
		return values
	elif type(values) == tuple and type(values[0]) == dict:
		return values[0]

	idx_start = 0
	idx_end = 0

	if type(tabs) != list:
		tabs = [tabs]

	for tab in tabs:
		for idx, key in enumerate(Unprompted.all_wizard_objects[tab][is_img2img]):
			# Get the length of this dictionary
			this_length = len(Unprompted.all_wizard_objects[tab][is_img2img][key])

			if key == option:
				idx_end = idx_start + this_length
				break
			else:
				idx_start += this_length

		if idx_end > 0:
			break

	# Filter the objects to the current shortcode
	values = values[idx_start:idx_end]

	# Create a new dict with the values
	result = {}
	for idx, key in enumerate(Unprompted.all_wizard_objects[tab][is_img2img][option]):
		if values[idx] != None and values[idx] != "":
			result[key] = values[idx]

	# Remove special entries that are only used with workflows
	# this includes _enable, _order, and _destination
	if remove_special:
		keys_to_remove = ["_enable", "_order", "_destination"]
		for key in keys_to_remove:
			result.pop(key, None)

	return result


def wizard_generate_template(option, is_img2img, html_safe=True, prepend="", append="", style="calls", *values):
	parsed_items = wizard_parse_gradio_inputs(WizardModes.TEMPLATES, is_img2img, Unprompted.wizard_template_ids[option], True, values)

	filepath = os.path.relpath(Unprompted.wizard_template_files[option], f"{base_dir}/{Unprompted.Config.template_directory}")

	# Remove file extension
	filepath = os.path.splitext(filepath)[0]

	if style == "calls":
		result = f"{Unprompted.Config.syntax.tag_start}call \"{filepath}\""
	else:
		result = {}

	for key in parsed_items:
		try:
			if type(parsed_items[key]) == list:
				# Check if this is a Gradio file list
				if all([hasattr(e, "name") for e in parsed_items[key]]):
					this_val = f"{Unprompted.Config.syntax.delimiter}".join([e.name for e in parsed_items[key]])
				else:
					this_val = f"{Unprompted.Config.syntax.delimiter}".join([str(e) for e in parsed_items[key]])
			else:
				this_val = parsed_items[key]

			if style == "calls":
				this_val = str(helpers.autocast(this_val)).replace("\"", "\'")
				if html_safe:
					this_val = html.escape(this_val, quote=False)
				this_val = Unprompted.make_alt_tags(this_val)

				#if " " in this_val:
				this_val = f"\"{this_val}\""  # Enclose in quotes if necessary
				result += f" {key}={this_val}"
			elif style == "json":
				result[key] = this_val
		except:
			Unprompted.log.exception(f"Error while parsing argument {key} for template `{option}`")
			pass

	if style == "calls":
		for kwarg in Unprompted.wizard_template_kwargs[option]:
			if kwarg == "name":
				this_kwarg = "template_name"
			else:
				this_kwarg = kwarg
			result += f" {this_kwarg}='{Unprompted.wizard_template_kwargs[option][kwarg]}'"

		# Closing bracket
		result += Unprompted.Config.syntax.tag_end

		return (prepend + result + append)
	elif style == "json":
		# Create new JSON object with the template name and arguments
		# template_obj = {Unprompted.wizard_template_kwargs[option]["name"]: result}
		return result


def wizard_generate_shortcode(option, is_img2img, html_safe=True, prepend="", append="", style="calls", *values):
	parsed_items = wizard_parse_gradio_inputs(WizardModes.SHORTCODES, is_img2img, option, True, values)

	if style == "calls":
		if hasattr(Unprompted.shortcode_objects[option], "wizard_prepend"):
			result = Unprompted.shortcode_objects[option].wizard_prepend
		else:
			result = Unprompted.Config.syntax.tag_start + option
	elif style == "json":
		result = {}

	block_content = ""

	for key in parsed_items:
		if type(parsed_items[key]) == list:
			# Check if this is a Gradio file list
			if all([hasattr(e, "name") for e in parsed_items[key]]):
				this_val = f"{Unprompted.Config.syntax.delimiter}".join([e.name for e in parsed_items[key]])
			else:
				this_val = f"{Unprompted.Config.syntax.delimiter}".join([str(e) for e in parsed_items[key]])
		else:
			this_val = parsed_items[key]

		if key == "content":
			block_content = this_val
			continue
		# TODO: Check if this is still being used
		elif key == "prompt":
			continue

		if style == "calls":
			if key.startswith("arg_str"):
				result += " \"" + str(this_val) + "\""
			elif key.startswith("arg_int"):
				result += " " + str(int(this_val))
			elif key.startswith("arg_verbatim"):
				result += " " + str(this_val)
			elif type(this_val) == bool:
				if this_val:
					result += " " + key
			elif type(this_val) == str:
				if len(this_val) > 0:
					if html_safe:
						this_val = html.escape(this_val, quote=False)
					result += f" {key}=\"{this_val}\""
			else:
				result += f" {key}={helpers.autocast(this_val)}"
		elif style == "json":
			result[key] = this_val

	if style == "calls":
		# Closing bracket
		if hasattr(Unprompted.shortcode_objects[option], "wizard_append"):
			result += Unprompted.shortcode_objects[option].wizard_append
		else:
			result += Unprompted.Config.syntax.tag_end

		if hasattr(Unprompted.shortcode_objects[option], "run_block"):
			if (append and not block_content):
				block_content = append
				append = ""
				prepend = ""
			result += block_content + Unprompted.Config.syntax.tag_start + Unprompted.Config.syntax.tag_close + option + Unprompted.Config.syntax.tag_end

		return (prepend + result + append)
	elif style == "json":
		result["content"] = block_content
		return result


def wizard_generate_capture(include_inference, include_prompt, include_neg_prompt, include_model, include_template_block):
	try:
		if Unprompted.main_p:
			result = f"<strong>RESULT:</strong> "
			prompt = ""
			neg_prompt = ""

			if include_template_block:
				result += f"{Unprompted.Config.syntax.tag_start}template name='Untitled'{Unprompted.Config.syntax.tag_end}"

			if include_inference != "none" or include_model:
				result += f"{Unprompted.Config.syntax.tag_start}sets"
				if include_model:
					result += f" sd_model='{opts.data['sd_model_checkpoint']}'"

			for att in dir(Unprompted.main_p):
				if not att.startswith("__"):
					att_val = getattr(Unprompted.main_p, att)
					if (att.startswith("unprompted_")):
						continue  # Skip special extension attributes
					elif att == "prompt":
						if include_prompt == "postprocessed":
							prompt = att_val
						else:
							prompt = Unprompted.original_prompt
					elif att == "negative_prompt":
						if include_neg_prompt == "postprocessed":
							neg_prompt = att_val
						else:
							neg_prompt = Unprompted.original_negative_prompt
					elif include_inference != "none":
						if (isinstance(att_val, int) or isinstance(att_val, float) or isinstance(att_val, str)):
							prefix = f" {att}="

							if isinstance(att_val, str):
								if (len(att_val) > 0 or include_inference == "verbose"):
									result += f"{prefix}'{att_val}'"
							else:
								if isinstance(att_val, bool):
									att_val = int(att_val == True)  # convert bool to 0 or 1
								if att_val == 0 and include_inference != "verbose":
									continue
								elif (att_val == float("inf") or att_val == float("-inf")) and include_inference != "verbose":
									continue
								result += f"{prefix}{html.escape(str(att_val))}"

			if include_inference != "none" or include_model:
				result += f"{Unprompted.Config.syntax.tag_end}"
			if include_prompt != "none":
				result += prompt
			if include_neg_prompt != "none" and len(neg_prompt) > 0:
				result += f"{Unprompted.Config.syntax.tag_start}set negative_prompt{Unprompted.Config.syntax.tag_end}{neg_prompt}{Unprompted.Config.syntax.tag_start}{Unprompted.Config.syntax.tag_close}set{Unprompted.Config.syntax.tag_end}"

		else:
			result = "<strong>ERROR:</strong> Could not detect your inference settings. Try generating an image first."
	except Exception as e:
		Unprompted.log.exception("Exception caught during Wizard Capture generation")
		result = f"<strong>ERROR:</strong> {e}"

	return result


def wizard_generate_autoinclude(style, tab, autoinclude_mode, idx, key, order, is_img2img, p, values):
	prompt = ""
	prefix = ""
	affix = ""

	if style == "calls":
		if autoinclude_mode == "negative_prompt":
			prompt = Unprompted.original_negative_prompt
		else:
			# if autoinclude_mode == "prompt":
			# 	prompt = Unprompted.original_prompt
			strings = wizard_prep_destination(autoinclude_mode, order)
			prefix = strings[0]
			affix = strings[1]

	if tab == WizardModes.SHORTCODES:
		fn = wizard_generate_shortcode
		option = key
	else:
		fn = wizard_generate_template
		option = idx

	if Unprompted.Config.ui.wizard_prepends:
		new_prompt = fn(option, is_img2img, False, prefix, prompt + affix, style, values)
	else:
		new_prompt = fn(option, is_img2img, False, prefix + prompt, affix, style, values)

	if style == "calls":
		Unprompted.log.debug("Auto-include result: " + new_prompt)

		if autoinclude_mode == "negative_prompt":
			Unprompted.original_negative_prompt = new_prompt
			p.all_negative_prompts[0] = Unprompted.original_negative_prompt
			p.original_negative_prompt = Unprompted.original_negative_prompt
		else:
			Unprompted.original_prompt += new_prompt
			p.all_prompts[0] = Unprompted.original_prompt
			p.unprompted_original_prompt = Unprompted.original_prompt
	elif style == "json":
		new_prompt["_order"] = int(order)
		new_prompt["_destination"] = autoinclude_mode

	return new_prompt


def wizard_process_autoincludes(style, is_img2img, p, values):
	autoinclude_data = []
	results = {}

	for tab in range(len(WizardModes)):
		groups = Unprompted.wizard_groups[tab][int(is_img2img)]
		for idx, key in enumerate(groups):
			if tab == WizardModes.TEMPLATES:
				this_key = Unprompted.wizard_template_ids[idx]
			else:
				this_key = key
			parsed_items = wizard_parse_gradio_inputs([mode.value for mode in WizardModes], is_img2img, this_key, False, values)

			# if (autoinclude_obj.value):
			if (parsed_items["_enable"]):
				autoinclude_data.append({"tab": tab, "mode": parsed_items["_destination"], "order": parsed_items["_order"], "idx": idx, "key": key, "dict": parsed_items})

	# Sort the autoinclude data by order
	autoinclude_data.sort(key=lambda x: x["order"])

	# Execute wizard_generate_autoinclude() in order
	for data in autoinclude_data:
		if style == "calls":
			Unprompted.log.debug(f"Auto-including `{data['key']}` in `{data['mode']}` at order {int(data['order'])}")
		result = wizard_generate_autoinclude(style, data["tab"], data["mode"], data["idx"], data["key"], data["order"], is_img2img, p, data["dict"])
		if style == "json":
			key = Unprompted.wizard_template_ids[data["idx"]] if data["tab"] == WizardModes.TEMPLATES else data["key"]
			if WizardModes(data["tab"]).name not in results:
				results[WizardModes(data["tab"]).name] = {}
			results[WizardModes(data["tab"]).name][key] = result

	if style == "json":
		return results


def get_local_file_dir(filename=None):
	# unp_dir = os.path.basename(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

	if filename:
		filepath = "/" + str(Path(os.path.relpath(filename, f"{base_dir}")).parent)
	else:
		filepath = ""

	return (f"file/{unprompted_dir}{filepath}")


def get_markdown(file):
	file = Path(base_dir) / file
	lines = file.open(mode='r', encoding='utf-8').readlines()
	final_string = ""
	for line in lines:
		# Skip h1 elements
		if not line.startswith("# "):
			final_string += line
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

					skip_gen = gr.Checkbox(label="Skip gen, use last image(s)", value=False)
					setattr(match_main_seed, "do_not_save_to_config", True)

				unprompted_seed = gr.Number(label="Unprompted Seed", value=-1)
				setattr(unprompted_seed, "do_not_save_to_config", True)

				if (os.path.exists(f"{base_dir}/{Unprompted.Config.template_directory}/pro/beautiful_soul_v0.1.0/main{Unprompted.Config.formats.txt}")):
					is_open = False
				else:
					is_open = True

				promos = []
				promos.append(f'<a href="https://payhip.com/b/L1uNF" target="_blank"><img src="{get_local_file_dir()}/images/promo_box_beautiful_soul.png" class="thumbnail"></a><h1><strong>Beautiful Soul</strong>: Bring your characters to life.</h1><p>A highly expressive character generator for the A1111 WebUI. With thousands of wildcards and direct ControlNet integration, this is by far our most powerful Unprompted template to date.</p><a href="https://payhip.com/b/L1uNF" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View premium assets for Unprompted">Download Now ➜</button></a>')
				promos.append(f'<a href="https://payhip.com/b/qLUX9" target="_blank"><img src="{get_local_file_dir()}/images/promo_box_demoncrawl_avatar_generator.png" class="thumbnail"></a><h1>The <strong>DemonCrawl</strong> Pixel Art Avatar Generator</h1><p>Create pixel art portraits in the style of the popular roguelite, <a href="https://demoncrawl.com" _target=blank>DemonCrawl</a>. Includes a custom Stable Diffusion model trained by the game\'s developer, as well as a custom GUI and the ability to randomize your prompts.</p><a href="https://payhip.com/b/qLUX9" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View premium assets for Unprompted">Download Now ➜</button></a>')
				promos.append(f'<a href="https://payhip.com/b/hdgNR" target="_blank"><img src="{get_local_file_dir()}/images/promo_box_fantasy.png" class="thumbnail"></a><h1>Create beautiful art for your <strong>Fantasy Card Game</strong></h1><p>Generate a wide variety of creatures and characters in the style of a fantasy card game. Perfect for heroes, animals, monsters, and even crazy hybrids.</p><a href="https://payhip.com/b/hdgNR" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View premium assets for Unprompted">Download Now ➜</button></a>')
				promos.append(f'<a href="https://github.com/ThereforeGames/unprompted" target="_blank"><img src="{get_local_file_dir()}/images/promo_github_star.png" class="thumbnail"></a><h1>Give Unprompted a <strong>star</strong> for visibility</h1><p>Most WebUI users have never heard of Unprompted. You can help more people discover it by giving the repo a ⭐ on Github. Thank you for your support!</p><a href="https://github.com/ThereforeGames/unprompted" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View the Unprompted repo">Visit Github ➜</button></a>')
				promos.append(f'<a href="https://github.com/sponsors/ThereforeGames" target="_blank"><img src="{get_local_file_dir()}/images/promo_github_sponsor.png" class="thumbnail"></a><h1>Sponsor Unprompted on GitHub</h1><p>Support the development of free, open-source software! Perks now available at different sponsorship tiers. All contributions are greatly appreciated - no matter how big or small. </p><a href="https://github.com/sponsors/ThereforeGames" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View the Unprompted repo">Visit Github ➜</button></a>')
				promos.append(f'<a href="https://github.com/sponsors/ThereforeGames" target="_blank"><img src="{get_local_file_dir()}/images/promo_bundle.png" class="thumbnail"></a><h1>New! Premium Template Bundle and Early Access</h1><p>Subscribe on GitHub to receive ALL of our premium templates, access to beta versions of Unprompted, and the supporters-only discussion board.</p><a href="https://github.com/sponsors/ThereforeGames" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View the Unprompted repo">Visit Github ➜</button></a>')
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
								_multiselect = True if "_multiselect" in pargs else False
								_show_label = bool(int(kwargs["_show_label"])) if "_show_label" in kwargs else True

								this_label = f"{friendly_name} {Unprompted.Config.syntax.wizard_delimiter} {pargs[0]}"

								# Produce UI based on type
								if (block_name == "textbox"):
									if "_placeholder" in kwargs:
										this_placeholder = kwargs["_placeholder"]
									else:
										this_placeholder = str(content)
									obj = gr.Textbox(label=this_label, lines=int(kwargs["_lines"]) if "_lines" in kwargs else 1, max_lines=int(kwargs["_max_lines"]) if "_max_lines" in kwargs else 1, placeholder=this_placeholder, info=_info, show_label=_show_label)
								elif (block_name == "checkbox"):
									obj = gr.Checkbox(label=this_label, value=bool(int(content)), info=_info, show_label=_show_label)
								elif (block_name == "number"):
									obj = gr.Number(label=this_label, value=int(content), interactive=True, info=_info, minimum=float(kwargs["_minimum"]) if "_minimum" in kwargs else None, maximum=float(kwargs["_maximum"]) if "_maximum" in kwargs else None, show_label=_show_label)
								elif (block_name == "dropdown"):
									_choices = Unprompted.parse_advanced(kwargs["_choices"], "wizard").split(Unprompted.Config.syntax.delimiter)
									_allow_custom_value = True if "_allow_custom_value" in pargs else False
									obj = gr.Dropdown(label=this_label, value=content, choices=_choices, info=_info, multiselect=_multiselect, show_label=_show_label, allow_custom_value=_allow_custom_value)
								elif (block_name == "radio"):
									obj = gr.Radio(label=this_label, choices=kwargs["_choices"].split(Unprompted.Config.syntax.delimiter), interactive=True, value=content, show_label=_show_label)
								elif (block_name == "slider"):
									obj = gr.Slider(label=this_label, value=float(content), minimum=float(kwargs["_minimum"]) if "_minimum" in kwargs else 1, maximum=float(kwargs["_maximum"]) if "_maximum" in kwargs else 10, step=kwargs["_step"] if "_step" in kwargs else 1, info=_info, show_label=_show_label)
								elif (block_name == "image"):
									if len(content) < 1:
										content = None
									obj = gr.Image(label=this_label, value=content, type="filepath", interactive=True, info=_info, show_label=_show_label, sources=["upload", "webcam"])
								elif (block_name == "file"):
									if len(content) < 1:
										content = None
									file_types = helpers.ensure(kwargs["_file_types"].split(Unprompted.Config.syntax.delimiter), list) if "_file_types" in kwargs else None

									obj = gr.File(label=this_label, type="file", value=content, interactive=True, info=_info, show_label=_show_label, file_count=kwargs["_file_count"] if "_file_count" in kwargs else "single", file_types=file_types)

								setattr(obj, "do_not_save_to_config", True)

								wiz_dict = Unprompted.all_wizard_objects[WizardModes.TEMPLATES][int(is_img2img)]
								if self.dropdown_item_id not in wiz_dict:
									wiz_dict[self.dropdown_item_id] = {}
								wiz_dict[self.dropdown_item_id][pargs[0]] = obj
							return ("")

						wizard_shortcode_parser.register(handler, "set", f"{Unprompted.Config.syntax.tag_close}set")

						def handler(keyword, pargs, kwargs, context):
							if "name" in kwargs:
								self.dropdown_item_name = kwargs["name"]
							if "id" in kwargs:
								self.dropdown_item_id = kwargs["id"]
							else:
								self.dropdown_item_id = self.dropdown_item_name
							if "destination" in kwargs:
								self.dropdown_item_destination = kwargs["destination"]
							if "order" in kwargs:
								self.dropdown_item_order = kwargs["order"]
							gr.Label(label="Options", value=f"{self.dropdown_item_name}", show_label=False)

							if "banner" in kwargs:
								banner_path = f"file/{unprompted_dir}/{kwargs['banner']}"
								# Include banner of the same name, if it exists
							else:
								banner_path = f"{os.path.splitext(self.dropdown_item_filepath)[0]}.png"

							if os.path.exists(banner_path):
								img = gr.Image(value=banner_path, elem_classes=["wizard-banner"], type="filepath", interactive=False, container=False, show_download_button=False)
								setattr(img, "do_not_save_to_config", True)
							self.wizard_template_kwargs = kwargs
							return ""

						wizard_shortcode_parser.register(handler, "template")

						def handler(keyword, pargs, kwargs, context, content):
							parse = True

							if pargs[0] == "accordion":
								block = gr.Accordion(kwargs["_label"] if "_label" in kwargs else "More", open=True if "_open" in pargs else False)
							elif pargs[0] == "row":
								block = gr.Row(equal_height=pargs["_equal_height"] if "_equal_height" in pargs else False)
							elif pargs[0] == "column":
								block = gr.Column(scale=int(pargs["_scale"]) if "_scale" in pargs else 1)
							elif pargs[0] == "tab":
								block = gr.Tab(label=kwargs["_label"] if "_label" in kwargs else "Tab")
							elif pargs[0] == "markdown":
								parse = False
								content = content.replace("\\r\\n", "<br>").replace("\t", "") + "<br><br>"
								if "_file" in kwargs:
									file = helpers.str_with_ext(os.path.dirname(self.dropdown_item_filepath) + "/" + kwargs["_file"], ".md")
									this_encoding = Unprompted.parse_advanced(kwargs["_encoding"], context) if "_encoding" in kwargs else "utf-8"

									if not os.path.exists(file):
										if "_suppress_errors" not in pargs:
											Unprompted.log.error(f"File does not exist: {file}")
										extra_content = ""
									else:
										with open(file, "r", encoding=this_encoding) as f:
											extra_content = f.read()
										f.close()

									content = extra_content + content
								block = gr.Markdown(value=content)

							setattr(block, "do_not_save_to_config", True)

							if parse:
								with block:
									wizard_shortcode_parser.parse(content)

							return ("")

						def preprocess(keyword, pargs, kwargs, context):
							return True

						wizard_shortcode_parser.register(handler, "wizard", f"{Unprompted.Config.syntax.tag_close}wizard", preprocess)

						def handler(keyword, pargs, kwargs, context):
							if self.dropdown_item_name:
								return get_local_file_dir(self.dropdown_item_name)
							return get_local_file_dir()

						wizard_shortcode_parser.register(handler, "base_dir")

						with gr.Tabs():

							self.filtered_templates = Unprompted.wizard_groups[WizardModes.TEMPLATES][int(is_img2img)]
							self.filtered_shortcodes = Unprompted.wizard_groups[WizardModes.SHORTCODES][int(is_img2img)]

							def wizard_populate_templates(region, first_load=False):
								import glob

								self.filtered_templates = Unprompted.wizard_groups[WizardModes.TEMPLATES][int(is_img2img)]

								def wizard_add_template(show_me=False):
									self.dropdown_item_name = filename  # This will be overwritten by the shortcode parser
									self.dropdown_item_id = filename
									self.dropdown_item_filepath = filename
									self.dropdown_item_destination = "prompt"
									self.dropdown_item_order = 1

									with gr.Group(visible=show_me) as self.filtered_templates[filename]:
										# Render the text file's UI with special parser object
										wizard_shortcode_parser.parse(file.read())
										wiz_dict = Unprompted.all_wizard_objects[WizardModes.TEMPLATES][int(is_img2img)]
										if self.dropdown_item_id not in wiz_dict:
											wiz_dict[self.dropdown_item_id] = {}

										# Auto-include is always the last element
										with gr.Row(equal_height=True, elem_classes=["wizard-autoinclude-row"], variant="panel"):
											obj = gr.Checkbox(label=f"🪄 Auto-include {self.dropdown_item_name} in:", value=hasattr(Unprompted.Config.ui.wizard_template_autoincludes, self.dropdown_item_name), elem_classes=["wizard-autoinclude", mode_string], scale=8)
											destination = gr.Dropdown(value=self.dropdown_item_destination, choices=["prompt", "negative_prompt", "after", "your_var"], allow_custom_value=True, elem_classes=["autoinclude-mode"], show_label=False, scale=4)
											order = gr.Number(show_label=False, value=self.dropdown_item_order, minimum=1, elem_classes=["autoinclude-order"], scale=3, min_width=1)
											setattr(obj, "do_not_save_to_config", True)

											wiz_dict[self.dropdown_item_id]["_enable"] = obj
											wiz_dict[self.dropdown_item_id]["_destination"] = destination
											wiz_dict[self.dropdown_item_id]["_order"] = order

									Unprompted.log.debug(f"Added {'img2img' if is_img2img else 'txt2img'} Wizard Template: {self.dropdown_item_name}")

								txt_files = glob.glob(f"{base_dir}/{Unprompted.Config.template_directory}/**/*.txt", recursive=True) if (not is_img2img) else Unprompted.wizard_template_files
								is_first = True

								with region:
									for filename in txt_files:

										with open(filename, encoding=Unprompted.Config.formats.default_encoding) as file:
											if is_img2img and first_load:
												wizard_add_template()
											else:
												first_line = file.readline()
												# Make sure this text file starts with the [template] tag - this identifies it as a valid template
												if first_line.startswith(f"{Unprompted.Config.syntax.tag_start}template"):
													file.seek(0)  # Go back to start of file

													wizard_add_template(is_first)

													Unprompted.wizard_template_names.append(self.dropdown_item_name)
													Unprompted.wizard_template_files.append(filename)
													Unprompted.wizard_template_ids.append(self.dropdown_item_id)
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
												Unprompted.all_wizard_objects[WizardModes.SHORTCODES][int(is_img2img)][key] = {}

												gr.Label(label="Options", value=f"[{key}]", show_label=False)

												if hasattr(Unprompted.shortcode_objects[key], "description"):
													with gr.Tab("About"):
														gr.Markdown(value=Unprompted.shortcode_objects[key].description)
												# Check if shortcode object has a documentation variable
												shortcode_docs = None
												if hasattr(Unprompted.shortcode_objects[key], "documentation"):
													shortcode_docs = Unprompted.shortcode_objects[key].documentation
												elif os.path.exists(f"{base_dir}/docs/shortcodes/{key}.md"):
													shortcode_docs = get_markdown(f"docs/shortcodes/{key}.md")
												if shortcode_docs:
													with gr.Tab("Documentation"):
														gr.Markdown(value=shortcode_docs)

												if hasattr(Unprompted.shortcode_objects[key], "run_block"):
													obj = gr.Textbox(label="Content", max_lines=2, min_lines=2)
													Unprompted.all_wizard_objects[WizardModes.SHORTCODES][int(is_img2img)][key]["content"] = obj
												# Run the shortcode's UI template to populate
												ui_objects = Unprompted.shortcode_objects[key].ui(gr)
												if ui_objects:
													for ui in ui_objects:
														this_label = ui.label.split(" ")[-1]
														Unprompted.all_wizard_objects[WizardModes.SHORTCODES][int(is_img2img)][key][this_label] = ui

												# Auto-include is always the last element
												with gr.Row(equal_height=True, elem_classes=["wizard-autoinclude-row"], variant="panel"):
													obj = gr.Checkbox(label=f"🪄 Auto-include [{key}] in:", value=hasattr(Unprompted.Config.ui.wizard_shortcode_autoincludes, key), elem_classes=["wizard-autoinclude", mode_string], scale=8)
													destination = Unprompted.shortcode_objects[key].destination if hasattr(Unprompted.shortcode_objects[key], "destination") else "prompt"
													destination_obj = gr.Dropdown(value=destination, choices=["prompt", "negative_prompt", "after", "your_var"], allow_custom_value=True, scale=4, elem_classes=["autoinclude-mode"], show_label=False)
													order = int(Unprompted.shortcode_objects[key].order) if hasattr(Unprompted.shortcode_objects[key], "order") else 1
													order_obj = gr.Number(show_label=False, value=order, minimum=1, elem_classes=["autoinclude-order"], scale=2, min_width=1)
													setattr(obj, "do_not_save_to_config", True)

													Unprompted.all_wizard_objects[WizardModes.SHORTCODES][int(is_img2img)][key]["_enable"] = obj
													Unprompted.all_wizard_objects[WizardModes.SHORTCODES][int(is_img2img)][key]["_destination"] = destination_obj
													Unprompted.all_wizard_objects[WizardModes.SHORTCODES][int(is_img2img)][key]["_order"] = order_obj

									self.shortcodes_dropdown[int(is_img2img)].change(fn=wizard_select_item, inputs=[self.shortcodes_dropdown[int(is_img2img)], gr.Variable(value=is_img2img)], outputs=list(self.filtered_shortcodes.values()))

								return gr.Dropdown.update(choices=list(Unprompted.shortcode_objects.keys()))

							def wizard_refresh_templates():
								Unprompted.log.debug("Refreshing the Wizard Templates...")
								Unprompted.log.warning("Sorry, Gradio is presently incapable of dynamically creating UI elements. You must restart the WebUI to update Wizard templates. This is expected to change in a future release: https://github.com/gradio-app/gradio/issues/4689")
								return ""
								if Unprompted.Config.ui.wizard_templates:
									Unprompted.wizard_template_names.clear()
									Unpromtped.wizard_template_ids.clear()
									Unprompted.wizard_template_files.clear()
									Unprompted.wizard_template_kwargs.clear()
									return wizard_populate_templates(self.templates_region[int(is_img2img)])
								return ""

							def wizard_refresh_shortcodes():
								Unprompted.log.debug("Refreshing the Wizard Shortcodes...")
								return wizard_populate_shortcodes(self.shortcodes_region[int(is_img2img)])

							if Unprompted.Config.ui.wizard_templates:
								with gr.Tab("Templates", elem_id="wizard-templates"):
									with gr.Row():
										self.templates_dropdown[int(is_img2img)] = gr.Dropdown(choices=[], label="Select template:", elem_id="wizard-dropdown", type="index", info="These are your GUI templates - you can think of them like custom scripts, except you can run an unlimited number of them at the same time.", value="Example Template")
										templates_refresh = ToolButton(value='\U0001f504', elem_id=f"templates-refresh")
										templates_refresh.click(fn=wizard_refresh_templates)  # , outputs=self.templates_dropdown[int(is_img2img)]
										ToolButton(value="🗑️", elem_id=f"templates-clear", tooltip="Clear all template auto-includes")

									self.templates_region[int(is_img2img)] = gr.Blocks()
									wizard_populate_templates(self.templates_region[int(is_img2img)], True)

									self.templates_dropdown[int(is_img2img)].choices = Unprompted.wizard_template_names

									wizard_template_btn = gr.Button(value="🧠 Generate Shortcode")

							if Unprompted.Config.ui.wizard_shortcodes:
								with gr.Tab("Shortcodes", elem_id="wizard-shortcodes"):
									shortcode_list = list(Unprompted.shortcode_objects.keys())
									with gr.Row():
										self.shortcodes_dropdown[int(is_img2img)] = gr.Dropdown(choices=shortcode_list, elem_id="wizard-dropdown", label="Select shortcode:", value=Unprompted.Config.ui.wizard_default_shortcode, info="GUI for setting up any shortcode in Unprompted. More engaging than reading the manual!")
										shortcodes_refresh = ToolButton(value='\U0001f504', elemn_id=f"shortcodes-refresh", tooltip="Refresh shortcode list (NOTE: Currently non-functional due to Gradio limitations.)")
										shortcodes_refresh.click(fn=wizard_refresh_shortcodes)  # , outputs=self.shortcodes_dropdown[int(is_img2img)]
										ToolButton(value="🗑️", elem_id=f"shortcodes-clear", tooltip="Clear all shortcode auto-includes")

									self.shortcodes_region[int(is_img2img)] = gr.Blocks()
									wizard_populate_shortcodes(self.shortcodes_region[int(is_img2img)], True)

									wizard_shortcode_btn = gr.Button(value="🧠 Generate Shortcode")

							if Unprompted.Config.ui.wizard_workflows:

								def wizard_save_workflow(is_img2img, original_filename, overwrite_existing_workflow, *values):
									import json, time

									start_time = time.time()
									file_affix = 1
									filename = original_filename
									if not overwrite_existing_workflow:
										while os.path.exists(f"{base_dir}/{Unprompted.Config.subdirectories.workflows}/{filename}.json"):
											filename = f"{original_filename}_{file_affix}"
											file_affix += 1

									json_obj = wizard_process_autoincludes("json", is_img2img, None, values)
									with open(f"{base_dir}/{Unprompted.Config.subdirectories.workflows}/{filename}.json", "w") as f:
										json.dump(json_obj, f, indent="\t")

									return f"<br><br>**Done!** Workflow `{filename}` saved in {round(time.time()-start_time,4)} seconds.<hr>"

								def wizard_delete_workflow(workflow_name):
									import os

									try:
										os.remove(f"{base_dir}/{Unprompted.Config.subdirectories.workflows}/{workflow_name}.json")
										return f"<br><br>**Done!** Workflow `{workflow_name}` deleted.<hr>"
									except FileNotFoundError:
										return f"<br><br>**Error:** Workflow `{workflow_name}` not found.<hr>"

								def wizard_load_workflow(is_img2img, workflow_name):
									import json, time

									start_time = time.time()

									with open(f"{base_dir}/{Unprompted.Config.subdirectories.workflows}/{workflow_name}.json", "r") as f:
										json_obj = json.load(f)

									changes = {}

									for tab in ["TEMPLATES", "SHORTCODES"]:
										wiz_dict = Unprompted.all_wizard_objects[WizardModes[tab]][int(is_img2img)]

										# Disable all auto-includes first
										for item in wiz_dict:
											if "_enable" in wiz_dict[item]:
												changes[wiz_dict[item]["_enable"]] = False

										if tab in json_obj:
											for item in json_obj[tab]:
												# Propagate the workflow's values into the UI
												if item in wiz_dict:
													ui_obj = wiz_dict[item]
													for subitem in json_obj[tab][item]:
														if subitem in ui_obj:
															Unprompted.log.debug(f"Workflow: Updating {item} - {subitem} to {json_obj[tab][item][subitem]}")
															changes[ui_obj[subitem]] = json_obj[tab][item][subitem]

													# Enable the auto-include checkbox
													changes[ui_obj["_enable"]] = True

									# Re-render the self.templates_region and self.shortcodes_region blocks
									changes[workflow_result] = f"<br><br>**Done!** Workflow `{workflow_name}` loaded in {round(time.time()-start_time,4)} seconds.<hr>"

									return changes

								def wizard_refresh_workflows(initial=False):
									import glob
									start_dir = base_dir + "/" + Unprompted.Config.subdirectories.workflows
									all_workflows = glob.glob(start_dir + "/**/*.json", recursive=True)
									# Get just the name and any subdirectories, no extension
									all_workflows = [os.path.splitext(os.path.relpath(x, start_dir))[0].replace("\\", "/") for x in all_workflows]

									if initial:
										return all_workflows
									return gr.Dropdown.update(choices=all_workflows)

								with gr.Tab("Workflows"):
									with gr.Row():
										workflows_dropdown = gr.Dropdown(elem_id="workflow-name", choices=wizard_refresh_workflows(True), label="Select workflow:", info="Workflows are a way to automate your Unprompted process. You can chain together templates and shortcodes to create a sequence of events that run automatically. This is useful for batch processing, complex image generation, or other tasks that require multiple steps.", allow_custom_value=True)
										save_workflow = ToolButton(value="💾", elem_id=f"workflows-save", tooltip="Save current workflow")
										load_workflow = ToolButton(value="📂", elem_id=f"workflows-load", tooltip="Load selected workflow")
										refresh_workflows = ToolButton(value="🔄️", elemn_id=f"workflow-refresh", tooltip="Refresh workflows")
										delete_workflow = ToolButton(value="🗑️", elem_id=f"workflows-clear", tooltip="Delete selected workflow")

									overwrite_existing_workflow = gr.Checkbox(label="Overwrite existing files on save?", value=False)

									workflow_result = gr.Markdown(value="<br><br><hr>", elem_classes=["workflow-result"])

									with gr.Accordion("Current workflow outline (TBA)"):
										workflow_outline = gr.Markdown(value="Feature coming soon.")

									all_wiz_obj = get_all_wizard_objects([is_img2img])

									save_workflow.click(fn=wizard_save_workflow, inputs=[gr.Variable(value=is_img2img), workflows_dropdown, overwrite_existing_workflow] + all_wiz_obj, outputs=workflow_result)
									# The syntax required for complex Gradio event listeners is just crazy

									all_wiz_obj.insert(0, workflow_result)

									load_workflow.click(fn=wizard_load_workflow, inputs=[gr.Variable(value=is_img2img), workflows_dropdown], outputs=all_wiz_obj)
									refresh_workflows.click(fn=wizard_refresh_workflows, outputs=workflows_dropdown)
									delete_workflow.click(fn=wizard_delete_workflow, inputs=[workflows_dropdown], outputs=workflow_result)

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

							wizard_result = gr.Code(label="Wizard Result", value="", elem_id="unprompted_result", lines=1, show_label=True)
							if Unprompted.Config.ui.wizard_templates:
								all_wiz_inputs = get_wizard_objects(WizardModes.TEMPLATES, is_img2img)
								wizard_template_btn.click(fn=wizard_generate_template, inputs=[self.templates_dropdown[int(is_img2img)], gr.Variable(value=is_img2img), gr.Variable(value=True), gr.Variable(value=""), gr.Variable(value=""), gr.Variable(value="calls")] + all_wiz_inputs, outputs=wizard_result)
							if Unprompted.Config.ui.wizard_shortcodes:
								all_wiz_inputs = get_wizard_objects(WizardModes.SHORTCODES, is_img2img)
								wizard_shortcode_btn.click(fn=wizard_generate_shortcode, inputs=[self.shortcodes_dropdown[int(is_img2img)], gr.Variable(value=is_img2img), gr.Variable(value=True), gr.Variable(value=""), gr.Variable(value=""), gr.Variable(value="calls")] + all_wiz_inputs, outputs=wizard_result)
							if Unprompted.Config.ui.wizard_capture:
								wizard_capture_btn.click(fn=wizard_generate_capture, inputs=[wizard_capture_include_inference, wizard_capture_include_prompt, wizard_capture_include_neg_prompt, wizard_capture_include_model, wizard_capture_add_template_block], outputs=wizard_result)

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

		return [is_enabled, unprompted_seed, match_main_seed, skip_gen] + get_all_wizard_objects([is_img2img])

	def process(self, p, is_enabled=True, unprompted_seed=-1, match_main_seed=True, skip_gen=False, *wizard_objects):
		if not is_enabled or not Unprompted.is_enabled:
			return p

		if skip_gen and Unprompted.last_cached_images:
			# Pseudo-skip the image generation process by minimizing inference steps
			Unprompted.log.debug("Pseudo-skipping image generation process...")
			p.steps = 1

		# test compatibility with controlnet
		Unprompted.main_p = p

		Unprompted.log.debug(f"Directory of the p object: {dir(p)}")

		# as of webui 1.5.1, creating a shallow copy of the p object no longer seems to work.
		# deepcopy throws errors as well.
		# Unprompted.p_copy = copy.copy(p)

		if match_main_seed:
			if p.seed == -1:
				from modules.processing import fix_seed
				fix_seed(p)
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

			wizard_process_autoincludes("calls", is_img2img, p, wizard_objects)

		Unprompted.original_negative_prompt = p.all_negative_prompts[0]
		if not hasattr(p, "unprompted_original_negative_prompt"):
			p.unprompted_original_negative_prompt = Unprompted.original_negative_prompt
		Unprompted.shortcode_user_vars = {}

		if Unprompted.Config.stable_diffusion.show_extra_generation_params:
			p.extra_generation_params.update({
			    "Unprompted Enabled": True,
			    "Unprompted Prompt": Unprompted.original_prompt.replace("\"", "'"),  # Must use single quotes or output will have backslashes
			    "Unprompted Seed": unprompted_seed
			})
			if len(Unprompted.original_negative_prompt) > 0:
				p.extra_generation_params.update({"Unprompted Negative Prompt": Unprompted.original_negative_prompt.replace("\"", "'")})

		# Instantiate special vars
		Unprompted.shortcode_user_vars["batch_index"] = 0  # legacy name for batch_count_index
		Unprompted.shortcode_user_vars["batch_count_index"] = 0
		Unprompted.shortcode_user_vars["batch_size_index"] = 0
		Unprompted.shortcode_user_vars["batch_real_index"] = 0
		Unprompted.shortcode_user_vars["batch_test"] = None
		Unprompted.original_model = opts.data["sd_model_checkpoint"]
		Unprompted.shortcode_user_vars["sd_model"] = opts.data["sd_model_checkpoint"]
		Unprompted.shortcode_user_vars["sd_base"] = "none"
		Unprompted.shortcode_user_vars["sd_res"] = 1024
		Unprompted.shortcode_user_vars["unprompted_seed"] = unprompted_seed
		Unprompted.shortcode_user_vars["sd_seed"] = p.seed
		if sd_models.model_data.sd_model:
			Unprompted.update_stable_diffusion_architecture_vars(sd_models.model_data.sd_model)

		if p.seed is not None and p.seed != -1.0:
			if (helpers.is_int(p.seed)):
				p.seed = int(p.seed)
			for i, val in enumerate(p.all_seeds):
				p.all_seeds[i] = p.seed + i
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
					if "single_seed" in Unprompted.shortcode_user_vars:
						p.all_seeds[i] = Unprompted.shortcode_user_vars["single_seed"]
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

		if unprompted_seed != -1:
			random.seed()

	def process_batch(self, p, is_enabled=True, unprompted_seed=-1, match_main_seed=True, skip_gen=False, *wizard_objects, **kwargs):
		if (is_enabled and Unprompted.is_enabled and Unprompted.Config.stable_diffusion.batch_count_method == "standard"):
			from modules.processing import extra_networks

			batch_count_index = Unprompted.shortcode_user_vars["batch_count_index"]

			Unprompted.log.debug(f"Starting process_batch() routine for batch_count_index #{batch_count_index}/{p.n_iter - 1}...")

			if skip_gen and Unprompted.last_cached_images:
				# Pseudo-skip the image generation process by minimizing inference steps
				Unprompted.log.debug("Pseudo-skipping image generation process...")
				if batch_count_index == 0:
					p.steps = 1
				else:
					return p

			batch_size_index = 0
			while batch_size_index < p.batch_size:
				Unprompted.log.debug(f"Starting subroutine for batch_size_index #{batch_size_index}/{p.batch_size - 1}...")
				batch_real_index = batch_count_index * p.batch_size + batch_size_index

				Unprompted.log.debug(f"Current value of batch_real_index: {batch_real_index}")

				if batch_count_index > 0:
					try:
						Unprompted.log.debug("Attempting to deactivate extra networks...")
						if hasattr(p, "hasattr"):
							extra_networks.deactivate(p, p.extra_network_data)
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
					Unprompted.shortcode_user_vars["all_prompts"][batch_real_index] = prompt_result
					Unprompted.shortcode_user_vars["all_negative_prompts"][batch_real_index] = negative_prompt_result

				p.all_prompts = Unprompted.shortcode_user_vars["all_prompts"]
				p.all_negative_prompts = Unprompted.shortcode_user_vars["all_negative_prompts"]

				Unprompted.shortcode_user_vars["prompts"][batch_size_index] = prompt_result
				Unprompted.shortcode_user_vars["negative_prompts"][batch_size_index] = negative_prompt_result

				batch_size_index += 1

			if (batch_count_index > 0):
				Unprompted.update_stable_diffusion_vars(p)

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
	def postprocess(self, p, processed, is_enabled=True, unprompted_seed=-1, match_main_seed=True, skip_gen=False, *wizard_objects):
		if not is_enabled or not Unprompted.is_enabled:
			return False

		if skip_gen and Unprompted.last_cached_images:
			Unprompted.log.debug("Replacing processed image(s) with cached image(s)...")
			processed.images = Unprompted.last_cached_images
		else:
			# Update cached images
			Unprompted.last_cached_images = processed.images[:Unprompted.Config.stable_diffusion.cached_images_limit]

		if not self.allow_postprocess:
			Unprompted.log.debug("Bypassing After routine to avoid infinite loop.")
			self.allow_postprocess = True
			return False  # Prevents endless loop with some shortcodes

		self.allow_postprocess = False
		processed = Unprompted.after(p, processed)

		self.allow_postprocess = True

		Unprompted.goodbye()

		return processed
