# Changelog
All notable changes to this project will be documented in this file.

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