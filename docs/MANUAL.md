# Unprompted Manual

**Note:** This file is a work-in-progress and might be better suited to a Wiki if there's enough interest. Shortcode syntax is subject to change based on community feedback.

## Adding New Shortcodes

Shortcodes are loaded as Python modules from `unprompted/shortcodes`. You can make your own shortcodes by creating files there (preferably within the `/custom` subdirectory.)

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

The `__init__` function gives the shortcode access to our main Unprompted object, and it's where you should declare any unique variables for your shortcode.

The `run_block` function contains the main logic for your shortcode. It has access to these special variables (the following documentation was pulled from the [Python Shortcodes](https://www.dmulholl.com/dev/shortcodes.html) library, on which Unprompted depends):

- `pargs`: a list of the shortcode's positional arguments.
- `kwargs`: a dictionary of the shortcode's keyword arguments.
- `context`: an optional arbitrary context object supplied by the caller.
- `content`: the string within the shortcode tags, e.g. `[tag]content[/tag]`

Positional and keyword arguments are passed as strings. The function itself should return a string which will replace the shortcode in the parsed text.

The `cleanup` function runs at the end of the processing chain. You can free any unnecessary variables from memory here.

For more details, please examine the code of the stock shortcodes.

## Atomic vs Block Shortcodes

Unprompted supports two types of shortcodes:

- Block shortcodes that require an end tag, e.g. `[set my_var]This is a block shortcode[/set]`
- Atomic shortcodes that are self-closing, e.g. `[get my_var]`

These are mutually exclusive. Shortcodes must be defined as one or the other.

The type is declared by including one of the following functions in your `.py` file:

```
def run_block(self, pargs, kwargs, context, content):
```

```
def run_atomic(self, pargs, kwargs, context):
```

Atomic shortcodes do not receive a `content` variable.

## Understanding the Processing Chain

It is important to understand that **inner shortcodes are processed before outer shortcodes**.

This has a number of advantages, but it does present one tricky situation: **conditional functions are weird.**

Consider the following code:

```
[if my_var=1][set another_var]0[/set][/if]
```

Anyone with a background in programming would take this to mean that `another_var` is set to 0 if my_var equals 1... but this is not the case here.

In Unprompted, `another_var` will equal 0 regardless of the outcome of the `if` statement.

The next section offers a solution.

## Secondary Shortcode Tags

Unprompted allows you to write tags using `<>` instead of `[]` to defer processing.

For example, if you want to set `another_var` to 0 when `my_var` equals 1, you should do it like this:

```
[if my_var=1]<set another_var>0</set>[/if]
```

This way, the inner shortcode is not processed until *after* it is returned by the outer `[if]` statement.

Secondary shortcode tags give us a couple additional benefits:

- If your shortcode is computationally expensive, you can avoid running it unless the outer shortcode succeeds. This is good for performance.
- **You can pass them as arguments in shortcodes that support it.** For example, if you want to run the `[chance]` shortcode with dynamic probability, you can do it like this: `[chance _probability="<get my_var>"]content[/chance]`

Secondary shortcode tags can have infinite nested depth. The number of `<>` around a shortcode indicates its nested level. Consider this example:

```
[if my_var=1]
<if another_var=1>
<<if third_var=1>>
<<<if fourth_var=1>>>
wow
<<</if>>>
<</if>>
</if>
[/if]
```

Whenever the `[]` statement succeeds, it will decrease the nested level of the resulting content. Our example returns:

```
[if another_var=1]
<if third_var=1>
<<if fourth_var=1>>
wow
<</if>>
</if>
[/if]
```

Rinse and repeat until no `<>` remain.


## The config file

Various aspects of Unprompted's behavior are controlled through `unprompted/config.json`.

If you wish to override the default settings, you should make another file at the same location called `config_user.json`. Modifications to the original config file will **not** be preserved between updates.

Here are some of the settings you can modify:

### debug (bool)

When `True`, you will see a lot more diagnostic information printed to the console during a run. You should use this when creating your own shortcode, template, or when filing a bug report.

### template_directory (str)

This is the base directory for your text files.

### txt_format (str)

This is the file extension that Unprompted will assume you're looking for with `[file]`.

### syntax/n_temp (str)

This is a temporary string that replaces all newline characters for easier/safer processing with Unprompted.

### syntax/n_final (str)

This is a string that `n_temp` is replaced with in the final output. Defaults to a space, which is helpful in most cases when coding multiline templates. In my experience, space creates the fewest problems, but feel free to experiment with other values.

### syntax/tag_start (str)

This is the string that indicates the start of a shortcode.

### syntax/tag_end (str)

This is the string that indicates the end of a shortcode.


### syntax/tag_start_alt (str)

This is the string that indicates the start of a secondary shortcode.

### syntax/tag_end_alt (str)

This is the string that indicates the end of a secondary shortcode.

### syntax/tag_close (str)

This is the string that indicates the closing tag of a block-scoped shortcode.

### syntax/tag_escape (str)

This is the string that allows you to print a shortcode as a literal string, bypassing the shortcode processor.

Note that you only have to include this string once, before the shortcode, as opposed to in front of every bracket.

In my experience, the escape character should be used sparingly as it doesn't play well with nested statements.


## Basic Shortcodes

This section describes all of the included basic shortcodes and their functionality.

### [#]

Use this to write comments in your templates. Comments are ultimately discarded by Unprompted and will not affect your final output.

```
[# This is my comment.]
```

### [##]

Same as `[#]` but for multiline comments.

```
[##]
This is my multiline comment.
We're still commenting.
I can't believe it, we're doing 3 lines of text!
[/##]
```

### [case]

See `[switch]`.

### [chance int {_sides}]

Returns the content if the integer you passed is greater than or equal to a randomly generated number between 1 and 100.

You can change the upper boundary by specifying the optional `_sides` argument.

Supports secondary shortcode tags with the optional `_probability` argument, e.g. `[chance _probability="<get my_var>"]content[/chance]`

```
[chance 25]I will show up in your prompt 25% of the time.[/chance]
```

### [choose]

Returns one of multiple options, as delimited by the vertical pipe or newline character.

```
[choose]red|yellow|blue|green[/choose]
```

### [config]

Updates your Unprompted settings with the content for the duration of a run.

Supports inline JSON as well as external JSON files.

Supports relative and absolute filepaths.

Do not enter a file extension, `.json` is assumed.

```
[config]{"debug":True,"shortcodes":{"choose_delimiter":"*"}}[/config]
```

```
[config]./my_custom_settings[/config]
```

### [elif]

Shorthand "else if." Equivalent to `[else]<if my_var="something">content</if>[/else]`.

```
[set my_var]5[/set]
[if my_var=6]Discard this content[/if]
[elif my_var=5]Return this content![/elif]
```

### [else]

Returns content if a previous conditional shortcode (e.g. `[if]` or `[chance]`) failed its check, otherwise discards content.

**Note:** In its current implementation, `[else]` should appear immediately after the conditional shortcode - don't try to get too crazy with nesting or delayed statements or it will probably fail.

```
[if my_var=0]Print something[/if][else]It turns out my_var did not equal 0.[/else]
```

### [eval]

Parses the content using Python's `eval()` statement, returning the result. Particularly useful for arithmetic. **Not safe over the network! Do not provide end users access to this shortcode with --share environments. Unprompted is intended for local use.**

```
[eval]5 + 5[/eval]
```

### [file path(str)]

Processes the content of `path` (including any shortcodes therein) and returns the result.

`unprompted/templates` is the base directory for this shortcode, e.g. `[file example/main]` will target `unprompted/templates/example/main.txt`.

Do not enter a file extension, `.txt` is assumed.

Supports relative paths by starting the `path` with `./`, e.g. `[file ./main]` will target the folder that the previously-called `[file]` resides in.

If the given `path` is a directory as opposed to a file, `[file]` will return the contents of a random file in that directory.

```
[file my_template/common/adjective]
```

### [get variable]

Returns the value of `variable`.

Supports secondary shortcode tags with the optional `_var` argument, e.g. `[get _var="<file example>"]`

You can add `_before` and `_after` content to your variable. This is particularly useful for enclosing the variable in escaped brackets, e.g. `[get my_var _before=[ _after=]]` will print `[value of my_var]`

```
My name is [get name]
```

### [if variable {_not} {_any} {_is}]

Checks whether `variable` is equal to the given value, returning the content if true, otherwise discarding the content.

Supports the testing of multiple variables, e.g. `[if var_a=1 var_b=50 var_c="something"]`. If one or more variables return false, the content is discarded.

The optional `_any` argument allows you to return the content if one of many variables return true. This is the equivalent of running "or" instead of "and" in programming, e.g. `[if _any var_a=1 var_b=50]`.

The optional `_not` argument allows you to test for false instead of true, e.g. `[if _not my_variable=1]` will return the content if `my_variable` does *not* equal 1.

The optional `_is` argument allows you to specify the comparison logic for your arguments. Defaults to `==`, which simply checks for equality. Other options include `>`, `>=`, `<` and `<=`. Example: `[if my_var="5" _is="<="]`

```
[if subject="man"]wearing a business suit[/if]
```

### [override variable]

Forces `variable` to equal the given value when attempting to `[set]` it.

Supports multiple variables.

In the example below, `my_variable` will equal "panda" after running the `[set]` shortcode.

```
[override my_variable="panda"][set my_variable]fox[/set]
```

### [random {_min} {_max} {_float}]

Returns a random integer between 0 and the given integer, e.g. `[random 2]` will return 0, 1, or 2.

You can specify the lower and upper boundaries of the range with `_min` and `_max`, e.g. `[random _min=5 _max=10]`.

If you pass `_float` into this shortcode, it will support decimal numbers instead of integers.

```
[set restore_faces][random 1][/set]
```

### [repeat times(int) {_sep}]

Processes and returns the content a number of `times`.

Supports secondary shortcode tags with the optional `_times` argument, e.g. `[repeat _times="<get my_var>"]`.

Supports the optional `_sep` argument which is a string delimiter inserted after each output, excluding the final output. Example: `[repeat 3 _sep="|"]content[/repeat]` will return `content|content|content`.

Supports float values as well. For example, `[repeat 4.2]content[/repeat]` will have a 20% chance to return `content` 5 times instead of 4.

```
[set my_var]0[/set]
[repeat 5]
Variable is currently: <set my_var _out _append>1</set>
[/repeat]
```

### [set {_append} {_prepend}]

Sets a variable to the given content.

`_append` will instead add the content to the end of the variable's current value, e.g. if `my_var` equals "hello" then `[set my_var _append] world.[/set]` will make it equal "hello world."

`_prepend` will instead add the content to the beginning of the variable's current value.

Supports all Stable Diffusion variables that are exposed via Automatic's Script system, e.g. `[set cfg_scale]5[/set]` will force the CFG Scale to be 5 for the run.

```
[set my_var]This is the value of my_var[/set]
```

### [switch var(str)]

Allows you to run different logic blocks with inner case statements that match the value of the given `var`.

Supports secondary shortcode tags with the optional `_var` argument, e.g. `[switch _var="<file my_file>"]`.

```
[set my_var]100[/set]
[switch my_var]
<case 1>Does not match</case>
<case 2>Does not match</case>
<case 100>Matches! This content will be returned</case>
<case 4>Does not match</case>
<case>If no other case matches, this content will be returned by default</case>
[/switch]
```

### [while variable {_not} {_any} {_is}]

Checks whether `variable` is equal to the given value, returning the content repeatedly until the condition is false. This can create an infinite loop if you're not careful.

Supports the testing of multiple variables, e.g. `[while var_a=1 var_b=50 var_c="something"]`. If one or more variables return false, the loop ends.

The optional `_any` argument will continue the loop if any of the provided conditions returns true.

The optional `_not` argument allows you to test for false instead of true, e.g. `[while _not my_variable=1]` will continue the loop so long as `my_variable` does *not* equal 1.

The optional `_is` argument allows you to specify the comparison logic for your arguments. Defaults to `==`, which simply checks for equality. Other options include `>`, `>=`, `<` and `<=`. Example: `[while my_var="5" _is="<="]`

```
[set my_var]3[/set]
[while my_var="10" _is="<"]
Output
<set my_var _append>1</set>
[/while]
```