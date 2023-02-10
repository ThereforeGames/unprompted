class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Replaces the content with one or more antonyms."
	def run_block(self, pargs, kwargs, context, content):
		from nltk import download
		download("wordnet")
		from nltk.corpus import wordnet
		import random

		pos = kwargs["type"] if "type" in kwargs else None
		enable_moby = bool(int(kwargs["enable_moby"])) if "enable_moby" in kwargs else True
		if pos == "verb": pos = wordnet.VERB
		elif pos == "noun": pos = wordnet.NOUN
		elif pos == "adjective": pos = wordnet.ADJ

		result = []
		max_results = int(kwargs["max"]) if "max" in kwargs else -1
		shuffle_results = bool(int(kwargs["shuffle_results"])) if "shuffle_results" in kwargs else True

		for syn in wordnet.synsets(content,pos=pos):
			for l in syn.lemmas():
				if l.antonyms():
					result.append(l.antonyms()[0].name().replace("_", " "))
		
		# Run synonym search on these results, because wordnet tends to produce very few antonyms
		if enable_moby:
			extra_antonyms = []
			for word in result:
				this_syn = self.Unprompted.shortcode_objects["synonyms"].run_block([],[],context,word)
				if (len(this_syn) > 0):
					this_syn = this_syn.split(self.Unprompted.Config.syntax.delimiter)
					extra_antonyms.extend(this_syn)

			result.extend(extra_antonyms)
		
		
		# Remove duplicates from results
		result = list(set(result))

		# Shuffle
		if shuffle_results: random.shuffle(result)

		# Truncate
		if max_results != -1: result = result[:max_results]		

		return((self.Unprompted.Config.syntax.delimiter).join(result))

	def ui(self,gr):
		pass