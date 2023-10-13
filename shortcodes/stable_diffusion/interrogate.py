try:
	from modules import shared
except:
	pass  # for unprompted_dry


class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Generates a caption for the given image using various technqiues."
		self.model = None
		self.processor = None
		self.last_method = ""
		self.last_model_name = ""

	def run_atomic(self, pargs, kwargs, context):
		from PIL import Image
		import lib_unprompted.helpers as helpers
		from lib_unprompted.clipxgpt.model.model import Net
		import torch

		image = self.Unprompted.parse_arg("image",False)
		if not image: image = self.Unprompted.current_image()
		if isinstance(image,str): image = Image.open(image)

		method = self.Unprompted.parse_arg("method","CLIP")
		model_name = self.Unprompted.parse_arg("model","")
		prompt = self.Unprompted.parse_arg("text","")
		question = self.Unprompted.parse_arg("question","")
		max_tokens = self.Unprompted.parse_arg("max_tokens",50)
		if question: prompt = f"Question: {question} Answer:"
		
		# Default models per method
		if not model_name:
			if method == "BLIP-2": model_name = "Salesforce/blip2-opt-2.7b"
			elif method == "CLIPxGPT": model_name = "large_model"

		image = self.Unprompted.parse_arg("image",False)
		if not image: image = self.Unprompted.current_image()
		if isinstance(image,str): image = Image.open(image)

		device ="cuda" if torch.cuda.is_available() else "cpu"
		unload = self.Unprompted.parse_arg("unload",False)

		def get_cached():
			if method != self.last_method or model_name != self.last_model_name or not self.model:
				self.log.info(f"Loading {method} model...")
				return False
			self.log.info(f"Using cached {method} model.")
			return self.model			
		
		if method == "BLIP-2":
			from transformers import AutoProcessor, Blip2ForConditionalGeneration
			model = get_cached()
			if not model:
				#with torch.device(device):
				self.processor = AutoProcessor.from_pretrained(model_name, cache_dir=f"{self.Unprompted.base_dir}/{self.Unprompted.Config.subdirectories.models}/BLIP-2", low_cpu_mem_usage=True)
				model = Blip2ForConditionalGeneration.from_pretrained(model_name, torch_dtype=torch.float16, cache_dir=f"{self.Unprompted.base_dir}/{self.Unprompted.Config.subdirectories.models}/BLIP-2", low_cpu_mem_usage=True)
				model.to(device)

			inputs = self.processor(image, text=prompt, return_tensors="pt").to(device, torch.float16)

			generated_ids = model.generate(**inputs, max_new_tokens=max_tokens)
			caption = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
			
		elif method == "CLIP":
			from modules import shared, lowvram, devices
			self.log.info("Calling the WebUI's standard CLIP interrogator...")
			# caption = shared.interrogator.interrogate(image.convert("RGB"))
			
			lowvram.send_everything_to_cpu()
			devices.torch_gc()
			shared.interrogator.load()
			caption = shared.interrogator.generate_caption(image.convert("RGB"))
			shared.interrogator.unload()

		elif method =="CLIPxGPT":
			import os
			model = get_cached()
			if not model:
				model = Net(
					clip_model="openai/clip-vit-large-patch14",
					text_model="gpt2-medium",
					ep_len=4,
					num_layers=5, 
					n_heads=16, 
					forward_expansion=4, 
					dropout=0.08, 
					max_len=40,
					device=device
				)
				ckp_file = f"{self.Unprompted.base_dir}/{self.Unprompted.Config.subdirectories.models}/clipxgpt/{model_name}.pt"
				if not os.path.exists(ckp_file):
					self.log.info("Downloading CLIPxGPT model...")
					helpers.download_file(ckp_file, f"https://drive.google.com/uc?export=download&id=1Gh32arzhW06C1ZJyzcJSSfdJDi3RgWoG")
				checkpoint = torch.load(ckp_file, map_location=device)
				model.load_state_dict(checkpoint, strict=False)

			model.eval()

			with torch.no_grad():
				caption, _ = model(image, 1.0) # temperature			

		self.log.debug(f"Caption method {method} returned: {caption}")

		# Cache handling
		self.last_method = method
		self.last_model_name = model_name
		if unload:
			self.model = None
			self.processor = None
		elif method != "CLIP":
			self.model = model

		return caption

	def ui(self, gr):
		gr.Image(label="Image to perform interrogation on (defaults to SD output) 🡢 image",type="filepath",interactive=True)
		gr.Radio(label="Interrogation method 🡢 method", value="CLIP", choices=["BLIP-2","CLIP","CLIPxGPT"], info="Note: The other methods require large model downloads!")
		gr.Text(label="Model name 🡢 model",value="",info="Accepts Hugging Face model strings")
		gr.Text(label="Context 🡢 context",value="",info="For BLIP-2, provide contextual information for the interrogation.")
		gr.Text(label="Question 🡢 question",value="",info="For BLIP-2, ask a question about the image.")
		gr.Slider(label="Max Tokens 🡢 max_tokens",value=50,min=1,max=100,step=1,info="For BLIP-2, the maximum number of tokens to generate.")