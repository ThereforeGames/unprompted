import cv2
try:
	from modules import shared
except:
	pass  # for unprompted_dry


class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Improves the quality of faces using various models."
		self.gpen_processor = None
		self.gpen_cache_model = ""

		self.wizard_prepend = f"{Unprompted.Config.syntax.tag_start}after{Unprompted.Config.syntax.tag_end}{Unprompted.Config.syntax.tag_start}restore_faces"
		self.wizard_append = Unprompted.Config.syntax.tag_end + Unprompted.Config.syntax.tag_start + Unprompted.Config.syntax.tag_close + "after" + Unprompted.Config.syntax.tag_end

		self.resample_methods = {}
		self.resample_methods["Nearest Neighbor"] = cv2.INTER_NEAREST
		self.resample_methods["Bilinear"] = cv2.INTER_LINEAR
		self.resample_methods["Area"] = cv2.INTER_AREA
		self.resample_methods["Cubic"] = cv2.INTER_CUBIC
		self.resample_methods["Lanczos"] = cv2.INTER_LANCZOS4

	def run_atomic(self, pargs, kwargs, context):
		import numpy as np
		from PIL import Image
		import lib_unprompted.helpers as helpers

		methods = kwargs["method"] if "method" in kwargs else "gpen"
		if self.Unprompted.Config.syntax.delimiter in methods: methods = methods.split(self.Unprompted.Config.syntax.delimiter)
		else: methods = [methods]
		
		visibility = float(self.Unprompted.parse_advanced(kwargs["visibility"], context)) if "visibility" in kwargs else 1.0
		resolution_preset = str(kwargs["resolution_preset"]) if "resolution_preset" in kwargs else "512"
		unload = self.Unprompted.shortcode_var_is_true("unload", pargs, kwargs)

		downscale_method = self.Unprompted.parse_arg("downscale_method","Bilinear")
		downscale_method = self.resample_methods[downscale_method]

		result = None

		_image = self.Unprompted.parse_alt_tags(kwargs["image"],context) if "image" in kwargs else False
		if _image:
			this_image = Image.open(_image)
		else: this_image = self.Unprompted.current_image()

		for this_method in methods:
			self.log.info(f"{this_method} face restoration starting...")

			restoration_method = this_method.lower()

			if restoration_method == "gpen":
				import lib_unprompted.helpers as helpers
				import lib_unprompted.gpen.__init_paths
				import torch
				from lib_unprompted.gpen.face_enhancement import FaceEnhancement
				import os
				import cv2
				import glob
				import time
				import math
				import argparse
				import numpy as np
				from PIL import Image, ImageDraw

				# Default args
				kwargs["model"] = kwargs["model"] if "model" in kwargs else f"GPEN-BFR-{resolution_preset}"
				kwargs["key"] = kwargs["key"] if "key" in kwargs else None
				kwargs["in_size"] = int(kwargs["in_size"]) if "in_size" in kwargs else int(resolution_preset)
				kwargs["out_size"] = kwargs["out_size"] if "out_size" in kwargs else None
				kwargs["channel_multiplier"] = kwargs["channel_multiplier"] if "channel_multiplier" in kwargs else 2
				kwargs["narrow"] = kwargs["narrow"] if "narrow" in kwargs else 1.0
				kwargs["alpha"] = kwargs["alpha"] if "alpha" in kwargs else 1.0
				kwargs["use_sr"] = kwargs["use_sr"] if "use_sr" in kwargs else False
				kwargs["use_cuda"] = kwargs["cuda"] if "use_cuda" in kwargs else torch.device('cuda' if torch.cuda.is_available() else 'cpu')
				kwargs["save_face"] = kwargs["save_face"] if "save_face" in kwargs else False
				kwargs["aligned"] = kwargs["aligned"] if "aligned" in kwargs else False
				kwargs["sr_model"] = kwargs["sr_model"] if "sr_model" in kwargs else "realesrnet"
				kwargs["sr_scale"] = kwargs["sr_scale"] if "sr_scale" in kwargs else 2
				kwargs["tile_size"] = kwargs["tile_size"] if "tile_size" in kwargs else 0
				kwargs["indir"] = "example/imgs"
				kwargs["outdir"] = "results/outs-BFR"
				kwargs["ext"] = ".jpg"

				args = helpers.AttrDict(kwargs)
				img = cv2.cvtColor(np.array(this_image), cv2.COLOR_RGB2BGR)

				models_dir = f"{self.Unprompted.base_dir}/{self.Unprompted.Config.subdirectories.models}"
				gpen_dir = f"{models_dir}/gpen/"

				if args.model=="GPEN-BFR-512":
					helpers.download_file(f"{gpen_dir}/{args.model}.pth","https://public-vigen-video.oss-cn-shanghai.aliyuncs.com/robin/models/GPEN-BFR-512.pth")
				elif args.model=="GPEN-BFR-1024":
					if not helpers.download_file(f"{gpen_dir}/{args.model}.pth","https://public-vigen-video.oss-cn-shanghai.aliyuncs.com/robin/models/GPEN-BFR-1024.pth"):
						self.log.error("The download link for the 1024 model doesn't appear to work. Try installing it manually into your unprompted/models/gpen folder: https://cyberfile.me/644d")
				elif args.model=="GPEN-BFR-2048":
					helpers.download_file(f"{gpen_dir}/{args.model}.pth","https://public-vigen-video.oss-cn-shanghai.aliyuncs.com/robin/models/GPEN-BFR-2048.pth")

				# Additional dependencies
				helpers.download_file(f"{gpen_dir}/ParseNet-latest.pth","https://public-vigen-video.oss-cn-shanghai.aliyuncs.com/robin/models/ParseNet-latest.pth")
				helpers.download_file(f"{gpen_dir}/realesrnet_x2.pth","https://public-vigen-video.oss-cn-shanghai.aliyuncs.com/robin/models/realesrnet_x2.pth")
				helpers.download_file(f"{gpen_dir}/RetinaFace-R50.pth","https://public-vigen-video.oss-cn-shanghai.aliyuncs.com/robin/models/RetinaFace-R50.pth")

				if unload or not self.gpen_processor or self.gpen_cache_model != resolution_preset:
					self.log.info("Loading FaceEnhancement object...")
					self.gpen_cache_model = resolution_preset
					self.gpen_processor = FaceEnhancement(args, base_dir=f"{models_dir}/", in_size=args.in_size, model=args.model, use_sr=args.use_sr, device=args.use_cuda, interp=downscale_method)
				else:
					self.log.info("Using cached FaceEnhancement object.")

				img_out, orig_faces, enhanced_faces = self.gpen_processor.process(img, aligned=args.aligned)

				result = Image.fromarray(cv2.cvtColor(img_out, cv2.COLOR_BGR2RGB))

				if unload:
					self.log.debug("Unloading GPEN from cache.")
					self.gpen_cache_model = ""
					self.gpen_processor = None

			# built-in restore methods
			else:
				for face_restorer in shared.face_restorers:
					if face_restorer.name().lower() == restoration_method:
						self.log.debug("Using WebUI's native restore.")

						result = face_restorer.restore(np.array(this_image))
						result = Image.fromarray(result)

						break
			
			self.log.info(f"{this_method} face restoration completed.")

		# Append to output window
		try:
			self.Unprompted.current_image(Image.blend(this_image, result, visibility))
		except:
			pass

		return ""

	def ui(self, gr):
		gr.Dropdown(label="Face restoration method 🡢 method", choices=[restorer.name() for restorer in shared.face_restorers] + ["GPEN"], value="GPEN", multiselect=True, interactive=True, info="You can enable multiple restoration methods with the standard delimiter.")
		gr.Slider(label="Restoration visibility 🡢 visibility", value=1.0, maximum=1.0, minimum=0.0, interactive=True, step=0.01)
		with gr.Accordion("🎭 GPEN Settings", open=False):
			gr.Radio(label="Resolution Preset 🡢 resolution_preset", choices=["512", "1024", "2048"], value="512", interactive=True, info="Increases clarity but may lead to an oversharpened look - counteract with the visibility slider.")
			gr.Dropdown(label="Downscale interpolation method 🡢 downscale_method", choices=list(self.resample_methods.keys()), value="Bilinear", interactive=True)
			gr.Checkbox(label="Unload GPEN model after inference 🡢 unload", info="Useful for devices with low memory, but increases inference time.")
