import launch

if not launch.is_installed("nltk"):
    launch.run_pip("install nltk", "requirements for Unprompted")
if not launch.is_installed("pattern"):
	launch.run_pip("install pattern@git+https://github.com/NicolasBizzozzero/pattern","requirements for Unprompted")
if not launch.is_installed("sentence-transformers"):
	launch.run_pip("install sentence-transformers","requirements for Unprompted - img2pez")
if not launch.is_installed("salesforce-lavis"):
	launch.run_pip("install salesforce-lavis","requirements for Unprompted - pix2pix_zero")

# Copy the ControlNet's cldm folder into venv to prevent the WebUI from crashing on startup if a ControlNet model was last active
if not launch.is_installed("cldm"):
	try:
		import shutil, os
		this_path = os.path.dirname(os.path.realpath(__file__))
		print("Unprompted - Copying ControlNet dependencies to venv...")
		destination = shutil.copytree(f"{this_path}/lib_unprompted/stable_diffusion/controlnet/cldm", f"{this_path}/../../venv/Lib/site-packages/cldm")
	except OSError as err:
		print("Copy error: % s" % err)

# pip install not working for groundingdino atm.
if not launch.is_installed("segment_anything"):
	launch.run_pip("install segment_anything","requirements for Unprompted - txt2mask")
#if not launch.is_installed("GroundingDINO"):
#	launch.git_clone("https://github.com/IDEA-Research/GroundingDINO.git", "venv", "GroundingDINO")
	