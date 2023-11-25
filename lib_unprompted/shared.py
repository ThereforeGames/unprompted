import json
from types import SimpleNamespace
import lib_unprompted.shortcodes as shortcodes
from lib_unprompted.simpleeval import simple_eval
import os
import glob
import importlib
import inspect
import sys
import time
import logging
from lib_unprompted import helpers


def parse_config(base_dir="."):
	cfg_dict = json.load(open(f"{base_dir}/config.json", "r", encoding="utf8"))
	user_config = f"{base_dir}/config_user.json"
	if (os.path.isfile(user_config)):
		import lib_unprompted.flatdict as flatdict
		flat_user_cfg = flatdict.FlatDict(json.load(open(user_config, "r", encoding="utf8")))
		flat_cfg = flatdict.FlatDict(cfg_dict)

		# Write differences to flattened dictionary
		flat_cfg.update(flat_user_cfg)

		# Unflatten
		cfg_dict = flat_cfg.as_dict()
	return (cfg_dict, json.loads(json.dumps(cfg_dict), object_hook=lambda d: SimpleNamespace(**d)))


class Unprompted:
	def load_shortcodes(self):
		start_time = time.time()
		self.log.info("Initializing Unprompted shortcode parser...")
		# Reset variables for reload support
		self.shortcode_objects = {}
		self.shortcode_modules = {}
		self.shortcode_user_vars = {}
		self.cleanup_routines = []
		self.after_routines = []

		# Load shortcodes
		import importlib.util

		all_shortcodes = glob.glob(self.base_dir + self.Config.base_dir + "/" + self.Config.subdirectories.shortcodes + "/**/*.py", recursive=True)
		for file in all_shortcodes:
			shortcode_name = os.path.basename(file).split(".")[0]

			# Import shortcode as module
			spec = importlib.util.spec_from_file_location(shortcode_name, file)
			self.shortcode_modules[shortcode_name] = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(self.shortcode_modules[shortcode_name])

			# Create handlers dynamically
			self.shortcode_objects[shortcode_name] = self.shortcode_modules[shortcode_name].Shortcode(self)

			if (hasattr(self.shortcode_objects[shortcode_name], "run_atomic")):
				if hasattr(self.shortcode_objects[shortcode_name], "run_preprocess"):

					def preprocess(keyword, pargs, kwargs, context):
						return (self.shortcode_objects[f"{keyword}"].run_preprocess(pargs, kwargs, context))

					@shortcodes.register(shortcode_name, None, preprocess)
					def handler(keyword, pargs, kwargs, context):
						self.prep_for_shortcode(keyword,pargs,kwargs,context)
						return (self.shortcode_objects[f"{keyword}"].run_atomic(pargs, kwargs, context))

				# Normal atomic
				else:

					@shortcodes.register(shortcode_name)
					def handler(keyword, pargs, kwargs, context):
						self.prep_for_shortcode(keyword,pargs,kwargs,context)
						return (self.shortcode_objects[f"{keyword}"].run_atomic(pargs, kwargs, context))
			else:
				# Allow shortcode to run before inner content
				if hasattr(self.shortcode_objects[shortcode_name], "preprocess_block"):

					def preprocess(keyword, pargs, kwargs, context):
						return (self.shortcode_objects[f"{keyword}"].preprocess_block(pargs, kwargs, context))

					@shortcodes.register(shortcode_name, f"{self.Config.syntax.tag_close}{shortcode_name}", preprocess)
					def handler(keyword, pargs, kwargs, context, content):
						self.prep_for_shortcode(keyword,pargs,kwargs,context,content)
						return (self.shortcode_objects[f"{keyword}"].run_block(pargs, kwargs, context, content))

				# Normal block
				else:

					@shortcodes.register(shortcode_name, f"{self.Config.syntax.tag_close}{shortcode_name}")
					def handler(keyword, pargs, kwargs, context, content):
						self.prep_for_shortcode(keyword,pargs,kwargs,context,content)
						return (self.shortcode_objects[f"{keyword}"].run_block(pargs, kwargs, context, content))

			# Setup extra routines
			if (hasattr(self.shortcode_objects[shortcode_name], "cleanup")):
				self.cleanup_routines.append(shortcode_name)
			if (hasattr(self.shortcode_objects[shortcode_name], "after")):
				self.after_routines.append(shortcode_name)

			# Create descendent logger
			self.shortcode_objects[shortcode_name].log = self.log.getChild(shortcode_name)

			self.log.debug(f"Loaded shortcode: {shortcode_name}")

		self.shortcode_parser = shortcodes.Parser(start=self.Config.syntax.tag_start, end=self.Config.syntax.tag_end, esc=self.Config.syntax.tag_escape, ignore_unknown=True)
		self.log.info(f"Finished loading in {time.time()-start_time} seconds.")

	def __init__(self, base_dir="."):
		self.VERSION = "10.5.0"

		self.shortcode_modules = {}
		self.shortcode_objects = {}
		self.shortcode_user_vars = {}
		self.routine = "none"
		self.cleanup_routines = []
		self.after_routines = []
		self.base_dir = base_dir
		self.current_context = None

		self.cfg_dict, self.Config = parse_config(base_dir)

		class LogFormatter(logging.Formatter):
			def __init__(self, format_str, config):
				super().__init__(format_str)
				self.Config = config

			if self.Config.logging.use_colors:

				def format(self, record):
					def set_col_width(width=8, col_string="", new_string="", increment=None):
						if self.Config.logging.improve_alignment:
							if not new_string: new_string = col_string
							if not increment: increment = width
							while (len(col_string) > width):
								width += increment
							num_spaces = width - len(col_string)
							col_string = f"{new_string}{' ' * max(0,num_spaces)}"
						return col_string

					def colorize_log_string(col_seq, string):
						reset_seq = (self.Config.logging.colors.RESET).encode().decode("unicode-escape")
						col_seq = col_seq.encode().decode("unicode-escape")
						return f"{col_seq}{string}{reset_seq}"

					import copy
					colored_record = copy.copy(record)

					levelname = colored_record.levelname
					color_sequence = getattr(self.Config.logging.colors, levelname, self.Config.logging.colors.RESET)
					colored_levelname = f"({colorize_log_string(color_sequence,levelname)})"

					colored_record.levelname = set_col_width(8, levelname, colored_levelname)

					colored_name = colorize_log_string(self.Config.logging.colors.FADED, colored_record.name)

					colored_record.name = colored_name

					return super().format(colored_record)

		self.log = logging.getLogger("Unprompted")
		self.log.propagate = False
		self.log.setLevel(getattr(logging, self.Config.logging.level))

		if not self.log.handlers:
			if self.Config.logging.file:
				handler = logging.FileHandler(self.Config.logging.file, self.Config.logging.filemode)
			else:
				handler = logging.StreamHandler(sys.stdout)

			log_format = self.Config.logging.format
			handler.setFormatter(LogFormatter(log_format, self.Config))
			self.log.addHandler(handler)

		self.log.info(f"Loading Unprompted v{self.VERSION} by Therefore Games")
		self.load_shortcodes()

	def start(self, string, debug=True):
		if debug: self.log.debug("Loading global variables...")
		for global_var, value in self.Config.globals.__dict__.items():
			self.shortcode_user_vars[self.Config.syntax.global_prefix+global_var] = value
		if debug: self.log.debug("Main routine started...")
		self.routine = "main"
		self.conditional_depth = -1
		result = self.process_string(string)
		if debug: self.log.debug("Main routine completed.")
		return result

	def cleanup(self):
		self.log.debug("Cleanup routine started...")
		self.routine = "cleanup"
		self.conditional_depth = 0
		for i in self.cleanup_routines:
			self.shortcode_objects[i].cleanup()
		self.log.debug("Cleanup routine completed.")

	def after(self, p=None, processed=None):
		self.log.debug("After routine started...")
		self.routine = "after"
		for i in self.after_routines:
			val = self.shortcode_objects[i].after(p, processed)
			if val: processed = val
		self.log.debug("After routine completed.")
		return processed

	def process_string(self, string, context=None, cleanup_extra_spaces=None):
		if cleanup_extra_spaces==None: cleanup_extra_spaces = self.Config.syntax.cleanup_extra_spaces

		self.conditional_depth += 1
		if context: self.current_context = context
		# First, sanitize contents
		string = self.shortcode_parser.parse(self.sanitize_pre(string, self.Config.syntax.sanitize_before), context)
		self.conditional_depth = max(0, self.conditional_depth -1)
		return (self.sanitize_post(string, cleanup_extra_spaces))

	def sanitize_pre(self, string, rules_obj, only_remove_last=False):
		for k, v in rules_obj.__dict__.items():
			if only_remove_last: v.join(string.rsplit(k, 1))
			else: string = string.replace(k, v)
		return (string)

	def sanitize_post(self, string, cleanup_extra_spaces=True):
		# Final sanitization routine
		sanitization_items = self.Config.syntax.sanitize_after.__dict__.items()
		for k, v in sanitization_items:
			string = helpers.strip_str(string, k)
		for k, v in sanitization_items:
			string = string.replace(k, v)
		if cleanup_extra_spaces: string = " ".join(string.split())  # Cleanup extra spaces
		return (string)

	def parse_filepath(self, string_orig, context="", root=None, must_exist=True):
		import random

		# Replace placeholders
		string = self.str_replace_macros(string_orig)

		# Relative path
		if (string[0] == "."):
			string = os.path.dirname(context) + "/" + string
			self.log.debug(f"Transformed relative path from \"{string_orig}\" to \"{string}\"")
		# Absolute path
		elif (os.path.isabs(string)):
			self.log.debug(f"Transformed absolute path from \"{string_orig}\" to \"{string}\"")
		# Internal (Unprompted) path
		else:
			if root is None: root = self.base_dir + "/" + self.Config.template_directory
			string = root + "/" + string
			self.log.debug(f"Transformed internal path from \"{string_orig}\" to \"{string}\"")

		files = glob.glob(string)
		filecount = len(files)
		if (filecount == 0):
			if must_exist:
				self.log.error(f"No files found at this location: {string}")
				return ("")
			else:
				return (string)
		elif filecount > 1:
			string = random.choice(files)

		return (string)

	def prep_for_shortcode(self, keyword, pargs, kwargs, context, content=""):
		"""Stores information about a shortcode into the Unprompted object for ease of access."""
		self.keyword = keyword
		self.pargs = pargs
		self.kwargs = kwargs
		self.context = context
		self.content = content
	
	def parse_arg(self, key, default=False, datatype=None, context=None, pargs=None, kwargs=None, arithmetic=True, delimiter=None):
		"""Processes the argument, casting it to the correct datatype."""
		# Load defaults from the Unprompted object
		# Note: You can manually set these to False
		if context == None: context = self.context
		if pargs == None: pargs = self.pargs
		if kwargs == None: kwargs = self.kwargs
		if delimiter == None: delimiter = self.Config.syntax.delimiter

		# If a datatype is not specified, we refer to the type of the default value
		if not datatype:
			datatype = type(default)

		if pargs and key in pargs:
			return True
		elif kwargs and key in kwargs:
			if arithmetic: default = self.parse_advanced(str(kwargs[key]),context)
			else: default = self.parse_alt_tags(str(kwargs[key]),context)
			if delimiter:
				try:
					# We will cast the value to a string so that we can split it, but
					# each index of the list will be cast back later
					str_val = str(default)
					if delimiter in str_val:
						default = str_val.split(delimiter)
				except:
					self.log.warning(f"Unable to split the kwarg {key} by the delimiter {delimiter}")
					pass

		try:
			if type(default) == list:
				for idx,val in enumerate(default):
					default[idx] = datatype(val)
			else:
				default = datatype(default)
		except ValueError:
			self.log.warning(f"Could not cast {default} to {datatype}.")
			pass

		return default

	
	def parse_advanced(self, string, context=None):
		"""First runs the string through parse_alt_tags, the result of which then goes through simpleeval"""
		if string is None: return ""
		
		if (len(string) < 1): return ""
		string = self.parse_alt_tags(string, context)
		if self.Config.advanced_expressions:
			try:
				return (helpers.autocast(simple_eval(string, names=self.shortcode_user_vars)))
			except:
				return (string)
		else:
			return (string)

	def parse_alt_tags(self, string, context=None, parser=None):
		"""Converts any alt tags and then parses the resulting shortcodes"""
		if string is None or len(string) < 1: return ""
		if parser is None: parser = self.shortcode_parser
		# Find maximum nested depth
		nested = 0
		while True:
			start_tag = self.Config.syntax.tag_start_alt * (nested + 1)
			if start_tag in string:
				nested += 1
			else:
				break

		tmp_start = "%_ts%"
		tmp_end = "%_te%"
		for i in range(nested, 0, -1):
			# Lower nested level by 1
			if i > 1:
				start_old = self.Config.syntax.tag_start_alt * i
				start_new = tmp_start * (i - 1)
				end_old = self.Config.syntax.tag_end_alt * i
				end_new = tmp_end * (i - 1)
			# Convert secondary tag to square bracket
			else:
				start_old = self.Config.syntax.tag_start_alt
				start_new = self.Config.syntax.tag_start
				end_old = self.Config.syntax.tag_end_alt
				end_new = self.Config.syntax.tag_end

			string = string.replace(start_old, start_new).replace(end_old, end_new)

		# Get rid of the temporary characters
		string = string.replace(tmp_start, self.Config.syntax.tag_start_alt).replace(tmp_end, self.Config.syntax.tag_end_alt)

		return (parser.parse(string, context))
	
	def make_alt_tags(self, string):
		"""Similar to parse_alt_tags, but in reverse; converts square brackets to nested alt tags."""
		if string is None or len(string) < 1: return ""
		
		# Find maximum nested depth
		nested = 0
		while True:
			start_tag = self.Config.syntax.tag_start_alt * (nested + 1)
			if start_tag in string:
				nested += 1
			else:
				break

		tmp_start = "%_ts%"
		tmp_end = "%_te%"
		for i in range(nested, 0, -1):
			# Increase nested level by 1
			start_old = self.Config.syntax.tag_start_alt * i
			start_new = tmp_start * (i + 1)
			end_old = self.Config.syntax.tag_end_alt * i
			end_new = tmp_end * (i + 1)

			string = string.replace(start_old, start_new).replace(end_old, end_new)
		
		# Convert primary square bracket tag to alt tag
		string = string.replace(self.Config.syntax.tag_start, self.Config.syntax.tag_start_alt).replace(self.Config.syntax.tag_end, self.Config.syntax.tag_end_alt)

		# Get rid of the temporary characters
		string = string.replace(tmp_start, self.Config.syntax.tag_start_alt).replace(tmp_end, self.Config.syntax.tag_end_alt)

		return (string)

	def is_system_arg(self, string):
		if (string[0] == "_"): return (True)
		return (False)

	def color_match(self, img_ref, img_src, method="hm-mkl-hm", iterations=1):
		from color_matcher import ColorMatcher
		from color_matcher.normalizer import Normalizer
		from PIL import Image
		import numpy
		cm = ColorMatcher()
		img_ref = Normalizer(numpy.array(img_ref)).uint8_norm()
		img_src = Normalizer(numpy.array(img_src)).uint8_norm()
		for i in range(iterations):
			img_src = cm.transfer(src=img_src, ref=img_ref, method=method)
		return (Image.fromarray(Normalizer(img_src).uint8_norm()))

	def shortcode_var_is_true(self, key, pargs, kwargs, context=None):
		if key in pargs: return True
		if key in kwargs and self.parse_advanced(kwargs[key], context): return True
		return False

	def load_jsons(self, paths, context=None):
		import json
		json_obj = {}
		jsons = paths.split(self.Config.syntax.delimiter)
		for this_json in jsons:
			filepath = self.parse_filepath(this_json, context, root=self.base_dir)
			json_obj = json.load(open(f"{filepath}", "r", encoding=self.Config.formats.default_encoding))
			# Delimiter support
			for key, val in json_obj.copy().items():
				keys = key.split(self.Config.syntax.delimiter)
				if len(keys) > 1:
					for key_part in keys:
						json_obj[key_part] = val
					del json_obj[key]
		return (json_obj)

	def update_controlnet_var(self, this_p, att):
		try:
			att_split = att.split("_")  # e.g. controlnet_0_enabled
			if len(att_split) >= 3 and any(chr.isdigit() for chr in att):  # Make sure we have at least 2 underscores and at least one number
				self.log.debug(f"Setting ControlNet value: {att}")
				cn_path = self.extension_path(self.Config.stable_diffusion.controlnet.extension)
				cnet = helpers.import_file(f"{self.Config.stable_diffusion.controlnet.extension}.scripts.external_code", f"{cn_path}/scripts/external_code.py")

				all_units = cnet.get_all_units_in_processing(this_p)

				if att_split[2] == "image":
					# Check if we supplied a string
					if isinstance(self.shortcode_user_vars[att], str):
						import imageio
						this_val = imageio.imread(self.str_replace_macros(self.shortcode_user_vars[att]))
					# Otherwise, assume we supplied a PIL image and convert to numpy
					else:
						import numpy
						this_val = numpy.array(self.shortcode_user_vars[att])
				else:
					this_val = self.shortcode_user_vars[att]
					# Apply preset model names
					if att_split[2] == "model":
						if self.shortcode_user_vars["sd_base"]== "sd1": cn_dict = self.Config.stable_diffusion.controlnet.sd1_models
						elif self.shortcode_user_vars["sd_base"] == "sdxl": cn_dict = self.Config.stable_diffusion.controlnet.sdxl_models

						if hasattr(cn_dict,this_val):
							this_val = getattr(cn_dict, this_val)
				setattr(all_units[int(att_split[1])], "_".join(att_split[2:]), this_val)
				cnet.update_cn_script_in_processing(this_p, all_units)
		except Exception as e:
			self.log.error(f"Could not set ControlNet value ({att}): {e}")

	def update_user_vars(self, this_p, user_vars=None):
		if not user_vars: user_vars = self.shortcode_user_vars
		# Set up system var support - copy relevant p attributes into shortcode var object
		for att in dir(this_p):
			if not att.startswith("__") and att not in ["sd_model", "batch_count_index", "batch_size_index", "extra_network_data"]:
				# self.log.debug(f"Setting {att} to {getattr(this_p, att)}")
				user_vars[att] = getattr(this_p, att)

	def update_stable_diffusion_vars(self, this_p):
		from modules import sd_models

		self.log.debug("Synchronizing Stable Diffusion variables with Unprompted...")

		p_dir = dir(this_p)
		for att in self.shortcode_user_vars:
			if att in p_dir and att != "sd_model":
				try:
					setattr(this_p, att, self.shortcode_user_vars[att])
				except Exception as e:
					self.log.exception(f"Exception while trying to update the Stable Diffusion attr: {att}")
			elif att == "sd_model" and self.shortcode_user_vars[att] != self.original_model and isinstance(self.shortcode_user_vars[att], str):
				info = sd_models.get_closet_checkpoint_match(self.shortcode_user_vars["sd_model"])
				if info:
					new_model = sd_models.load_model(info, None)  #, None
					self.shortcode_user_vars["sd_base"] = "none"
					if new_model:
						# Update `sd_base` special variable
						try:  # temporary workaround for sd.next lacking these variables
							if new_model.is_sdxl: self.shortcode_user_vars["sd_base"] = "sdxl"
							elif new_model.is_sd2: self.shortcode_user_vars["sd_base"] = "sd2"
							elif new_model.is_sd1: self.shortcode_user_vars["sd_base"] = "sd1"
						except:
							pass
			elif att == "sd_vae":
				from modules import sd_vae
				info = sd_vae.find_vae_near_checkpoint(self.shortcode_user_vars[att])
				if info:
					sd_vae.reload_vae_weights(None, info)
			# control controlnet
			elif att.startswith("controlnet_") or att.startswith("cn_"):
				self.update_controlnet_var(this_p, att)

	def batch_test_bypass(self, batch_idx):
		"""This is used by shortcodes that implement batch processing to determine if we should skip a certain image per the expression stored in the batch_test user var."""
		if "batch_test" in self.shortcode_user_vars and self.shortcode_user_vars["batch_test"] and not simple_eval(f"{batch_idx} {self.shortcode_user_vars['batch_test']}", names=self.shortcode_user_vars):
			self.log.debug(f"Bypassing this batch item per batch_test expression: {batch_idx} is not {self.shortcode_user_vars['batch_test']}")
			return True
		return False

	def extension_path(self, name, allow_disabled=False):
		"""Traverses the modules.extensions list to check for presence of an extension with a given name. If found, returns the full path of the extension."""
		from modules import extensions
		for e in extensions.extensions:
			if e.name == name:
				if e.enabled or allow_disabled:
					return (e.path)
				else:
					self.log.warning(f"Extension {name} found but is not enabled.")
					return None
		return None

	def is_var_deprecated(self, var_name):
		deprecated_vars = {}
		deprecated_vars["batch_index"] = "batch_count_index"

		if var_name in deprecated_vars:
			if self.Unprompted.Config.logging.deprecated_warnings: self.log.warning(f"The variable {var_name} is deprecated! You may want to use {deprecated_vars[var_name]} instead.")
			return True

		return False

	def prevent_else(self, else_id=None):
		if not else_id: else_id = self.conditional_depth
		self.shortcode_objects["else"].do_else[str(else_id)] = False

	def str_replace_macros(self, string):
		return string.replace("%BASE_DIR%", self.base_dir)

	def current_image(self, new_image=None, update_init_images=True):
		"""Gets or sets an image for shortcode processing depending on the context."""
		idx = self.shortcode_user_vars["batch_real_index"] if "batch_real_index" in self.shortcode_user_vars else 0
		try:
			if self.routine == "after":
				if new_image:
					self.after_processed.images[idx] = new_image
				else: return self.after_processed.images[idx]
			elif "init_images" in self.shortcode_user_vars and self.shortcode_user_vars["init_images"]:
				if new_image:
					self.shortcode_user_vars["init_images"][idx] = new_image
				else: return self.shortcode_user_vars["init_images"][idx]
			elif "default_image" in self.shortcode_user_vars:
				if new_image:
					self.shortcode_user_vars["default_image"] = new_image
				else: return self.shortcode_user_vars["default_image"]
		except Exception as e:
			self.log.exception("Could not find the current image.")
			return None

		if new_image:
			if update_init_images:
				# Resize the mask to match the new image if necessary
				if "image_mask" in self.shortcode_user_vars and self.shortcode_user_vars["image_mask"]:
					self.log.debug(f"Detected `image_mask`. Ensuring it matches the size of our new image...")
					self.shortcode_user_vars["image_mask"] = self.shortcode_user_vars["image_mask"].resize(new_image.size)

				if self.routine == "after":
					self.shortcode_user_vars["init_images"][idx] = self.after_processed.images[idx]
				
				# Update the SD vars if Unprompted.main_p exists
				#if hasattr(self, "main_p"):
				#	self.update_stable_diffusion_vars(self.main_p)
			return True
		return None

	def escape_tags(self, string, new_start = None, new_end = None):
		if not new_start: new_start = self.Config.syntax.tag_escape+self.Config.syntax.tag_start_alt
		if not new_end: new_end = self.Config.syntax.tag_escape+self.Config.syntax.tag_end_alt
		# self.log.warning(f"string is {string}")
		# self.log.warning(f"string after replacing is {string.replace(self.Config.syntax.tag_start,new_start).replace(self.Config.syntax.tag_end,new_end)}")
		return string.replace(self.Config.syntax.tag_start,new_start).replace(self.Config.syntax.tag_end,new_end)