
class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Optimize a hard prompt using the PEZ algorithm and CLIP encoders, AKA Hard Prompts Made Easy."

	def run_atomic(self, pargs, kwargs, context):
		if "init_images" not in self.Unprompted.shortcode_user_vars:
			return

		import lib_unprompted.hard_prompts_made_easy as pez
		import lib_unprompted.pez_open_clip as open_clip
		import torch
		from modules.images import flatten
		from modules.shared import opts
		import argparse

		img = flatten(self.Unprompted.shortcode_user_vars["init_images"][0], opts.img2img_background_color)

		# Load params as specified by the official repo
		args = argparse.Namespace()
		# TODO: Allow these values to be configured via shortcode arguments
		setattr(args,"prompt_len",8)
		setattr(args,"iter",3000)
		setattr(args,"lr",0.1)
		setattr(args,"weight_decay",0.1)
		setattr(args,"prompt_bs",1)
		setattr(args,"print_step",100)
		setattr(args,"batch_size",1)
		setattr(args,"clip_model","ViT-L-14")
		setattr(args,"clip_pretrain","openai")

		# load CLIP model
		device = "cuda" if torch.cuda.is_available() else "cpu"
		model, _, preprocess = open_clip.create_model_and_transforms(args.clip_model, pretrained=args.clip_pretrain, device=device)

		# You may modify the hyperparamters
		args.prompt_len = 8 # number of tokens for the learned prompt

		# optimize prompt
		learned_prompt = pez.optimize_prompt(model, preprocess, args, device, target_images=[img])

		return learned_prompt
	
	def ui(self,gr):
		pass