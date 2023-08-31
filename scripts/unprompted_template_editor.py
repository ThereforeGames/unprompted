from lib_unprompted.shared import parse_config

import modules.scripts as scripts

base_dir = scripts.basedir()
cfg_dict, Config = parse_config(base_dir)

if Config.stable_diffusion.template_editor:
	import os.path
	from pathlib import Path

	import pathlib
	import os
	import re
	import glob
	from modules import extra_networks
	from modules.ui_components import FormRow, FormColumn, FormGroup, ToolButton, FormHTML

	import gradio as gr
	from modules.ui_components import ToolButton

	from modules.processing import Processed, process_images
	from modules.shared import opts
	from modules import script_callbacks, sd_models, shared

	refresh_symbol = '\U0001f504'  # 🔄
	folder_symbol_unprompted = '\U0001f5c1'  # 🗁
	save_style_symbol_unprompted = '\U0001f5ab'  # 🖫
	extra_networks_symbol = '\U0001F3B4'  # 🎴

	folder = f"{base_dir}/{Config.template_directory}"

	def get_file_list(folder):
		return [os.path.relpath(os.path.join(dirpath, file), folder).replace("\\", "/") for (dirpath, dirnames, filenames) in os.walk(folder) for file in filenames if file.endswith(".txt")]

	def generate_file_list_html(file_list):
		html_content = "<div style='height: 300px; overflow-y: scroll;'><ul>"
		for file in file_list:
			html_content += f"<li><button style='background-color:FFFFFF00;'  onMouseOver=\"this.style.backgroundColor='#8888AA99'\" onMouseOut=\"this.style.backgroundColor='#FFFFFF00'\"  onclick='loadFile(\"{file}\")'>{file}</button></li>"
		html_content += "</ul></div>"
		return html_content

	def on_ui_tabs():
		def refresh_file_list():
			# print(f"REFRESHING LIST: {folder}")
			file_list = get_file_list(f"{folder}")
			file_list_html = generate_file_list_html(file_list)
			html_update = None
			html_update = gr.HTML.update(file_list_html)
			return html_update

		def load_file(file_name):
			# print(f"loading: {file_name}")

			with open(f"{folder}/{file_name}", "r") as file:
				content = file.read()
			# print(f"content: {content}")
			# update main_edit_space woth content
			return content

		def save_file(file_name, content):
			# print(f"loading: {file_name}")
			with open(f"{folder}/{file_name}", "w") as file:
				file.write(content)

		with gr.Blocks() as unprompted_editor_ui:
			with gr.Row(elem_id=f"unprompted_toprow"):
				with gr.Column(scale=1, min_width=200):
					# Add HTML element for file list
					templates = gr.HTML(value="", elem_id="file_list", css=".myButtons:hover {background-color: #4CAF50;color: white;}")
					with gr.Row():
						refresh_button_unprompted = ToolButton(value=refresh_symbol, elem_id=f"refresh_button_unprompted")
						load_button_unprompted = ToolButton(value=folder_symbol_unprompted, elem_id=f"load_button_unprompted")
						save_button_unprompted = ToolButton(value=save_style_symbol_unprompted, elem_id=f"save_button_unprompted")
					with gr.Row():
						# Add save name text box
						save_name = gr.Textbox(value="", label="Save Name", elem_id="save_name")
				with gr.Column(scale=4, min_width=900):
					main_edit_space = gr.Textbox(value="", label="Text Editor", interactive=True, lines=20, elem_id="unprompted_edit_space_prompt")
					# extra_networks_button = ToolButton(value=extra_networks_symbol, elem_id=f"unprompted_edit_space_extra_networks_button")
					with gr.Accordion("Extra Networks", open=False):
						extra_networks_tab = gr.Tabs(elem_id="unprompted_edit_space_extra_tabs")
						extra_networks_tab.__enter__()

						with gr.Blocks(elem_id="unprompted_edit_space_extra_networks", visible=False) as extra_networks:
							from modules import ui_extra_networks
							extra_networks_ui_unprompted_edit_space = ui_extra_networks.create_ui(extra_networks, [extra_networks_tab], 'unprompted_edit_space')
							extra_networks_ui_unprompted_gallery = gr.Textbox(visible=False)

			ui_extra_networks.setup_ui(extra_networks_ui_unprompted_edit_space, extra_networks_ui_unprompted_gallery)

			extra_networks_tab.__exit__()

			refresh_button_unprompted.click(fn=refresh_file_list, inputs=[], outputs=[
			    templates,
			])
			load_button_unprompted.click(fn=load_file, inputs=[
			    save_name,
			], outputs=[
			    main_edit_space,
			])
			save_button_unprompted.click(fn=save_file, inputs=[
			    save_name,
			    main_edit_space,
			], outputs=[])

		return (unprompted_editor_ui, "Unprompted Template Editor", "unprompted_editor_ui"),

	script_callbacks.on_ui_tabs(on_ui_tabs)
