class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Converts the content verb into another conjugated form."
	def run_block(self, pargs, kwargs, context, content):
		from pattern.en import conjugate

		alias = kwargs["alias"] if "alias" in kwargs else None

		if alias:
			return(conjugate(content,alias))
		else:
			tense = kwargs["tense"] if "tense" in kwargs else "indefinite"
			person = int(kwargs["person"]) if "person" in kwargs else 3
			number = kwargs["number"] if "number" in kwargs else "singular"
			mood = kwargs["mood"] if "mood" in kwargs else "indicative"
			aspect = kwargs["aspect"] if "aspect" in kwargs else "imperfective"
			negated = bool(int(kwargs["negated"])) if "negated" in kwargs else False
			parse = bool(int(kwargs["parse"])) if "parse" in kwargs else True

			return(conjugate(content,tense=tense,person=person,number=number,mood=mood,aspect=aspect,negated=negated,parse=parse))

	def ui(self,gr):
		pass