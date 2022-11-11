# Changelog
All notable changes to this project will be documented in this file.

## 0.7.0 - 11 November 2022
## Added
- New `[config]` shortcode
- The `[choose]` delimiter is now specified in config.json (defaults to `|`)
- New `parse_filepath(string, context)` function in shared.py that supports both relative and absolute path handling
- Merged `.gitignore` PR (thank you @MaikoTan!)

## 0.6.0 - 6 November 2022
## Added
- New `[elif]` shortcode
- The `[repeat]` shortcode now accepts floats, e.g. 4.6 has a 60% chance of repeating 5 times instead of 4
- The `[repeat]` shortcode now supports `_sep` which is a string delimiter to insert after each output, excluding the final output
- New `autocast()` function in shared.py that will convert a variable to str, int, or float automatically
- New `templates/examples` for snippets of code that demonstrate cool ways of combining shortcodes you may not have considered

## Changed
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