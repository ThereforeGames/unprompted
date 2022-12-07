<p align="center">
<img src="https://user-images.githubusercontent.com/95403634/206286547-53f22ebf-e5fc-4bbd-8bad-53b9cb17ae64.png">
</p>

<p align="center"><strong>Links:</strong> 📣 <a href="./docs/ANNOUNCEMENTS.md">Announcements</a> | 📘 <a href="./docs/MANUAL.md">Manual</a> | ⏱ <a href="./docs/CHANGELOG.md">Changelog</a> | 🎓 <a href="./docs/GUIDE.md">Starter Guide</a></p>

## Introduction

**Unprompted is a powerful templating language written in Python.**

Unlike most templating languages, Unprompted was designed for **maximum readibility with natural language.** It is built around `[shortcodes]` and inspired by the likes of BBCode.

You can use Unprompted as a standalone library (e.g. `unprompted_dry.py`) or as an extension for [AUTOMATIC1111's Stable Diffusion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui). The extension allows you to create expressive, re-usable prompt templates that are both versatile and easy on the eyes.

## Features

- **29 shortcodes** provided out of the box - there are `[if]` conditionals, powerful `[file]` imports, `[for]` loops and everything else the prompting enthusiast could possibly want
- Easily extendable with **custom shortcodes**
- Simple creation of `.txt` templates that can be organized according to your preferences
- Supports recursion, nested shortcodes, advanced logic operators, custom configs, pretty much all the good stuff one might expect from a modern language
- Supports **numerous Stable Diffusion variables** such as `negative_prompt` and `cfg_scale`
- Comprehensive documentation that is always up-to-date
- Free
- Developed by a human

## Installation

1. Visit the **Extensions** tab of Automatic's WebUI.
2. Visit the **Available** subtab.
3. Uncheck the "ads" filter and press the **Load from** button.
4. Scroll down to **Unprompted** and press the **Install** button.

## Usage

First, try the included demo template by entering the following as your prompt:

`[file human/main]`

This is a simple "person generator" that automatically chooses characteristics like hair color, race, and posture.

The `[file]` shortcode will look in `unprompted/templates` for the specified text file (in this case `unprompted/templates/human/main.txt`.) You do not need to enter the file extension.

**Example output:**

![image](https://user-images.githubusercontent.com/95403634/206287476-eb37cdaa-723d-41f4-bac9-02056e55767a.png)

## Next Steps

Once you have verified that Unprompted is installed and running correctly, you have a couple options:

1. You can visit the 🎓 [Starter Guide](./docs/GUIDE.md) for a crash course on creating your own templates
2. Or dive into the deep end by exploring the comprehensive 📘 [Manual](./docs/MANUAL.md)

## Premium Templates

While Unprompted is completely free to use, we do offer **Premium Template add-ons** that demonstrate what the software is truly capable of.

<img align="left" src="https://i.ibb.co/1MSpHL4/Fantasy-Card-Template2.png" width=150>

### [Fantasy Card Template](https://payhip.com/b/hdgNR)
Generate a wide variety of creatures and characters in the style of a fantasy card game. Perfect for heroes, animals, monsters, and even crazy hybrids.
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
Purchases help fund this project. Your support is greatly appreciated! ❤️

## Acknowledgements

A big "thank you" to the authors of the following libraries that Unprompted depends on:

- [Python Shortcodes](https://www.dmulholl.com/dev/shortcodes.html) by Darren Mulholland
- [Simple Eval](https://github.com/danthedeckie/simpleeval) by @danthedeckie
- [Casefy](https://github.com/dmlls/python-casefy) by @dmlls


## 🔧 Found a problem? [Open an Issue.](https://github.com/ThereforeGames/unprompted/issues)

## 💬 For discussion and template sharing, use [the Discussion Board.](https://github.com/ThereforeGames/unprompted/discussions)