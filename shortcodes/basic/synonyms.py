class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Replaces the content with one or more synonyms."

	def run_block(self, pargs, kwargs, context, content):
		import lib_unprompted.helpers as helpers
		from nltk import download
		download("wordnet")
		from nltk.corpus import wordnet
		# from nltk import download
		# from collections import Counter
		# from nltk.corpus import reuters
		import os, re, random

		include_self = True if "include_self" in pargs else False
		enable_wordnet = bool(int(kwargs["enable_wordnet"])) if "enable_wordnet" in kwargs else True
		enable_moby = bool(int(kwargs["enable_moby"])) if "enable_moby" in kwargs else True
		shuffle_results = bool(int(kwargs["shuffle_results"])) if "shuffle_results" in kwargs else True

		synonyms = []
		max_results = int(kwargs["max"]) if "max" in kwargs else -1

		moby_dir = f"{self.Unprompted.base_dir}/lib_unprompted"
		moby_filename = "mthesaur.txt"
		moby_file = f"{moby_dir}/{moby_filename}"

		if enable_moby is True:
			# Download the Moby Thesaurus
			if not os.path.exists(moby_file):
				print("Downloading the Moby II Thesaurus (~24 MB)...")
				helpers.download_file(moby_file, f"https://ia800205.us.archive.org/7/items/mobythesauruslis03202gut/mthesaur.txt")

			# Process Moby thesaurus results
			with open(moby_file.format(os.path.dirname(os.path.abspath(__file__)))) as f:
				word_regex = re.compile(r"\n{},[\w+|,|  | -]+".format(content))
				words = re.findall(word_regex, f.read())
				if len(words) > 0:
					synonyms.extend(words[0].replace("{},".format(content), "").replace("\n", "").split(","))

		# Add results from wordnet
		if enable_wordnet is True:
			content = content.replace(" ", "_")
			pos = kwargs["type"] if "type" in kwargs else None
			if pos == "verb": pos = wordnet.VERB
			elif pos == "noun": pos = wordnet.NOUN
			elif pos == "adjective": pos = wordnet.ADJ
			for syn in wordnet.synsets(content, pos=pos):
				for l in syn.lemmas():
					synonyms.append(l.name().replace("_", " "))

		# Remove duplicates from results
		synonyms = list(set(synonyms))

		if include_self:
			if content not in synonyms: synonyms.append(content)
		elif content in synonyms: synonyms.remove(content)

		# Remove uncommon results
		# parsing a corpus is unfortunately slow and not a foolproof method of detecting common words
		# download("reuters")
		# texts = reuters.words()[:100000]
		# wordcounts = Counter(i.lower() for i in reuters.words())
		# for i,word in enumerate(synonyms):
		# 	print(f"{word}: {wordcounts[word]}")

		# Shuffle
		if shuffle_results: random.shuffle(synonyms)

		# Truncate
		if max_results != -1: synonyms = synonyms[:max_results]

		return ((self.Unprompted.Config.syntax.delimiter).join(synonyms))

	def ui(self, gr):
		pass