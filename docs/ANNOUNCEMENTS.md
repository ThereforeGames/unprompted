# Unprompted Announcements
Stay informed on the latest Unprompted news and updates.

<details><summary>Spice It Up - 6 March 2024</summary>

Hi folks,

I have just released Unprompted v10.7.0, which includes two notable features:

First, the **Magic Spice template** that aims to "beautify" your Stable Diffusion results using techniques from [Fooocus](https://github.com/lllyasviel/Fooocus) and elsewhere.

It can, for example: run a GPT-2 model to expand your prompt, automatically apply optimized Loras and embeddings, and even fix issues with image contrast. Here are some before/after examples using the `allspice_v1` preset:

![magic_spice_demo]([base_dir]/images/posts/magic_spice_demo.jpg)

This update also adds the `[autotone]` shortcode, which implements the Photoshop algorithm by the same name. It adjusts the black point of an image to enhance contrast. Particularly useful when working with low CFG or Loras that present gamma problems. Simply include `[after][autotone][/after]` in your prompts to engage the feature:

![autotone_demo]([base_dir]/images/posts/autotone_demo.png)

Finally, v10.7.0 addresses a few bugs and improves compatibility with the Forge WebUI.

Thank you for enjoying Unprompted.

</details>

<details><summary>Cool Autumn Update — 11 October 2023</summary>

Hi folks,

I'm pleased to announce the release of Unprompted v10.0.0. This is a major update that brings a number of new features and improvements, including:

## Facelift

![facelift_demo]([base_dir]/images/posts/facelift_demo.png)

This template utilizes the new shortcodes `[faceswap]` and `[restore_faces]` to provide an all-in-one solution for faceswapping.

It aims to provide a few benefits over other popular solutions such as Roop:

- Faster inference time due to caching features. Facelift is a couple seconds faster than Roop on my machine (Geforce 3090.) Caching can be disabled for low-memory devices.
- I include a copy of the `insightface` package to circumvent known challenges of installing said package via pip.
- While `insightface` is still the best available option for faceswapping, Facelift supports additional additional techniques `ghost` and `face_fusion`. You can chain them together for potentially better results.
- Similarity-based handling of multiple faces. Facelift will automatically select the best face to swap with, and can be configured to bypass itself if the similarity doesn't meet a `minimum_threshold`.
- You can run Facelift on an arbitrary image instead of the SD ouput.

And don't forget:

## GPEN Support

The A1111 WebUI natively supports CodeFormer and GFPGAN for face restoration, but not GPEN. Unprompted implements it in v10. You can use it with `[restore_faces]` or through the Facelift template. GPEN is a great option for face restoration, and I've found that it often produces better results than the other two.

## Civitai Downloader

You can now download Civitai files directly from your prompt:

```
Photo of a dog [civitai lora "epiCRealismHelper" 0.5]
```

This will automatically request "epicRealismHelper" from the Civitai API, download the first result, and format your prompt accordingly (e.g `Photo of a dog <lora:epiCRealismHelper:0.5>`).

If it can't find said file from the search term alone, you can specify an optional `_id` parameter as shown:

```
[civitai lora "epiCRealismHelper" 0.5 _id=110334]
```

This makes it easier than ever to share your prompts with others. And it won't ping the API if you already have the file downloaded.

## New premium template: Beautiful Soul

![beautiful_soul]([base_dir]/images/posts/beautiful_soul.png)

Beautiful Soul is a highly expressive character generator for Unprompted. It features thousands of wildcards and integration with ControlNet. Check it out if you're interested, it's a great way to produce very unique characters and support Unprompted while doing so: https://payhip.com/b/L1uNF

It is currently available at an introductory price.

---

As always, you can check out the full changelog here: https://github.com/ThereforeGames/unprompted/blob/main/docs/CHANGELOG.md

If you run into any issues with the new version, please open an issue on Github and I'll be happy to help. The faceswapping stuff has a lot of dependencies, so it's possible that something might break on your machine. I've tested it on Windows, but not Linux or Mac.

Have an awesome day!
</details>

<details><summary>Zoom Enhance Enhanced — 1 August 2023</summary>

Hi folks,

Over the last few weeks, I have released many improvements to Unprompted's logging capabilities. The motivation for these updates was in part due to a longstanding issue with zoom_enhance that I was having trouble figuring out.

Well, I can say now with reasonable confidence that the problem was related to the way I was copying the WebUI's `p` object. In recent versions of the WebUI, my shallow copy of `p` led to numerous problems with image processing. Switching to a deep copy was not a viable alternative, because the object contains custom modules that Python's `copy()` method doesn't know what to do with.

Now in Unprompted v9.13.2, all processes in the `[after]` routine will refer to the original `p` object instead. The reason I didn't do this in the first place is because it means I have to temporarily disable other scripts with compatibility issues, such as ControlNet and Regional Prompter. Some scripts are more difficult to disable than others, but I think I got the major ones sorted out.

Let's go over some other exciting changes to `[zoom_enhance]`:

- If a certain extension isn't playing nice with my bypass rules, **you can use the `_alt` parg to engage alternate image processing.** This sends the generation task off to `[img2img]`, which instantiates its own `p` object and should prove more compatible (at the cost of some performance and overhead.)

- In img2img mode, **you can now use `[zoom_enhance]` outside of the `[after]` block!** This means the shortcode will run on your init image before the WebUI has a chance to modify it. Very useful if you just want to enhance an existing image without re-processing the entire thing. Keep in mind that the normal img2img task will still run afterwards and output a second picture. Until I find a way to disable that, you can simply lower the stepcount to 1 to minimize runtime.

- **You can now chain together multiple `[zoom_enhance]` blocks which will run independently of each other.** Prior to this, you would have to specify multiple masks and replacement rules using the vertical pipe delimiter, e.g. `mask="face|hands" replacement="better face|better hands"`, but this was a bit unintuitive and prone to error on certain kinds of images. (The option is still there if you need it.)

With the longstanding bugs solved, I plan to experiment with other interesting features for `[zoom_enhance]` as well as the companion template Bodysnatcher. Let me know if you have any ideas you would like to see added, either for this shortcode or Unprompted in general. 🙂

Thanks for reading!

</details>

<details><summary>Hot Summer Update — 24 June 2023</summary>

Hello! It's been a couple months since I've had time to work on Unprompted, but I'm happy to finally announce the arrival of v9.3.0 - just in time for the summer. 😎

This is mainly a quality-of-life update that will make your prompting workflow more convenient. Let's go over what's new:

## The [bypass] shortcode

You can now selectively disable shortcodes for the duration of a run!

Let's say you're working on a lengthy script and you want to disable all instances of `[txt2mask]` for debugging purposes. Rather than having to carefully extract bits of code, you can just slap a `[bypass]` at the start of your script:

```
[bypass txt2mask]
```

Additionally, you could use this shortcode inside of a conditional like `[if]` for some fancy logic processing. Why would you want to do that? Well, I have no idea, but you can do it!

## The Wizard Capture tab

I added a snazzy new tab to the Wizard that lets you produce code for the last image you generated.

It contains a `[sets]` block with your inference settings (CFG scale, denoising strength, etc) as well as your prompt and negative prompt.

You can save the code to your `templates` directory and call it later with `[file]`, or send it to somebody as an easy 'preset' for foolproof image reproduction.

## Reworked Wizard UIs

![new_txt2mask_ui]([base_dir]/images/posts/new_txt2mask_ui.png)

The `[txt2mask]` and Bodysnatcher interfaces have received a facelift! They were getting a bit unwieldy with so many options, so I categorized everything into accordion menus and improved the labels in some cases.

## [txt2mask] now supports FastSAM

A new image masking method called FastSAM [made some waves on the Stable Diffusion Reddit](https://www.reddit.com/r/StableDiffusion/comments/14fuqju/fast_segment_anything_40msimage/) earlier this week.

I have implemented it in `[txt2mask]` - simply set `method` to `fastsam` to give it a try!

I can confirm that it is indeed fast. However, `clipseg` is still superior in terms of accuracy. To date, I have incorporated three different types of "Segment Anything" solutions (`clip_surgery`, `grounding_dino`, `fastsam`) and unfortunately none of them are particularly good at creating segmentation masks from text prompts. SAM likely needs additional postprocessing before it can compete with `clipseg` for the purpose of text masking.

## What's next?

I am fairly satisfied withUnprompted's list of features, so I plan to turn my attention to GitHub and catch up on the issue tracker. The next couple patches will likely focus on improving stability.

Enjoy!

</details>

<details><summary>The Big Syntax Update — 25 April 2023</summary>

As part of my ongoing effort to transform Unprompted into a full-featured programming language, I have finally addressed one of its biggest pain points: nested shortcode syntax! Writing logic-heavy templates is a whole lot simpler now.

Take, for example, a snippet of Unprompted code in **the old syntax:**

```
[if my_var=1]
	{if another_var=2}
		{{if third_var=3}}
			{{{sets fourth_var=4}}}
			{{{sets reaction="ew"}}}
		{{/if}}
	{/if}
[/if]
```

Keeping track of the number of squiggly brackets to use was a painful affair, and you better pray you didn't have to refactor large swathes of code.

Now, you just write your nested statements like you would in any normal language. Here's **the new syntax:**

```
[if my_var=1]
	[if another_var=2]
		[if third_var=3]
			[sets fourth_var=4]
			[sets reaction="wow so clean"]
		[/if]
	[/if]
[/if]
```

Of course, you could just combine all those `[if]` blocks into a single statement... but I'm trying to show off the nesting functionality!

This works with every block-scope shortcode that needed it, including `[for]` loops, `[swich]` blocks, and more.

## The catch

The catch is, shortcodes that support the new nesting format will no longer parse `{}` like they used to. **Old templates will have to be updated to the new format manually.**

I have already updated the `common/templates/functions` files for you. If you want a closer look at the new syntax, please check `common/templates/functions/bodysnatcher.txt` - it covers a lot of ground.


## Are secondary shortcode tags { } still needed? 

There is one situation where you will still need to use secondary shortcode tags: **use {} when you want to pass shortcodes directly into the arguments of other shortcodes.** For example:

```
[file "{choose}some_file|another_file{/choose}"]
```

This is one limitation of the shortcode engine that does not bother me much. If anything, it might be easier to read this way as opposed to a shortcode with a bunch of square brackets nested into the arguments. The current implementation is at least visually distinct.

It is also worth noting that the new nesting syntax must be "applied" to the source file of every shortcode that should support it, like so:

```
def preprocess_block(self,pargs,kwargs,context): return True
```

I believe I already added this to all the relevant shortcodes, but if there are any I missed, they will default to the old `{}` syntax. Don't forget to use `preprocess_block()` if you're making your own shortcodes.

## Other syntax changes

Unprompted v9.0.0 includes a few other changes to the language:

- The `[choose]` shortcode now pairs much better with `[file]`. Previously, you had to include your `[choose][/choose]` inside of a file itself. Now, you can do this: `[choose][file somefile][/choose]` and it will pick a random line from `somefile`. This makes it easier to import wildcard lists that were made for other extensions.
- Some shortcodes, such as `[set]` will now sanitize the content with the new `Unprompted.Config.syntax.sanitize_block` rule.
- You can now use advanced expressions with `[sets]`, e.g. `[sets my_var="1 + 1"]` will set `my_var` to 2.

Please see the changelog for more details.

Thank you for your continued support, and have fun!

[Discuss this post 🡢](https://github.com/ThereforeGames/unprompted/discussions/135)

</details>

<details><summary>Introducing the "Bodysnatcher" Template — 16 April 2023</summary>

The latest version of the Unprompted extension includes **a GUI template for full-body swaps!** To my knowledge, it is the first of its kind. Let me explain what makes it a potentially interesting addition to your workflow:

Bodysnatcher leverages an assortment of shortcodes as well as ControlNet to replace (or "recast") a subject **without affecting the background or other objects in your image.**

![tony_soprano_to_brad_pitt]([base_dir]/images/bodysnatcher_example_1.png)

When you enable the template and press Generate, it sets off the following chain of events:

- First, Bodysnatcher calculates the canvas size automatically, so you do not have to specify width or height.
- It creates an inpainting mask of the desired subject (i.e. "man") using txt2mask.
- It runs the main img2img swap.
- Finally, it improves face details on the resulting image with [zoom_enhance].

Here's a visual representation of the process:

![bodysnatcher_process]([base_dir]/images/bodysnatcher_example_2.png)

Imagine doing all of that by hand. No thank you!

## Use Cases

With txt2video breakthroughs happening left and right, you could soon use Bodysnatcher to recast actors in a live production or video game.

![bodysnatcher_process]([base_dir]/images/bodysnatcher_example_3.png)

Additionally, this template can help with creating more variety in a dataset. Let's say you wanted to finetune an embedding on an article of clothing - you need pictures of said clothing worn in different contexts. If all of your training images show the same person in the same clothes, you risk cooking the wrong data into your embedding.

Using Bodysnatcher and the right ControlNet units, you can stretch a limited set of data a lot further. Leveraging AI to improve AI models has a lot of untapped potential.

## Obligatory "Does It Work On Waifus?"

Sort of. The initial image must have some shading and depth to it, otherwise you are going to have a rough time achieving consistent style in your swaps. Finding a good balance between likeness and style is more difficult with anime. Character Loras just aren't built for this kind of thing - possibly because they're trained on relatively few parameters. Lycoris and Textual Inversion seem to fare better. But Dreambooth is still unrivaled in terms of quality and flexibility.

Also, you will need to find a different ControlNet "loadout" for anime. I got okay results with the new lineart_anime model, openpose_full and color. Dial the weight back to 0.25-0.5 and set denoising strength quite high (>=0.9), otherwise your character likeness will go out the window.

![bodysnatcher_process]([base_dir]/images/bodysnatcher_example_4.png)

## More Features

Bodysnatcher has a few other bells and whistles I haven't mentioned yet:

- There's an option to "keep original hands and feet" which helps cut down on the nightmare fuel. Assuming both actors share a similar body type and skin tone, you don't really need to regenerate their extremities.
- You can use loras and embeddings within the subject field.
- Compatible with batch size and batch count.
- Compatible with "Only masked" mode if you want to make high res stuff.
- It's primarily intended for photos that depict a single subject of the given class. If your class is "woman" and the picture contains two women, both of them are gonna get bodysnatched. You can, however, draw a mask on the content you want to "lock in" - anything you mask manually will not change.
- It's remarkably consistent once you set it up. I haven't cherrypicked any of the example images. Of course, that has a lot to do with using ControlNet (the GOAT) and quality models.

Have fun!

</details>

<details><summary>Enhance! CSI Magic Brought to Life — 12 March 2023</summary>

I'm pleased to announce the latest addition to Unprompted: the `[zoom_enhance]` shortcode.

Named after [the totally-not-fake technology from CSI](https://www.youtube.com/watch?v=I_8ZH1Ggjk0), `zoom_enhance` allows you to automatically upscale small details within your image where Stable Diffusion tends to struggle. It is particularly good at fixing faces and hands in long-distance shots.

![zoom_enhance_example](https://user-images.githubusercontent.com/95403634/224587439-947cf094-2d20-45f7-9c2c-491b51d62683.png)

## How does it work?

The `[zoom_enhance]` shortcode searches your image for specified target(s), crops out the matching regions and processes them through `[img2img]`. It then blends the result back into your original image. All of this happens behind-the-scenes without adding any unnecessary steps to your workflow. Just set it and forget it.

## Features and Benefits

- Great in both txt2img and img2img modes.
- The shortcode is powered by the `[txt2mask]` implementation of clipseg, which means you can search for literally anything as a replacement target, and you get access to the full suite of `[txt2mask]` settings, such as `padding` and `negative_mask`.
- It's also pretty good at deepfakes. Set `mask="face"` and `replacement="another person's face"` and check out the results.
- It applies a gaussian blur to the boundaries of the upscaled image which helps it blend seamlessly with the original.
- It is equipped with **Dynamic Denoising Strength** which is based on a simple idea: the smaller your replacement target, the worse it probably looks. Think about it: when you generate a character who's far away from the camera, their face is often a complete mess. So, the shortcode will use a high denoising strength for small objects and a low strength for larger ones.
- It is significantly faster than Hires. Fix and won't mess up the rest of your image.
- Compatible with A1111's color correction setting, which you'll probably want to use to avoid issues related to over-saturation.
- In many cases, it makes the "restore faces" option obsolete. Try the shortcode with and without "restore faces" and see for yourself.
- Unlike "restore faces," `[zoom_enhance]` won't interfere with the style of your image. Face restoration is biased toward photography. With this shortcode, you can provide a subject like "illustration of walter white face" to avoid that problem.
- Compatible with all models. You can even use `[set sd_model]` to change your checkpoint just during the upscale step.
- Compatible with batch size and batch count.

## More Examples

Don't take my word for it. Judge for yourself.

![zoom_enhance_example_parrot](https://user-images.githubusercontent.com/95403634/224598218-c469c44d-0ee4-4b9d-8082-7d9930573e81.png)
![zoom_enhance_example_dragon](https://user-images.githubusercontent.com/95403634/224598221-cc07b75a-8587-4d05-9d73-d6f2f6415dd1.png)
![zoom_enhance_example_maisie](https://user-images.githubusercontent.com/95403634/224598223-0725d178-9033-4fac-8c49-755b16faab60.png)
![zoom_enhance_example_trump](https://user-images.githubusercontent.com/95403634/224598224-633e6464-d05c-4c0e-af0b-4c498aa19534.png)

## How to Use

You can access the GUI through **Unprompted » Wizard » Shortcodes » zoom_enhance**:

![image](https://user-images.githubusercontent.com/95403634/224593040-41ab6d55-5366-4752-9880-c3d88360096b.png)

Or slam this into your prompt:

```
[after]{zoom_enhance}[/after]
```

It goes inside of an `[after]` block because it is supposed to execute **after** the generation of an image.

By default, it will look for `face` and replace it with an upscaled `face`. If you're making a specific person --such as Walter White--you should provide a more specific `replacement` value like so:

```
[after]{zoom_enhance replacement="walter white face"}[/after]
```

If you want to fix hands instead of a face, you can try something like this:

```
[after]{zoom_enhance mask="fingers" replacement="closeup hand" max_denoising_strength=0.9 precision=120}[/after]
```
**Note:** it's going to take some trial and error to find optimized settings for hands. Let me know if you find a config that works better than the one above.

You can place multiple `zoom_enhance` blocks back-to-back. Fixes multiple problem areas in one go.

## Limitations

- Because this shortcode calls an img2img task in an unusual manner, it may not be compatible with every extension. Try disabling your other extensions if you run into issues.
- This shortcode has not yet been throughly battle-tested. Your bug reports are appreciated.

</details>

<details><summary>Synonyms, Sketches and Wizards — 28 January 2023</summary>

It's been a while since the last announcement post... let's catch up on some of the new features in Unprompted!

Earlier this week, I added a new tab to the Wizard panel called **Functions Mode**. It searches your templates folder for txt files that begin with the special `[template]` block. These files are then assembled into **custom GUIs** based on their `[set _new]` calls. In other words, your templates can now contain **logic** and **interface elements** inside of a single text file. Very easy to share with others. I hope you'll give Functions Mode a try!

Next, we have a bunch of new natural language processing features in Unprompted. With the power of [NLTK](https://github.com/nltk/nltk) and the [Moby Thesaurus](http://onlinebooks.library.upenn.edu/webbin/gutbook/lookup?num=3202), you can now find synonyms, antonyms, hypernyms, and hyponyms for any text. Once the word databases are downloaded to your machine, an internet connection is not required to use these features.

What are hyponyms and hypernyms, you might ask? Well, they describe a hierarchical relationship between words. For example, **dog** and **cat** are hyponyms of **animal**, and **animal** is a hypernym of **dog** and **cat**.

You can use these functions in place of a traditional set of wildcards. Of course, it's hard to beat a nice, curated list of terms, but if you want fast results, give something like this a try:

```
[hyponyms max=1]food[/hyponyms]
```

Presto, you've got random food.

There have also been some cool updates for the `[txt2mask]` feature. [Shoutout to Weber Samuel](https://github.com/ThereforeGames/unprompted/pull/48) for introducing several new parameters such as negative precision as well as multiple init image support. Very handy!

I also added **Inpaint Sketch compatibility** in the form of the new `sketch_color` and `sketch_alpha` parameters. This can give you much more control over your img2img results, and in the future may even support multiple colors per mask.

That's all for now. Enjoy!

</details>

<details><summary>Happy Holidays from Unprompted — 22 December 2022</summary>

Yep, it's time for some gifts. 🎅

In the newly released Unprompted v4.2.0, the `[txt2mask]` shortcode has received a massive upgrade.

It is now compatible with [the new refined CLIPseg weights](https://github.com/timojl/clipseg#new-fine-grained-weights) which will help you create higher fidelity masks.

If your masks are still looking a bit "blocky," give the new `smoothing` argument a try. Set it to a value around 20 and you should get nice, rounded shapes:

<img src="https://user-images.githubusercontent.com/95403634/209241225-28d5937e-549b-4eae-a719-e055222809e5.png" height=250>

Additionally, you can now specify `size_var` which will cause the shortcode to calculate the amount of space that your mask occupies in the canvas. You can use this to intelligently adjust other parameters, such as CFG scale. For example, if you mask out the "face" of a subject, but it represents a very small percentage of the canvas, you may decide to lower your img2img CFG.

This update also introduces a few new shortcodes for file handling as well as enhancements for `[get]`. Check out the Changelog for more details.

Have a Merry Christmas!

</details>

<details><summary>Housekeeping Update along with txt2mask Support! — 11 December 2022</summary>

Welcome to Unprompted v4.0.0!

The WebUI extension has received a major facelift. It does a much better job now of utilizing the Gradio interface. For example, our markdown files are rendered in the app itself (maybe you're seeing that right now?), so you no longer have to visit Github or wade through your filesystem to figure out what's new. Even the Manual is right there at your fingertips.

It's more than just a pretty face though. Unprompted v4.0.0 also overhauls the "Dry Run" feature to make it... even drier. Previously, Dry Run would engage the WebUI's "Generation" pipeline which meant it had to produce a dummy image. Not great. Fortunately, this is no longer the case.

We have also added an "Enabled" checkbox to the UI so you don't have to switch tabs when you wish to temporarily bypass Unprompted.

On the shortcode side of things, I have rewritten my [txt2mask](https://github.com/ThereforeGames/txt2mask) script as a native Unprompted shortcode. This means you can create unique mask selections for every image in a batch operation!

I hope to add more Stable Diffusion-centric shortcodes in the near future. Up until now, most of my development attention has been spent on building a strong foundation for Unprompted as a general templating language. I think it's in a pretty good spot now, so I can start focusing more on the reason this software exists in the first place: to greatly improve our prompting workflows.

Enjoy.
</details>

<details><summary>Big Update Released & The Direction of Unprompted — 7 December 2022</summary>

In the hopes of establishing a direct line of communication with the userbase, I am going to use this file for sharing news and updates about Unprompted.

You can always refer to [CHANGELOG.md](https://github.com/ThereforeGames/unprompted/blob/main/docs/CHANGELOG.md) for itemized description of changes, but sometimes it's nice to read about things less technically.

An hour ago, I released Unprompted v2.0.0, which is my largest update since launch. It introduces a streamlined form of "advanced expressions" that, in my view, brings Unprompted up to the level of a real, honest-to-goodness templating language.

With advanced expressions, you can really go to town with your shortcode arguments. You can mix-and-match shortcodes with logic evaluation as such:

`[if "variable_a is 'something' and variable_b is not {choose}option a|option b|option c{/choose}"]Print me[/if]`

Under the hood, these expressions are processed with the [simpleeval library](https://github.com/danthedeckie/simpleeval) which is designed to be safe for networked use.

There is one fairly significant drawback to this new feature: I had to change secondary shortcode syntax from `<>` to `{}`. Personally, I liked the aesthetics of `<>` a bit better, but it conflicted with less-than, greater-than logic operators. This means that older templates may not work in v2.0.0, which is a bit of a pain. I only make breaking changes like this when I feel it's worthwhile.

Now that Unprompted has a fairly robust feature set, I plan on turning my attention to bug reports. There are a few kinks I'd like to address soon. In particular, [Unprompted does not work well with the Dynamic Prompts extension](https://github.com/ThereforeGames/unprompted/issues/16), possibly due to a limitation in the A1111 WebUI. I am considering a few different solutions to this - feel free to weigh in with your own input.

Additionally, I would like to overhaul the extension UI as well as the github docs. Both of these were hastily thrown together and could benefit from a lot of polish. You can expect improvements in these areas over the next few updates!

That's all for now - thank you for reading, and good luck with your prompts!
</details>