class Shortcode():
	'''Returns the number of items in a delimited string.'''
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted

	def run_atomic(self, pargs, kwargs, context):
		_delimiter = self.Unprompted.parse_advanced(kwargs["_delimiter"],context) if "_delimiter" in kwargs else self.Unprompted.Config.syntax.delimiter
		_max = self.Unprompted.parse_advanced(kwargs["_max"],context) if "_max" in kwargs else -1
		strings = pargs[0].split(_delimiter,_max)
		return(len(strings))