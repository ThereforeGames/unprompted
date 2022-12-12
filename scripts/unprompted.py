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


def get_markdown(file):
	file = Path(base_dir) / file
	lines = file.open(mode='r', encoding='utf-8').readlines()
	final_string = ""
	for line in lines:
		# Skip h1 elements
		if not line.startswith("# "): final_string += line
	return final_string

class Scripts(scripts.Script):
	def title(self):
		return "Unprompted"

	def show(self, is_img2img):
		return scripts.AlwaysVisible

	def ui(self, is_img2img):
		with gr.Group():
			with gr.Accordion("Unprompted", open=False):
				is_enabled = gr.Checkbox(label="Enabled", value=True)

				if (os.path.exists(f"{base_dir}/{Unprompted.Config.template_directory}/pro/fantasy_card/main{Unprompted.Config.txt_format}")): is_open = False
				else: is_open = True
				
				with gr.Accordion("Promo", open=is_open):
					plug = gr.HTML(label="plug",value=f'<a href="https://payhip.com/b/hdgNR" target="_blank"><img src="https://i.ibb.co/1MSpHL4/Fantasy-Card-Template2.png" style="float: left;width: 150px;margin-bottom:10px;"></a><h1 style="font-size: 20px;letter-spacing:0.015em;margin-top:10px;">NEW! <strong>Premium Fantasy Card Template</strong> is now available.</h1><p style="margin:1em 0;">Generate a wide variety of creatures and characters in the style of a fantasy card game. Perfect for heroes, animals, monsters, and even crazy hybrids.</p><a href="https://payhip.com/b/hdgNR" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View premium assets for Unprompted">Learn More ➜</button></a><hr style="margin:1em 0;clear:both;"><p style="max-width:80%"><em>Purchases help fund the continued development of Unprompted. Thank you for your support!</em> ❤</p>')

				with gr.Accordion("Dry Run", open=True):
					dry_run_prompt = gr.Textbox(lines=2,placeholder="Test prompt",show_label=False)
					dry_run = gr.Button(value="Process Text")
					dry_run_result = gr.HTML(label="dry_run_result",value="")
					dry_run.click(fn=do_dry_run,inputs=dry_run_prompt,outputs=dry_run_result)


				with gr.Tab("💡 About"):
					about = gr.Markdown(value=get_markdown("docs/ABOUT.md").replace("$VERSION",Unprompted.VERSION))

				with gr.Tab("📣 Announcements"):
					announcements = gr.Markdown(value=get_markdown("docs/ANNOUNCEMENTS.md"))

				with gr.Tab("⏱ Changelog"):
					changelog = gr.Markdown(value=get_markdown("docs/CHANGELOG.md"))
				
				with gr.Tab("📘 Manual"):
					manual = gr.Markdown(value=get_markdown("docs/MANUAL.md"))

				with gr.Tab("🎓 Starter Guide"):
					guide = gr.Markdown(value=get_markdown("docs/GUIDE.md"))

		return [is_enabled]

	def process(self, p, is_enabled):
		if not is_enabled:
			return p
		
		# Reset vars
		original_prompt = p.all_prompts[0]
		original_negative_prompt = p.all_negative_prompts[0]
		Unprompted.shortcode_user_vars = {}

		# Extra vars
		Unprompted.shortcode_user_vars["batch_index"] = 0

		# Set up system var support - copy relevant p attributes into shortcode var object
		for att in dir(p):
			if not att.startswith("__"):
				Unprompted.shortcode_user_vars[att] = getattr(p,att)

		Unprompted.shortcode_user_vars["prompt"] = Unprompted.process_string(original_prompt)
		Unprompted.shortcode_user_vars["negative_prompt"] = Unprompted.process_string(Unprompted.shortcode_user_vars["negative_prompt"] if "negative_prompt" in Unprompted.shortcode_user_vars else original_negative_prompt)

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
					p.all_prompts[i] = Unprompted.process_string(original_prompt)
					p.all_negative_prompts[i] = Unprompted.process_string(Unprompted.shortcode_user_vars["negative_prompt"] if "negative_prompt" in Unprompted.shortcode_user_vars else original_negative_prompt)

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
	def run(self, p):
		# After routines
		Unprompted.log("Entering After routine...")
		for i in Unprompted.after_routines:
			Unprompted.shortcode_objects[i].after()