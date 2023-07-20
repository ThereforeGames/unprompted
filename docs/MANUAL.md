# Unprompted Manual

Shortcode syntax is subject to change based on community feedback.

If you encounter any confusing, incomplete, or out-of-date information here, please do not hesitate to open an issue. I appreciate it!

## ❔ Known Issues

<details><summary>Compatibility with ControlNet</summary>

To achieve compatibility between Unprompted and ControlNet, you must manually rename the `unprompted` extension folder to `_unprompted`. This is due to [a limitation in the Automatic1111 extension framework](https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/8011) whereby priority is determined alphabetically.

</details>

<details><summary>Compatibility with other extensions</summary>

The following extension(s) are known to cause issues with Unprompted:

- **stable-diffusion-webui-pixelization**: seems to break Unprompted when "Pixelization" is added as a postprocessing operation in the WebUI settings.

</details>

<details><summary>WebUI randomly locking up</summary>

Gradio v3.2.x reportedly causes some performance issues due to websocket functionality. Try adding `--no-gradio-queue` to your launch options as a possible workaround.

</details>

## 🎓 Proficiency

<details><summary>Atomic vs Block Shortcodes</summary>

Unprompted supports two types of shortcodes:

- Block shortcodes that require an end tag, e.g. `[set my_var]This is a block shortcode[/set]`
- Atomic shortcodes that are self-closing, e.g. `[get my_var]`

These are mutually exclusive. Shortcodes must be defined as one or the other.

</details>

<details><summary>Creating Your Own Shortcodes</summary>

Shortcodes are loaded as Python modules from `unprompted/shortcodes`. You can make your own shortcodes by creating files there (preferably within a subdirectory called `custom`.)

The shortcode name is defined by the filename, e.g. `override.py` will give you the ability to use `[override]`. Shortcode filenames should be unique.

A shortcode is structured as follows:

```
class Shortcode():
	"""A description of the shortcode goes here."""
	def __init__(self,Unprompted):
		self.Unprompted = Unprompted

	def run_block(self, pargs, kwargs, context,content):
		
		return("")

	def cleanup(self):
		
		return("")
```

You can declare an atomic shortcode by replacing `run_block()` with `run_atomic()`:

```
def run_atomic(self, pargs, kwargs, context):
```

Unlike Blocks, our Atomic shortcode does not receive a `content` variable.

The `__init__` function gives the shortcode access to our main Unprompted object, and it's where you should declare any unique variables for your shortcode.

The `run_block` function contains the main logic for your shortcode. It has access to these special variables (the following list was pulled from the [Python Shortcodes](https://www.dmulholl.com/dev/shortcodes.html) library, on which Unprompted depends):

- `pargs`: a list of the shortcode's positional arguments.
- `kwargs`: a dictionary of the shortcode's keyword arguments.
- `context`: an optional arbitrary context object supplied by the caller.
- `content`: the string within the shortcode tags, e.g. `[tag]content[/tag]`

Positional arguments (`pargs`) and keyword arguments (`kwargs`) are passed as strings. The `run_` function itself returns a string which will replace the shortcode in the parsed text.

The `cleanup()` function runs at the end of the processing chain. You can free any unnecessary variables from memory here.

Regarding Blocks, it is important to understand that **the parser evalutes inner shortcodes before outer shortcodes.** Sometimes this is not desirable, such as when dealing with a "conditional" shortcode like `[if]`. Let's consider the following example:

```
[if my_var=1][set another_var]0[/set][/if]
```

In this case, we **do not** want to set `another_var` to 0 unless the outer `[if]` statement succeeds. For this reason, the `[if]` shortcode includes a special `preprocess_block()` function:

```
def preprocess_block(self,pargs,kwargs,context): return True
```

When the parser encounters a block shortcode, it runs the `preprocess_block()` function if it exists. If that function returns True, then any future shortcodes are "blocked" by the parser until it finds the endtag (`[/if]`). This is what allows us to override the normal "inner-before-outer" processing flow.

The `preprocess_block()` function is also useful for executing arbitrary code before parsing the remaining text. Just be aware that the function is not aware of the shortcode's content, and that no `run_...()` functions have executed before this step.

</details>

<details><summary>Secondary Shortcode Tags</summary>

You can use shortcodes directly in the arguments of other shortcodes with **secondary tags.**

To do this, simply write your tags with squiggly brackets `{}` instead of square brackets `[]`. Let's look at an example:

```
[file "{choose}some_file|another_file{/choose}"]
```

Instead of passing `[file]` a specific filename, we are using `{choose}` to pick between `some_file` and `another_file`.

Secondary shortcode tags can have infinite nested depth. The number of `{}` around a shortcode indicates its nested level.

> **💡 Notice:** As of Unprompted v9.0.0, do not use secondary shortcode tags inside of block content. They are only used within arguments now. Please see the 25 April 2023 announcement for more information.

</details>

<details><summary>Advanced Expressions</summary>

Most shortcodes support programming-style evaluation via the [simpleeval library](https://github.com/danthedeckie/simpleeval).

This allows you to enter complex expressions in ways that would not be possible with standard shortcode arguments. For example, the `[if]` shortcode expects unique variable keys and a singular type of comparison logic, which means you **cannot** do something like this:

`[if var_a>=1 var_a!=5]`

However, with advanced expressions, you definitely can! Simply put quotes around your expression and Unprompted will parse it with simpleeval. Check it out:

`[if "var_a>=10 and var_a!=5"]Print me[/if]`

If you wish to compare strings, use `is` and single quotes as shown below:

`[if "var_a is 'man' or var_a is 'woman'"]My variable is either man or woman[/if]`

You can even mix advanced expressions with shortcodes. Check this out:

`[if "var_a is {file test_one} or var_a is {choose}1|2|3{/choose}"]`

**The secondary shortcode tags are processed first** and then the resulting string is processed by simpleeval.

For more information on constructing advanced expressions, check the documentation linked above.

</details>

<details><summary>Escaping Characters</summary>

Use the backtick to print a shortcode as a literal part of your prompt. This may be useful if you wish to take advantage of the prompt editing features of the A1111 WebUI (which are denoted with square brackets and could thus conflict with Unprompted shortcodes.)

Note: you only need to put a single backtick at the start of the shortcode to escape the entire sequence. Inner shortcodes will be processed as normal.

Also note: if a shortcode is undefined, Unprompted will print it as a literal as if you had escaped it.

```
Photo of a `[cat|dog]
```

</details>

<details><summary>Multi-line Atomic Shortcodes</summary>

In my testing, it appears to be possible to write lengthy atomic shortcodes across multiple lines, provided **the first line has a trailing space** and **each subsequent line has a leading space.** Here is an example:

```
[sets 
 cn_0_enabled=1 cn_0_pixel_perfect=1 cn_0_module=softedge_hed cn_0_model=controlnet11Models_softedge cn_0_weight=0.25
 cn_1_enabled=1 cn_1_pixel_perfect=1 cn_1_module=mediapipe_face cn_1_model=control_mediapipe_face_sd15_v2 cn_1_weight=1.0
 cn_2_enabled=1 cn_2_pixel_perfect=1 cn_2_module=t2ia_color_grid cn_2_model=coadapter-color-sd15v1 cn_2_weight=1.0
 cn_3_enabled=1 cn_3_pixel_perfect=1 cn_3_module=openpose_full cn_3_model=controlnet11Models_openpose cn_3_weight=1.0
 ]
```

Do note, however, that your mileage may vary if you are not using the default sanitization rules.

</details>

<details><summary>Special Variables</summary>

In addition to all of the Stable Diffusion variables exposed by Automatic1111's WebUI, Unprompted gives you access to the following variables:

### batch_index

An integer that correponds to your progress in a batch run. For example, if your batch count is set to 5, then `batch_index` will return a value from 0 to 4.

### batch_test

Shortcodes that implement batch processing--such as `[zoom_enhance]`--will test the expression stored in `batch_test` against the batch item index to determine if an image should be bypassed by the shortcode.

Example: you set `batch_test` to `<= 3` and you run a batch process with 5 images. The fifth image will be skipped by shortcodes such as `[zoom_enhance]`. (`batch_index` is zero-indexed, so 3 corresponds to the fourth image.)

### sd_model

You can set this variable to the name of a Stable Diffusion checkpoint, and Unprompted will load that checkpoint at the start of inference. This variable is powered by the WebUI's `get_closet_checkpoint_match()` function, which means that your model name does not have to be 100% accurate - but you should strive to use a string that's as accurate as possible.

### single_seed

You can set this integer variable to lock the seed for all images in a batch run.

You might be wondering why `[set seed]x[/set]` won't accomplish the same thing. Well, this is because the WebUI populates another variable called `all_seeds` for batch runs. It takes your initial seed (let's say 1000) and increments it by 1 for each successive image. So if you're making 4 images (i.e. `batch_count` = 4) and you set `seed` to 1000, your seeds will actually look like this: 1000, 1001, 1002, 1003.

The `single_seed` variable will instead force all the seeds to your chosen value.

It is functionally equivalent to the following:

```
[array all_seeds _fill=1000]
```

### controlnet_*

You can use `[set]` to manage ControlNet settings in this format:

```
[sets controlnet_unit_property=value]
```

Where **unit** is an integer that corresponds to the index of a ControlNet unit (between 0 and your maximum number of units).

Here is a list of valid properties at the time of writing:

- enabled
- module
- model
- weight
- image (loads a file from a filepath string)
- invert_image
- resize_mode
- rgbbgr_mode
- low_vram
- processor_res
- threshold_a
- threshold_b
- guidance_start
- guidance_end
- guess_mode

For example, we can enable units #0 and #3 and set the weight of unit #3 to 0.5 as follows:

```
[sets controlnet_0_enabled=1 controlnet_3_enabled=1 controlnet_3_weight=0.5]
```

You may also use the shorthand `cn_` in place of `controlnet_`.

</details>

<details><summary>Why some shortcode arguments begin with an _underscore</summary>

We use underscores to denote optional system arguments in shortcodes that may also accept dynamic, user-defined arguments.

Take a look at `[replace]` as an example.

`[replace]` allows you to modify a string with arbitrary before-after argument pairings, e.g. `[replace this=that red=blue]`.

However, `[replace]` also features system arguments like `_count` and so the shortcode must have a way to differentiate between the two types.

In short, if the argument begins with `_`, the program will assume it is a system argument of some kind.

That said, we're still ironing out the methodology for underscores - at the moment, some arguments may use underscores where it isn't strictly necessary. If you find any such cases feel free to open an Issue or Discussion Thread about it.

</details>

<details><summary>The config file</summary>

Various aspects of Unprompted's behavior are controlled through `unprompted/config.json`.

If you wish to override the default settings, you should make another file at the same location called `config_user.json`. Modifications to the original config file will **not** be preserved between updates.

Here are some of the settings you can modify:

<details><summary>beta_features (bool)</summary>

Opt into unfinished features by setting `beta_features` to true.

</details>

<details><summary>log_contexts (str)</summary>

This is a comma-delimited list that determines what types of messages will appear in the output console. Defaults to `RESULT,WARNING,ERROR`.

Note: `log_contexts` replaces the old `debug` config setting. If you want to see debug messages, simply add `DEBUG` to the list.

</details>

<details><summary>advanced_expressions (bool)</summary>

This determines whether expressions will be processed by simpleeval. Disable for slightly better performance at the cost of breaking some templates.

</details>

<details><summary>skip_requirements (bool)</summary>

Bypasses the startup requirements check (`install.py`) to minimize startup time.

</details>

<details><summary>template_directory (str)</summary>

This is the base directory for your text files.

</details>

<details><summary>txt_format (str)</summary>

This is the file extension that Unprompted will assume you're looking for with `[file]`.

</details>

<details><summary>syntax.sanitize_before (dict)</summary>

This is a dictionary of strings that will be replaced at the start of processing. By default, Unprompted will swap newline and tab characters to the `\\n` placeholder.

</details>

<details><summary>syntax.sanitize_after (dict)</summary>

This is a dictionary of strings that will be replaced after processing. By default, Unprompted will convert the `\\n` placeholder to a space.

</details>

<details><summary>syntax.tag_start (str)</summary>

This is the string that indicates the start of a shortcode.

</details>

<details><summary>syntax.tag_end (str)</summary>

This is the string that indicates the end of a shortcode.

</details>

<details><summary>syntax.tag_start_alt (str)</summary>

This is the string that indicates the start of a secondary shortcode.

</details>

<details><summary>syntax.tag_end_alt (str)</summary>

This is the string that indicates the end of a secondary shortcode.

</details>

<details><summary>syntax.tag_close (str)</summary>

This is the string that indicates the closing tag of a block-scoped shortcode.

</details>

<details><summary>syntax.tag_escape (str)</summary>

This is the string that allows you to print a shortcode as a literal string, bypassing the shortcode processor.

Note that you only have to include this string once, before the shortcode, as opposed to in front of every bracket.

</details>

<details><summary>templates/default (str)</summary>

This is the final string that will be processed by Unprompted, where `*` is the user input.

The main purpose of this setting is for hardcoding shortcodes you want to run every time. For example: `[img2img_autosize]*`

</details>

<details><summary>templates/default_negative (str)</summary>

Same as above, but for the negative prompt.

</details>

</details>

## 🧙 The Wizard

<details><summary>What is the Wizard?</summary>

The Unprompted WebUI extension has a dedicated panel called the Wizard. It is a GUI-based shortcode builder.

Pressing **"Generate Shortcode"** will assemble a ready-to-use block of code that you can add to your prompts.

Alternatively, you can enable `Auto-include this in prompt` which will add the shortcode to your prompts behind the scenes. This essentially lets you use Unprompted shortcodes as if they were standalone scripts. You can enable/disable this setting on a per-shortcode basis.

The Wizard includes three distinct modes: Shortcodes, Templates, and Capture.

</details>

<details><summary>Shortcodes Mode</summary>

This mode presents you with a list of all shortcodes that have a `ui()` block in their source code.

You can add Wizard UI support to your own custom shortcodes by declaring a `ui()` function as shown below:

```
	def ui(self,gr):
		gr.Radio(label="Mask blend mode 🡢 mode",choices=["add","subtract","discard"],value="add",interactive=True)
		gr.Checkbox(label="Show mask in output 🡢 show")
		gr.Checkbox(label="Use legacy weights 🡢 legacy_weights")
		gr.Number(label="Precision of selected area 🡢 precision",value=100,interactive=True)
		gr.Number(label="Padding radius in pixels 🡢 padding",value=0,interactive=True)
		gr.Number(label="Smoothing radius in pixels 🡢 smoothing",value=20,interactive=True)
		gr.Textbox(label="Negative mask prompt 🡢 negative_mask",max_lines=1)
		gr.Textbox(label="Save the mask size to the following variable 🡢 size_var",max_lines=1)
```

The above code is the entirety of txt2mask's UI at the time of writing. We recommend examining the .py files of other shortcodes if you want to see additional examples of how to construct your UI.

Every possible shortcode argument is exposed in the UI, labeled in the form of `Natural description 🡢 technical_argument_name`. The Wizard only uses the technical_argument_name when constructing the final shortcode.

There are a few reserved argument names that will modify the Wizard's behavior:

- `verbatim`: This will inject the field's value directly into the shortcode. Useful for shortcodes that can accept multiple, optional arguments that do not have pre-determined names.
- `str`: This will inject the field's value into the shortcode, enclosing it in quotation marks.
- `int`: This will inject the field's value into the shortcode, casting it as an integer. 

</details>

<details><summary>Templates Mode</summary>

This mode presents you with a list of txt files inside your `Unprompted/templates` directory that begin with a `[template]` block.

By including this block in your file, Unprompted will parse the file for its `[set x _new]` statements and adapt those into a custom Wizard UI.

The `_new` argument means *"only set this variable if it doesn't already exist,"* which are generally the variables we want to show in a UI.

The `[template]` block supports the optional `name` argument which is a friendly name for your function shown in the Templates dropdown menu.

The content of `[template]` is a description of your script to be rendered with [Markdown](https://www.markdownguide.org/basic-syntax/), which means you can include rich content like pictures or links. It will show up at the top of your UI.

The `[set]` block supports `_ui` which determines the type of UI element to render your variable as. Defaults to `textbox`. Here are the possible types:

- `textbox`: Ideal for strings. The content of your `[set]` block will be rendered as placeholder text.
- `number`: Ideal for integers. 
- `radio`: A list of radio buttons that are determined by the `_choices` argument, constructed as a delimited list.
- `dropdown`: A dropdown menu that is populated by the `_choices` argument, constructed as a delimited list.
- `slider`: Limits selection to a range of numbers. You must also specify `_minimum`, `_maximum` and `_step` (step size, normally 1) for this element to work properly.

The `[set]` block supports `_info` which is descriptive text that will appear near the UI element.

Supports the `[wizard_ui_accordion]` shortcode which will group the inner `[set]` blocks into a collapsible UI element.

</details>

<details><summary>Capture Mode</summary>

This mode offers a convenient way to produce the code for the last image you generated.

It has a few settings that change how the code is formatted:

- **Include inference settings:** Determines which inference options to show as a `[sets]` block. These are settings such as CFG Scale, batch count, etc. On `simple`, it will exclude variables with a value of 0 as well as empty strings. `Verbose` gives you everything.
- **Include (negative) prompt:** Determines whether to show the prompt. On `original`, it will show the prompt with shortcodes intact, whereas `postprocessed` gives you the prompt after shortcodes have been executed.
- **Include model:** adds the checkpoint name to the `[sets]` block.
- **Add [template] block**: Prepends the result with a placeholder `[template]` block that makes your code compatible with the Wizard Templates tab.


</details>

## ⚙️ Shortcodes

<details><summary>Basic Shortcodes</summary>

This section describes all of the included basic shortcodes and their functionality.

<details><summary>[#]</summary>

## Comment

Use this to write comments in your templates. Comments are ultimately discarded by Unprompted and will not affect your final output.

```
[# This is my comment.]
```
</details>

<details><summary>[##]</summary>

Same as `[#]` but for multiline comments.

```
[##]
This is my multiline comment.
We're still commenting.
I can't believe it, we're doing 3 lines of text!
[/##]
```

</details>

<details><summary>[after after_index(int)]</summary>

Processes the content after the main task is complete.

This is particularly useful with the A1111 WebUI, as it gives you the ability to queue up additional tasks. For example, you can run img2img after txt2img from the same template.

Supports the optional `after_index` argument which lets you control the order of multiple `[after]` blocks. Defaults to 0. For example, the `[after 2]` block will execute before the `[after 3]` block.

You can `[get after_index]` inside of the `[after]` block, which can be useful when working with arrays and for loops.

```
Photo of a cat
[after]
	[sets prompt="Photo of a dog" denoising_strength=0.75]
	[img2img]
[/after]
```

</details>

<details><summary>[antonyms]</summary>

Replaces the content with one or more random antonyms. This shortcode is powered by a combination of WordNet and Moby Thesaurus II. Does not require an online connection after first use (word databases are downloaded to disk.)

The optional `max` argument allows you to specify the maximum number of antonyms to return. Defaults to -1, which returns all antonyms. The antonyms list is delimited by `Unprompted.Config.syntax.delimiter`.

The optional `include_self` positional argument determines whether the original content can be returned as a possible result. Defaults to False.

The optional `enable_moby` keyword argument determines whether Moby Thesaurus II will be referenced. Defaults to True. On first use, the Moby Thesaurus will be downloaded to the `lib_unprompted` folder - it is about 24 MB.

The optional `enable_wordnet` keyword argument determines whether WordNet will be referenced. Defaults to True.

It is worth noting that Moby does not have native antonym support. This shortcode first queries WordNet, the results of which are then sent to Moby via `[synonyms]`.

```
[antonyms]cold[/antonyms]
```

</details>

<details><summary>[array name(str)]</summary>

Manages a group or list of values.

The first positional argument, `name`, must be a string that corresponds to a variable name for the array. You can later use the same identifier with `[get]` to retrieve every value in the array as a delimited string.

If you want to **retrieve** values at specific indexes, supply the indexes as positional arguments as shown below:

```
[array my_array 2 4 3]
```

If you want to **set** values at specific indexes, supply the indexes as keyword arguments as shown below:

```
[array my_array 2="something" 4=500 3="something else"]
```

Supports the optional `_delimiter` argument that defines the separator string when retrieving multiple values from the array. Defaults to your `Config.syntax.delimiter` setting.

Supports `_append` which allows you to add values to the end of the array. You can pass multiple values into `_append` with your `_delimiter` string, e.g. `[array my_array _append="something|another thing|third thing"]`.

Similarly, supports `_prepend` which allows you to insert values to the beginning of the array.

Supports `_del` which will remove a value from the array at the specified index, e.g.

```
BEFORE: my_array = 5,7,9,6
```
```
[my_array _del=1]
```
```
AFTER: my_array = 5,9,6
```

Supports `_remove` which will remove the first matching value from the array, e.g.

```
BEFORE: my_array = 5,7,9,6
```
```
[my_array _remove=9]
```
```
AFTER: my_array = 5,7,6
```

Supports `_find` which will return the index of the first matching value in the array.

Supports `_shuffle` which will randomize the order of the array.

Supports `_fill` kwarg which will populate the entire array with a given value.

</details>

<details><summary>[article]</summary>

Returns the content prefixed with the correct English indefinite article, in most cases `a` or `an`.

Supports the optional `definite` positional argument which will instead return the definite article as a prefix, usually `the`.

```
[article]tiger[/article]
```

```
RESULT: a tiger
```

```
[article]apple[/article]
```
```
RESULT: an apple
```

</details>

<details><summary>[autocorrect]</summary>

Performs word-by-word spellcheck on the content, replacing any typos it finds with the most likely correction.

Powered by the [pattern](https://github.com/clips/pattern/wiki/pattern-en) library - see pattern docs for more info.

Supports the optional `confidence` argument, which is a float between 0 and 1 that determines how similar the suggested correction must be to the original content. Defaults to 0.85.

```
[autocorrect]speling is vrey dfficult soemtims, okky!!![/autocorrect]
```
```
RESULT: spelling is very difficult sometimes, okay!!!
```

</details>

<details><summary>[bypass]</summary>

Allows you to disable the execution of specific shortcodes for the remainder of the run. It is similar to `[override]`, but for shortcodes instead of variables. Particularly useful for debugging purposes.

Provide the names of the shortcodes you wish to disable as pargs, separated by spaces.

If you supply `_toggle`, the shortcode can re-enable shortcodes that were previously bypassed.

```
[bypass repeat chance][repeat 3]do not print me[/repeat][chance 100]skip this too[/chance]print me
```
```
RESULT: print me
```

</details>

<details><summary>[case]</summary>

See `[switch]`.

</details>

<details><summary>[casing type]</summary>

Converts the casing of content to the selected type. Possible types:

- uppercase
- lowercase
- camelcase
- pascalcase
- snakecase
- constcase
- kebabcase
- upperkebabcase
- separatorcase
- sentencecase
- titlecase
- alphanumcase

For more information on these types, consult the [casefy docs](https://github.com/dmlls/python-casefy), the library on which this shortcode depends.

```
[casing uppercase]why am i screaming[/casing]
```
```
Result: WHY AM I SCREAMING
```

</details>

<details><summary>[chance int {_sides}]</summary>

Returns the content if the integer you passed is greater than or equal to a randomly generated number between 1 and 100.

You can change the upper boundary by specifying the optional `_sides` argument.

```
[chance 25]I will show up in your prompt 25% of the time.[/chance]
```

</details>

<details><summary>[choose]</summary>

Randomly returns one of multiple options, as delimited by the vertical pipe or newline character.

Supports `_case` which overrides the random nature of this shortcode with a pre-determined index (starting at 0.) Example: `[choose _case=1]red|yellow|green[/choose]` will always return `yellow`. You can also pass a variable into this argument.

Supports an optional positional argument that tells the shortcode how many times to execute (default 1). For example: `[choose 2]Artist One|Artist Two|Artist Three|Artist Four[/choose]` will return two random artists.

Supports the optional `_sep` argument which is a string delimeter that separates multiple options to be returned (defaults to `, `). In the example above, you might get `Artist One, Artist Three` as a result. When only returning one option, `_sep` is irrelevant.

Supports the optional `_weighted` argument, which allows you to customize the probability of each option. Weighted mode expects the content to alternate between **weight value** and **the option itself** using the normal delimiter. For example, if you want your list to return Apple 30% of the time, Strawberry 50% of the time, and Blueberry 20% of the time you can do it like this:

```
[choose _weighted]
3|Apple
5|Strawberry
2|Blueberry
[/choose]
```

If you skip a weight value--e.g. `3|Apple|Strawberry`--then the following option (Strawberry) will automatically have a weight value of 1.

The weight value dictates the number of times that an option is added to the master list of choices, which is then shuffled and picked from at random. So, if your content is `2|Blue|3|Red|Green` the master list becomes `Blue,Blue,Red,Red,Red,Green`.

Supports the `_raw` parg, which prevents the execution of inner shortcodes except the one that is selected by `[choose]`.

```
[choose]red|yellow|blue|green[/choose]
```

</details>

<details><summary>[config]</summary>

Updates your Unprompted settings with the content for the duration of a run. Generally you would put this at the top of a template.

Supports inline JSON as well as external JSON files.

Supports relative and absolute filepaths.

Do not enter a file extension, `.json` is assumed.

```
[config]{"debug":True,"shortcodes":{"choose_delimiter":"*"}}[/config]
```

```
[config]./my_custom_settings[/config]
```

</details>

<details><summary>[conjugate]</summary>

Converts the verbs in the content to variety of conjugated forms.

Powered by the [pattern](https://github.com/clips/pattern/wiki/pattern-en) library - see pattern docs for more info.

Supports the optional `tense` argument. Defaults to `present`. Other options include: `infinitive`, `past`, `future`.

Supports the optional `person` argument for perspective. Defaults to `3`. Other options include: `1`, `2` and `none`.

Supports the optional `number` argument. Defaults to `singular`. Also supports `plural`.

Supports the optional `mood` argument. Defaults to `indicative`. Other options include: `imperative`, `conditional` and `subjunctive`.

Supports the optional `aspect` argument. Defaults to `imperfective`. Other options include: `perfective` and `progressive`.

Supports the optional `negated` boolean argument. Defaults to 0.

Supports the optional `parse` boolean argument. Defaults to 1.

Supports the optional `alias` argument, which is a shorthand "preset" for the above settings. Overrides your other arguments. The following aliases are supported: `inf`,`1sg`,`2sg`,`3sg`,`pl`,`part`,`p`,`1sgp`,`2sgp`,`3gp`,`ppl`,`ppart`.

```
[conjugate tense="past"]She says[/conjugate]
```
```
RESULT: She said
```

</details>

<details><summary>[do until(str)]</summary>

Do-until style loop. The content is processed, then the `until` expression is evaluated - if it's false, the content is processed again. Repeat until `until` is true.

```
[sets my_var=0]
[do until="my_var > 5"]
	Print me
	[sets my_var="my_var + 1"]
[/do]
```

</details>

<details><summary>[elif]</summary>

Shorthand "else if." Equivalent to `[else][if my_var="something"]content[/if][/else]`.

```
[set my_var]5[/set]
[if my_var=6]Discard this content[/if]
[elif my_var=5]Return this content![/elif]
```

</details>

<details><summary>[else]</summary>

Returns content if a previous conditional shortcode (e.g. `[if]` or `[chance]`) failed its check, otherwise discards content.

**Note:** In its current implementation, `[else]` should appear immediately after the conditional shortcode - don't try to get too crazy with nesting or delayed statements or it will probably fail.

```
[if my_var=0]Print something[/if][else]It turns out my_var did not equal 0.[/else]
```

</details>

<details><summary>[eval]</summary>

Parses the content using the simpleeval library, returning the result. Particularly useful for arithmetic.

simpleeval is designed to prevent the security risks of Python's stock `eval` function, however I make no assurances in this regard. If you wish to use Unprompted in a networked environment, do so at your own risk.

```
[eval]5 + 5[/eval]
```

</details>

<details><summary>[file path(str)]</summary>

Processes the content of `path` (including any shortcodes therein) and returns the result.

`unprompted/templates` is the base directory for this shortcode, e.g. `[file example/main]` will target `unprompted/templates/example/main.txt`.

Do not enter a file extension, `.txt` is assumed.

Supports relative paths by starting the `path` with `./`, e.g. `[file ./main]` will target the folder that the previously-called `[file]` resides in.

This shortcode is powered by Python's glob module, which means it supports wildcards and other powerful syntax expressions. For example, if you wanted to process a random file inside of the `common` directory, you would do so like this: `[file common/*]`

Supports optional keyword arguments that are passed to `[set]` for your convenience. This effectively allows you to use `[file]` like a function in programming, e.g. `[file convert_to_roman_numeral number=7]`.

The file is expected to be `utf-8` encoding. You can change this with the optional `_encoding` argument.

```
[file my_template/common/adjective]
```

</details>

<details><summary>[filelist path(str)]</summary>

Returns a delimited string containing the full paths of all files in a given path.

This shortcode is powered by Python's glob module, which means it supports wildcards and other powerful syntax expressions.

Supports the optional `_delimiter` argument which lets you specify the separator between each filepath. It defaults to your config's `syntax.delimiter` value (`|`).

Supports the optional `_basename` parg that causes the shortcode to return filenames instead of full paths.

Supports the optional `_hide_ext` parg that causes the shortcode to trim filename extensions out of the returned string.

Supports the macro `%BASE_DIR%` which will be substituted with an absolute path to the Unprompted extension.

```
[filelist "C:/my_pictures/*.*"]
```

</details>

<details><summary>[for var "test var" "update var"]</summary>

Returns the content an arbitrary number of times until the `test` condition returns false.

Importantly, the `test` and `update` arguments must be enclosed in quotes because they are parsed as advanced expressions.

`var` is initialized as a user variable and can be accessed as normal, e.g. `[get var]` is valid.

The result of the `update` argument is set as the value of `var` at the end of each loop step.

```
[for i=0 "i<10" "i+1"]
Current value of i: [get i]
[/for]
```

</details>

<details><summary>[get variable]</summary>

Returns the value of `variable`.

Supports secondary shortcode tags with the optional `_var` argument, e.g. `[get _var="<file example>"]`.

You can add `_before` and `_after` content to your variable. This is particularly useful for enclosing the variable in escaped brackets, e.g. `[get my_var _before=[ _after=]]` will print `[value of my_var]`.

Supports the optional `_default` argument, the value of which is returned if your variable does not exist e.g. `[get car_color _default="red"]`.

Supports returning multiple variables, e.g. `[get var_a var_b]` will return the values of two variables separated by a comma and space.

You can change the default separator with `_sep`.

```
My name is [get name]
```

</details>

<details><summary>[if variable {_not} {_any} {_is}]</summary>

Checks whether `variable` is equal to the given value, returning the content if true, otherwise discarding the content.

Supports the testing of multiple variables, e.g. `[if var_a=1 var_b=50 var_c="something"]`. If one or more variables return false, the content is discarded.

The optional `_any` argument allows you to return the content if one of many variables return true. This is the equivalent of running "or" instead of "and" in programming, e.g. `[if _any var_a=1 var_b=50]`.

The optional `_not` argument allows you to test for false instead of true, e.g. `[if _not my_variable=1]` will return the content if `my_variable` does *not* equal 1.

The optional `_is` argument allows you to specify the comparison logic for your arguments. Defaults to `==`, which simply checks for equality. Other options include `!=`, `>`, `>=`, `<` and `<=`. Example: `[if my_var="5" _is="<="]`

Supports [advanced expressions](#advanced-expressions) - useful for testing complex conditions.

```
[if subject="man"]wearing a business suit[/if]
```

```
(Advanced expression demo)
[if "subject is 'man' or subject is 'woman'"]wearing a shirt[/if]
```

</details>

<details><summary>[hypernyms]</summary>

Replaces the content with one or more random hypernyms. This shortcode is powered by WordNet.

The optional `max` argument allows you to specify the maximum number of hypernyms to return. Defaults to -1, which returns all hypernyms. The hypernyms list is delimited by `Unprompted.Config.syntax.delimiter`.

```
[hypernyms max=1]dog[/hypernyms]
```

```
Possible result: animal
```

</details>

<details><summary>[hyponyms]</summary>

Replaces the content with one or more random hyponyms. This shortcode is powered by WordNet.

The optional `max` argument allows you to specify the maximum number of hyponyms to return. Defaults to -1, which returns all hyponyms. The hyponyms list is delimited by `Unprompted.Config.syntax.delimiter`.

```
[hyponyms]animal[/hyponyms]
```

```
Possible results: dog, cat, bird, ...
```

</details>

<details><summary>[info]</summary>

Prints metadata about the content. You must pass the type(s) of data as positional arguments.

Supports `character_count` for retrieving the number of individual characters in the content.

Supports `word_count` for retrieving the number of words in the content, using space as a delimiter.

Supports `sentence_count` for retrieving the number of sentences in the content. Powered by the nltk library.

Supports `filename` for retreiving the base name of a file from the filepath content. For example, if the content is `C:/pictures/delicious hamburger.png` then this will return `delicious hamburger`.

Supports `string_count` for retrieving the number of a custom substring in the content. For example, `[info string_count="the"]the frog and the dog and the log[/info]` will return 3.

Supports `clip_count` for retrieving the number of CLIP tokens in the content (i.e. a metric for prompt complexity.) This argument is only supported within the A1111 WebUI environment.

```
[info word_count]A photo of Emma Watson.[/info]
```
```
Result: 5
```

</details>

<details><summary>[length]</summary>

Returns the number of items in a delimited string or `[array]` variable.

Supports the optional `_delimiter` argument which lets you specify the separator between each item. It defaults to your config's `syntax.delimiter` value (`|`).

Supports the optional `_max` argument which caps the value returned by this shortcode. Defaults to -1, which is "no cap."

```
[length "item one|item two|item three"]
```
```
Result: 3
```

</details>

<details><summary>[log]</summary>

Prints a message to the console.

By default, the message context is `DEBUG`. The first positional argument determines the context.

```
[log ERROR]The value of [get some_variable] is wrong![/log]
```

</details>

<details><summary>[max]</summary>

Returns the greatest value among the arguments. Supports advanced expressions.

```
[sets var_a=2 var_b=500]
[max var_b var_a "100+2" "37"]
```
```
Result: 500
```

</details>

<details><summary>[min]</summary>

Returns the smallest value among the arguments. Supports advanced expressions.

```
[sets var_a=2 var_b=500]
[min var_b var_a "100+2" "37"]
```
```
Result: 2
```

</details>

<details><summary>[override variable]</summary>

Forces `variable` to equal the given value when attempting to `[set]` it.

Supports multiple variables.

In the example below, `my_variable` will equal "panda" after running the `[set]` shortcode.

```
[override my_variable="panda"][set my_variable]fox[/set]
```

</details>

<details><summary>[pluralize]</summary>

Returns the content in its plural form. Powered by the [pattern](https://github.com/clips/pattern/wiki/pattern-en) library - see pattern docs for more info.

Supports the optional `pos` argument. This is the target position of speech and defaults to "noun." In some rare cases, you may want to switch this to "adjective."

```
[pluralize]child[/pluralize]
```
```
RESULT: children
```

</details>

<details><summary>[random {_min} {_max} {_float}]</summary>

Returns a random integer between 0 and the given integer, e.g. `[random 2]` will return 0, 1, or 2.

You can specify the lower and upper boundaries of the range with `_min` and `_max`, e.g. `[random _min=5 _max=10]`.

If you pass `_float` into this shortcode, it will support decimal numbers instead of integers.

```
[set restore_faces][random 1][/set]
```

</details>

<details><summary>[repeat times(int) {_sep}]</summary>

Processes and returns the content a number of `times`.

Supports the optional `_sep` argument which is a string delimiter inserted after each output, excluding the final output. Example: `[repeat 3 _sep="|"]content[/repeat]` will return `content|content|content`.

Supports float values as well. For example, `[repeat 4.2]content[/repeat]` will have a 20% chance to return `content` 5 times instead of 4.

```
[set my_var]0[/set]
[repeat 5]
Variable is currently: [set my_var _out _append]1[/set]
[/repeat]
```

</details>

<details><summary>[replace]</summary>

Updates the content using argument pairings as replacement logic.

Arguments are case-sensitive.

Supports the optional `_from` and `_to` arguments, which can process secondary shortcode tags as replacement targets, e.g. `[replace _from="{get var_a}" _to="{get var_b}"]`.

Supports the optional `_count` argument which limits the number of occurances to replace. For example, `[replace the="a" _count=1]the frog and the dog and the log[/replace]` will return `a frog and the dog and the log`.

Supports the optional `_insensitive` parg to enable case-insensitive search-and-replace.

Supports the optional `_load` kwarg for importing from:to replacement directions from one or more external JSON files.

```
[replace red="purple" flowers="marbles"]
A photo of red flowers.
[/replace]
```
```
Result: A photo of purple marbles.
```

</details>

<details><summary>[round {_precision}]</summary>

Allows you to round the first parg to a certain level of precision.

Supports the optional `_place` int kwarg which determines the level of precision. Defaults to 0.

Supports the optional `_up` parg which will round the number up (ceiling function) instead of normal rounding.

Supports the optional `_down` parg which will round the number down (flooring function) instead of normal rounding.

Supports rounding of both integer and float values.

```
Float example...
[round 1.345 _place=1]
```
```
RESULT: 1.3
```
```
Integer example...
[round 1678 _place=1]
```
```
RESULT: 1680
```

</details>

<details><summary>[set {_append} {_prepend}]</summary>

Sets a variable to the given content.

`_append` will instead add the content to the end of the variable's current value, e.g. if `my_var` equals "hello" then `[set my_var _append] world.[/set]` will make it equal "hello world."

`_prepend` will instead add the content to the beginning of the variable's current value.

Supports the optional `_new` argument which will bypass the shortcode if the variable already exists.

Supports the optional `_choices` argument, which is a delimited string of accepted values. The behavior of this argument depends on whether or not the `_new` argument is present:

- If `_new` and the variable exists with a value that is not accepted by `_choices`, then `_new` is bypassed.
- If not `_new` and we're trying to set a value that is not accepted by `_choices`, then the `[set]` block is bypassed.
- In the Wizard UI for certain kinds of elements, `_choices` is used to populate the element, such as a dropdown menu or radio group.

Supports all Stable Diffusion variables that are exposed via Automatic's Script system, e.g. `[set cfg_scale]5[/set]` will force the CFG Scale to be 5 for the run.

Supports the `_remember` parg that will invoke the `[remember]` shortcode with your variable. See `[remember]` for more information.

```
[set my_var]This is the value of my_var[/set]
```

</details>

<details><summary>[sets]</summary>

The atomic version of `[set]` that allows you to set multiple variables at once.

This shortcode processes your arguments with `[set]` directly, meaning you can take advantage of system arguments supported by `[set]`, such as `_new`.

Supports the optional `_load` kwarg for importing key:value pairs from one or more external JSON files.

```
[sets var_a=10 var_b=something var_c=500]
```

</details>

<details><summary>[singularize]</summary>

Returns the content in its singular form. Powered by the [pattern](https://github.com/clips/pattern/wiki/pattern-en) library - see pattern docs for more info.

Supports the optional `pos` argument. This is the target position of speech and defaults to "noun." In some rare cases, you may want to switch this to "adjective."

```
[singularize]children[/singularize]
```
```
RESULT: child
```

</details>

<details><summary>[substring {start} {end} {step} {unit}]</summary>

Returns a slice of the content as determined by the keyword arguments.

`start` is the beginning of the slice, zero indexed. Defaults to 0.

`end` is the last position of the slice. Defaults to 0.

Alternatively, you can pass a string into `start` or `end` and it will find the index of that string within the `content`.

`step` is the skip interval. Defaults to 1 (in other words, a continuous substring.)

`unit` is either `characters` or `words` and refers to the unit of the aforementioned arguments. Defaults to `characters`.

```
[substring start=1 end=3 unit=words]A photo of a giant dog.[/substring]
```
```
Result: photo of a
```

</details>

<details><summary>[switch var(str)]</summary>

Allows you to run different logic blocks with inner case statements that match the value of the given positional argument.

Both `[switch]` and `[case]` support advanced expressions.

```
[set my_var]100[/set]
[switch my_var]
	[case 1]Does not match[/case]
	[case 2]Does not match[/case]
	[case 100]Matches! This content will be returned[/case]
	[case 4]Does not match[/case]
	[case]If no other case matches, this content will be returned by default[/case]
[/switch]
```

</details>

<details><summary>[synonyms]</summary>

Replaces the content with one or more random synonyms. This shortcode is powered by a combination of WordNet and Moby Thesaurus II. Does not require an online connection after first use (word databases are downloaded to disk.)

The optional `max` argument allows you to specify the maximum number of synonyms to return. Defaults to -1, which returns all synonyms. The synonym list is delimited by `Unprompted.Config.syntax.delimiter`.

The optional `include_self` positional argument determines whether the original content can be returned as a possible result. Defaults to False.

The optional `enable_moby` keyword argument determines whether Moby Thesaurus II will be referenced. Defaults to True. On first use, the Moby Thesaurus will be downloaded to the `lib_unprompted` folder - it is about 24 MB.

The optional `enable_wordnet` keyword argument determines whether WordNet will be referenced. Defaults to True.

```
[synonyms]amazing[/synonyms]
```

</details>

<details><summary>[while variable {_not} {_any} {_is}]</summary>

Checks whether `variable` is equal to the given value, returning the content repeatedly until the condition is false. This can create an infinite loop if you're not careful.

This shortcode also supports advanced expression syntax, e.g. `[while "some_var >= 5 and another_var < 2"]`. The following arguments are only relevant if you **don't** want to use advanced expressions:

Supports the testing of multiple variables, e.g. `[while var_a=1 var_b=50 var_c="something"]`. If one or more variables return false, the loop ends.

The optional `_any` argument will continue the loop if any of the provided conditions returns true.

The optional `_not` argument allows you to test for false instead of true, e.g. `[while _not my_variable=1]` will continue the loop so long as `my_variable` does *not* equal 1.

The optional `_is` argument allows you to specify the comparison logic for your arguments. Defaults to `==`, which simply checks for equality. Other options include `!=`, `>`, `>=`, `<` and `<=`. Example: `[while my_var="5" _is="<="]`

```
Advanced expression demo:
[set my_var]3[/set]
[while "my_var < 10"]
	Output
	[sets my_var="my_var + 1"]
[/while]
```

```
[set my_var]3[/set]
[while my_var="10" _is="<"]
	Output
	[sets my_var="my_var + 1"]
[/while]
```

</details>

<details><summary>[unset variable]</summary>

Removes one or more variables from memory.

Note that variables are automatically deleted at the end of each run - you do **not** need to manually clean memory in most cases. The `[unset]` shortcode is for advanced use.

```
[set var_a=10 var_b="something"]
[unset var_a var_b]
```

</details>
</details>

<details><summary>Stable Diffusion Shortcodes</summary>

This section describes all of the included shortcodes which are specifically designed for use with the A1111 WebUI.

<details><summary>[file2mask]</summary>

Allows you to modify or replace your img2img mask with arbitrary files.

Supports the `mode` argument which determines how the file mask will behave alongside the existing mask:
- `add` will overlay the two masks. This is the default value.
- `discard` will scrap the existing mask entirely.
- `subtract` will remove the file mask region from the existing mask region.

Supports the optional `_show` positional argument which will append the final mask to your generation output window.

```
Walter White[file2mask "C:/pictures/my_mask.png"]
```

</details>

<details><summary>[img2img]</summary>

Used within the `[after]` block to append an img2img task to your generation.

The image resulting from your main prompt (e.g. the txt2img result) will be used as the initial image for `[img2img]`.

While this shortcode does not take any arguments, most img2img settings can be set in advance. **Does not currently support batch_size or batch_count** - coming soon!

```
Photo of a cat
[after]
	[sets prompt="Photo of a dog" denoising_strength=0.75]
	[img2img]
[/after]
```

</details>

<details><summary>[img2img_autosize]</summary>

Automatically adjusts the width and height parameters in img2img mode based on the proportions of the input image.

Stable Diffusion generates images in sizes divisible by 8 pixels. If your initial image is something like 504x780, this shortcode will set the width and height to 512x768.

Supports the `unit` shortcode which lets you specify the resolution multiplier. Must be divisible by 8. Defaults to 64.

Supports `target_size` which is the minimum possible size of either dimension. Defaults to 512.

Supports `only_full_res` which, if true, will bypass this shortcode unless the "full resolution inpainting" setting is enabled. Defaults to false.

```
[img2img_autosize] Photo of a cat
```

</details>

<details><summary>[img2pez]</summary>

Performs an advanced CLIP interrogation technique on the initial image known as [Hard Prompts Made Easy](https://github.com/YuxinWenRick/hard-prompts-made-easy).

Be aware that this technique is essentially a training routine and will significantly lengthen your inference time, at least on the default settings. On a Geforce 3090, it appears to take around 1-2 minutes.

By default, this shortcode is only compatible with SD 1.5 models. If you wish to use it with SD 2.1 or Midjourney, please set `clip_model` to `ViT-H-14` and `clip_pretrain` to `laion2b_s32b_b79k`. It does work surprisingly well with Midjourney.

Supports the optional `image_path` argument. This is a path to file(s) or a directory to use as the initial image. If not provided, it will default to the initial image in your img2img tab. Note: you can supply multiple paths delimited by `Unprompted.Config.syntax.delimiter`, and img2pez will optimize a single prompt across all provided images.

Supports the optional `prompt_length` argument, which is the length of the resulting prompt in tokens. Default to 16.

Supports the optional `iterations` argument, which is the total number of training steps to perform. Defaults to 200.

Supports the optional `learning_rate` argument. Defaults to 0.1.

Supports the optional `weight_decay` argument. Defaults to 0.1.

Supports the amusingly-named `prompt_bs` argument, which is described by the technique's authors as "number of intializations." Defaults to 1.

Supports the optional `clip_model` argument. Defaults to ViT-L-14.

Supports the optional `pretrain_clip` argument. Defaults to openai.

Supports the optional `free_memory` argument which attempts to free the CLIP model from memory as soon as the img2pez operation is finished. This isn't recommended unless you are running into OOM issues.

</details>

<details><summary>[init_image path(str)]</summary>

Loads an image from the given `path` and sets it as the initial image for use with img2img.

Note that `path` must be an absolute path, including the file extension.

If the given `path` ends with the `*` wildcard, `[init_image]` will choose a random file in that directory.

**Important:** At the moment, you still have to select an image in the WebUI before pressing Generate, or this shortcode will throw an error. You can select any image - it doesn't matter what it is, just as long as the field isn't empty.

```
[init_image "C:/pictures/my_image.png"]
```

</details>

<details><summary>[invert_mask]</summary>

Inverts the mask. Great in combination with `[txt2mask]` and `[instance2mask]`.

</details>

<details><summary>[instance2mask]</summary>

Uses Mask R-CNN (an instance segmentation model) to predict instances. The found instances are mask. Different from `[txt2mask]` as it allows to run the inpainting for each found instance individually. This is useful, when using high resolution inpainting. This shortcode only works in the img2img tab of the A1111 WebUI.
**Important:** If per_instance is used it is assumed to be the last operator changing the mask.

The supported classes of instances are:
- `person`
- `bicycle`
- `car`
- `motorcycle`
- `airplane`
- `bus`
- `train`
- `truck`
- `boat`
- `traffic light`
- `fire hydrant`
- `stop sign`
- `parking meter`
- `bench`
- `bird`
- `cat`
- `dog`
- `horse`
- `sheep`
- `cow`
- `elephant`
- `bear`
- `zebra`
- `giraffe`
- `backpack`
- `umbrella`
- `handbag`
- `tie`
- `suitcase`
- `frisbee`
- `skis`
- `snowboard`
- `sports ball`
- `kite`
- `baseball bat`
- `baseball glove`
- `skateboard`
- `surfboard`
- `tennis racket`
- `bottle`
- `wine glass`
- `cup`
- `fork`
- `knife`
- `spoon`
- `bowl`
- `banana`
- `apple`
- `sandwich`
- `orange`
- `broccoli`
- `carrot`
- `hot dog`
- `pizza`
- `donut`
- `cake`
- `chair`
- `couch`
- `potted plant`
- `bed`
- `dining table`
- `toilet`
- `tv`
- `laptop`
- `mouse`
- `remote`
- `keyboard`
- `cell phone`
- `microwave`
- `oven`
- `toaster`
- `sink`
- `refrigerator`
- `book`
- `clock`
- `vase`
- `scissors`
- `teddy bear`
- `hair drier`
- `toothbrush`

Supports the `mode` argument which determines how the text mask will behave alongside a brush mask:
- `add` will overlay the two masks. This is the default value.
- `discard` will ignore the brush mask entirely.
- `subtract` will remove the brush mask region from the text mask region.
- `refine` will limit the inital mask to the selected instances.

Supports the optional `mask_precision` argument which determines the confidence of the instance mask. Default is 0.5, max value is 1.0. Lowering this value means you may select more than you intend per instance (instances may overlap).

Supports the optional `instance_precision` argument which determines the classification thresshold for instances to be masked. Reduce this, if instances are not detected successfully. Default is 0.85, max value is 1.0. Lowering this value can lead to wrongly classied areas.

Supports the optional `padding` argument which increases the radius of the instance masks by a given number of pixels.

Supports the optional `smoothing` argument which refines the boundaries of the mask, allowing you to create a smoother selection. Default is 0. Try a value of 20 or greater if you find that your masks are blocky.

Supports the optional `select` argument which defines how many instances to mask. Default value is 0, which means all instances.

Supports the optional `select_mode` argument which specifies which instances are selected:
- `overlap` will select the instances starting with the instance that has the greatest absolute brushed mask in it.
- `overlap relative` behaves similar to `overlap` but normalizes the areas by the size of the instance.
- `greatest area` will select the greatest instances by pixels first.
- `random` will select instances in a random order
Defaults to `overlap`.

Supports the optional `show` positional argument which will append the final masks to your generation output window and for debug purposes a combined instance segmentation image.

Supports the optional `per_instance` positional argument which will render and append the selected masks individually. Leading to better results if full resolution inpainting is used.

```
[instance2mask]clock[/txt2mask]
```

</details>

<details><summary>[remember]</summary>

Allows you to keep one or more variables in memory for the duration of a batch run (i.e. runs where `batch_count` > 1). This overrides Unprompted's default behavior of completely resetting the `shortcode_user_vars` object after each image.

Here is a practical example:

Let's say you have a template where you want to pass different values to `[zoom_enhance]` that correspond to the `batch_index` of the run.

To do this, we can create an `[array]` and append a new value to it each step of the run. We will mark the array with `[remember]` and tell `[zoom_enhance]` to look up the `batch_index` position of the array.


```
[array zoom_replacements _append="{get subject}"]
[if batch_index=0]
	[remember zoom_replacements]
	[after][zoom_enhance replacement="{array zoom_replacements batch_index}" negative_replacement="worst quality"][/after]
[/if]
```
```
[remember var_a var_b]
```

</details>

<details><summary>[txt2img]</summary>

Runs a txt2img task inside of an `[after]` block.

The txt2img settings are determined by your user variables. In the following example, we explicitly update the CFG scale and prompt for the task:

```
[after][sets cfg_scale=15 prompt="horse"][txt2img][/after]original prompt goes here
```

</details>

<details><summary>[txt2mask]</summary>

A port of [the script](https://github.com/ThereforeGames/txt2mask) by the same name, `[txt2mask]` allows you to create a region for inpainting based only on the text content (as opposed to the brush tool.) This shortcode only works in the img2img tab of the A1111 WebUI.

Supports the `method` argument which determines the technology to use for masking. Defaults to `clipseg`. Can be changed to `fastsam` or `clip_surgery`, both of which utilize [Segment Anything](https://segment-anything.com/) instead. Although SAM technology is newer, my testing has shown that `clipseg` is still the most accurate method by far.

Supports the `mode` argument which determines how the text mask will behave alongside a brush mask:
- `add` will overlay the two masks. This is the default value.
- `discard` will ignore the brush mask entirely.
- `subtract` will remove the brush mask region from the text mask region.

Supports the optional `precision` argument which determines the confidence of the mask. Default is 100, max value is 255. Lowering this value means you may select more than you intend.

Supports the optional `padding` argument which increases the radius of your selection by a given number of pixels.

Supports the optional `smoothing` argument which refines the boundaries of the mask, allowing you to create a smoother selection. Default is 20. Try increasing this value if you find that your masks are looking blocky.

Supports the optional `size_var` argument which will cause the shortcode to calculate the region occupied by your mask selection as a percentage of the total canvas. That value is stored into the variable you specify. For example: `[txt2mask size_var=test]face[/txt2mask]` if "face" takes up 40% of the canvas, then the `test` variable will become 0.4.

Supports the optional `negative_mask` argument which will subtract areas from the content mask.

Supports the optional `neg_precision` argument which determines the confidence of the negative mask. Default is 100, the valid range is 1 to 255. Lowering this value means you may select more than you intend.

Supports the optional `neg_padding` which is the same as `padding` but for the negative prompts.

Supports the optional `neg_smoothing` which is the same as `smoothing` but for the negative prompts.

Supports the optional `sketch_color` argument which enables support for "Inpaint Sketch" mode. Using this argument will force "Inpaint Sketch" mode regardless of which img2img tab you are on. The `sketch_color` value can either be a preset color string, e.g. `sketch_color="tan"` ([full list of color strings available here](https://github.com/python-pillow/Pillow/blob/12028c9789c3c6ac15eb147a092bfc463ebbc398/src/PIL/ImageColor.py#L163)) or an RGB tuple, e.g. `sketch_color="127,127,127"`. Currently, txt2mask only supports single-color masks.

Supports the optional `sketch_alpha` argument, which should be paired with `sketch_color`. The `sketch_alpha` value is the level of mask transparency, from 0 (invisible) to 255 (fully opaque.)

Due to a limitation in the A1111 WebUI at the time of writing, the `sketch_alpha` parameter is **not** the same as the "mask transparency" option in the UI. "Mask transparency" is not stored in the `p` object as far as I can tell, so txt2mask implements its own custom solution.

Supports the optional `save` argument which will output the final mask as a PNG image to the given filepath.

Supports the optional `show` positional argument which will append the final mask to your generation output window.

Supports the optional `legacy_weights` positional argument which will utilize the original CLIPseg weights. By default, `[txt2mask]` will use the [refined weights](https://github.com/timojl/clipseg#new-fine-grained-weights).

Supports the `unload_model` argument, which will unload the masking model after processing. On my GTX 3090, this adds about 3 seconds to inference time (using the clipseg model). Defaults to `False`, and should only be enabled on devices with low memory.

The content and `negative_mask` both support the vertical pipe delimiter (`|`) which allows you to specify multiple subjects for masking.

Supports the optional `stamp` kwarg that pastes a temporary PNG onto the init image before running mask processing, useful for redacting a portion of the image for example. The value of `stamp` is the name of a file in `images/stamps` without extension.

Supports the optional `stamp_method` kwarg to choose the sizing and positioning of stamp logic. Valid options are `stretch` and `center`.

Supports the optional `stamp_x` and `stamp_y` kwargs for precise positioning of the stamp. Both default to 0.

Supports the optional `stamp_blur` parg which is the pixel radius of the stamp's gaussian blur filter. Defaults to 0, which disables the filter altogether.

```
[txt2mask]head and shoulders[/txt2mask]Walter White
```

</details>

<details><summary>[zoom_enhance]</summary>

Upscales a selected portion of an image via `[img2img]` and `[txt2mask]`, then pastes it seamlessly back onto the original.

Greatly improves low-resolution details like faces and hands. It is significantly faster than Hires Fix and more flexible than the "Restore Faces" option.

It must be used within an `[after]` block.

Supports the `_alt` parg which engages alternate processing. May help those who are having trouble with the shortcode, but is perhaps not fully compatible with ControlNet.

Supports the `mask` keyword argument which is a region to search for within your image. Defaults to `face`. Note that if multiple non-contiguous regions are found, they will be processed independently.

Supports the `replacement` keyword argument which is the prompt that will be used on the `mask` region via `[img2img]`. Defaults to `face`. If you're generating a specific character--say Walter White--you'll want to set `replacement` to a more specific value, like `walter white face`.

Supports the `negative_replacement` keyword argument, which is the negative prompt that will be used on the mask region via `[img2img]`. Defaults to an empty string.

Both `replacement` and `negative_replacement` support multiple, delimited search terms via `Unprompted.config.syntax.delimiter`.

Supports the `inherit_negative` parg, which copies your main negative prompt to the `[img2img]` replacement task. If used in conjunction with `negative_replacement`, the replacement negative becomes: `main_negative_prompt negative_replacement_value`. If you have multiple, delimited `negative_replacement` values, your main negative prompt will be preprended to all of them.

Supports the `background_mode` parg which will invert the class mask and disable the zoom_enhance step. In other words, you can use this when you want to replace the background instead of the subject. When using this mode, you will likely need to increase `mask_precision` to ~150 or so.

Supports `mask_sort_method` which is used when multiple, non-contiguous masks are detected. Defaults to `left-to-right`. Options include: `left-to-right`, `right-to-left`, `top-to-bottom`, `bottom-to-top`, `big-to-small`, `small-to-big`, `unsorted`.

Supports the `mode` keyword argument, which determines how the shortcode will interact with a pre-existing image mask. Defaults to `subtract`, which will remove your masked pixels from the shortcode's calculations. Options include: `add`, `subtract`, `discard`.

Supports the `bypass_adaptive_hires` positional argument. By default, the shortcode will scale up some inference settings such as CFG scale and sharpness depending on the resolution of the init image. Include this argument to disable that behavior.

Supports the `hires_size_max` keyword argument which is a hard limit on the size of the upscaled image, in order to avoid OOM errors. Defaults to 1024.

Supports the `blur_size` keyword argument, which corresponds to the radius of the gaussian blur that will be applied to the mask of the upscaled image - this helps it blend seamlessly back into your original image. Defaults to `0.03`. Note: this is a float that is a percentage of the total canvas size; 0.03 means 3% of the total canvas.

Supports the `sharpen_amount` argument, which is a float that determines the strength of the unsharp filter that is applied in post-processing.

Supports the `denoising_max` keyword argument. The `[zoom_enhance]` shortcode is equipped with **dynamic denoising strength** based on a simple idea: the smaller the mask region, the higher denoise we should apply. This argument lets you set the upper limit of that feature.

Supports the `mask_size_max` keyword argument. Defaults to `0.5`. If a mask region is determined to be greater than this value, it will not be processed by `[zoom_enhance]`. The reason is that large objects generally do not benefit from upscaling.

Supports the `min_area` keyword argument. Defaults to `50`. If the pixel area of a mask is smaller than this, it may be a false-positive mask selection or at least not worth upscaling.

Supports the `contour_padding` keyword argument. This is the radius in pixels to extend the mask region by. Defaults to `0`.

Supports the `upscale_width` and `upscale_height` arguments. Default to `512`. This is the resolution to use with `[img2img]` and should usually match the native resolution of your Stable Diffusion model.

Supports the `include_original` positional argument. This will append the original, "non-zoom-enhanced" image to your output window. Useful for before-after comparisons.

Supports the `upscale_method` and `downscale_method` arguments which determine the algorithms for image rescaling. Upscale defaults to `Nearest Neighbor`. Downscale defaults to `Lanczos`. Options include: `Nearest Neighbor`, `Box`, `Bilinear`, `Hamming`, `Bicubic`, `Lanczos`.

Supports the `color_correction_method` argument which will attempt to match the color grading of the upscaled image to the original. Defaults to `none`. Options include: `none`,`mvgd`,`mkl`,`hm-mvgd-hm`,`hm-mkl-hm`.

Supports the `color_correct_strength` argument which is an integer that determines how many times to run the color correction algorithm. Defaults to 1.

Supports the `color_correct_timing` argument which determines when to run the color correction algorithm. Defaults to `pre`, which will run color correction before upscaling. Options include `pre` and `post`.

Supports the `controlnet_preset` kwarg which is the name of a file in `templates/presets/controlnet` containing instructions for loading one more ControlNet units.

Supports the experimental `use_starting_face` parg which will upscale the initial image's face as opposed to the resulting img2img's face. (Irrelevant in txt2img mode.)

Supports the `debug` positional argument, which will output a series of images to your WebUI folder over the course of processing.

This shortcode is compatible with batch count and batch size.


```
[after][zoom_enhance][/after]
```

</details>

</details>

<details><summary>Legacy Shortcodes</summary>

Legacy shortcodes are those which are no longer officially supported. Please be aware that they may not work as expected and could be removed from future versions of Unprompted without warning.

<details><summary>[controlnet]</summary>

**Reason for legacy status:** The popular [ControlNet extension by Mikubill](https://github.com/Mikubill/sd-webui-controlnet) was released less than 24 hours after this shortcode and is much more robust. ControlNet is a complicated, time-consuming feature to support and I cannot justify further development when the alternative software is already so good.

Enables support for [ControlNet](https://github.com/lllyasviel/ControlNet) models in img2img mode. ControlNet is a neural network structure to control diffusion models by adding extra conditions.

You need a bare minimum of 8 GB of VRAM to use this shortcode, although 12 GB is recommended.

Supports the `model` argument, which is the name of a ControlNet checkpoint in your `models/Stable-diffusion` directory (do not include the file extension.) You can download ControlNet checkpoints from [the official HuggingFace page](https://huggingface.co/lllyasviel/ControlNet/tree/main/models).

For each model, you also need a copy of the [cldm_v15.yaml](https://github.com/lllyasviel/ControlNet/tree/main/models) config file. Rename it to match the name of the ControlNet model, e.g. `control_sd15_normal.yaml`.

For each model, you also need the associated [annotator files available here](https://huggingface.co/lllyasviel/ControlNet/tree/main/annotator/ckpts). Place these into your  `extensions/unprompted/lib_unprompted/stable_diffusion/controlnet/annotator/ckpts` folder.

If you run into any errors, please triple-check your filepaths before opening a bug report.

You can use ControlNet with custom SD 1.5 models [by merging checkpoints as described here](https://github.com/lllyasviel/ControlNet/issues/4#issuecomment-1426877944).

Please be aware that the last part of your model's filename indicates which type of ControlNet model it is. The following ControlNet model types are supported: `openpose`, `scribble`, `mlsd`, `depth`, `normal`, `hed`, `canny`, `seg`

ControlNet models should **not** be loaded manually from your WebUI dropdown.

Supports the `save_memory` argument to minimize VRAM requirements.

Supports the `detect_resolution` argument which is the size of the detected map. Defaults to 512. Some models may perform better at 384. Lowering this value to 256 may help with VRAM requirements.

Supports the `eta` argument.

Supports the following model-specific arguments: `value_threshold`, `distance_threshold`, `bg_threshold`, `low_threshold`, `high_threshold`

</details>

<details><summary>[enable_multi_images]</summary>

**Reason for legacy status:** This shortcode was introduced by a PR and is reportedly not compatible with recent versions of the WebUI.

This is a helper shortcode that should be used if multiple init images, multiple masks or in combination with instance2mask per_instance should be used. Use this shortcode at the very end of the prompt, such that it can gather the correct init images and masks. Note that this operator will change the batch_size and batch_count (n_iter).

</details>

<details><summary>[pix2pix_zero]</summary>

**Reason for legacy status:** the pix2pix-zero method [was not what I originally thought](https://github.com/AUTOMATIC1111/stable-diffusion-webui/discussions/7711#discussioncomment-4952579) which was sort of a buzzkill. As it stands, I believe ControlNet is better suited at most tasks, but I can't make any definitive claims about that - pix2pix-zero went under the radar and does merit further testing.

If you wish to use this shortcode, you will need to modify the hardcoded path to a diffusers model on line 33.

</details>

</details>