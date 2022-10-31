# Unprompted by Therefore Games. All Rights Reserved.
# https://patreon.com/thereforegames
# https://github.com/ThereforeGames/unprompted

import modules.scripts as scripts
import gradio as gr

from modules import processing, images, shared, sd_samplers
from modules.processing import process_images, Processed
from modules.shared import opts, cmd_opts, state, Options

from unprompted.lib.shared import Unprompted

# Main object
Unprompted = Unprompted()

class Script(scripts.Script):
	def title(self):
		return "Unprompted"

	def show(self, is_img2img):
		return True

	def ui(self, is_img2img):
		dry_run = gr.Checkbox(label="Dry Run",value=False)
		plug = gr.HTML(label="plug",value='<div class="gr-block gr-box relative w-full overflow-hidden border-solid border border-gray-200 gr-panel" style="padding:20px;"><a href="https://payhip.com/b/hdgNR" target="_blank"><img src="https://i.ibb.co/1MSpHL4/Fantasy-Card-Template2.png" style="float: left;width: 150px;margin-bottom:10px;"></a><h1 style="font-size: 20px;letter-spacing:0.015em;margin-top:10px;">NEW! <strong>Premium Fantasy Card Template</strong> is now available.</h1><p style="margin:1em 0;">Generate a wide variety of creatures and characters in the style of a fantasy card game. Perfect for heroes, animals, monsters, and even crazy hybrids.</p><a href="https://payhip.com/b/hdgNR" target=_blank><button class="gr-button gr-button-lg gr-button-secondary" title="View premium assets for Unprompted">Learn More ➜</button></a><hr style="margin:1em 0;clear:both;"><p><em>Purchases help fund the continued development of Unprompted. Thank you for your support!</em> ❤</p></div>')
		return [dry_run, plug]

	def run(self, p, dry_run, plug):
		if (dry_run):
			temp_debug = Unprompted.Config.debug
			Unprompted.Config.debug = True

		# Reset vars
		Unprompted.shortcode_user_vars = {}

		# Set up system var support - copy relevant p attributes into shortcode var object
		for att in dir(p):
			if not att.startswith("__"):
				Unprompted.shortcode_user_vars[att] = getattr(p,att)

		Unprompted.shortcode_user_vars["prompt"] = Unprompted.process_string(p.prompt)

		# Apply any updates to system vars
		for att in dir(p):
			if not att.startswith("__"):
				setattr(p,att,Unprompted.shortcode_user_vars[att])	

		# Process any remaining shortcodes in the negative prompt
		p.negative_prompt = Unprompted.process_string(p.negative_prompt)

		# Skips the bulk of inference (note: still produces a blank image)
		if (dry_run):
			p.batch_size = 1
			p.steps = 0
			Unprompted.Config.debug = temp_debug

		# Cleanup routines
		Unprompted.log("Entering cleanup routine...",False)
		for i in Unprompted.cleanup_routines:
			Unprompted.shortcode_objects[i].cleanup()

		# Make image
		processed = processing.process_images(p)
		return processed