import json
from types import SimpleNamespace
import lib_unprompted.shortcodes as shortcodes
from lib_unprompted.simpleeval import simple_eval
import os
import glob
import importlib
import inspect
import sys

class Unprompted:
	def __init__(self, base_dir="."):
		self.VERSION = "7.0.0"

		print(f"(Unprompted v{self.VERSION} by Therefore Games)")
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

		self.log(f"Debug mode is {self.Config.debug}",False,"SETUP")
		
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
				@shortcodes.register(shortcode_name)
				def handler(keyword, pargs, kwargs, context):
					return(self.shortcode_objects[f"{keyword}"].run_atomic(pargs, kwargs, context))
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
	
	def shortcode_string_log(self):
		return("["+os.path.basename(inspect.stack()[1].filename)+"]")

	def process_string(self, string, context=None):
		# First, sanitize contents
		for k,v in self.Config.syntax.sanitize_before.__dict__.items():
			string = string.replace(k,v)
		string = self.shortcode_parser.parse(string,context)

		# Final sanitization routine
		sanitization_items = self.Config.syntax.sanitize_after.__dict__.items()
		for k,v in sanitization_items:
			string = self.strip_str(string,k)
		for k,v in sanitization_items:
			string = string.replace(k,v)

		string = " ".join(string.split()) # Cleanup extra spaces
		return(string)

	def parse_filepath(self,string,context = ""):
		# Relative path
		if (string[0] == "."):
			string = os.path.dirname(context) + "/" + string
		# Absolute path
		else: string = self.base_dir + "/" + self.Config.template_directory + "/" + string
		return(string)

	def parse_advanced(self,string,context=None):
		"""First runs the string through parse_alt_tags, the result of which then goes through simpleeval"""
		string = self.parse_alt_tags(string,context)
		if self.Config.advanced_expressions:
			try:
				return(self.autocast(simple_eval(string,names=self.shortcode_user_vars)))
			except: return(string)
		else: return(string)
		

	def parse_alt_tags(self,string,context=None):
		"""Converts any alt tags and then parses the resulting shortcodes"""

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

		return(self.shortcode_parser.parse(string,context))
	
	def log(self,string,show_caller=True,context="DEBUG"):
		if (context != "DEBUG" or self.Config.debug):
			this_string = f"({context})"
			if show_caller: this_string += " ["+os.path.relpath(inspect.stack()[1].filename,__file__).replace("..\\","")+"]"
			this_string += f" {string}"
			print(this_string)
	
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
		if (self.is_float(var)):
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