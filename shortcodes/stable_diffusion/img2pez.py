class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Optimize a hard prompt using the PEZ algorithm and CLIP encoders, AKA Hard Prompts Made Easy."
		self.learned_prompts = []

	def run_atomic(self, pargs, kwargs, context):
		import lib_unprompted.stable_diffusion.hard_prompts_made_easy as pez
		import lib_unprompted.stable_diffusion.pez_open_clip as open_clip
		import torch
		from modules.images import flatten
		from modules.shared import opts
		import argparse

		# optimize prompt
		self.log.debug("Starting prompt optimization")

		# Workaround for conflict between optim_utils.py and batch processing
		if self.Unprompted.shortcode_user_vars["batch_real_index"] == 0:
			imgs = []

			if "init_images" in self.Unprompted.shortcode_user_vars:
				for img in self.Unprompted.shortcode_user_vars["init_images"]:
					imgs.append(flatten(img, opts.img2img_background_color))

			image_path = kwargs["image_path"] if "image_path" in kwargs else ""
			if (len(image_path) > 0):
				from PIL import Image
				image_paths = image_path.split(self.Unprompted.Config.syntax.delimiter)
				for img in image_paths:
					imgs.append(Image.open(img))

			if (len(imgs) < 1):
				self.log.error("No input images found!")
				return ""

			prompt_len = int(float(kwargs["prompt_length"])) if "prompt_length" in kwargs else 16
			iterations = int(float(kwargs["iterations"])) if "iterations" in kwargs else 200
			learning_rate = float(kwargs["learning_rate"]) if "learning_rate" in kwargs else 0.1
			weight_decay = float(kwargs["weight_decay"]) if "weight_decay" in kwargs else 0.1
			prompt_bs = int(float(kwargs["prompt_bs"])) if "prompt_bs" in kwargs else 1

			if "preset" in kwargs and kwargs["preset"] == "2.1":
				clip_model = "ViT-H-14"
				clip_pretrain = "laion2b_s32b_b79k"
			else:
				clip_model = kwargs["clip_model"] if "clip_model" in kwargs else "ViT-L-14"
				clip_pretrain = kwargs["clip_pretrain"] if "clip_pretrain" in kwargs else "openai"

			print_step = int(float(kwargs["print_step"])) if "print_step" in kwargs else 100
			batch_size = int(float(kwargs["batch_size"])) if "batch_size" in kwargs else 1

			# Set up params with argparse since it's the format used in the original repo
			args = argparse.Namespace()

			setattr(args, "prompt_len", prompt_len)
			setattr(args, "iter", iterations)
			setattr(args, "lr", learning_rate)
			setattr(args, "weight_decay", weight_decay)
			setattr(args, "prompt_bs", prompt_bs)
			setattr(args, "print_step", print_step)
			setattr(args, "batch_size", batch_size)
			setattr(args, "clip_model", clip_model)
			setattr(args, "clip_pretrain", clip_pretrain)

			# load CLIP model
			device = "cuda" if torch.cuda.is_available() else "cpu"
			model, _, preprocess = open_clip.create_model_and_transforms(args.clip_model, pretrained=args.clip_pretrain, device=device)

			for i in range(self.Unprompted.main_p.n_iter * self.Unprompted.main_p.batch_size):
				self.learned_prompts.append(pez.optimize_prompt(model, preprocess, args, device, target_images=imgs, target_prompts=None))

			if "free_memory" in pargs:
				self.log.debug("Freeing img2pez memory")
				import gc
				model = None
				preprocess = None
				_ = None
				gc.collect()
				with torch.no_grad():
					torch.cuda.empty_cache()
		else:
			self.log.warning("The img2pez library has limited support with WebUI batch processing; all img2pez prompts are generated at the start of the run and its settings cannot be changed mid-run.")

		return self.learned_prompts[self.Unprompted.shortcode_user_vars["batch_real_index"]]

	def cleanup(self):
		self.learned_prompts = []

	def ui(self, gr):
		gr.Text(label="Image path 🡢 image_path", placeholder="Leave blank to use the initial img2img image. Supports multiple paths.")
		gr.Number(label="Prompt length 🡢 prompt_length", value=16, interactive=True)
		gr.Number(label="Iterations 🡢 iterations", value=200, interactive=True)
		gr.Number(label="Learning rate 🡢 learning_rate", value=0.1, interactive=True)
		gr.Number(label="Weight decay 🡢 weight_decay", value=0.1, interactive=True)
		gr.Number(label="Prompt bs (well, that's what they call it) 🡢 prompt_bs", value=1, interactive=True)
		gr.Dropdown(label="CLIP model 🡢 clip_model", choices=["ViT-L-14", "ViT-H-14"], value="ViT-L-14", interactive=True)
		gr.Dropdown(label="CLIP pretrain 🡢 clip_pretrain", choices=["openai", "laion2b_s32b_b79k"], value="openai", interactive=True)
		gr.Checkbox(label="Try freeing CLIP model from memory? 🡢 free_memory", value=False)
