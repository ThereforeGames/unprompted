import launch

if not launch.is_installed("nltk"):
    launch.run_pip("install nltk", "requirements for Unprompted")
if not launch.is_installed("pattern"):
	launch.run_pip("install pattern@git+https://github.com/NicolasBizzozzero/pattern","requirements for Unprompted")
# For "Hard Prompts Made Easy"
if not launch.is_installed("sentence-transformers"):
	launch.run_pip("install sentence-transformers","requirements for Unprompted")