from re import sub
from modules.processing import StableDiffusionProcessingImg2Img, Processed, process_images
from modules import images
from torchvision.transforms.functional import to_pil_image, pil_to_tensor
import torch
from modules.shared import opts, state

class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.init_images = []
		self.image_masks = []
		self.processing = False
		self.orginal_n_iter = None
		self.description = "Allows to use multiple init_images or multiple masks"

	def run_atomic(self, pargs, kwargs, context):
		if self.processing:
			return ""

		had_init_image = False
		if "init_images" in self.Unprompted.shortcode_user_vars:
			self.init_images += self.Unprompted.shortcode_user_vars["init_images"]
			had_init_image = True

		if "image_masks" in self.Unprompted.shortcode_user_vars:
			self.image_masks += [self.Unprompted.shortcode_user_vars["image_masks"]]
		elif "image_mask" in self.Unprompted.shortcode_user_vars:
			self.image_masks += [[self.Unprompted.shortcode_user_vars["image_mask"]]]
		elif had_init_image:
			# each init_image has at least an empty mask
			self.image_masks += [[]]

		if "n_iter" in self.Unprompted.shortcode_user_vars:
			self.orginal_n_iter = self.Unprompted.shortcode_user_vars["n_iter"] 
			self.Unprompted.shortcode_user_vars["n_iter"] = 0

		return ""

	def after(self, p:StableDiffusionProcessingImg2Img, processed: Processed):
		if not self.processing and self.orginal_n_iter is not None:
			self.processing = True

			try:
				mask_count = sum([len(masks) for masks in self.image_masks])
				if mask_count == 0:
					state.job_count = self.orginal_n_iter
				else:
					if len(self.init_images) == 1:
						state.job_count = mask_count * self.orginal_n_iter
					else:
						state.job_count = mask_count

				batched_init_imgs = [self.init_images[idx:idx+p.batch_size] for idx in range(0, len(self.init_images), p.batch_size)]
				batched_prompts = [p.all_prompts[idx:idx+p.batch_size] for idx in range(0, len(p.all_prompts), p.batch_size)]
				batched_neg_prompts = [p.all_negative_prompts[idx:idx+p.batch_size] for idx in range(0, len(p.all_negative_prompts), p.batch_size)]
				batched_masks = [self.image_masks[idx:idx+p.batch_size] for idx in range(0, len(self.image_masks), p.batch_size)]
				batched_seeds = [p.all_seeds[idx:idx+p.batch_size] for idx in range(0, len(p.all_seeds), p.batch_size)]

				create_grid = not p.do_not_save_grid
				save_imgs = not p.do_not_save_samples

				p.do_not_save_grid = True
				p.do_not_save_samples = True

				p.n_iter = 1
				if len(self.init_images) == 1:
					batched_init_imgs = [[self.init_images[0]] * p.batch_size] * self.orginal_n_iter
					batched_masks = [[self.image_masks[0]] * p.batch_size] * self.orginal_n_iter

				for init_imgs, prompts, neg_prompts, seeds, maskss in zip(batched_init_imgs, batched_prompts, batched_neg_prompts, batched_seeds, batched_masks):
					if sum([len(masks) for masks in maskss]) == 0:
						p.init_images = init_imgs
						p.all_prompts = batched_prompts
						p.all_negative_prompts = batched_neg_prompts
						p.all_seeds = seeds
						p.mask = None
						sub_processed = process_images(p)
						processed.images += sub_processed.images
					else:
						output_resolution = (init_imgs[0].width, init_imgs[0].height) if p.inpaint_full_res else (p.width, p.height)

						if len(self.init_images) == 1:
							imgs = torch.stack([pil_to_tensor(init_imgs[0].resize(output_resolution))] * p.batch_size).clone()
							
							for idx, mask in enumerate(maskss[0]):
								p.init_images = [to_pil_image(img) for img in imgs]
								p.image_mask = mask
								p.all_prompts = prompts
								p.all_negative_prompts = neg_prompts
								p.all_seeds = [seed + idx + 800 for seed in seeds]

								sub_processed = process_images(p)

								mask = mask.resize(output_resolution)
								mask = pil_to_tensor(mask) > 0
								mask = mask.broadcast_to(imgs.shape)

								imgs[mask] = torch.stack([pil_to_tensor(img) for img in sub_processed.images[:len(imgs)]])[mask]

							processed.images += [to_pil_image(img) for img in imgs]
						else:
							for init_img, prompt, neg_prompt, seed, masks in zip(init_imgs, prompts, neg_prompts, seeds, maskss):
								img = pil_to_tensor(init_img.resize(output_resolution))
								
								for idx, mask in enumerate(masks):
									p.batch_size = 1
									p.init_images = [to_pil_image(img)]
									p.image_mask = mask
									p.all_prompts = [prompt]
									p.all_negative_prompts = [neg_prompt]
									p.all_seeds = [seed + idx + 800]

									sub_processed = process_images(p)

									mask = mask.resize(output_resolution)
									mask = pil_to_tensor(mask) > 0
									mask = mask.broadcast_to(img.shape)

									img[mask] = pil_to_tensor(sub_processed.images[0])[mask]

								processed.images.append(to_pil_image(img))

				if opts.samples_save and save_imgs:
					for img, prompt, neg_prompt, seed in zip(processed.images, p.all_prompts, p.all_negative_prompts, p.all_seeds):
						images.save_image(img, p.outpath_samples, "", seed, prompt, opts.samples_format)

				if create_grid and len(processed.images) >  1:
					grid = images.image_grid(processed.images, p.batch_size * len(batched_init_imgs))
					if opts.return_grid:
						processed.images.insert(0, grid)
						processed.index_of_first_image = 1
					if opts.grid_save:
						images.save_image(grid, p.outpath_grids, "grid", p.all_seeds[0], p.all_prompts[0], opts.grid_format, short_filename=not opts.grid_extended_filename, p=p, grid=True)

			finally:
				self.processing = False
				self.init_images = []
				self.image_masks = []
				self.orginal_n_iter = None

			


	def ui(self,gr):
		pass