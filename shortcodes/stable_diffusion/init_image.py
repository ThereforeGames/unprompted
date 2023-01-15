import glob
import random
import os
from modules.processing import process_images,fix_seed,Processed, StableDiffusionProcessingImg2Img
from modules import images
from modules.shared import opts, state

class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.description = "Loads an image from the given path and sets it as the initial image for use with img2img."
		self.support_multiple = False
		self.init_images = []

	def run_atomic(self, pargs, kwargs, context):
		from PIL import Image

		path = self.Unprompted.parse_alt_tags(pargs[0],context)

		files = glob.glob(path)
		if (len(files) == 0):
			self.Unprompted.log(f"No files found at this location: {path}",True,"ERROR")
			return("")
		file = random.choice(files)

		self.Unprompted.log(f"Loading file: {file}")

		if not os.path.exists(file):
			self.Unprompted.log(f"File does not exist: {file}",True,"ERROR")
			return("")

		self.Unprompted.shortcode_user_vars["init_images"] = [Image.open(file)]

		self.support_multiple = "support_multiple" in pargs
		if self.support_multiple:
			self.init_images += self.Unprompted.shortcode_user_vars["init_images"]
			self.Unprompted.shortcode_user_vars["n_iter"] = 0

		return ""


	def after(self,p:StableDiffusionProcessingImg2Img,processed:Processed):
		if self.support_multiple:
			# block recursion
			self.support_multiple = False
			
			p.n_iter = 1
			create_grid = not p.do_not_save_grid
			p.do_not_save_grid = True

			batched_init_imgs = [self.init_images[idx:idx+p.batch_size] for idx in range(0, len(self.init_images), p.batch_size)]
			batched_prompts = [p.all_prompts[idx:idx + p.batch_size] for idx in range(0, len(p.all_prompts), p.batch_size)]
			state.job_count = len(batched_prompts)
			for init_imgs, batched_prompts in zip(batched_init_imgs, batched_prompts):
				p.init_images = init_imgs
				p.all_prompts = batched_prompts

				sub_processed = process_images(p)
				processed.images += sub_processed.images

			if create_grid and len(processed.images) != 1:
				grid = images.image_grid(processed.images, p.batch_size * len(batched_init_imgs))
				if opts.return_grid:
					processed.images.insert(0, grid)
					processed.index_of_first_image = 1
				if opts.grid_save:
					images.save_image(grid, p.outpath_grids, "grid", p.all_seeds[0], p.all_prompts[0], opts.grid_format, short_filename=not opts.grid_extended_filename, p=p, grid=True)

			self.init_images = []

	def ui(self,gr):
		gr.File(label="Image path",file_type="image")
		gr.Checkbox(label="Use multiple init_images 🡢 support_multiple")