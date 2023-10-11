class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Downloads a file using the Civitai API (unless you already have the file in question) and automatically adds it to your prompt."
		self.extra_nets = None

	def is_network_installed(self, net, paths, exts=[".pt", ".ckpt", ".safetensors"]):
		"""Based on list_available_networks() from extensions-builtin/Lora/networks.py.
		It's not clear if there's a better/more standardized means of checking the
		user's installed extra networks. Please let me know if there is such a thing..."""

		from modules import shared
		import os
		# from modules.paths_internal import models_path

		os.makedirs(shared.cmd_opts.lora_dir, exist_ok=True)

		candidates = []
		for path in paths:
			candidates += list(shared.walk_files(path, allowed_extensions=exts))
		
		for filename in candidates:
			if os.path.isdir(filename):
				continue

			name = os.path.splitext(os.path.basename(filename))[0]
			if name == net:
				self.log.debug(f"Extra network {net} is already installed: {filename}")
				return True
		
		return False

	def run_atomic(self, pargs, kwargs, context):
		import lib_unprompted.helpers as helpers
		import requests, os
		from modules import shared

		net_directories = []
		url = kwargs["_api"] if "_api" in kwargs else "https://civitai.com/api/v1/models"
		mvid = False
		mid = False

		if "_mvid" in kwargs:
			url = url.replace("models",f"model-versions/{kwargs['_mvid']}")
			mvid = True
		elif "_id" in kwargs:
			mid = True
			url += f"/{kwargs['_id']}"

		# Shorthand use with pargs
		# e.g. [civitai lora "filename" 1.0 "search query"]
		idx = 0 # 1 if "_id" in kwargs else 0
		for parg in pargs:
			if self.Unprompted.is_system_arg(parg): idx -= 1
			else:
				parsed = self.Unprompted.parse_advanced(parg)
				if idx == 0: kwargs["types"] = parsed
				elif idx == 1:
					kwargs["_file"] = parsed
					kwargs["query"] = parsed
				elif idx == 2 or idx == 3:
					if helpers.is_float(parsed):
						kwargs["_weight"] = parsed
					else: kwargs["query"] = parsed
			idx += 1

		if "query" not in kwargs and "_id" not in kwargs and "_mvid" not in kwargs:
			self.log.error("You must pass a query or _id to this shortcode.")
			return ""

		debug = self.Unprompted.parse_arg("_debug", False)

		# Defaults
		if "limit" not in kwargs: kwargs["limit"] = 1
		timeout = kwargs["_timeout"] if "_timeout" in kwargs else 60
		filename = kwargs["_file"] if "_file" in kwargs else kwargs["query"]
		weight = self.Unprompted.parse_arg("_weight",1.0)
		activate = self.Unprompted.parse_arg("_activate",True)
		subpath = self.Unprompted.parse_arg("_subpath","")
		if subpath: subpath += "/"

		# Fix case-sensitivity of types and apply other helpful conversions
		if "types" in kwargs:
			kwargs["types"] = kwargs["types"].lower()
			net_type = kwargs["types"]
		else: net_type = "lora"

		if net_type in ["checkpoint","sd"]:
			from modules.paths_internal import models_path
			kwargs["types"] = "Checkpoint"
			net_directories = [models_path]
		elif net_type == "lora":
			kwargs["types"] = ["LORA","LoCon"]
			net_directories = [shared.cmd_opts.lora_dir,shared.cmd_opts.lyco_dir_backcompat]
		elif net_type == "locon":
			kwargs["types"] = "LoCon"
			net_directories = [shared.cmd_opts.lyco_dir_backcompat]
		elif net_type in ["textualinversion","embedding","ti"]:
			kwargs["types"] = "TextualInversion"
			net_directories = [shared.cmd_opts.embeddings_dir]
		elif net_type == "hypernetwork":
			kwargs["types"] = "Hypernetwork"
			net_directories = [shared.cmd_opts.hypernetwork_dir]
		elif net_type == "aestheticgradient":
			kwargs["types"] = "AestheticGradient"
			# TODO: Figure out correct path for AG files
			net_directories = [shared.cmd_opts.embeddings_dir]
		elif net_type in ["controlnet","cn"]:
			from modules.paths_internal import extensions_dir
			kwargs["types"] = "Controlnet"
			net_directories = [extensions_dir+self.Unprompted.Config.stable_diffusion.controlnet_name+"/models"]
		elif net_type in ["poses","pose","openpose"]:
			kwargs["types"] = "Poses"
			net_directories = [self.Unprompted.base_dir+"/user/poses"]

		if not self.is_network_installed(filename,net_directories):
			# Remove system arguments from kwargs dict because we don't need to waste anyone's bandwidth
			for k in list(kwargs.keys()):
				if k.startswith("_"):
					del kwargs[k]

			self.log.info(f"Requesting {filename} from the Civitai API...")
			r = requests.get(url, params=kwargs, timeout=timeout)

			if r.status_code == requests.codes.ok:
				try:
					json_obj = r.json()
					if debug:
						self.log.info(f"JSON object: {json_obj}")
					
					if not mvid and not mid:
						if "items" in json_obj:
							json_obj = json_obj["items"]
							num_results = len(json_obj)
							if num_results:
								if num_results > 1: self.log.warning(f"Civitai returned {num_results} results for your search. We will only process the first result.")
							else:
								self.log.error("Civitai did not find any search results for your parameters.")
								return ""
							json_obj = json_obj[0]
						else:
							self.log.error("Civitai returned a malformed JSON object; the `items` key was not found.")
							return ""
					
					if not mvid:
						model_versions = json_obj["modelVersions"][0]
						file_info = model_versions["files"][0]
					else:
						file_info = json_obj["files"][0]

					try:
						file_path = f"{net_directories[0]}/{subpath}{file_info['name']}"
						# update filename for final string
						filename = os.path.basename(os.path.splitext(file_path)[0])
						helpers.download_file(file_path,file_info["downloadUrl"],headers={"Content-Disposition":"attachment"})
					except:
						self.log.exception("An error occurred while downloading the Civitai file.")

				except Exception as e:
					self.log.exception("Exception caught while decoding JSON")
					return ""
			else:
				self.log.error(f"Request to Civitai API yielded bad response: {r.status_code}")
				return ""

		# Return assembled prompt string
		if activate:
			if net_type in ["lora","locon"]:
				return f"<lora:{filename}:{weight}>"
			elif kwargs["types"] == "TextualInversion":
				return f"({filename}:{weight})"

		return ""