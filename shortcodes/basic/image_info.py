class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Returns various types of metadata about the image."
		self.iqa_metrics = {}

	def run_atomic(self, pargs, kwargs, context):
		from PIL import Image
		return_string = ""
		delimiter = ","
		image = self.Unprompted.parse_alt_tags(kwargs["file"],context) if "file" in kwargs else self.Unprompted.current_image()

		if isinstance(image,str):
			try:
				image = Image.open(image)
			except:
				self.log.error(f"Could not open image {image}")
				return ""

		if "width" in pargs:
			return_string += str(image.width) + delimiter
		if "height" in pargs:
			return_string += str(image.height) + delimiter
		if "aspect_ratio" in pargs:
			return_string += str(image.width / image.height) + delimiter
		if "filename" in pargs:
			from pathlib import Path
			return_string += Path(image.filename).stem + delimiter
		if "filetype" in pargs:
			return_string += image.format + delimiter
		if "filesize" in pargs:
			import sys
			return_string += str(sys.getsizeof(image.tobytes())) + delimiter
		if "iqa" in kwargs:
			import pyiqa, torch
			
			metrics = self.Unprompted.parse_alt_tags(kwargs["iqa"],context).split(self.Unprompted.Config.syntax.delimiter)
			for metric_name in metrics:
				if metric_name not in self.iqa_metrics:
					self.log.info(f"Creating IQA metric `{metric_name}`...")
					self.iqa_metrics[metric_name] = pyiqa.create_metric(metric_name, device=torch.device("cuda") if torch.cuda.is_available() else "cpu", as_loss=False)
				else:
					self.log.info(f"Using cached IQA metric `{metric_name}`")

				score = self.iqa_metrics[metric_name](image).cpu().item()
				
				return_string += str(score) + delimiter
		if "pixel_count" in pargs:
			return_string += str(image.width * image.height) + delimiter

		if "unload_metrics" in pargs:
			self.iqa_metrics = {}
		
		return (return_string[:-len(delimiter)])

	def ui(self, gr):
		gr.Textbox(label="Path to image (uses SD image by default) 🡢 str")
		gr.Textbox(label="Image Quality Assessment metric(s) 🡢 iqa")
