from lib.stable_diffusion.clipseg.models.clipseg import CLIPDensePredT
from kornia.morphology import dilation, erosion
from kornia.filters import box_blur
from PIL import ImageOps
from torchvision.utils import draw_segmentation_masks
from torchvision.transforms.functional import pil_to_tensor, to_pil_image
import os.path
import torch
from torchvision import transforms
from modules.images import flatten
from modules.shared import opts

class Shortcode():
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted
		self.image_mask = None
		self.show = False
		self.description = "Creates an image mask from the content for use with inpainting."

	def run_block(self, pargs, kwargs, context, content):
		if "init_images" not in self.Unprompted.shortcode_user_vars:
			return

		device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

		brush_mask_mode = self.Unprompted.parse_advanced(kwargs["mode"],context) if "mode" in kwargs else "add"
		self.show = True if "show" in pargs else False

		self.legacy_weights = True if "legacy_weights" in pargs else False
		smoothing = int(self.Unprompted.parse_advanced(kwargs["smoothing"],context)) if "smoothing" in kwargs else 20
		neg_smoothing = int(self.Unprompted.parse_advanced(kwargs["neg_smoothing"],context)) if "neg_smoothing" in kwargs else 20

		# Pad the mask by applying a dilation or erosion
		mask_padding = int(self.Unprompted.parse_advanced(kwargs["padding"],context) if "padding" in kwargs else 0)
		neg_mask_padding = int(self.Unprompted.parse_advanced(kwargs["neg_padding"],context) if "neg_padding" in kwargs else 0)
		padding_dilation_kernel = None
		if (mask_padding != 0):
			padding_dilation_kernel = torch.ones(abs(mask_padding), abs(mask_padding), device=device)

		neg_padding_dilation_kernel = None
		if (neg_mask_padding != 0):
			neg_padding_dilation_kernel = torch.ones(abs(neg_mask_padding), abs(neg_mask_padding), device=device)

		prompts = content.split(self.Unprompted.Config.syntax.delimiter)
		prompt_parts = len(prompts)

		if "negative_mask" in kwargs:
			negative_prompts = (self.Unprompted.parse_advanced(kwargs["negative_mask"],context)).split(self.Unprompted.Config.syntax.delimiter)
			negative_prompt_parts = len(negative_prompts)
		else: negative_prompts = None

		mask_precision = min(1.0,float(self.Unprompted.parse_advanced(kwargs["precision"],context) if "precision" in kwargs else 0.4))
		neg_mask_precision = min(1.0,float(self.Unprompted.parse_advanced(kwargs["neg_precision"],context) if "neg_precision" in kwargs else 0.4))

		def overlay_mask_part(img, final_img, mode):
			if mode == "discard": 
				return torch.logical_and(img, final_img)
			else: 
				return torch.logical_or(img, final_img)

		def process_mask_parts(these_preds, mode, final_img = None, mask_precision=0.4, mask_padding=0, padding_dilation_kernel=None, smoothing=None):
			masks = torch.sigmoid(these_preds)
			
			if padding_dilation_kernel is not None:
				if mask_padding > 0: 
					img = dilation(masks, kernel=padding_dilation_kernel)
				else: 
					masks = erosion(masks, kernel=padding_dilation_kernel)
			if smoothing is not None:
				masks = box_blur(masks, (smoothing,smoothing))

			masks = masks.squeeze(1)
			masks = masks > mask_precision
			masks = masks > 0

			if mode == "discard": 
				masks = ~masks

			for i, mask in enumerate(masks):
				# overlay mask parts
				if (i > 0 or final_img is not None): mask = overlay_mask_part(mask, final_img, mode)

				final_img = mask
			return final_img

		def get_mask():
			# load model
			model = CLIPDensePredT(version='ViT-B/16', reduce_dim=64, complex_trans_conv=not self.legacy_weights)
			model_dir = f"{self.Unprompted.base_dir}/lib/stable_diffusion/clipseg/weights"
			os.makedirs(model_dir, exist_ok=True)

			d64_filename = "rd64-uni.pth" if self.legacy_weights else "rd64-uni-refined.pth"
			d64_file = f"{model_dir}/{d64_filename}"
			d16_file = f"{model_dir}/rd16-uni.pth"

			# Download model weights if we don't have them yet
			if not os.path.exists(d64_file):
				print("Downloading clipseg model weights...")
				self.Unprompted.download_file(d64_file,f"https://owncloud.gwdg.de/index.php/s/ioHbRzFx6th32hn/download?path=%2F&files={d64_filename}")
				self.Unprompted.download_file(d16_file,"https://owncloud.gwdg.de/index.php/s/ioHbRzFx6th32hn/download?path=%2F&files=rd16-uni.pth")

			# non-strict, because we only stored decoder weights (not CLIP weights)
			model.load_state_dict(torch.load(d64_file), strict=False);	
			model = model.eval().to(device=device)

			transform = transforms.Compose([
				transforms.ToTensor(),
				transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
				transforms.Resize((512, 512)),
			])
			flattened_input = flatten(self.Unprompted.shortcode_user_vars["init_images"][0], opts.img2img_background_color)
			img = transform(flattened_input).unsqueeze(0)

			# predict
			with torch.no_grad():
				preds = model(img.repeat(prompt_parts,1,1,1).to(device=device), prompts)[0]
				if (negative_prompts): negative_preds = model(img.repeat(negative_prompt_parts,1,1,1).to(device=device), negative_prompts)[0]

			if "image_mask" not in self.Unprompted.shortcode_user_vars: self.Unprompted.shortcode_user_vars["image_mask"] = None
			
			if (brush_mask_mode == "add" and self.Unprompted.shortcode_user_vars["image_mask"] is not None):
				final_img = self.Unprompted.shortcode_user_vars["image_mask"].convert("L").resize((512,512))
				final_img = pil_to_tensor(final_img).to(device=device) > 0
			else: final_img = None

			# process masking
			final_img = process_mask_parts(preds,"add",final_img,mask_precision, mask_padding, padding_dilation_kernel, smoothing)

			# process negative masking
			if brush_mask_mode == "subtract" and self.Unprompted.shortcode_user_vars["image_mask"] is not None:
				mask = pil_to_tensor(self.Unprompted.shortcode_user_vars["image_mask"].convert("L").resize(512, 512))
				mask = mask > 0
				mask = ~mask
				final_img = overlay_mask_part(final_img, mask, "discard")
			if negative_prompts: 
				final_img = process_mask_parts(negative_preds,"discard",final_img,neg_mask_precision, neg_mask_padding, neg_padding_dilation_kernel, neg_smoothing)

			if "size_var" in kwargs:
				subject_size = final_img.sum() / torch.prod(torch.tensor(final_img.shape))
				self.Unprompted.shortcode_user_vars[kwargs["size_var"]] = subject_size

			final_img = to_pil_image(final_img.cpu().float())
			
			return final_img

		# Set up processor parameters correctly
		self.image_mask = get_mask().resize((self.Unprompted.shortcode_user_vars["init_images"][0].width,self.Unprompted.shortcode_user_vars["init_images"][0].height))
		self.Unprompted.shortcode_user_vars["mode"] = 1
		self.Unprompted.shortcode_user_vars["mask_mode"] = 1
		self.Unprompted.shortcode_user_vars["image_mask"] =self.image_mask
		self.Unprompted.shortcode_user_vars["mask_for_overlay"] = self.image_mask
		self.Unprompted.shortcode_user_vars["latent_mask"] = None # fixes inpainting full resolution

		if "save" in kwargs: self.image_mask.save(f"{self.Unprompted.parse_advanced(kwargs['save'],context)}.png")

		return ""
	
	def after(self,p=None,processed=None):
		if self.image_mask and self.show:
			processed.images.append(self.image_mask)
			
			overlayed_init_img = draw_segmentation_masks(pil_to_tensor(p.init_images[0]), pil_to_tensor(self.image_mask) > 0)
			processed.images.append(to_pil_image(overlayed_init_img))
			self.image_mask = None
			self.show = False
			return processed
	
	def ui(self,gr):
		gr.Radio(label="Mask blend mode 🡢 mode",choices=["add","subtract","discard"],value="add",interactive=True)
		gr.Checkbox(label="Show mask in output 🡢 show")
		gr.Checkbox(label="Use legacy weights 🡢 legacy_weights")
		gr.Number(label="Precision of selected area 🡢 precision",value=100,interactive=True)
		gr.Number(label="Padding radius in pixels 🡢 padding",value=0,interactive=True)
		gr.Number(label="Smoothing radius in pixels 🡢 smoothing",value=20,interactive=True)
		gr.Textbox(label="Negative mask prompt 🡢 negative_mask",max_lines=1)
		gr.Textbox(label="Save the mask size to the following variable 🡢 size_var",max_lines=1)