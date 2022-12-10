# Changelog
All notable changes to this project will be documented in this file. For more details on new features, please check the Manual.

## 3.0.0 - 10 December 2022
### Added
- The `[info]` shortcode now supports `clip_count`

### Changed
- Fixed an issue with the negative prompt in batch sizes greater than 2

### Removed
- The `[chance]` shortcode no longer supports `_probability` as the first argument now automatically accepts expressions and secondary shortcode tags

## 2.0.2 - 7 December 2022
### Changed
- Overhauled Github README.md
- Possibly fixed compatibility issue with Dynamic Prompts

## 2.0.1 - 7 December 2022
### Changed
- The `[file]` shortcode will throw a soft error if the provided filepath is not valid, rather than completely aborting Unprompted (Issue #23)
- Fixed a string truncation issue related to the sanitization filter (Issue #26)

## 2.0.0 - 7 December 2022
### Added
- Implemented advanced expression support for nearly all shortcodes
- New shortcode `[do]` for "do until" style loops
- New shortcode `[min]` for returning the value of the smallest variable among the arguments
- New shortcode `[max]` for returning the value of the greatest variable among the arguments
- New shortcode `[unset]` that removes one or more variables from memory
- New function `parse_advanced` that consolidates calls to simpleeval
- The `[choose]` shortcode can now return multiple options
- The `[choose]` shortcode now supports the optional `_sep` argument, which is a string delimeter used when returning multiple options
- The `[info]` shortcode now supports the `string_count` argument, which returns the number of matching strings in the content
- The `[replace]` shortcode now supports the `_count` variable, which defines the number of occurances to replace
- The `[set]` and `[sets]` shortcodes now support the `_new` argument, which will bypass the shortcode if the variable(s) already exist
- Advanced expression support can be toggled in config.json
- New example `reverse_string.txt`

### Changed
- Secondary shortcode tags have been changed from `<>` to `{}` for compatibility with advanced expression statements
- Updated example `update_variable.txt`
- Fixed potential crash related to `autocast` function
- Fixed a bug in the `[sets]` shortcode
- Fixed a couple bugs related to advanced expressions

### Removed
- The `[repeat]` shortcode no longer supports `_times` as the first argument now automatically accepts expressions and secondary shortcode tags
- The `[switch]` shortcode no longer supports `_var` as the first argument now automatically accepts expressions and secondary shortcode tags

> **Important Note:** the change to secondary shortcode tags will unfortunately break some existing templates. In general, I try to avoid making such changes, but in this case it was the best way to get secondary tags to interact well with advanced expressions - the <> characters conflicted with less-than, greater-than conditional checks. On the plus side, we can now do stuff like this: [if "{file some_script} < 2"]print me[/if]. Should be quite powerful!

> If you wish to revert this behavior (not recommended) you can do so by creating a file called config_user.json, setting advanced_expressions to false, tag_start_alt to <, and tag_start_end to >. Refer to config.json for exact formatting. Be aware that these changes will break advanced expressions.

## 1.2.0 - 2 December 2022
### Added
- New `[sets]` atomic shortcode for setting multiple variables at once

### Changed
- `[eval]` can now read user variables

## 1.1.0 - 2 December 2022
### Added
- New `[for]` shortcode, as in for loops
- New `[casing]` shortcode powered by @dmlls casefy library
- The `[if]` and `[while]` shortcodes now support advanced expressions via simpleeval, e.g. `[if "var_a==10 and var_b<=50"]`
- The `[if]` and `[while]` shortcodes now support `!=` as an operator type for `_is`

## 1.0.0 - 1 December 2022
### Added
- New `[info]` shortcode that prints metadata about the content (either `character_count` or `word_count` at the moment)
- New `[substring]` shortcode for slicing content
- The `[file]` shortcode now supports the setting of variables through keyword arguments, which effectively allows you to use this shortcode like a function in programming
- The `[get]` shortcode now supports optional `_default` argument, the value of which is returned if the selected variable does not exist
- The `[replace]` shortcode now supports optional `_from` and `_to` arguments which can process secondary shortcode tags
- New example `random_emphasis.txt`

### Changed
- The `[eval]` shortcode now utilizes the simpleeval library by @danthedeckie, which should be safe for networked environments (no gurantees though - use Unprompted at your own risk)
- Check `shortcodes/basic/eval.py` for instructions on reverting the shortcode to its old, strictly-for-local-use behavior
- The tab character is now replaced with a blank string instead of space

## 0.10.0 - 30 November 2022
### Added
- New `[replace]` shortcode

### Changed
- Replaced `n_temp` and `n_final` config settings with `sanitize_before` and `sanitize_after` that let you define any number of characters to modify before/after processing
- Tab character (`\t`) is now ignored by default, which will hopefully make it easier to format complex templates for readability
- All string sanitization logic has been moved into the `process_string()` function
- Fixed an issue with `negative_prompt` logic

## 0.9.0 - 29 November 2022
### Added
- Updated `negative_prompt` to support the latest version of Automatic1111's WebUI, which permits batch support for negative prompts

## 0.8.0 - 13 November 2022
### Added
- New system variable `batch_index` for making decisions based on the progress into a batch run
- The `[choose]` shortcode now accepts `_case` which bypasses the random selection with a given number or variable

## 0.7.0 - 11 November 2022
### Added
- New `[config]` shortcode
- The `[choose]` delimiter is now specified in config.json (defaults to `|`)
- New `parse_filepath(string, context)` function in shared.py that supports both relative and absolute path handling
- Merged `.gitignore` PR (thank you @MaikoTan!)

## 0.6.0 - 6 November 2022
### Added
- New `[elif]` shortcode
- The `[repeat]` shortcode now accepts floats, e.g. 4.6 has a 60% chance of repeating 5 times instead of 4
- The `[repeat]` shortcode now supports `_sep` which is a string delimiter to insert after each output, excluding the final output
- New `autocast()` function in shared.py that will convert a variable to str, int, or float automatically
- New `templates/examples` for snippets of code that demonstrate cool ways of combining shortcodes you may not have considered

### Changed
- Fixed an issue with `[repeat]` outputting its content once more than intended

## 0.5.1 - 5 November 2022
### Changed
- Fixed an issue with `[set]` converting to float in situations where int is preferred

## 0.5.0 - 5 November 2022
### Added
- Button for dismissing the ad
- The ad will be dismissed automatically if you purchase the Fantasy Template Pack

## 0.4.0 - 4 November 2022
### Added
- Config option `batch_support` which, if enabled, will generate random prompts for every image in a batch as opposed to using the same prompt for the entire batch

## 0.3.0 - 4 November 2022
### Added
- Support for infinite nesting of secondary shortcode tags
- New shortcode `[while]` for looping content until the condition returns false
- `[chance]` now supports `_sides` which determines the upper bound of the chance roll (default is 100)

### Changed
- The `[if]` `_operator` argument has been renamed to `_is` for readability

## 0.2.0 - 4 November 2022
### Added
- New shortcode `[##]` for multiline comments
- Documentation for `config.json`
- `[if]` now supports `_any` which flips from "and" to "or" multivar processing
- `[if]` now supports `_operator` which determines the comparison logic for your arguments

### Changed
- Overhauled codebase in order to load as an A1111 extension rather than a script, please re-review the installation instructions!
- Renamed `DOCUMENTATION.md` to `MANUAL.md`

## 0.1.1 - 2 November 2022
### Added
- `[get]` now supports `_before` and `_after` arguments
- `[set]` now supports secondary shortcode tags

### Changed
- `[file]` now strips leading and trailing newline characters

## 0.1.0 - 1 November 2022
### Added
- Added `[switch]` and `[case]` shortcodes
- Added `[repeat]` shortcode
- Added `is_equal()` function to Unprompted object that checks for loose equality of two variables

### Changed
- Fixed `_append` and `_prepend` behavior of `[set]` when used with int values

## 0.0.1 - 31 October 2022
### Added
- Initial release