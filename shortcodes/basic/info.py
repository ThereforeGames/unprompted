class Shortcode():
	"""Returns various types of metadata about the content."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
	def run_block(self, pargs, kwargs, context, content):
		return_string = ""
		delimiter = ","

		if "character_count" in pargs: return_string += str(len(content)) + delimiter
		if "word_count" in pargs: return_string += str(len(content.split())) + delimiter
		if "string_count" in kwargs: return_string += str(content.count(kwargs["string_count"])) + delimiter
		if "clip_count" in pargs:
			try:
				from ldm.modules.encoders.modules import FrozenCLIPEmbedder
				import torch
				test = FrozenCLIPEmbedder().cuda()
				batch_encoding = test.tokenizer(content, truncation=True, max_length=77, return_length=True,
					return_overflowing_tokens=False, padding="max_length", return_tensors="pt")
				tokens = batch_encoding["input_ids"]
				count = torch.count_nonzero(tokens - 49407)
				return_string += str(count.item()) + delimiter
			except ImportError: self.Unprompted.log(f"Could not import FrozenCLIPEmbedder",True,"ERROR")
			
		return(return_string[:-1])