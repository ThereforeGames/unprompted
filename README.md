<p align="center">
<img src="https://user-images.githubusercontent.com/95403634/206286547-53f22ebf-e5fc-4bbd-8bad-53b9cb17ae64.png">
</p>

<p align="center"><strong>Links:</strong> 📣 <a href="./docs/ANNOUNCEMENTS.md">Announcements</a> | 📘 <a href="./docs/MANUAL.md">Manual</a> | ⏱ <a href="./docs/CHANGELOG.md">Changelog</a> | 🎓 <a href="./docs/GUIDE.md">Starter Guide</a></p>

## Introduction

**Unprompted is a powerful templating language and Swiss Army knife for the Stable Diffusion WebUI.**

Unlike most templating languages, Unprompted was designed for **maximum readibility with natural language.** It is built around `[shortcodes]` and inspired by the likes of BBCode.

You can use Unprompted as a standalone library (e.g. `unprompted_dry.py`) or as an extension for [AUTOMATIC1111's Stable Diffusion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui). The extension allows you to create expressive, re-usable prompt templates that are both versatile and easy on the eyes.

Additionally, it gives you access to **exclusive Stable Diffusion features** such as txt2mask, txt2img2img, zoom_enhance, and more.

## Features

- [x] **Dozens of shortcodes** provided out of the box - there are `[if]` conditionals, powerful `[file]` imports, `[for]` loops and everything else the prompting enthusiast could possibly want
- [x] Yes, you can use it for wildcards, e.g. `[choose]red|blue|yellow[/choose]` or `[choose][file somefile][/choose]` to pick a line at random
- [x] Easily extendable with **custom shortcodes**
- [x] Simple creation of `.txt` templates that can be organized according to your preferences
- [x] Supports recursion, nested shortcodes, advanced logic operators, custom configs, pretty much all the good stuff one might expect from a modern language
- [x] Supports **numerous Stable Diffusion variables** such as `negative_prompt` and `cfg_scale`
- [x] Supports natural language processing features such as auto-pluralization, finding synonyms, and even verb conjugation
- [x] Includes a growing list of examples that demonstrate advanced functionality, such as **customizing the weight of a choice list** and **applying emphasis to a random part of your prompt**
- [x] Comprehensive documentation that is always up-to-date
- [x] Free
- [x] Developed by a human

## Installation

We provide two methods of installation:

<details><summary>How to install directly... (click to expand)</summary>

1. Visit the **Extensions** tab of Automatic's WebUI.
2. Visit the **Install from URL** subtab.
3. Paste this repo's URL into the first field: `https://github.com/ThereforeGames/unprompted`
4. Click **Install**.

</details>

<details><summary>How to install through extensions index... (click to expand)</summary>

1. Visit the **Extensions** tab of Automatic's WebUI.
2. Visit the **Available** subtab.
3. Uncheck the "ads" filter and press the **Load from** button.
4. Scroll down to **Unprompted** and press the **Install** button. (Or use CTRL+F for convenience)

</details>

With either method, **please be sure to restart your WebUI after installing.** This allows Unprompted to download its Python dependencies.

## Usage

First, try the included demo template by entering the following as your prompt - this will verify that Unprompted was installed correctly:

`[file common/examples/human/main]`

This is a simple "person generator" that automatically chooses characteristics like hair color, race, and posture.

The `[file]` shortcode will look in `unprompted/templates` for the specified text file (in this case `unprompted/templates/common/examples/human/main.txt`.) You do not need to enter the file extension.

**Example output:**

![image](https://user-images.githubusercontent.com/95403634/206287476-eb37cdaa-723d-41f4-bac9-02056e55767a.png)

## Next Steps

Once you have verified that Unprompted is installed and running correctly, you have a couple options:

1. You can visit the 🎓 [Starter Guide](./docs/GUIDE.md) for a crash course on creating your own templates
2. Or dive into the deep end by exploring the comprehensive 📘 [Manual](./docs/MANUAL.md)

---

## Premium Templates

While Unprompted is completely free to use, we do offer **Premium Template add-ons** that demonstrate some of the software's more advanced functionality.

<img align="left" src="https://i.ibb.co/NYh7ZGS/promo-box-beautiful-soul.png" width=150>

### [Beautiful Soul Template](https://payhip.com/b/L1uNF)
A highly expressive character generator for the A1111 WebUI. With thousands of wildcards and direct ControlNet integration, this is by far our most powerful Unprompted template to date. <strong>Available at half price until November 11th!</strong>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<img align="left" src="https://i.postimg.cc/nhchddM9/Demon-Crawl-Avatar-Generator-Box.png" width=150>

### [DemonCrawl Avatar Generator](https://payhip.com/b/qLUX9)
Generate pixel art in the style of DemonCrawl with this custom Stable Diffusion model! Trained on more than 50 avatars from the game. Create your very own character portraits even if you're not an artist!
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
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
<sub>**Note:** *For context, I am a solo developer who is not associated with any commercial entities (beyond my own LLC), nor have I received any research grants for this project. Unprompted was funded completely out-of-pocket. Your generosity helps justify the 100s of hours I spent developing this software! ❤️*</sub>

---

## Acknowledgements

We would like to thank the authors of the following libraries, which are used by Unprompted:

- [Python Shortcodes](https://www.dmulholl.com/dev/shortcodes.html) by Darren Mulholland
- [Simple Eval](https://github.com/danthedeckie/simpleeval) by @danthedeckie
- [Casefy](https://github.com/dmlls/python-casefy) by @dmlls
- [CLIPseg](https://github.com/timojl/clipseg) by uddecke, Timo and Ecker, Alexander
- [CLIP Surgery](https://github.com/xmed-lab/CLIP_Surgery) by Yi Li and Hualiang Wang and Yiqun Duan and Xiaomeng Li
- [NLTK](https://github.com/nltk/nltk) by Bird, S., Klein, E., & Loper, E., O'Reilly Media, Inc.
- [pattern](https://github.com/clips/pattern) by Tom De Smedt and Walter Daelemans
- [Moby Thesaurus II](http://onlinebooks.library.upenn.edu/webbin/gutbook/lookup?num=3202) by Grady Ward
- [Insightface](https://github.com/deepinsight/insightface) by Jia Guo, Jiankang Deng, Xiang An, Jack Yu, Baris Gecer
- [Ghost](https://github.com/ai-forever/ghost) by A. Groshev, A. Maltseva, D. Chesakov, A. Kuznetsov and D. Dimitrov
- [FaceFusion](https://github.com/facefusion/facefusion) by Henry Ruhs
- [GPEN](https://github.com/yangxy/GPEN) by Tao Yang, Peiran Ren, Xuansong Xie, and Lei Zhang

---

### 🔧 Found a problem? [Open an Issue.](https://github.com/ThereforeGames/unprompted/issues)

### 💬 For discussion and template sharing, use [the Discussion Board.](https://github.com/ThereforeGames/unprompted/discussions)

### ⭐ Like my work? Please consider giving the repo a "star" for visibility.