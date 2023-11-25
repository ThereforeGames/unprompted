class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Rounds a given number to a certain level of precision. Works with integers and floats."

	def run_atomic(self, pargs, kwargs, context):
		import math
		import lib_unprompted.helpers as helpers
		if not len(pargs):
			self.log.error("No number found at pargs[0]")
			return ""

		place = int(float(self.Unprompted.parse_advanced(kwargs["_place"]))) if "_place" in kwargs else 0
		num = self.Unprompted.parse_advanced(pargs[0], context)

		if "_up" in pargs: round_func = math.ceil
		elif "_down" in pargs: round_func = math.floor
		else: round_func = round

		self.log.debug(f"Rounding the following number: {num}")

		def round_helper(num, place):
			multiplier = pow(10, place)
			return int(round_func(num / multiplier)) * multiplier

		if "." in str(num):
			if (round_func == round): return round_func(num, place)
			else: return round_helper(num, place)
		elif helpers.is_int(num):
			return round_helper(num, place)
		else:
			self.log.error(f"The number does not appear to be a valid type: {num}")
			return ""

	def ui(self, gr):
		gr.Textbox(label="Round this number 🡢 str", max_lines=1, placeholder="1.345")
		gr.Number(label="Digit precision 🡢 _place", value=0, interactive=True)