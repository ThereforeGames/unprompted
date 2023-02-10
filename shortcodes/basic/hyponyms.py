class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Replaces the content with one or more synonyms."
	def run_block(self, pargs, kwargs, context, content):
		from nltk import download
		download("wordnet")
		import random
		from nltk.corpus import wordnet
		result = []
		max_results = int(kwargs["max"]) if "max" in kwargs else -1
		shuffle_results = bool(int(kwargs["shuffle_results"])) if "shuffle_results" in kwargs else True

		content = content.replace(" ","_")

		pos = kwargs["type"] if "type" in kwargs else None
		if pos == "verb": pos = wordnet.VERB
		elif pos == "noun": pos = wordnet.NOUN
		elif pos == "adjective": pos = wordnet.ADJ

		hyponyms = wordnet.synsets(content,pos=pos)[0]
		hypos = hypos = lambda s:s.hyponyms()

		for syn in list(hyponyms.closure(hypos)):
			for i in syn.lemmas():
				result.append(i.name().replace("_", " "))

		# Remove duplicates from results
		result = list(set(result))

		# Shuffle
		if shuffle_results: random.shuffle(result)

		# Truncate
		if max_results != -1: result = result[:max_results]
		
		return((self.Unprompted.Config.syntax.delimiter).join(result))

	def ui(self,gr):
		pass