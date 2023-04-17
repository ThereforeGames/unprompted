# Unprompted Announcements
Stay informed on the latest Unprompted news and updates.

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