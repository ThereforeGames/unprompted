# Unprompted by Therefore Games. All Rights Reserved.
# https://patreon.com/thereforegames
# https://github.com/ThereforeGames/unprompted

# This script is intended to be used as an extension for Automatic1111's Stable Diffusion WebUI.

import gradio as gr

import modules.scripts as scripts
from modules.processing import process_images,fix_seed,Processed
from modules.shared import opts, cmd_opts, state, Options
from pathlib import Path

import sys
import os

base_dir = scripts.basedir()
sys.path.append(base_dir)
# Main object
from lib.shared import Unprompted

Unprompted = Unprompted(base_dir)
Unprompted.wizard_shortcodes = [{}, {}]
Unprompted.wizard_dropdown = None

def do_dry_run(string):
	Unprompted.log(string)
	# Reset vars
	Unprompted.shortcode_user_vars = {}
	unp_result = Unprompted.process_string(string)
	# Cleanup routines
	Unprompted.log("Entering cleanup routine...",False)
	for i in Unprompted.cleanup_routines:
		Unprompted.shortcode_objects[i].cleanup()
	return f"<strong>RESULT:</strong> {unp_result}"

def wizard_select_shortcode(option,is_img2img):
	# Unprompted.wizard_dropdown.update(value=option)
	Unprompted.wizard_dropdown.value = option
	filtered_shortcodes = Unprompted.wizard_shortcodes[int(is_img2img)]
	results = [gr.update(visible=(option == key)) for key in filtered_shortcodes.keys()]
	return results

def wizard_set_event_listener(obj):
	obj.change(fn=lambda val: wizard_update_value(obj,val),inputs=obj)

def wizard_update_value(obj,val):
	obj.value = val # TODO: Rewrite this with Gradio update function if possible

def wizard_generate_shortcode(option,is_img2img,original_content=""):
	result = Unprompted.Config.syntax.tag_start + option
	filtered_shortcodes = Unprompted.wizard_shortcodes[int(is_img2img)]
	group = filtered_shortcodes[option]
	block_content=""
	prepend="<strong>RESULT:</strong> "

	try:
		for gr_obj in group.children[1].children:
			if gr_obj.label=="Content":
				block_content = gr_obj.value
			else:
				if (not gr_obj.value): continue # Skip empty fields

				arg_name = gr_obj.label.split(" ")[-1] # Get everything after the last space
				block_name = gr_obj.get_block_name()
				# Rules
				if (arg_name == "str"):
					result += " \"" + str(gr_obj.value) + "\""
				elif (arg_name == "int"):
					result += " " + str(int(gr_obj.value))
				elif (arg_name == "verbatim"):
					result += " " + str(gr_obj.value)
				elif (block_name=="checkbox"):
					if gr_obj.value: result += " " + arg_name
				elif (block_name=="number"): result += f" {arg_name}={int(gr_obj.value)}"
				elif (block_name=="textbox"):
					if len(gr_obj.value) > 0: result += f" {arg_name}=\"{gr_obj.value}\""
				else: result += f" {arg_name}=\"{gr_obj.value}\""
	except: pass

	# Closing bracket
	result += Unprompted.Config.syntax.tag_end

	if hasattr(Unprompted.shortcode_objects[option],"run_block"):
		if (original_content and not block_content):
			block_content = original_content
			original_content = ""
			prepend = ""
		result += block_content + Unprompted.Config.syntax.tag_start + Unprompted.Config.syntax.tag_close + option + Unprompted.Config.syntax.tag_end
	
	if (original_content): result += original_content
	else: result = prepend + result

	return result

def get_markdown(file):
	file = Path(base_dir) / file
	lines = file.open(mode='r', encoding='utf-8').readlines()
	final_string = ""
	for line in lines:
		# Skip h1 elements
		if not line.startswith("# "): final_string += line
	return final_string

# Workaround for Gradio checkbox label+value bug https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/6109
def gradio_enabled_checkbox_workaround():
	return(Unprompted.Config.ui.enabled)

class Scripts(scripts.Script):
	def title(self):
		return "Unprompted"

	def show(self, is_img2img):
		return scripts.AlwaysVisible

	def ui(self, is_img2img):
		with gr.Group():
			with gr.Accordion("Unprompted", open=Unprompted.Config.ui.open):
				is_enabled = gr.Checkbox(label="Enabled",value=gradio_enabled_checkbox_workaround)

				if (os.path.exists(f"{base_dir}/{Unprompted.Config.template_directory}/pro/fantasy_card/main{Unprompted.Config.txt_format}")): is_open = False
				else: is_open = True
				
				with gr.Accordion("🎉 Promo", open=is_open):
					plug = gr.HTML(label="plug",value=f'<a href="https://payhip.com/b/hdgNR" target="_blank"><img src="https://i.ibb.co/1MSpHL4/Fantasy-Card-Template2.png" style="float: left;width: 150px;margin-bottom:10px;"></a><h1 style="font-size: 20px;letter-spacing:0.015em;margin-top:10px;">NEW! <strong>Premium Fantasy Card Template</strong> is now available.</h1><p style="margin:1em 0;">Generate a wide variety of creatures and characters in the style of a fantasy card game. Perfect for heroes, animals, monsters, and even crazy hybrids.</p><a href="https://payhip.com/b/hdgNR" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View premium assets for Unprompted">Learn More ➜</button></a><hr style="margin:1em 0;clear:both;"><p style="max-width:80%"><em>Purchases help fund the continued development of Unprompted. Thank you for your support!</em> ❤</p>')

				with gr.Accordion("🧙 Wizard", open=Unprompted.Config.ui.wizard_open):
					if Unprompted.Config.ui.wizard_enabled:
						shortcode_list = list(Unprompted.shortcode_objects.keys())
						Unprompted.wizard_dropdown = gr.Dropdown(choices=shortcode_list,label="Shortcode",value=Unprompted.Config.ui.wizard_default_shortcode)
						filtered_shortcodes = Unprompted.wizard_shortcodes[int(is_img2img)]
						for key in shortcode_list:
							if (hasattr(Unprompted.shortcode_objects[key],"ui")):
								with gr.Group(visible = (key == Unprompted.wizard_dropdown.value)) as filtered_shortcodes[key]:
									gr.Label(label="Options",value=f"{key}: {Unprompted.shortcode_objects[key].description}")
									if hasattr(Unprompted.shortcode_objects[key],"run_block"): gr.Textbox(label="Content",max_lines=2,min_lines=2)
									Unprompted.shortcode_objects[key].ui(gr)
									# Add event listeners
									for child in filtered_shortcodes[key].children:
										if ("change" in dir(child) and child.get_block_name() != "label"):
											# use function to pass obj by reference
											wizard_set_event_listener(child)

						Unprompted.wizard_dropdown.change(fn=wizard_select_shortcode,inputs=[Unprompted.wizard_dropdown,gr.Variable(value=is_img2img)],outputs=list(filtered_shortcodes.values()))
						wizard_btn = gr.Button(value="Generate Shortcode")
						wizard_result = gr.HTML(label="wizard_result",value="")
						wizard_btn.click(fn=wizard_generate_shortcode,inputs=[Unprompted.wizard_dropdown,gr.Variable(value=is_img2img)],outputs=wizard_result)
					else: gr.HTML(label="wizard_debug",value="You have disabled the Wizard in your config.")

					wizard_autoinclude = gr.Checkbox(label="Auto-include in prompt",value=Unprompted.Config.ui.wizard_autoinclude)
					
				with gr.Accordion("📝 Dry Run", open=Unprompted.Config.ui.dry_run_open):
					dry_run_prompt = gr.Textbox(lines=2,placeholder="Test prompt",show_label=False)
					dry_run = gr.Button(value="Process Text")
					dry_run_result = gr.HTML(label="dry_run_result",value="")
					dry_run.click(fn=do_dry_run,inputs=dry_run_prompt,outputs=dry_run_result)
				
				with gr.Tab("💡 About"):
					about = gr.Markdown(value=get_markdown("docs/ABOUT.md").replace("$VERSION",Unprompted.VERSION))
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
					open_templates.click(fn=lambda: open_folder(f"{base_dir}/{Unprompted.Config.template_directory}"),inputs=[],outputs=[])

				with gr.Tab("📣 Announcements"):
					announcements = gr.Markdown(value=get_markdown("docs/ANNOUNCEMENTS.md"))

				with gr.Tab("⏱ Changelog"):
					changelog = gr.Markdown(value=get_markdown("docs/CHANGELOG.md"))
				
				with gr.Tab("📘 Manual"):
					manual = gr.Markdown(value=get_markdown("docs/MANUAL.md"))

				with gr.Tab("🎓 Starter Guide"):
					guide = gr.Markdown(value=get_markdown("docs/GUIDE.md"))

				
		return [is_enabled,wizard_autoinclude]
	
	def process(self, p, is_enabled, wizard_autoinclude):
		if not is_enabled:
			return p
		
		def apply_prompt_template(string,template):
			return template.replace("*",string)

		# Reset vars
		original_prompt = p.all_prompts[0]

		if wizard_autoinclude and Unprompted.Config.ui.wizard_enabled:
			original_prompt = wizard_generate_shortcode(Unprompted.wizard_dropdown.value,hasattr(p,"init_images"),original_prompt)

		original_negative_prompt = p.all_negative_prompts[0]
		Unprompted.shortcode_user_vars = {}

		# Extra vars
		Unprompted.shortcode_user_vars["batch_index"] = 0

		# Set up system var support - copy relevant p attributes into shortcode var object
		for att in dir(p):
			if not att.startswith("__"):
				Unprompted.shortcode_user_vars[att] = getattr(p,att)

		Unprompted.shortcode_user_vars["prompt"] = Unprompted.process_string(apply_prompt_template(original_prompt,Unprompted.Config.templates.default))
		Unprompted.shortcode_user_vars["negative_prompt"] = Unprompted.process_string(apply_prompt_template(Unprompted.shortcode_user_vars["negative_prompt"] if "negative_prompt" in Unprompted.shortcode_user_vars else original_negative_prompt,Unprompted.Config.templates.default_negative))

		# Apply any updates to system vars
		for att in dir(p):
			if not att.startswith("__"):
				setattr(p,att,Unprompted.shortcode_user_vars[att])	

		if p.seed is not None and p.seed != -1.0:
			if (Unprompted.is_int(p.seed)): p.seed = int(p.seed)
			p.all_seeds[0] = p.seed
		else:
			p.seed = -1
			p.seed = fix_seed(p)

		# Batch support
		if (Unprompted.Config.stable_diffusion.batch_support):
			for i, val in enumerate(p.all_prompts):
				if (i == 0):
					Unprompted.shortcode_user_vars["batch_index"] = i
					p.all_prompts[0] = Unprompted.shortcode_user_vars["prompt"]
					p.all_negative_prompts[0] = Unprompted.shortcode_user_vars["negative_prompt"]
				else:
					Unprompted.shortcode_user_vars = {}
					Unprompted.shortcode_user_vars["batch_index"] = i
					p.all_prompts[i] = Unprompted.process_string(apply_prompt_template(original_prompt,Unprompted.Config.templates.default))
					p.all_negative_prompts[i] = Unprompted.process_string(apply_prompt_template(Unprompted.shortcode_user_vars["negative_prompt"] if "negative_prompt" in Unprompted.shortcode_user_vars else original_negative_prompt,Unprompted.Config.templates.default_negative))

				Unprompted.log(f"Result {i}: {p.all_prompts[i]}",False)
		# Keep the same prompt between runs
		else:
			for i, val in enumerate(p.all_prompts):
				p.all_prompts[i] = Unprompted.shortcode_user_vars["prompt"]
				p.all_negative_prompts[i] = Unprompted.shortcode_user_vars["negative_prompt"]

		# Cleanup routines
		Unprompted.log("Entering Cleanup routine...",False)
		for i in Unprompted.cleanup_routines:
			Unprompted.shortcode_objects[i].cleanup()

	# After routines
	def postprocess(self, p, processed, is_enabled, test):
		# TODO: 'test' appears to contain the name of this file in new versions of A1111, need to figure out what the point of it is
		Unprompted.log("Entering After routine...")
		for i in Unprompted.after_routines:
			Unprompted.shortcode_objects[i].after(p,processed)