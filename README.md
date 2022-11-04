# Unprompted for Stable Diffusion
Supercharge your prompt workflow with this powerful scripting language!

![unprompted_header](https://user-images.githubusercontent.com/95403634/199041569-7c6c5748-e7dc-4068-943f-c2d92745dbb5.png)

## Introduction

**Unprompted** is a highly modular extension for [AUTOMATIC1111's Stable Diffusion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) that allows you to include various shortcodes in your prompts. You can pull text from files, set up your own variables, process text through conditional functions, and so much more - it's like wildcards on steroids.

While the intended usecase is Stable Diffusion, **this engine is also flexible enough to serve as an all-purpose text generator.** You can run the included `unprompted_dry.py` without any external dependencies.

Still under active development - I am excited to read your feedback but please keep in mind that this is an early release!

Developed & tested on Windows 11 with Python v3.9.7. Built on top of Darren Mulholland's excellent [Python Shortcodes](https://www.dmulholl.com/dev/shortcodes.html) library.

## Installation

> **⚠️ Important!** Unprompted was converted from a script to an extension on 11/4. The file structure has changed as a result. If you installed an old version of Unprompted, you should remove `unprompted.py` from `/scripts` as well as the `unprompted` directory (taking a backup of your customizations if needed) before updating.

1. Visit the **Extensions** tab of Automatic's WebUI.
2. Visit the **Install from URL** subtab.
3. Paste the URL for this repo and enter `unprompted` as the local directory name.
4. Press Install!

## Basic Usage

Try the included demo by entering the following as your prompt:

`[file human/main]`

> **💡 Tip:** This is a simple "human generator" that will choose characteristics like hair color, race, and posture.

The `[file]` shortcode looks in `unprompted/templates` for the specified text file (in this case `unprompted/templates/human/main.txt`.) You do not need to type the file extension.

Example output:

![image](https://user-images.githubusercontent.com/95403634/198927183-d98cdbb9-dab5-4623-9e1f-b77a0292714e.png)

## Learn More

There are too many features to include on one page!

To learn more about what Unprompted is (and isn't) capable of, please check out the following resources:

- [Starter Guide](./docs/GUIDE.md)
- [Manual](./docs/MANUAL.md)
- [Changelog](./docs/CHANGELOG.md)

For an example of a working, sophisticated template, you can [check out the inexpensive Fantasy Card Template here](https://payhip.com/b/hdgNR). Purchases will help continue to fund this project. ❤

> 🔧 If you run into a problem, feel free to [open an Issue.](https://github.com/ThereforeGames/unprompted/issues)

> 💬 For general discussion and template sharing, use [our Discussions board.](https://github.com/ThereforeGames/unprompted/discussions)