class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Rounds a given number to a certain level of precision. Works with integers and floats."

	def run_atomic(self, pargs, kwargs, context):
		import math
		if not len(pargs):
			self.Unprompted.log("No number found at pargs[0]", context="ERROR")
			return ""

		place = int(float(self.Unprompted.parse_advanced(kwargs["_place"]))) if "_place" in kwargs else 0
		num = self.Unprompted.parse_advanced(pargs[0], context)

		if "_up" in pargs: round_func = math.ceil
		elif "_down" in pargs: round_func = math.floor
		else: round_func = round

		self.Unprompted.log(f"Rounding the following number: {num}")

		if "." in str(num):
			if (round_func == round): return round_func(num, place)
			else: return round_func(num)
		elif self.Unprompted.is_int(num):
			multiplier = pow(10, place)
			num = int(round_func(num / multiplier)) * multiplier
			return num
		else:
			self.Unprompted.log_error("The number is not a valid type: ", num)
			return ""

	def ui(self, gr):
		gr.Textbox(label="Round this number 🡢 str", max_lines=1, placeholder="1.345")
		gr.Number(label="Digit precision 🡢 _place", value=0, interactive=True)