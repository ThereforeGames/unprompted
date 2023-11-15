<p align="center">
<img src="https://user-images.githubusercontent.com/95403634/206286547-53f22ebf-e5fc-4bbd-8bad-53b9cb17ae64.png">
</p>

<p align="center"><strong>Links:</strong> 📣 <a href="./docs/ANNOUNCEMENTS.md">Announcements</a> | 📘 <a href="./docs/MANUAL.md">Manual</a> | ⏱ <a href="./docs/CHANGELOG.md">Changelog</a> | 🎓 <a href="./docs/GUIDE.md">Starter Guide</a></p>

## 👋 Introduction

Unprompted is a **powerful templating language** and **Swiss Army knife** for the [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui).

Built around `[shortcodes]`, Unprompted is uniquely designed for **maximum readibility with natural language.** This makes it **easy to learn and use**, even for those with no prior programming experience.

## 📦 Features

- [x] Free
- [x] Includes **70+ shortcodes** out of the box - there are `[if]` conditionals, powerful `[file]` imports, `[choose]` blocks for flexible wildcards, and everything else the prompting enthusiast could possibly want
- [x] Easily extendable with **custom shortcodes**
- [x] Numerous Stable Diffusion features such as `[txt2mask]` and Bodysnatcher that are exclusive to Unprompted
- [x] Ability to organize your `.txt` templates into **folders and subfolders** according to your own preferences
- [x] As **a modern language**, Unprompted supports recursion, nested shortcodes, advanced logic operators, custom configs, pretty much all the good stuff one might expect from the 21st century
- [x] You can programmatically **read and write any Stable Diffusion variable** exposed by the WebUI, such as `negative_prompt` and `cfg_scale`
- [x] Supports **natural language processing features** such as auto-pluralization, finding synonyms, and even verb conjugation
- [x] Includes a growing list of examples that demonstrate advanced functionality, such as **customizing the weight of a choice list** and **applying emphasis to a random part of your prompt**
- [x] Comprehensive documentation that is always up-to-date
- [x] Made by an organic human lifeform

## 🔧 Installation

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

## 📚 Usage

First, let's verify that your installation was successful by trying out an included template. Add this to your prompt:

`[call common/examples/human/main]`

This is a simple "person generator" that automatically chooses characteristics like hair color, race, and posture.

The `[call]` shortcode will look in `unprompted/templates` for the specified text file (so in this case `unprompted/templates/common/examples/human/main.txt`.) You do not need to enter the file extension.

**Example output:**

![image](https://github.com/ThereforeGames/unprompted/assets/95403634/2549646a-8003-4fc0-9bac-2b1011c93f7c)

## 🚀 Next Steps

Now that you have verified Unprompted is installed and running correctly, you have a couple options:

1. Visit the 🎓 [Guides](./docs/GUIDE.md) page and follow our walkthrough on creating your own templates
2. Explore the comprehensive 📘 [Manual](./docs/MANUAL.md) and figure things out at your own pace

---

## 🛒 Premium Templates

While Unprompted is **completely free to use**, we do offer **Premium Template packs** that demonstrate some of the software's more advanced functionality.

<img align="left" src="https://i.ibb.co/hsW7yCN/promo-box-beautiful-soul.png" width=150>

### [Beautiful Soul Template](https://payhip.com/b/L1uNF)
A highly expressive character generator for the A1111 WebUI. With thousands of wildcards and direct ControlNet integration, this is by far our most powerful Unprompted template to date.</strong>
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
<sub>**Note:** *For context, I am a solo developer who is not associated with any commercial entities (beyond my own LLC), nor have I received any grants for this project. Unprompted was funded completely out-of-pocket. Your generosity helps justify the 100s of hours I spent developing this software. ❤️*</sub>

---

## 🙏 Acknowledgements

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

### 🐛 Found a bug? [Open an Issue.](https://github.com/ThereforeGames/unprompted/issues)

### 💬 For discussion and template sharing, use [the Discussion Board.](https://github.com/ThereforeGames/unprompted/discussions)

### ⭐ Like my work? Please consider giving the repo a "star" for visibility.