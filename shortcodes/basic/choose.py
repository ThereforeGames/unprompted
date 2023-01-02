import random

class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns one of multiple options, delimited by newline or vertical pipe"

	def run_block(self, pargs, kwargs, context, content):
		final_string = ""

		parts = content.replace(getattr(self.Unprompted.Config.syntax.sanitize_before,"\n","\\n"),self.Unprompted.Config.syntax.delimiter).split(self.Unprompted.Config.syntax.delimiter)

		# Remove empty lines
		parts = list(filter(None, parts))

		if ("_weighted" in pargs):
			weighted_list = []
			checking_weight = True
			this_weight = 1

			for idx,part in enumerate(parts):
				if checking_weight:
					this_weight = self.Unprompted.autocast(part)
					
					if (isinstance(this_weight,str)):
						this_weight = 1
						checking_weight = False
					elif isinstance(this_weight,float):
						probability = (this_weight % 1)
						this_weight = int(this_weight)
						if (probability >= random.uniform(0,1)): this_weight += 1
				
				if not checking_weight:
					for x in range(0, this_weight): weighted_list.append(part)

				checking_weight = not checking_weight
			
			parts = weighted_list

		times = 1
		for parg in pargs:
			if (parg[0] == "_"): continue # Skips system arguments
			times = self.Unprompted.parse_advanced(parg,context)
			break

		_sep = self.Unprompted.parse_advanced(kwargs["_sep"],context) if "_sep" in kwargs else ", "
		_case = max(min(len(parts)-1, int(self.Unprompted.parse_advanced(kwargs["_case"],context))), 0) if "_case" in kwargs else -1

		for x in range(0, times):
			part_index = random.choice(range(len(parts))) if _case == -1 else _case
			final_string += self.Unprompted.parse_alt_tags(parts[part_index],context)
			
			if (times > 1 and x != times - 1):
				del parts[part_index] # Prevent the same choice from being made again
				final_string += _sep

		return final_string

	def ui(self,gr):
		gr.Number(label="Number of times to choose 🡢 int",value=1,interactive=True)
		gr.Textbox(label="String delimiter when returning more than one choice 🡢 _sep",max_lines=1,placeholder=", ")
		gr.Checkbox(label="Custom weight per option 🡢 _weighted")
		gr.Number(label="Override random nature of shortcode with predetermined outcome 🡢 _case",value=-1,interactive=True)