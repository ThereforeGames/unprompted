class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Updates a string using the arguments for replacement logic."
	def run_block(self, pargs, kwargs, context, content):
		
		_insensitive = self.Unprompted.shortcode_var_is_true("_insensitive",pargs,kwargs)

		if "_load" in kwargs:
			jsons = self.Unprompted.load_jsons(self.Unprompted.parse_advanced(kwargs["_load"],context),context)
			kwargs.update(jsons)
		
		for key, value in kwargs.items():
			if (key == "_from"):
				from_value = self.Unprompted.parse_advanced(value,context)
				to_value = self.Unprompted.parse_advanced(kwargs["_to"] if "_to" in kwargs else "",context)
			elif (key[0] != "_"):
				from_value = self.Unprompted.parse_advanced(key,context) # key
				to_value = self.Unprompted.parse_advanced(value,context)
			else: continue

			if _insensitive:
				import re
				_count = int(float(kwargs["_count"])) if "_count" in kwargs else 0
				compiled = re.compile(re.escape(from_value), re.IGNORECASE)
				content = compiled.sub(to_value, content, count=_count)
			else:
				if ("_count" in kwargs): content = content.replace(from_value,to_value,self.Unprompted.parse_advanced(kwargs["_count"]))
				else: content = content.replace(from_value,to_value)

		return(content)

	def ui(self,gr):
		gr.Textbox(label="Arbitrary replacement arguments in old=new format 🡢 verbatim",max_lines=1,placeholder='hello="goodbye" red="blue"')
		gr.Textbox(label="Original value, with advanced expression support 🡢 _from",max_lines=1)
		gr.Textbox(label="New value, with advanced expression support 🡢 _to",max_lines=1)
		gr.Textbox(label="Path to one or more JSON files containing from:to replacement data 🡢 ldata",max_lines=1)
		gr.Number(label="Maximum number of times the replacement may occur 🡢 _count",max_lines=1,value=-1)