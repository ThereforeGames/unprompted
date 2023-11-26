class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Cast the content to a given datatype."

	def run_block(self, pargs, kwargs, context, content):
		if len(pargs):
			datatype = self.Unprompted.parse_alt_tags(pargs[0],context)

			def to_int(val):
				return int(float(val))

			valid_functions = {
				"int": to_int,
				"float": float,
				"str": str,
				"bool": bool,
				"list": list,
				"dict": dict,
				# Add more casting functions as needed
			}

			try:
				# Check if the datatype is a built-in function
				if datatype in valid_functions:
					return valid_functions[datatype](content)
				else:
					self.log.error(f"Invalid datatype `{datatype}` - returning `content` unchanged.")
					return content
			except Exception as e:
				self.log.error(f"Error casting `{content}` to `{datatype}`: {e}")
				return content
		else:
			self.log.error("No datatype specified - returning `content` unchanged.")
			return content

	def ui(self,gr):
		gr.Textbox(label="New datatype 🡢 str",choices=["str","int","float","bool","list","dict"],default="str")