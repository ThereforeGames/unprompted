# Unprompted Announcements

## **Big Update Released & The Direction of Unprompted** (7 December 2022)
In the hopes of establishing a direct line of communication with the userbase, I am going to use this file for sharing news and updates about Unprompted.

You can always refer to [CHANGELOG.md](https://github.com/ThereforeGames/unprompted/blob/main/docs/CHANGELOG.md) for itemized description of changes, but sometimes it's nice to read about things less technically.

An hour ago, I released Unprompted v2.0.0, which is my largest update since launch. It introduces a streamlined form of "advanced expressions" that, in my view, brings Unprompted up to the level of a real, honest-to-goodness templating language.

With advanced expressions, you can really go to town with your shortcode arguments. You can mix-and-match shortcodes with logic evaluation as such:

`[if "variable_a is 'something' and variable_b is not {choose}option a|option b|option c{/choose}"]Print me[/if]`

Under the hood, these expressions are processed with the [simpleeval library](https://github.com/danthedeckie/simpleeval) which is designed to be safe for networked use.

There is one fairly significant drawback to this new feature: I had to change secondary shortcode syntax from `<>` to `{}`. Personally, I liked the aesthetics of `<>` a bit better, but it conflicted with less-than, greater-than logic operators. This means that older templates may not work in v2.0.0, which is a bit of a pain. I only make breaking changes like this when I feel it's worthwhile.

Now that Unprompted has a fairly robust feature set, I plan on turning my attention to bug reports. There are a few kinks I'd like to address soon. In particular, [Unprompted does not work well with the Dynamic Prompts extension](https://github.com/ThereforeGames/unprompted/issues/16), possibly due to a limitation in the A1111 WebUI. I am considering a few different solutions to this - feel free to weigh in with your own input.

Additionally, I would like to overhaul the extension UI as well as the github docs. Both of these were hastily thrown together and could a lot of polish. You can expect improvements in these areas over the next few updates!

That's all for now - thank you for reading, and good luck with your prompts!