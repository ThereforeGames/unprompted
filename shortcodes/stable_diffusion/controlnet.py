class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "A neural network structure to control diffusion models by adding extra conditions."
		self.detect_resolution = 512
		self.save_memory = False
		self.steps = 20
	
	def run_atomic(self, pargs, kwargs, context):
		if "init_images" not in self.Unprompted.shortcode_user_vars:
			self.Unprompted.log("This shortcode is only supported in img2img mode.","ERROR")
		
		self.steps = self.Unprompted.shortcode_user_vars["steps"]
		# Hacky way of bypassing the normal img2img routine
		self.Unprompted.shortcode_user_vars["steps"] = 1

		if "detect_resolution" in kwargs: self.detect_resolution = kwargs["detect_resolution"]
		if "save_memory" in pargs: self.save_memory = True
		return("")

	def after(self,p=None,processed=None):
		import torch
		import cv2
		import einops
		import numpy as np
		import lib_unprompted.stable_diffusion.controlnet.config as config
		from PIL import Image

		from modules.images import flatten
		from modules.shared import opts	

		from lib_unprompted.stable_diffusion.controlnet.annotator.util import resize_image, HWC3
		from lib_unprompted.stable_diffusion.controlnet.annotator.openpose import apply_openpose
		from lib_unprompted.stable_diffusion.controlnet.cldm.model import create_model, load_state_dict
		from lib_unprompted.stable_diffusion.controlnet.ldm.models.diffusion.ddim import DDIMSampler

		import sys
		sys.path.append(f"{self.Unprompted.base_dir}/lib_unprompted/stable_diffusion/controlnet")

		model = create_model(f"{self.Unprompted.base_dir}/lib_unprompted/stable_diffusion/controlnet/models/cldm_v15.yaml").cpu()
		model.load_state_dict(load_state_dict(f"{self.Unprompted.base_dir}/lib_unprompted/stable_diffusion/controlnet/models/control_sd15_openpose.pth", location='cpu'),strict=False)
		model = model.cuda()
		ddim_sampler = DDIMSampler(model)

		image_resolution = 512

		num_samples = self.Unprompted.shortcode_user_vars["batch_size"]

		with torch.no_grad():
			for img in self.Unprompted.shortcode_user_vars["init_images"]:
				img = np.asarray(flatten(img, opts.img2img_background_color))

				input_image = HWC3(img)
				detected_map, _ = apply_openpose(resize_image(input_image, self.detect_resolution))
				detected_map = HWC3(detected_map)
				img = resize_image(input_image, image_resolution)
				H, W, C = img.shape

				detected_map = cv2.resize(detected_map, (W, H), interpolation=cv2.INTER_NEAREST)

				control = torch.from_numpy(detected_map.copy()).float().cuda() / 255.0
				control = torch.stack([control for _ in range(num_samples)], dim=0)
				control = einops.rearrange(control, 'b h w c -> b c h w').clone()

				# we're already seeded bro 8)
				#if seed == -1:
				#	seed = random.randint(0, 65535)
				# seed_everything(seed)

				if self.save_memory:
					model.low_vram_shift(is_diffusing=False)

				cond = {"c_concat": [control], "c_crossattn": [model.get_learned_conditioning([self.Unprompted.shortcode_user_vars["prompt"]] * num_samples)]}
				un_cond = {"c_concat": [control], "c_crossattn": [model.get_learned_conditioning([self.Unprompted.shortcode_user_vars["negative_prompt"]] * num_samples)]}
				shape = (4, H // 8, W // 8)

				if self.save_memory:
					model.low_vram_shift(is_diffusing=True)

				samples, intermediates = ddim_sampler.sample(self.steps, num_samples,
															shape, cond, verbose=False, eta=self.Unprompted.shortcode_user_vars["denoising_strength"],
															unconditional_guidance_scale=self.Unprompted.shortcode_user_vars["cfg_scale"],
															unconditional_conditioning=un_cond)

				if self.save_memory:
					model.low_vram_shift(is_diffusing=False)

				x_samples = model.decode_first_stage(samples)
				x_samples = (einops.rearrange(x_samples, 'b c h w -> b h w c') * 127.5 + 127.5).cpu().numpy().clip(0, 255).astype(np.uint8)

				for i in range(num_samples):
					output = Image.fromarray(x_samples[i])
					output_map = Image.fromarray(detected_map)
					processed.images.append(output)
					processed.images.append(output_map)
		
		print("done")
		
		# processed.images.append([detected_map])
		return(processed)

	def ui(self,gr):
		pass