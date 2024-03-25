class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Autocompletes the content with a given GPT model."
		self.cache_model_name = ""
		self.cache_tokenizer_name = ""
		self.cache_task = ""
		self.cache_model = None
		self.cache_tokenizer = None

	def run_block(self, pargs, kwargs, context, content):
		from transformers import set_seed

		transformers_class = self.Unprompted.parse_arg("transformers_class", "auto")

		task = self.Unprompted.parse_advanced(kwargs["task"], context) if "task" in kwargs else "text-generation"

		instruction = self.Unprompted.parse_arg("instruction", "")
		prefix = self.Unprompted.parse_arg("prefix", "")
		affix = self.Unprompted.parse_arg("affix", "")

		do_cache = not self.Unprompted.shortcode_var_is_true("unload", pargs, kwargs)

		output_key = "generated_text"
		if task == "summarization": output_key = "summary_text"

		max_length = int(self.Unprompted.parse_advanced(kwargs["max_length"], context)) if "max_length" in kwargs else 50

		min_length = int(self.Unprompted.parse_advanced(kwargs["min_length"], context)) if "min_length" in kwargs else 1

		num_return_sequences = 1

		model_dir = f"{self.Unprompted.base_dir}/{self.Unprompted.Config.subdirectories.models}/gpt"

		model_name = self.Unprompted.parse_advanced(kwargs["model"], context) if "model" in kwargs else "LykosAI/GPT-Prompt-Expansion-Fooocus-v2"

		tokenizer_name = self.Unprompted.parse_arg("tokenizer", model_name)

		if do_cache and model_name == self.cache_model_name and task == self.cache_task and tokenizer_name == self.cache_tokenizer_name:
			tokenizer = self.cache_tokenizer
			model = self.cache_model
		else:
			model = model_name
			tokenizer = model

			try:
				if task == "text-generation":
					if transformers_class == "auto":
						from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
						tokenizer = AutoTokenizer.from_pretrained(tokenizer, cache_dir=model_dir)
						model = AutoModelForCausalLM.from_pretrained(model, cache_dir=model_dir)
					elif transformers_class == "t5":
						from transformers import T5Tokenizer, T5ForConditionalGeneration
						tokenizer = T5Tokenizer.from_pretrained(tokenizer, cache_dir=model_dir)
						model = T5ForConditionalGeneration.from_pretrained(model, cache_dir=model_dir, device_map="auto")
			except Exception as e:
				self.Unprompted.error(f"Failed to load the model or tokenizer: {e}")

			if do_cache:
				self.cache_model_name = model_name
				self.cache_tokenizer_name = tokenizer_name
				self.cache_tokenizer = tokenizer
				self.cache_model = model
				self.cache_task = task

		set_seed(self.Unprompted.shortcode_user_vars["seed"])

		if transformers_class == "auto":
			generator = pipeline(task, model=model, tokenizer=tokenizer, model_kwargs={"cache_dir": model_dir}, device=self.Unprompted.main_p.sd_model.device)

			gpt_result = generator(content, min_length=min_length, max_length=max_length, num_return_sequences=num_return_sequences, prefix=instruction)[0][output_key]
		elif transformers_class == "t5":
			input_text = f"{instruction} {content}"
			input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to("cuda")
			outputs = model.generate(input_ids, max_new_tokens=max_length)
			gpt_result = tokenizer.decode(outputs[0])

		if instruction:
			gpt_result = gpt_result.replace(instruction, "")

		if prefix:
			gpt_result = f"{prefix} {gpt_result}"
		if affix:
			gpt_result = f"{gpt_result} {affix}"

		return gpt_result

	def ui(self, gr):
		gr.Dropdown(label="GPT model 🡢 model", info="The first time you use a model, it will be downloaded to your `unprompted/models/gpt` directory. Each model is approximately between 300MB-1.4GB. Credit to the model author names are included in the dropdown below.", value="LykosAI/GPT-Prompt-Expansion-Fooocus-v2", choices=["LykosAI/GPT-Prompt-Expansion-Fooocus-v2", "Gustavosta/MagicPrompt-Stable-Diffusion", "daspartho/prompt-extend", "succinctly/text2image-prompt-generator", "microsoft/Promptist", "AUTOMATIC/promptgen-lexart", "AUTOMATIC/promptgen-majinai-safe", "AUTOMATIC/promptgen-majinai-unsafe", "Gustavosta/MagicPrompt-Dalle", "kmewhort/stable-diffusion-prompt-bolster", "Ar4ikov/gpt2-650k-stable-diffusion-prompt-generator", "Ar4ikov/gpt2-medium-650k-stable-diffusion-prompt-generator", "crumb/bloom-560m-RLHF-SD2-prompter-aesthetic", "Meli/GPT2-Prompt", "DrishtiSharma/StableDiffusion-Prompt-Generator-GPT-Neo-125M", "facebook/bart-large-cnn", "gpt2"])
		gr.Text(label="Tokenizer model 🡢 tokenizer", value="", info="The tokenizer model to use; defaults to the GPT model.")
		gr.Text(label="Instruction 🡢 instruction", value="", info="Text to prepend to the content; may help steer the model's output.")
		gr.Text(label="Prefix 🡢 prefix", value="", info="Text to prepend to the GPT's result.")
		gr.Text(label="Affix 🡢 affix", value="", info="Text to append to the GPT's result.")
		gr.Dropdown(label="Task 🡢 task", info="Not every model is compatible with every task.", value="text-generation", choices=["text-generation", "summarization"])
		gr.Number(label="Minimum number of words returned 🡢 min_length", value=1, interactive=True)
		gr.Number(label="Maximum number of words returned 🡢 max_length", value=50, interactive=True)
		gr.Checkbox(label="Unload the model from cache after use 🡢 unload")
