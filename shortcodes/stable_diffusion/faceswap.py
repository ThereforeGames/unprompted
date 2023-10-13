class Shortcode():
	def __init__(self, Unprompted):
		self.Unprompted = Unprompted
		self.description = ""

		self.fs_pipelines = ["face_fusion","ghost","insightface"]
		self.fs_now = ""
		self.fs_pipeline = {}
		for pipeline in self.fs_pipelines:
			self.fs_pipeline[pipeline] = {}

		self.fs_face_path = None

		self.wizard_prepend = f"{Unprompted.Config.syntax.tag_start}after{Unprompted.Config.syntax.tag_end}{Unprompted.Config.syntax.tag_start}faceswap"

		self.wizard_append = Unprompted.Config.syntax.tag_end + Unprompted.Config.syntax.tag_start + Unprompted.Config.syntax.tag_close + "after" + Unprompted.Config.syntax.tag_end

	def run_atomic(self, pargs, kwargs, context):
		import lib_unprompted.helpers as helpers
		from PIL import Image

		if len(pargs) < 1:
			self.log.error("You must pass a path to a face image as the first parg.")
			return ""
		all_pipelines = (kwargs["pipeline"] if "pipeline" in kwargs else "insightface").split(self.Unprompted.Config.syntax.delimiter)

		providers = ["CPUExecutionProvider"]
		model_dir = f"{self.Unprompted.base_dir}/{self.Unprompted.Config.subdirectories.models}"

		unload_parts = self.Unprompted.parse_arg("unload","")
		minimum_similarity = float(self.Unprompted.parse_arg("minimum_similarity",-1000.0))

		_body = self.Unprompted.parse_alt_tags(kwargs["body"],context) if "body" in kwargs else False
		if _body:
			orig_img = Image.open(_body)
		else: orig_img = self.Unprompted.current_image()
		
		face_string = self.Unprompted.parse_advanced(pargs[0])
		faces = face_string.split(self.Unprompted.Config.syntax.delimiter)

		def get_cached(part):
			if part in self.fs_pipeline[self.fs_now] and part not in unload_parts and "all" not in unload_parts:
				self.log.info(f"Using cached {part}.")
				return self.fs_pipeline[self.fs_now][part]
			self.log.info(f"Processing {part}...")
			return False

		for swap_method in all_pipelines:
			
			result = None
			self.log.info(f"Starting faceswap: {swap_method}")
			self.fs_now = swap_method

			if swap_method == "insightface":
				import lib_unprompted.insightface as insightface
				
				import numpy as np
				import cv2

				def get_faces(img_data: np.ndarray, face_index=0, det_size=(640, 640)):
					face_analyser = insightface.app.FaceAnalysis(name="buffalo_l", providers=providers)
					face_analyser.prepare(ctx_id=0, det_size=det_size)
					face = face_analyser.get(img_data)

					if len(face) == 0 and det_size[0] > 320 and det_size[1] > 320:
						det_size_half = (det_size[0] // 2, det_size[1] // 2)
						return get_faces(img_data, face_index=face_index, det_size=det_size_half)
					try:
						if face_index == -1: return sorted(face, key=lambda x: x.bbox[0])
						else: return sorted(face, key=lambda x: x.bbox[0])[face_index]
					except IndexError:
						return None

				these_faces = (self.fs_face_path == face_string) and get_cached("face")
				if not these_faces:
					# TODO: Avoid reloading faces that were already in self.fs_face_path
					self.fs_pipeline[swap_method]["face"] = []
					for facepath in faces:
						source_img = Image.open(facepath)
						source_img = cv2.cvtColor(np.array(source_img), cv2.COLOR_RGB2BGR)
						face = get_faces(source_img, face_index=0)
						if face:
							self.fs_pipeline[swap_method]["face"].append(face)

				target_img = cv2.cvtColor(np.array(orig_img), cv2.COLOR_RGB2BGR)

				if self.fs_pipeline[swap_method]["face"] is not None:
					result = target_img

					this_model = get_cached("model")
					if not this_model:
						if not helpers.download_file(f"{model_dir}/insightface/inswapper_128.onnx","https://github.com/facefusion/facefusion-assets/releases/download/models/inswapper_128.onnx"):
							continue
						model_path = f"{model_dir}/insightface/inswapper_128.onnx"
						self.fs_pipeline[swap_method]["model"] = insightface.model_zoo.get_model(model_path, providers=providers)

					target_faces = get_faces(target_img, face_index=-1)
					if target_faces:
						for source_idx, source_face in enumerate(self.fs_pipeline[swap_method]["face"]):
							self.log.debug(f"Seeking swap target for new face #{source_idx}")

							similarities = [None]*len(target_faces)
							
							for idx, target_face in enumerate(target_faces):
								# For each face, find the most similar face in the source image and swap it in.
								if target_face.embedding is not None:
									# Find the most similar face in the source image
									similarity = np.dot(
										source_face.embedding,
										target_face.embedding,
									)
									
									self.log.debug(f"Similarity of face #{idx}: {similarity}")
									similarities[idx] = similarity
							
							highest_similarity = max(similarities)
							if highest_similarity >= minimum_similarity:
								most_similar_idx = similarities.index(max(similarities))
								result = self.fs_pipeline[swap_method]["model"].get(
												result,
												target_faces[most_similar_idx],
												source_face,
											)
							
								# Remove this target face to avoid swapping it with the remaining images
								target_faces.pop(most_similar_idx)
								# Break out of the source_face loop in case there are no more target faces
								if not target_faces: break
							else:
								self.log.info("No faces met the minimum similarity threshold.")
						
						result = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
					else:
						self.log.error(f"No target face detected.")
				else:
					self.log.error("No source face detected.")

			elif swap_method == "face_fusion":
				import cv2
				import numpy as np
				from modelscope.outputs import OutputKeys
				from modelscope.pipelines import pipeline
				from modelscope.utils.constant import Tasks

				model = get_cached("model")
				if not model:
					self.fs_pipeline[swap_method]["model"] = pipeline(Tasks.image_face_fusion, model='damo/cv_unet-image-face-fusion_damo', preprocessor="image-face-fusion")

				result = Image.fromarray(cv2.cvtColor(np.array(self.fs_pipeline[swap_method]["model"](dict(template=orig_img, user=face))[OutputKeys.OUTPUT_IMG]), cv2.COLOR_RGB2BGR))
			elif swap_method == "ghost":
				import cv2
				import torch
				import os
				import lib_unprompted.insightface_021 as insightface

				import lib_unprompted.helpers as helpers
				from lib_unprompted.ghost.utils.inference.image_processing import crop_face, get_final_image
				from lib_unprompted.ghost.utils.inference.core import model_inference

				from lib_unprompted.ghost.network.AEI_Net import AEI_Net
				from lib_unprompted.ghost.coordinate_reg.image_infer import Handler
				from lib_unprompted.ghost.insightface_func.face_detect_crop_multi import Face_detect_crop
				from lib_unprompted.ghost.arcface_model.iresnet import iresnet100
				from lib_unprompted.ghost.models.pix2pix_model import Pix2PixModel
				from lib_unprompted.ghost.models.config_sr import TestOptions

				# Prep default args
				kwargs["G_path"] = self.Unprompted.parse_arg("G_path",f"{model_dir}/ghost/G_unet_2blocks.pth")
				kwargs["backbone"] = self.Unprompted.parse_arg("backbone","unet")
				kwargs["num_blocks"] = self.Unprompted.parse_arg("num_blocks", 2)
				kwargs["batch_size"] = self.Unprompted.parse_arg("batch_size", 40)
				kwargs["crop_size"] = self.Unprompted.parse_arg("crop_size", 224)
				kwargs["use_sr"] = self.Unprompted.parse_arg("use_sr", False)
				kwargs["similarity_th"] = self.Unprompted.parse_arg("similarity_th", 0.15)
				kwargs["source_paths"] = [face]
				kwargs["target_faces_paths"] = []
				# Video not supported in this implementation
				kwargs["target_video"] = "examples/videos/nggyup.mp4"
				kwargs["out_video_name"] = "examples/results/result.mp4"
				kwargs["image_to_image"] = True
				kwargs["target_image"] = [orig_img]
				kwargs["out_image_name"] = "examples/results/result.png"

				args = helpers.AttrDict(kwargs)

				def init_models(args):
					cached_model = get_cached("model")
					if cached_model:
						app = self.fs_pipeline[swap_method]["model"]["app"]
						G = self.fs_pipeline[swap_method]["model"]["G"]
						netArc = self.fs_pipeline[swap_method]["model"]["netArc"]
						handler = self.fs_pipeline[swap_method]["model"]["handler"]
						model = self.fs_pipeline[swap_method]["model"]["model"]
					else:
						# process downloads
						helpers.download_file(f"{model_dir}/ghost/antelope/glintr100.onnx","https://github.com/sberbank-ai/sber-swap/releases/download/antelope/glintr100.onnx")
						helpers.download_file(f"{model_dir}/ghost/antelope/scrfd_10g_bnkps.onnx","https://github.com/sberbank-ai/sber-swap/releases/download/antelope/scrfd_10g_bnkps.onnx")
						helpers.download_file(f"{model_dir}/ghost/backbone.pth","https://github.com/sberbank-ai/sber-swap/releases/download/arcface/backbone.pth")
						helpers.download_file(f"{model_dir}/ghost/G_unet_2blocks.pth","https://github.com/sberbank-ai/sber-swap/releases/download/sber-swap-v2.0/G_unet_2blocks.pth")

						# model for face cropping
						app = Face_detect_crop(name="antelope", root=f"{model_dir}/ghost")
						app.prepare(ctx_id= 0, det_thresh=0.6, det_size=(640,640))

						# main model for generation
						G = AEI_Net(args.backbone, num_blocks=args.num_blocks, c_id=512)
						G.eval()
						G.load_state_dict(torch.load(args.G_path, map_location=torch.device('cpu')))
						G = G.cuda()
						G = G.half()

						# arcface model to get face embedding
						netArc = iresnet100(fp16=False)
						netArc.load_state_dict(torch.load(f'{model_dir}/ghost/backbone.pth'))
						netArc=netArc.cuda()
						netArc.eval()

						# model to get face landmarks 
						handler = Handler(f'{self.Unprompted.base_dir}/lib_unprompted/ghost/coordinate_reg/model/2d106det', 0, root=f"{model_dir}/ghost", ctx_id=0, det_size=640)

						# model to make superres of face, set use_sr=True if you want to use super resolution or use_sr=False if you don't
						if args.use_sr:
							os.environ['CUDA_VISIBLE_DEVICES'] = '0'
							torch.backends.cudnn.benchmark = True
							opt = TestOptions()
							#opt.which_epoch ='10_7'
							model = Pix2PixModel(opt)
							model.netG.train()
						else:
							model = None
						
						self.fs_pipeline[swap_method]["model"] = {}
						self.fs_pipeline[swap_method]["model"]["app"] = app
						self.fs_pipeline[swap_method]["model"]["G"] = G
						self.fs_pipeline[swap_method]["model"]["netArc"] = netArc
						self.fs_pipeline[swap_method]["model"]["handler"] = handler
						self.fs_pipeline[swap_method]["model"]["model"] = model
					
					return app, G, netArc, handler, model

				app, G, netArc, handler, model = init_models(args)
				
				# get crops from source images
				# print('List of source paths: ',args.source_paths)
				source = []
				try:
					for source_img in args.source_paths: 
						img = cv2.imread(source_img)
						img = crop_face(img, app, args.crop_size)[0]
						source.append(img[:, :, ::-1])
				except TypeError:
					self.log.error("Could not parse face from the image in given filepath.")
					return ""
					
				target_full = helpers.pil_to_cv2(orig_img)
				full_frames = [target_full]
				
				# get target faces that are used for swap
				set_target = True

				target = [crop_face(target_full, app, args.crop_size)[0]]
				
				# start = time.time()
				final_frames_list, crop_frames_list, full_frames, tfm_array_list = model_inference(full_frames, source, target, netArc, G, app, set_target, similarity_th=args.similarity_th, crop_size=args.crop_size, BS=args.batch_size)
				
				result = get_final_image(final_frames_list, crop_frames_list, full_frames[0], tfm_array_list, handler)
				result = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))						
			
			# TODO: SimSwap pipeline does not play well with WebUI torch load functions e.g.
			# ModuleNotFoundError: No module named 'models.arcface_models'
			elif swap_method == "simswap":
				self.log.error("SimSwap isn't ready yet. Sorry!")
				continue
				# Fix dependency 404 errors
				# import os.path as osp
				# import sys
				# def add_path(path):
				# 	if path not in sys.path:
				# 		sys.path.insert(0, path)	
				# path = osp.join(self.Unprompted.base_dir, "lib_unprompted/simswap/models")
				# add_path(path)									

				from torchvision import transforms
				from lib_unprompted.simswap.insightface_func.face_detect_crop_single import Face_detect_crop
				from lib_unprompted.simswap.models.models import create_model
				from lib_unprompted.simswap.models import arcface_models
				from lib_unprompted.simswap.options.test_options import TestOptions
				from lib_unprompted.simswap.util.norm import SpecificNorm
				from lib_unprompted.simswap.util.reverse2original import reverse2wholeimage
				from lib_unprompted.simswap.parsing_model.model import BiSeNet
				import torch.nn.functional as F
				import lib_unprompted.insightface as insightface
				import numpy as np
				import cv2

				import torch
				from modules import safe

				def _totensor(array):
					tensor = torch.from_numpy(array)
					img = tensor.transpose(0, 1).transpose(0, 2).contiguous()
					return img.float().div(255)

				class Object(object):
					pass

				opt = Object()
				opt.name = "people"
				opt.gpu_ids = "0"
				opt.checkpoints_dir = f'{self.Unprompted.base_dir}/{self.Unprompted.Config.subdirectories.models}/simswap'

				opt.norm = "batch"
				opt.isTrain = True
				opt.use_dropout = False
				opt.data_type = 32
				opt.verbose = False
				opt.fp16 = False
				opt.local_rank = 0

				opt.dataroot = "./datasets/cityscapes/"
				opt.resize_or_crop = "scale_width"
				opt.serial_batches = False
				opt.no_flip = False
				opt.nThreads = 2
				opt.max_dataset_size = float("inf")

				opt.ntest = float("inf")
				opt.results_dir = "./results"
				opt.aspect_ratio = 1.0
				opt.phase = "test"
				opt.which_epoch = "latest"
				opt.how_many = 50
				opt.cluster_path = "features_clustered_010.npy"
				opt.use_encoded_image = True
				opt.export_onnx = ""
				opt.engine = ""
				opt.onnx = ""
				opt.Arc_path = f"{self.Unprompted.base_dir}/{self.Unprompted.Config.subdirectories.models}/simswap/arcface_checkpoint.tar"
				opt.pic_a_path = "c:/pic"
				opt.pic_b_path = "c:/pic"
				opt.pic_specific_path = './crop_224/zrf.jpg'
				opt.multisepcific_dir = "./demo_file"
				opt.video_path = "G:/swap_data/video/HSB_Demo_Trim.mp4"
				opt.temp_path = "./temp_results"
				opt.output = "./output/"
				opt.id_thres = 0.03
				opt.no_simswaplogo = True
				opt.use_mask = False
				opt.crop_size = 512

				transformer_Arcface = transforms.Compose([transforms.ToTensor(), transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])

				# test

				# opt.Arc_model = torch.load(opt.Arc_path, map_location=torch.device("cpu"))

				# def handler(module, name):
				# 	if module == 'torch' and name in ['float64', 'float16']:
				# 		return getattr(torch, name)
				# 	return None
				# with safe.Extra(handler):
				# 	opt.Arc_model = torch.load(opt.Arc_path)
				opt.Arc_model = safe.unsafe_torch_load(opt.Arc_path)

				start_epoch, epoch_iter = 1, 0
				crop_size = 512

				if crop_size == 512:
					opt.which_epoch = 550000
					opt.name = '512'
					mode = 'ffhq'
				else:
					mode = 'None'

				model = create_model(opt)
				model.eval()

				spNorm = SpecificNorm()
				app = Face_detect_crop(name="antelope", root=f'{self.Unprompted.base_dir}/{self.Unprompted.Config.subdirectories.models}/simswap')
				app.prepare(ctx_id=0, det_thresh=0.6, det_size=(640, 640), mode=mode)

				with torch.no_grad():
					img_a_whole = cv2.cvtColor(np.array(orig_img), cv2.COLOR_RGB2BGR)
					img_a_align_crop, _ = app.get(img_a_whole, crop_size)
					img_a_align_crop_pil = Image.fromarray(cv2.cvtColor(img_a_align_crop[0], cv2.COLOR_BGR2RGB))
					img_a = transformer_Arcface(img_a_align_crop_pil)
					img_id = img_a.view(-1, img_a.shape[0], img_a.shape[1], img_a.shape[2])

					# convert numpy to tensor
					img_id = img_id.cuda()

					#create latent id
					img_id_downsample = F.interpolate(img_id, size=(112, 112))
					latend_id = model.netArc(img_id_downsample)
					latend_id = F.normalize(latend_id, p=2, dim=1)

					############## Forward Pass ######################

					# pic_b = opt.pic_b_path
					img_b_whole = cv2.imread(face)

					img_b_align_crop_list, b_mat_list = app.get(img_b_whole, crop_size)
					# detect_results = None
					swap_result_list = []

					b_align_crop_tenor_list = []

					for b_align_crop in img_b_align_crop_list:

						b_align_crop_tenor = _totensor(cv2.cvtColor(b_align_crop, cv2.COLOR_BGR2RGB))[None, ...].cuda()

						swap_result = model(None, b_align_crop_tenor, latend_id, None, True)[0]
						swap_result_list.append(swap_result)
						b_align_crop_tenor_list.append(b_align_crop_tenor)

					if opt.use_mask:
						n_classes = 19
						net = BiSeNet(n_classes=n_classes)
						net.cuda()
						save_pth = f"{self.Unprompted.base_dir}/{self.Unprompted.Config.subdirectories.models}/simswap/79999_iter.pth"
						net.load_state_dict(torch.load(save_pth))
						net.eval()
					else:
						net = None

					result = reverse2wholeimage(b_align_crop_tenor_list, swap_result_list, b_mat_list, crop_size, img_b_whole, None, None, True, pasring_model =net,use_mask=opt.use_mask, norm = spNorm)

			# Append to output window
			try:
				self.Unprompted.current_image(result)
			except:
				continue

		# Free cache
		for part in unload_parts:
			self.fs_pipeline[swap_method].pop(part, None)
		if "face" in unload_parts: self.fs_face_path = None
		else: self.fs_face_path = face_string
			
		return ""

	def ui(self, gr):
		with gr.Row():
			gr.Image(label="New face image to swap to 🡢 str",type="filepath",interactive=True)
			gr.Image(label="Body image to perform swap on (defaults to SD output) 🡢 body",type="filepath",interactive=True)
		gr.Dropdown(label="Faceswap pipeline(s) 🡢 pipeline", choices=self.fs_pipelines, value="insightface", multiselect=True, interactive=True, info="You can enable multiple pipelines with the standard delimiter. Please note that each pipeline must download its models on first use.")
		gr.Dropdown(label="Unload pipeline parts from cache 🡢 unload", choices=["all","face","model"],multiselect=True,interactive=True,info="You can release some or all of the pipeline parts from your cache after inference. Useful for low-memory devices.")