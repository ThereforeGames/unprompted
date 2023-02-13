import launch

if not launch.is_installed("nltk"):
    launch.run_pip("install nltk", "requirements for Unprompted")
if not launch.is_installed("pattern"):
	launch.run_pip("install pattern@git+https://github.com/NicolasBizzozzero/pattern","requirements for Unprompted")
if not launch.is_installed("sentence-transformers"):
	launch.run_pip("install sentence-transformers","requirements for Unprompted - img2pez")
if not launch.is_installed("salesforce-lavis"):
	launch.run_pip("install salesforce-lavis","requirements for Unprompted - pix2pix_zero")