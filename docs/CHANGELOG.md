# Changelog
All notable changes to this project will be documented in this file.

## 0.3.0 - 4 November 2022
### Added
- Support for infinite nesting of secondary shortcode tags
- New shortcode `[while]` for looping content until the condition returns false
- `[chance]` now supports `_sides` which determines the upper bound of the chance roll (default is 100)
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