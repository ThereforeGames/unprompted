import launch

if not launch.is_installed("nltk"):
    launch.run_pip("install nltk", "requirements for Unprompted")