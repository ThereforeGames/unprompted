class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Slices up the content."

	def run_block(self, pargs, kwargs, context,content):
		import lib_unprompted.helpers as helpers
		start = self.Unprompted.parse_advanced(kwargs["start"],context) if "start" in kwargs else 0
		end = self.Unprompted.parse_advanced(kwargs["end"],context) if "end" in kwargs else 0

		# Support strings to search for
		if helpers.is_int(start): start = int(start)
		else: start = content.find(start)
		if helpers.is_int(end): end = int(end)
		else: end = content.find(end)

		step = int(self.Unprompted.parse_advanced(kwargs["step"],context))  if "step" in kwargs else 1
		unit = kwargs["unit"] if "unit" in kwargs else "characters"

		if start == -1: start = None
		if end == -1: end = None

		if unit == "words":
			arr = content.split()
			return_string = " ".join(arr[start:end])
		else:
			return_string = content[start:end:step]

		return(return_string)

	def ui(self,gr):
		gr.Number(label="Beginning index of the substring 🡢 start",value=0,interactive=True)
		gr.Number(label="Ending index of the substring 🡢 end",value=0,interactive=True)
		gr.Number(label="Step size 🡢 step",value=1,interactive=True)
		gr.Radio(label="Unit type 🡢 unit",choices=["characters","words"],value="characters",interactive=True)