class Shortcode():
	"""Returns various types of metadata about the content."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_block(self, pargs, kwargs, context, content):
		return_string = ""
		delimiter = ","

		if "character_count" in pargs: return_string += str(len(content)) + delimiter
		if "word_count" in pargs: return_string += str(len(content.split())) + delimiter
		if "string_count" in kwargs: return_string += str(content.count(kwargs["string_count"])) + delimiter

		return(return_string[:-1])