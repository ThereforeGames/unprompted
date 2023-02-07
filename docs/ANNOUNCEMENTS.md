# Unprompted Announcements
Stay informed on the latest Unprompted news and updates.

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