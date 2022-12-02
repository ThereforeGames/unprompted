import operator
from lib.simpleeval import simple_eval
class Shortcode():
	"""Loops content until the condition returns false."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.ops = {"==":self.Unprompted.is_equal,"!=":self.Unprompted.is_not_equal,"<":operator.lt,"<=":operator.le,">":operator.gt,">=":operator.ge}
	
	def run_block(self, pargs, kwargs, context,content):
		final_string = ""

		_not = "_not" in pargs
		_any = "_any" in pargs

		is_true = not _any

		_is = kwargs["_is"] if "_is" in kwargs else "=="

		do_advanced_expression = False

		while True:
			for key in pargs:
				if (key[0] == "_"): continue # Skips system arguments
				do_advanced_expression = True
				if (simple_eval(key,names=self.Unprompted.shortcode_user_vars)):
					if _any:
						is_true = True
						break
				elif not _any:
					is_true = False
				break

			if not do_advanced_expression:
				for key, value in kwargs.items():
					if (key[0] == "_"): continue # Skips system arguments

					this_value = self.Unprompted.parse_alt_tags(value,context)

					# Fix data type
					if (_is != "=="):
						self.Unprompted.shortcode_user_vars[key] = float(self.Unprompted.shortcode_user_vars[key])
						this_value = float(this_value)				

					if (self.ops[_is](self.Unprompted.shortcode_user_vars[key],this_value)):
						if _any:
							is_true = True
							break
					elif not _any:
						is_true = False
					break

			if ((is_true and not _not) or (_not and not is_true)):
				final_string += self.Unprompted.parse_alt_tags(content,context)
			else:
				break
			
		return(final_string)				