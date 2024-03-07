class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Adjusts the black point of the image to maximize contrast."

		self.wizard_append = Unprompted.Config.syntax.tag_end + Unprompted.Config.syntax.tag_start + Unprompted.Config.syntax.tag_close + "after" + Unprompted.Config.syntax.tag_end

	def run_atomic(self, pargs, kwargs, context):
		from PIL import Image, ImageOps, ImageEnhance
		import numpy as np
		import lib_unprompted.helpers as helpers
		image = self.Unprompted.parse_alt_tags(kwargs["file"], context) if "file" in kwargs else self.Unprompted.current_image()
		show = self.Unprompted.parse_arg("show", False)
		out = self.Unprompted.parse_arg("out", "")

		if isinstance(image, str):
			try:
				image = Image.open(image)
			except:
				self.log.error(f"Could not open image {image}")
				return ""

		# Reinterpretation of Photoshop's "Auto Tone"
		# Thank you to Gerald Bakker for the following writeup on the algorithm:
		# https://geraldbakker.nl/psnumbers/auto-options.html

		shadows = np.array(helpers.str_to_rgb(self.Unprompted.parse_arg("shadows", "0,0,0")))
		# midtones are only used in other algorithms:
		midtones = helpers.str_to_rgb(self.Unprompted.parse_arg("midtones", "128,128,128"))
		highlights = np.array(helpers.str_to_rgb(self.Unprompted.parse_arg("highlights", "255,255,255")))
		shadow_clip = self.Unprompted.parse_arg("shadow_clip", 0.001)
		highlight_clip = self.Unprompted.parse_arg("highlight_clip", 0.001)

		# Convert the image to a numpy array
		img_array = np.array(image, dtype=np.float32)

		def calculate_adjustment_values(hist, total_pixels, clip_percent):
			clip_threshold = total_pixels * clip_percent
			cumulative_hist = hist.cumsum()

			# Find the first and last indices where the cumulative histogram exceeds the clip thresholds
			lower_bound_idx = np.where(cumulative_hist > clip_threshold)[0][0]
			upper_bound_idx = np.where(cumulative_hist < (total_pixels - clip_threshold))[0][-1]

			return lower_bound_idx, upper_bound_idx

		# Process each channel (R, G, B) separately
		for channel in range(3):
			# Calculate the histogram of the current channel
			hist, _ = np.histogram(img_array[:, :, channel].flatten(), bins=256, range=[0, 255])

			# Total number of pixels
			total_pixels = img_array.shape[0] * img_array.shape[1]

			# Calculate the adjustment values based on clipping percentages
			dark_value, light_value = calculate_adjustment_values(hist, total_pixels, shadow_clip)
			_, upper_light_value = calculate_adjustment_values(hist, total_pixels, highlight_clip)

			# Adjust light_value using upper_light_value for highlights
			light_value = max(light_value, upper_light_value)

			# Avoid division by zero
			if light_value == dark_value:
				continue

			# Scale and clip the channel values
			img_array[:, :, channel] = (img_array[:, :, channel] - dark_value) * (highlights[channel] - shadows[channel]) / (light_value - dark_value) + shadows[channel]
			img_array[:, :, channel] = np.clip(img_array[:, :, channel], 0, 255)

		# Make sure the data type is correct for PIL
		img_array = np.clip(img_array, 0, 255).astype(np.uint8)

		new_image = Image.fromarray(img_array)

		if show:
			self.Unprompted.after_processed.images.append(image)

		if out:
			new_image.save(out)

		self.Unprompted.current_image(new_image)

	def ui(self, gr):
		gr.Textbox(label="Path to image (uses SD image by default) 🡢 str")
