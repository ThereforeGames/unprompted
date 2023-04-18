import launch, shutil, os
this_path = os.path.dirname(os.path.realpath(__file__))

def migrate_folder(old_dir,new_dir):
	try:
		if (os.path.isdir(old_dir)):
			os.makedirs(new_dir, exist_ok=True)
			file_names = os.listdir(old_dir)
			for file_name in file_names:
				shutil.move(os.path.join(old_dir, file_name), new_dir)
			os.rmdir(old_dir)
			print(f"Migrated dependencies to new location: {new_dir}")
	except Exception as e: print(f"Error while trying to migrate folder: {e}")

if not launch.is_installed("nltk"):
    launch.run_pip("install nltk", "requirements for Unprompted")
if not launch.is_installed("pattern"):
	launch.run_pip("install pattern@git+https://github.com/NicolasBizzozzero/pattern","requirements for Unprompted")
if not launch.is_installed("sentence-transformers"):
	launch.run_pip("install sentence-transformers","requirements for Unprompted - img2pez")
if not launch.is_installed("salesforce-lavis"):
	launch.run_pip("install salesforce-lavis","requirements for Unprompted - pix2pix_zero")

# Move existing model downloads to new location as of v8.2.0
migrate_folder(f"{this_path}/lib_unprompted/stable_diffusion/clipseg/weights",f"{this_path}/models/clipseg")
migrate_folder(f"{this_path}/lib_unprompted/segment_anything/weights",f"{this_path}/models/segment_anything")
migrate_folder(f"{this_path}/lib_unprompted/groundingdino/weights",f"{this_path}/models/groundingdino")

# Copy the ControlNet's cldm folder into venv to prevent the WebUI from crashing on startup if a ControlNet model was last active
if not launch.is_installed("cldm"):
	try:
		import shutil
		print("Unprompted - Copying ControlNet dependencies to venv...")
		destination = shutil.copytree(f"{this_path}/lib_unprompted/stable_diffusion/controlnet/cldm", f"{this_path}/../../venv/Lib/site-packages/cldm")
	except OSError as err:
		print("Copy error: % s" % err)

if not launch.is_installed("segment_anything"):
	launch.run_pip("install segment_anything","requirements for Unprompted - txt2mask")

if not launch.is_installed("color-matcher"):
	launch.run_pip("install color-matcher","requirements for Unprompted - zoom_enhance")

