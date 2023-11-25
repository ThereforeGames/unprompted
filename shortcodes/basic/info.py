class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns various types of metadata about the content."

	def run_block(self, pargs, kwargs, context, content):
		return_string = ""
		delimiter = ","

		if "character_count" in pargs: return_string += str(len(content)) + delimiter
		if "word_count" in pargs: return_string += str(len(content.split())) + delimiter
		if "sentence_count" in pargs:
			import nltk
			nltk.download("punkt")
			from nltk.tokenize import sent_tokenize
			return_string += str(len(sent_tokenize(content))) + delimiter
		if "filename" in pargs:
			from pathlib import Path
			return_string += Path(content).stem + delimiter
		if "string_count" in kwargs: return_string += str(content.count(kwargs["string_count"])) + delimiter
		if "clip_count" in pargs:
			try:
				from ldm.modules.encoders.modules import FrozenCLIPEmbedder
				import torch
				test = FrozenCLIPEmbedder().cuda()
				batch_encoding = test.tokenizer(content, truncation=True, max_length=77, return_length=True, return_overflowing_tokens=False, padding="max_length", return_tensors="pt")
				tokens = batch_encoding["input_ids"]
				count = torch.count_nonzero(tokens - 49407)
				return_string += str(count.item()) + delimiter
			except ImportError:
				self.log.error(f"Could not import FrozenCLIPEmbedder")

		return (return_string[:-len(delimiter)])

	def ui(self, gr):
		gr.Checkbox(label="Return the character count 🡢 character_count")
		gr.Checkbox(label="Return the word count 🡢 word_count")
		gr.Checkbox(label="Return the sentence count 🡢 sentence_count")
		gr.Checkbox(label="Return the filename 🡢 filename")
		gr.Checkbox(label="Return the CLIP token count (prompt complexity) 🡢 clip_count")
		gr.Textbox(label="Return the count of a custom substring 🡢 string_count", max_lines=1)
