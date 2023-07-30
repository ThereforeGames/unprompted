class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = "Manually call random.seed() at will"

	def run_atomic(self, pargs, kwargs, context):
		import random

		if len(pargs) > 0:
			new_seed = int(self.Unprompted.parse_advanced(pargs[0], context))
		else:
			new_seed = self.Unprompted.main_p.seed

		if new_seed == -1:
			from modules.processing import fix_seed
			fix_seed(self.Unprompted.main_p)
			new_seed = self.Unprompted.main_p.seed

		random.seed(new_seed)
		self.Unprompted.shortcode_user_vars["seed"] = new_seed
		self.Unprompted.shortcode_user_vars["all_seeds"][self.Unprompted.shortcode_user_vars["batch_real_index"]] = new_seed

		self.Unprompted.main_p.seed = new_seed
		self.Unprompted.main_p.all_seeds[self.Unprompted.shortcode_user_vars["batch_real_index"]] = new_seed
		if self.Unprompted.main_p.seeds:
			self.Unprompted.main_p.seeds[self.Unprompted.shortcode_user_vars["batch_size_index"]] = new_seed

		return ""

	def ui(self, gr):
		gr.Text(label="New seed value")