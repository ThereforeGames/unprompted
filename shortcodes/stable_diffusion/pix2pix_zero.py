class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "A diffusion-based image-to-image approach that allows users to specify the edit direction on-the-fly."

	def run_block(self, pargs, kwargs, context):
		import sys, os, pdb
		sys.path.append(f"{self.Unprompted.base_dir}/lib_unprompted/stable_diffusion/pix2pix_zero/pix2pix_zero_utils")
		from diffusers import DDIMScheduler
		from ddim_inv import DDIMInversion
		from scheduler import DDIMInverseScheduler
		from edit_pipeline import EditingPipeline
		from edit_directions import construct_direction
		from modules import sd_models, shared
		from modules.images import flatten
		from modules.shared import opts
		import argparse
		import numpy as np
		import torch
		import requests
		import glob
		from PIL import Image

		from lavis.models import load_model_and_preprocess

		imgs = []
		if "init_images" in self.Unprompted.shortcode_user_vars:
			for img in self.Unprompted.shortcode_user_vars["init_images"]:
				imgs.append(flatten(img, opts.img2img_background_color))

		results_folder = kwargs["results_folder"] if "results_folder" in kwargs else f"{self.Unprompted.base_dir}/lib_unprompted/stable_diffusion/pix2pix_zero/output"
		steps = int(float(kwargs["steps"])) if "steps" in kwargs else 50
		model_path = "T:\\code\python\\automatic-stable-diffusion-webui\\models\\diffusers\\sd14"
		float_16 = True if "float_16" in pargs else False

		def inversion(input_image=imgs,results_folder=results_folder,num_ddim_steps=steps,model_path=model_path,use_float_16=float_16):

			# make the output folders
			os.makedirs(os.path.join(results_folder, "inversion"), exist_ok=True)
			os.makedirs(os.path.join(results_folder, "prompt"), exist_ok=True)

			if use_float_16:
				torch_dtype = torch.float16
			else:
				torch_dtype = torch.float32


			# load the BLIP model
			model_blip, vis_processors, _ = load_model_and_preprocess(name="blip_caption", model_type="base_coco", is_eval=True, device=torch.device("cuda"))
			# make the DDIM inversion pipeline    
			pipe = DDIMInversion.from_pretrained(f"{model_path}", torch_dtype=torch_dtype).to("cuda")
			pipe.scheduler = DDIMInverseScheduler.from_config(pipe.scheduler.config)

			for idx,img in enumerate(input_image):
				# bname = os.path.basename(args.input_image).split(".")[0]
				img = img.resize((512,512), Image.Resampling.LANCZOS)
				# generate the caption
				_image = vis_processors["eval"](img).unsqueeze(0).cuda()
				prompt_str = model_blip.generate({"image": _image})[0]
				x_inv, x_inv_image, x_dec_img = pipe(
					prompt_str, 
					guidance_scale=1,
					num_inversion_steps=num_ddim_steps,
					img=img,
					torch_dtype=torch_dtype
				)
				# save the inversion
				torch.save(x_inv[0], os.path.join(results_folder, f"inversion/{idx}.pt"))
				# save the prompt string
				with open(os.path.join(results_folder, f"prompt/{idx}.txt"), "w") as f:
					f.write(prompt_str)


		def edit_real(inversion=f"{results_folder}/inversion/0.pt",prompt=f"{results_folder}/prompt/0.txt",task_name="cat2dog",results_folder=results_folder,num_ddim_steps=steps,model_path=model_path,xa_guidance=0.1,negative_guidance_scale=5.0,use_float_16=float_16):

			os.makedirs(os.path.join(results_folder, "edit"), exist_ok=True)
			os.makedirs(os.path.join(results_folder, "reconstruction"), exist_ok=True)

			if use_float_16:
				torch_dtype = torch.float16
			else:
				torch_dtype = torch.float32

			# if the inversion is a folder, the prompt should also be a folder
			assert (os.path.isdir(inversion)==os.path.isdir(prompt)), "If the inversion is a folder, the prompt should also be a folder"
			if os.path.isdir(inversion):
				l_inv_paths = sorted(glob(os.path.join(inversion, "*.pt")))
				l_bnames = [os.path.basename(x) for x in l_inv_paths]
				l_prompt_paths = [os.path.join(prompt, x.replace(".pt",".txt")) for x in l_bnames]
			else:
				l_inv_paths = [inversion]
				l_prompt_paths = [prompt]

			# Make the editing pipeline
			pipe = EditingPipeline.from_pretrained(model_path, torch_dtype=torch_dtype).to("cuda")
			pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)


			emb_dir = f"{self.Unprompted.base_dir}/lib_unprompted/stable_diffusion/pix2pix_zero/pix2pix_zero_utils/embeddings_sd_1.4"
			embs_a = torch.load(os.path.join(emb_dir, f"cat.pt"))
			embs_b = torch.load(os.path.join(emb_dir, f"dog.pt"))
			final_emb = (embs_b.mean(0)-embs_a.mean(0)).unsqueeze(0)

			for inv_path, prompt_path in zip(l_inv_paths, l_prompt_paths):
				prompt_str = open(prompt_path).read().strip()
				rec_pil, edit_pil = pipe(prompt_str,
						num_inference_steps=num_ddim_steps,
						x_in=torch.load(inv_path).unsqueeze(0),
						edit_dir=final_emb,
						guidance_amount=xa_guidance,
						guidance_scale=negative_guidance_scale,
						negative_prompt=prompt_str # use the unedited prompt for the negative prompt
				)
				
				bname = os.path.basename(inversion).split(".")[0]
				edit_pil[0].save(os.path.join(results_folder, f"edit/{bname}.png"))
				rec_pil[0].save(os.path.join(results_folder, f"reconstruction/{bname}.png"))

		
		# Doesn't support ckpt or we could do this:
		# sd_models.model_path+"\\"+shared.opts.sd_model_checkpoint.split(" ", 1)[0]
		inversion()
		edit_real()


		return("")
	
	def ui(self,gr):
		pass