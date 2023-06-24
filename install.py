import os
this_path = os.path.dirname(os.path.realpath(__file__))

if os.path.isfile(f"{this_path}/config_user.json"):
	import json
	cfg_dict = json.load(open(f"{this_path}/config_user.json", "r", encoding="utf8"))
	if "skip_requirements" in cfg_dict and cfg_dict["skip_requirements"]:
		print("Unprompted - Skipping install.py check per skip_requirements flag")
		quit()
		
import launch, shutil, pkg_resources

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

# Move existing model downloads to new location as of v8.2.0
# TODO: Implement a pre-startup version check to determine if we need to run upgrade tasks like this
migrate_folder(f"{this_path}/lib_unprompted/stable_diffusion/clipseg/weights",f"{this_path}/models/clipseg")
migrate_folder(f"{this_path}/lib_unprompted/segment_anything/weights",f"{this_path}/models/segment_anything")
migrate_folder(f"{this_path}/lib_unprompted/groundingdino/weights",f"{this_path}/models/groundingdino")

requirements = os.path.join(this_path,"requirements.txt")
with open(requirements) as file:
	for package in file:
		try:
			package_with_comment = package.split("#",1)
			package = package_with_comment[0].strip()
			reason = package_with_comment[1].strip()
			
			if "==" in package:
				package_name, package_version = package.split("==")
				installed_version = pkg_resources.get_distribution(package_name).version
				if installed_version != package_version:
					launch.run_pip(f"install {package}", f"requirements for Unprompted - {reason}: updating {package_name} version from {installed_version} to {package_version}")
			elif not launch.is_installed(package):
				launch.run_pip(f"install {package}", f"requirements for Unprompted - {reason}: {package}")
		except Exception as e:
			print(e)
			print(f"(ERROR) Failed to install {package} dependency for Unprompted - {reason} functions may not work")
			pass

# (Legacy) Copy the ControlNet's cldm folder into venv to prevent the WebUI from crashing on startup if a ControlNet model was last active
if not launch.is_installed("cldm"):
	try:
		import shutil
		print("Unprompted - Copying ControlNet dependencies to venv...")
		destination = shutil.copytree(f"{this_path}/lib_unprompted/stable_diffusion/controlnet/cldm", f"{this_path}/../../venv/Lib/site-packages/cldm")
	except OSError as err:
		print("Copy error: % s" % err)
		pass

