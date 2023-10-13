class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Downloads a file using the Civitai API (unless you already have the file in question) and automatically adds it to your prompt."
		self.extra_nets = None

	def network_path(self, net, paths, exts=[".pt", ".ckpt", ".safetensors"]):
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
				return filename
		
		return None

	def run_atomic(self, pargs, kwargs, context):
		import lib_unprompted.helpers as helpers
		import requests, os, json
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
		filename = kwargs["_file"] if "_file" in kwargs else self.Unpromtped.parse_arg("query","")
		weight = self.Unprompted.parse_arg("_weight",1.0)
		activate = self.Unprompted.parse_arg("_activate",True)
		words = self.Unprompted.parse_arg("_words",False)
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
			net_directories = [extensions_dir+self.Unprompted.Config.stable_diffusion.controlnet.extension+"/models"]
		elif net_type in ["poses","pose","openpose"]:
			kwargs["types"] = "Poses"
			net_directories = [self.Unprompted.base_dir+"/user/poses"]

		net_path = self.network_path(filename,net_directories)
		if not net_path:
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
						if words and "trainedWords" in model_versions: words = " ".join(model_versions["trainedWords"])
					else:
						file_info = json_obj["files"][0]
						if words and "trainedWords" in json_obj: words = " ".join(json_obj["trainedWords"])

					try:
						file_path = f"{net_directories[0]}/{subpath}{file_info['name']}"
						# update filename for final string
						filename = os.path.basename(os.path.splitext(file_path)[0])
						helpers.download_file(file_path,file_info["downloadUrl"],headers={"Content-Disposition":"attachment"})
					except:
						self.log.exception("An error occurred while downloading the Civitai file.")

					if words:
						# Replace the extension in file_path with .json:
						json_path = os.path.splitext(file_path)[0]+".json"
						# Create and open json_path for writing:
						with open(json_path, "w") as json_file:
							json.dump({"activation text":words}, json_file)

				except Exception as e:
					self.log.exception("Exception caught while decoding JSON")
					return ""
			else:
				self.log.error(f"Request to Civitai API yielded bad response: {r.status_code}")
				return ""
		# We already have the file, check for activation text in json
		elif words:
			json_path = os.path.splitext(net_path)[0]+".json"
			if os.path.exists(json_path):
				with open(json_path, "r") as json_file:
					json_obj = json.load(json_file)
					if "activation text" in json_obj:
						words = json_obj["activation text"]
					else:
						self.log.debug(f"Activation text not found in {json_path}.")
			else:
				self.log.debug(f"No JSON found at {json_path}.")
			

		# Return assembled prompt string
		return_string = ""
		if words: return_string += words + " "
		if activate:
			if net_type in ["lora","locon"]:
				return_string += f"<lora:{filename}:{weight}>"
			elif kwargs["types"] == "TextualInversion":
				return_string += f"({filename}:{weight})"

		return return_string
	
	def ui(self, gr):
		return