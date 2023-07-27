class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Attempts to correct the spelling of content."

	def run_block(self, pargs, kwargs, context, content):
		from pattern.en import suggest
		from nltk import download, word_tokenize
		from nltk.tokenize.treebank import TreebankWordDetokenizer

		# requirement for word_tokenize
		download("punkt")

		confidence = float(kwargs["confidence"]) if "confidence" in kwargs else 0.85
		final_words = word_tokenize(content)  # content.split()

		for idx, word in enumerate(final_words):
			suggestions = suggest(word)
			for suggestion in suggestions:
				self.log.debug(f"Suggestion for {word}: {suggestion}")
				if suggestion[1] >= confidence:
					final_words[idx] = suggestion[0]  # Replace with corrected term
				break  # Looks like the suggestions are sorted by confidence, so we can just break right away

		# Put sentence back together. This is punctuation-aware, so it's better than " ".join
		detokenizer = TreebankWordDetokenizer()
		final_words = detokenizer.detokenize(final_words)

		return (final_words)

	def ui(self, gr):
		pass