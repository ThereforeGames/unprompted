import lib.casefy as casefy
class Shortcode():
	"""Converts the casing of content."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted

	def run_block(self, pargs, kwargs, context, content):
		if (pargs[0] == "camelcase"): return casefy.camelcase(content)
		elif (pargs[0] == "uppercase"): return content.upper()
		elif (pargs[0] == "lowercase"): return content.lower()
		elif (pargs[0] == "pascalcase"): return casefy.pascalcase(content)
		elif (pargs[0] == "snakecase"): return casefy.snakecase(content)
		elif (pargs[0] == "constcase"): return casefy.constcase(content)
		elif (pargs[0] == "kebabcase"): return casefy.kebabcase(content)
		elif (pargs[0] == "upperkebabcase"): return casefy.upperkebabcase(content)
		elif (pargs[0] == "separatorcase"): return casefy.separatorcase(content)
		elif (pargs[0] == "sentencecase"): return casefy.sentencecase(content)
		elif (pargs[0] == "titlecase"): return casefy.titlecase(content)
		elif (pargs[0] == "alphanumcase"): return casefy.alphanumcase(content)
		
		# No matching conversion found
		return content