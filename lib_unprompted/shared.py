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

class Unprompted:
	def __init__(self, base_dir="."):
		start_time = time.time()
		self.VERSION = "9.5.1"

		self.log(f"Loading Unprompted v{self.VERSION} by Therefore Games",False,"SETUP")
		self.log("Initializing Unprompted object...",False,"SETUP")

		self.shortcode_modules = {}
		self.shortcode_objects = {}
		self.shortcode_user_vars = {}
		self.cleanup_routines = []
		self.after_routines = []
		self.base_dir = base_dir

		self.log("Loading configuration files...",False,"SETUP")

		self.cfg_dict = json.load(open(f"{base_dir}/config.json", "r", encoding="utf8"))
		user_config = f"{base_dir}/config_user.json"
		if (os.path.isfile(user_config)):
			import lib_unprompted.flatdict as flatdict
			flat_user_cfg =  flatdict.FlatDict(json.load(open(user_config,"r",encoding="utf8")))
			flat_cfg = flatdict.FlatDict(self.cfg_dict)
			
			# Write differences to flattened dictionary
			flat_cfg.update(flat_user_cfg)

			# Unflatten
			self.cfg_dict = flat_cfg.as_dict()
		self.Config = json.loads(json.dumps(self.cfg_dict), object_hook=lambda d: SimpleNamespace(**d))

		self.log(f"Logging enabled for the following message types: {self.Config.log_contexts}",False,"SETUP")
		self.Config.log_contexts = self.Config.log_contexts.split(",")
		
		
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

			if (hasattr(self.shortcode_objects[shortcode_name],"run_atomic")):
				if hasattr(self.shortcode_objects[shortcode_name],"run_preprocess"):
					def preprocess(keyword, pargs, kwargs, context):
						return(self.shortcode_objects[f"{keyword}"].run_preprocess(pargs, kwargs, context))
					@shortcodes.register(shortcode_name, None, preprocess)
					def handler(keyword, pargs, kwargs, context):
						return(self.shortcode_objects[f"{keyword}"].run_atomic(pargs, kwargs, context))					
				# Normal atomic
				else:
					@shortcodes.register(shortcode_name)
					def handler(keyword, pargs, kwargs, context):
						return(self.shortcode_objects[f"{keyword}"].run_atomic(pargs, kwargs, context))
			else:
				# Allow shortcode to run before inner content
				if hasattr(self.shortcode_objects[shortcode_name],"preprocess_block"):
					def preprocess(keyword, pargs, kwargs, context):
						return(self.shortcode_objects[f"{keyword}"].preprocess_block(pargs, kwargs, context))
					@shortcodes.register(shortcode_name, f"{self.Config.syntax.tag_close}{shortcode_name}", preprocess)
					def handler(keyword, pargs, kwargs, context, content):
						return(self.shortcode_objects[f"{keyword}"].run_block(pargs, kwargs, context, content))
				# Normal block
				else:
					@shortcodes.register(shortcode_name, f"{self.Config.syntax.tag_close}{shortcode_name}")
					def handler(keyword, pargs, kwargs, context, content):
						return(self.shortcode_objects[f"{keyword}"].run_block(pargs, kwargs, context, content))
			
			# Setup extra routines
			if (hasattr(self.shortcode_objects[shortcode_name],"cleanup")):
				self.cleanup_routines.append(shortcode_name)
			if (hasattr(self.shortcode_objects[shortcode_name],"after")):
				self.after_routines.append(shortcode_name)

			self.log(f"Loaded shortcode: {shortcode_name}",False)

		self.shortcode_parser = shortcodes.Parser(start=self.Config.syntax.tag_start, end=self.Config.syntax.tag_end, esc=self.Config.syntax.tag_escape, ignore_unknown=True)
		self.log(f"Unprompted finished loading in {time.time()-start_time} seconds.",False)
	
	def shortcode_string_log(self):
		return("["+os.path.basename(inspect.stack()[1].filename)+"]")

	def process_string(self, string, context=None, cleanup_extra_spaces=True):
		# First, sanitize contents
		string = self.shortcode_parser.parse(self.sanitize_pre(string,self.Config.syntax.sanitize_before),context)
		return(self.sanitize_post(string,cleanup_extra_spaces))

	def sanitize_pre(self, string, rules_obj,only_remove_last=False):
		for k,v in rules_obj.__dict__.items():
			if only_remove_last: v.join(string.rsplit(k, 1))
			else: string = string.replace(k,v)
		return(string)
	
	def sanitize_post(self, string, cleanup_extra_spaces=True):
		# Final sanitization routine
		sanitization_items = self.Config.syntax.sanitize_after.__dict__.items()
		for k,v in sanitization_items:
			string = self.strip_str(string,k)
		for k,v in sanitization_items:
			string = string.replace(k,v)
		if cleanup_extra_spaces: string = " ".join(string.split()) # Cleanup extra spaces
		return(string)

	def parse_filepath(self,string,context = "",root=None):
		import random
		# Relative path
		if (string[0] == "."):
			string = os.path.dirname(context) + "/" + string
		# Absolute path
		else:
			if root is None: root = self.base_dir+"/"+self.Config.template_directory
			string = root + "/" + string

		files = glob.glob(string)
		filecount = len(files)
		if (filecount == 0):
			self.log(f"No files found at this location: {string}",True,"ERROR")
			return("")
		elif filecount > 1:
			string = random.choice(files)

		return(string)

	def parse_advanced(self,string,context=None):
		"""First runs the string through parse_alt_tags, the result of which then goes through simpleeval"""
		if string is None: return ""
		if (len(string) < 1): return ""
		string = self.parse_alt_tags(string,context)
		if self.Config.advanced_expressions:
			try:
				return(self.autocast(simple_eval(string,names=self.shortcode_user_vars)))
			except: return(string)
		else: return(string)
		

	def parse_alt_tags(self,string,context=None,parser=None):
		"""Converts any alt tags and then parses the resulting shortcodes"""
		if string is None or len(string) < 1: return ""
		if parser is None: parser = self.shortcode_parser
		# Find maximum nested depth
		nested = 0
		while True:
			start_tag = self.Config.syntax.tag_start_alt * (nested + 1)
			if start_tag in string:
				nested += 1
			else: break
		
		tmp_start = "%_ts%"
		tmp_end = "%_te%"
		for i in range(nested,0,-1):
			# Lower nested level by 1
			if i > 1:
				start_old = self.Config.syntax.tag_start_alt * i
				start_new = tmp_start * (i-1)
				end_old = self.Config.syntax.tag_end_alt * i
				end_new = tmp_end * (i-1)
			# Convert secondary tag to square bracket
			else:
				start_old = self.Config.syntax.tag_start_alt
				start_new = self.Config.syntax.tag_start
				end_old = self.Config.syntax.tag_end_alt
				end_new = self.Config.syntax.tag_end

			string = string.replace(start_old,start_new).replace(end_old,end_new)		

		# Get rid of the temporary characters
		string = string.replace(tmp_start,self.Config.syntax.tag_start_alt).replace(tmp_end,self.Config.syntax.tag_end_alt)

		return(parser.parse(string,context))
	
	def log(self,string,show_caller=True,context="DEBUG",caller=None):
		if (context=="SETUP" or context in self.Config.log_contexts or "ALL" in self.Config.log_contexts):
			this_string = f"({context})"
			if show_caller:
				if caller is None: caller = " ["+os.path.relpath(inspect.stack()[1].filename,__file__).replace("..\\","")+"]"
				this_string += caller
			this_string += f" {string}"
			print(this_string)

	def log_error(self,e, msg=""):
		import traceback
		self.log(msg + ''.join(traceback.TracebackException.from_exception(e).format()),context="ERROR",caller=" ["+os.path.relpath(inspect.stack()[1].filename,__file__).replace("..\\","")+"]")

	def strip_str(self,string,chop):
		while True:
			if chop and string.endswith(chop):
				string = string[:-len(chop)]
			else: break
		while True:
			if chop and string.startswith(chop):
				string = string[len(chop):]
			else: break
		return string

	def is_system_arg(self,string):
		if (string[0] == "_"): return(True)
		return(False)

	def is_equal(self,var_a,var_b):
		"""Checks if two variables equal each other, taking care to account for datatypes."""
		if (self.is_float(var_a)): var_a = float(var_a)
		if (self.is_float(var_b)): var_b = float(var_b)
		if (str(var_a) == str(var_b)): return True
		else: return False
	
	def is_not_equal(self,var_a,var_b):
		return not self.is_equal(var_a,var_b)

	def is_float(self,value):
		try:
			float(value)
			return True
		except:
			return False

	def is_int(self,value):
		try:
			int(value)
			return True
		except:
			return False

	def autocast(self,var):
		"""Converts a variable between string, int, and float depending on how it's formatted"""
		original_var = var
		if original_var == "inf" or original_var == "-inf": return(original_var)
		elif (self.is_float(var)):
			var = float(var)
			if int(var) == var and "." not in str(original_var): var = int(var)
		elif (self.is_int(var)): var = int(var)
		return(var)
	
	def download_file(self,filename, url):
		import requests
		with open(filename,'wb') as fout:
			response = requests.get(url, stream=True)
			response.raise_for_status()
			# Write response data to file
			for block in response.iter_content(4096):
				fout.write(block)

	def color_match(self,img_ref,img_src,method="hm-mkl-hm",iterations=1):
		from color_matcher import ColorMatcher
		from color_matcher.normalizer import Normalizer
		from PIL import Image
		import numpy
		cm = ColorMatcher()
		img_ref = Normalizer(numpy.array(img_ref)).uint8_norm()
		img_src = Normalizer(numpy.array(img_src)).uint8_norm()
		for i in range(iterations):
			img_src = cm.transfer(src=img_src, ref=img_ref, method=method)
		return(Image.fromarray(Normalizer(img_src).uint8_norm()))

	def shortcode_var_is_true(self,key,pargs,kwargs,context=None):
		if key in pargs: return True
		if key in kwargs and self.parse_advanced(kwargs[key],context): return True
		return False
	
	def load_jsons(self,paths,context=None):
		import json
		json_obj = {}
		jsons = paths.split(self.Config.syntax.delimiter)
		for this_json in jsons:
			filepath = self.parse_filepath(this_json,context,root=self.base_dir)
			json_obj = json.load(open(f"{filepath}", "r", encoding="utf8"))
			# Delimiter support
			for key,val in json_obj.copy().items():
				keys = key.split(self.Config.syntax.delimiter)
				if len(keys) > 1:
					for key_part in keys: json_obj[key_part] = val
					del json_obj[key]
		return(json_obj)

	def update_controlnet_var(self,this_p,att):
		try:
			att_split = att.split("_") # e.g. controlnet_0_enabled
			if len(att_split) >= 3 and any(chr.isdigit() for chr in att): # Make sure we have at least 2 underscores and at least one number
				self.log(f"Setting ControlNet value: {att}")
				import importlib
				cnet = importlib.import_module("extensions.sd-webui-controlnet.scripts.external_code", "external_code")
				all_units = cnet.get_all_units_in_processing(this_p)

				if att_split[2] == "image":
					import imageio
					this_val = imageio.imread(self.shortcode_user_vars[att])
				else: 
					this_val = self.shortcode_user_vars[att]
				setattr(all_units[int(att_split[1])],"_".join(att_split[2:]),this_val)
				cnet.update_cn_script_in_processing(this_p, all_units)
		except Exception as e:
			self.log(f"Could not set ControlNet value ({att}): {e}",context="ERROR")
	
	def update_stable_diffusion_vars(self,this_p):
		from modules import sd_models

		# Apply any updates to system vars
		for att in dir(this_p):
			if not att.startswith("__") and att != "sd_model" and att in self.shortcode_user_vars:
				try:
					setattr(this_p,att,self.shortcode_user_vars[att])
				except Exception as e:
					self.log_error(e,"Could not update Stable Diffusion attr: ")
		
		# Special handling of vars
		for att in self.shortcode_user_vars:
			# change models
			if att == "sd_model" and self.shortcode_user_vars[att] != self.original_model and isinstance(self.shortcode_user_vars[att],str):
				info = sd_models.get_closet_checkpoint_match(self.shortcode_user_vars["sd_model"])
				if info: sd_models.load_model(info,None,None)
			# control controlnet
			elif att.startswith("controlnet_") or att.startswith("cn_"):
				self.update_controlnet_var(this_p,att)