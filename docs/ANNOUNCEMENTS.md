# Unprompted Announcements
Stay informed on the latest Unprompted news and updates.

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