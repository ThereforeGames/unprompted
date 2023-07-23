# Changelog
All notable changes to this project will be documented in this file.

For more details on new features, please check the [Manual](./MANUAL.md).

<details open><summary>9.8.0 - 22 July 2023</summary>

### About
This update integrates batch processing with the WebUI's `process_batch()` routine - this allows Unprompted to change system variables such as CFG scale or model checkpoint between each image generation. I hope the added flexibility proves useful for your prompting workflows. If you find that the new system is incompatible with a particular shortcode, please open an issue for me and use the `legacy` setting as a short-term workaround. Thanks!

### Changed
- Batch processing will now update Stable Diffusion vars after each image
- Due to the above change, the `Unprompted.Config.stable_diffusion.batch_support` setting has been renamed to `Unprompted.Config.stable_diffusion.batch_method` with a default setting of `standard`
- You can set the `batch_method` to `legacy` if you prefer the old implementation, or `none` to disable batch support altogether

### Fixed
- `[round]`: Fixed `_up` and `_down` with floats
- `[choose]`: The `_raw` parg no longer replaces linebreaks with the delimiter character in a selected `[file]`
- `[remember]`: Fixed this shortcode unintentionally adding "None" to prompt

</details>

<details><summary>9.7.0 - 20 July 2023</summary>

### Added
- New shortcode `[round]`: Rounds the first parg to a certain level of precision, e.g. 1.345 at `_place=1` yields 1.3, and 1644 at `_place=2` yields 1600
- `[remember]`: Added Wizard UI
- New WebUI Template Editor tab by o0oradaro0o (PR #146)
- Minor UI updates for the Template Editor after merging
- New config setting `stable_diffusion.template_editor`: you can set to `false` to disable the Template Editor tab

</details>

<details><summary>9.6.0 - 20 July 2023</summary>

### About
This update resolves a number of issues related to `batch_index` evaluation, which were causing degraded image quality with `[zoom_enhance]`.

### Beta
- `[img2img]`: updated for compatibility with the A1111 dev branch

### Added
- New shortcode `[remember]`: Allows you to declare the names of variables you would like to keep over the course of a batch run
- `[set]` and `[sets]`: Now support `_remember` parg, which invokes the `[remember]` shortcode with your variable(s)
- New special variable `batch_test`: Shortcodes that implement batch processing--such as `[zoom_enhance]`--will evaluate your `batch_test` expression against the batch item index to determine if it should be bypassed, e.g. if `batch_test` is  `<= 5` and we're on the seventh image, it won't be processed by `[zoom_enhance]`.

### Changed
- Enabled Python formatter yapf with args `{use_tabs: 1,column_limit: 999}`, please make sure any code submitted in a PR adheres to the same formatting rules

### Fixed
- `[zoom_enhance]`: Improved batch support for `replacement` and `negative_replacement`
- `[zoom_enhance]`: Can access `batch_index` variable correctly
- `[zoom_enhance]`: Fixed `seed` value not synchronizing correctly with batch process
- Fixed an issue where explicitly setting the `negative_prompt` in a batch run where `batch_index` > 0 would not take effect
</details>

<details><summary>9.5.1 - 3 July 2023</summary>

### Fixed
- `[txt2img]`: Fixed an issue with this shortcode not receiving updates to the `p` object while in txt2img mode
</details>

<details><summary>9.5.0 - 2 July 2023</summary>

### Added
- New special variable `single_seed`: forces the same seed value for all images in a batch
- `[array]`: New kwarg `_fill` lets you replace all values in the array with a specified value

### Changed
- Wizard Capture tab no longer prints special extension attributes such as `unprompted_original_prompt` since they are not needed for image reproduction
- `[enable_multi_images]`: Now considered a legacy shortcode as it is reportedly incompatible with recent version of the WebUI (this shortcode was originally merged from a PR)

### Fixed
- Img2img batch tab should now correctly re-evaluate shortcodes when batch_count > 1
- Resolved compatibility issue with hires. fix in newer versions of the WebUI

</details>

<details><summary>9.4.0 - 29 June 2023</summary>

### Added
- Attempting to introduce img2img batch tab support, this is experimental and may not work with every shortcode
- `[txt2mask]`: Compatibility with img2img batch tab tensor masks
- `[zoom_enhance]`: Now supports `_alt` which uses the `[img2img]` shortcode for processing instead of the native `process_images_inner()` function - may improve compatibility for some users
- `[choose]`: Now supports `_raw` which prevents inner shortcodes from running except the one that is chosen
- `[img2img_autosize]`: Now supports `unit` which lets you adjust the rounding multiplier of the output resolution, defaults to 64
- Added "WARNING" as a default console message log type

### Fixed
- `[choose]`: Parses secondary tags after selecting an option
- `[img2img]`: Fixed bug in `update_controlnet_var()` call
- Improved error catching in `unprompted_dry.py`
- The `update_controlnet_var()` script will check to see if the given att has a number to avoid false positives (such as `controlnet_initial_noise_modifier`)

</details>

<details><summary>9.3.1 - 28 June 2023</summary>

### Added
- New guide: "Setting up Replacement Terms"

### Changed
- `[zoom_enhance]`: Improved Wizard GUI
- Moved older changelog entries into their own accordion menu
- Wizard Capture `simple` inference settings no longer capture inf values
- Tested compatibility with WebUI 1.4.0 and updated compatibility blurb as such

### Fixed
- The `autocast()` function no longer crashes when given infinity
- `[choose]`: Fixed a crash related to using secondary shortcode arguments in the content
- `[if]`: Fixed `context` value
- `[autocorrect]`: Fixed missing `punkt` dependency download
- Merged [#159 by bsweezy](https://github.com/ThereforeGames/unprompted/pull/159): Fix restore_faces brackets in example template

</details>

<details><summary>9.3.0 - 24 June 2023</summary>

### Added
- New shortcode `[bypass]`: allows you to bypass specific shortcodes, useful for debugging
- New Wizard Capture tab that assembles code for the last image you generated
- `[txt2mask]`: now supports `fastsam` mask method
- `[zoom_enhance]`: now supports `inherit_negative` parg to copy your main negative prompt to the replacement img2img task
- Bodysnatcher v1.3.1: now supports the aforementioned `inherit_negative` feature of `[zoom_enhance]` (true by default)
- You can minimize startup time by setting `skip_requirements` to true in `config_user.json`
- Atomic shortcodes may now utilize `run_preprocess()` similar to block shortcodes

### Changed
- `[txt2mask]`: Improved Wizard GUI
- Bodysnatcher v1.3.1: Improved Wizard GUI
- Tested compatibility with WebUI 1.3.2 and updated compatibility blurb as such

### Fixed
- `[zoom_enhance]`: Potentially fixed a compatibility issue with newer versions of ControlNet
- Updated checkpoint name detection, hopefully more reliable as a result
- Temporarily lowered sampling steps of img2img_general_v1 and img2img_full_denoise_v1 from 25 to 24 as a workaround for an odd visual glitch

### Removed
- `[txt2mask]`: mask method `grounded_sam` has been removed due to inferior results compared to `clip_surgery` and `fastsam`, all of which are based on similar technology

</details>

<details><summary>9.2.1 - 21 May 2023</summary>

### Fixed
- Crash related to install issue with legacy controlnet requirements

</details>

<details><summary>9.2.0 - 13 May 2023</summary>

### Added
- New shortcode `[txt2img]` for use within the `[after]` block
- New directory `templates/common/presets/inference` with a few presets
- Bodysnatcher v1.3.0: new setting `inference_preset` that will load settings from the aforementioned directory
- New function `Unprompted.update_stable_diffusion_vars()` to write changes from `shortcode_user_vars` to a specified `p` object
- Compatibility blurb added to About panel

### Changed
- The promo boxart is now loaded from the local filesystem instead of an online imagehost
- The `templates/common/controlnet_presets` directory has been moved to `templates/common/presets/controlnet`
- Rewrote `install.py` to be more modular
- Bodysnatcher v1.3.0: minor UI updates
- Updated the manual

### Removed
- Bodysnatcher v1.3.0: removed `use_optimized_inference_settings` in favor of the new `inference_preset` setting

</details>

<details><summary>9.1.2 - 5 May 2023</summary>

### Fixed
- `[img2img]`: updated for compatibility with latest WebUI
</details>

<details><summary>9.1.1 - 29 April 2023</summary>

### Changed
- Fixed an issue with reading `controlnet_x_image` variable
- Speculative fix for `postprocess()` routine not receiving updated images

</details>

<details><summary>9.1.0 - 28 April 2023</summary>

### Added
- `[choose]`: supports `_sanitize` to override the default content sanitization rules
- `[filelist]`: now supports `_basename` to return filenames instead of full paths
- `[filelist]`: now supports `_hide_ext` to discard file extensions from the returned string
- `[filelist]`: will now substitute `%BASE_DIR%` with an absolute path to the Unprompted extension
- `[replace]`: now supports `_insensitive` for enabling case-insensitive operations
- `[replace]`: now supports `_load` for importing from:to replacement directions from one or more external JSON files
- `[sets]`: now supports `_load` for importing key:value pairs from one or more external JSON files
- `[zoom_enhance]`: now supports `controlnet_preset`
- `[zoom_enhance]`: now supports experimental `use_starting_face` which will upscale the initial image's face as opposed to the resulting img2img's face
- `[zoom_enhance]`: more arguments available in the Wizard UI
- `[txt2mask]`: more arguments available in the Wizard UI
- New shortcode `[log]`: prints a message to the console
- Bodysnatcher v1.2.0: now supports `face_controlnet_preset` which is applied during the `[zoom_enhance]` step
- New ControlNet preset `photo_fast_v1`: tries to retain as much of the composition as possible with only a single CN unit
- New ControlNet preset `photo_face_v1`: work-in-progress preset that attempts to maximize likeness of a close-up portrait image
- ControlNet variables can be set with the shorthand prefix `cn_` instead of `controlnet_`

### Changed
- Bodysnatcher v1.2.0: now populates the list of ControlNet presets with files from `templates/common/controlnet_presets`
- Bodysnatcher v1.2.0: enabled `pixel_perfect` for all ControlNet templates

</details>

<details><summary>9.0.1 - 25 April 2023</summary>

### Changed
- `[switch]`, `[case]`: fixed issue with new nested syntax compatibility
- `[case]`: fixed issue with default case
- `[choose]`: fixed an issue with `[choose][file somefile][/choose]` syntax
- `[zoom_enhance]`: fixed issue with `color_correct_timing` set to `post`
- `[zoom_enhance]`: speculative fix for crash related to `unsharp_mask()` function

</details>

<details><summary>9.0.0 - 25 April 2023</summary>

### About
**Important:** This version features a number of changes to Unprompted's syntax that may break existing templates. Please see the latest announcement for more details.

### Added
- Block shortcodes can now implement `preprocess_block()` which allows them to take priority over any inner shortcodes
- `[if]`, `[else]`, `[elif]`, `[do]`, `[for]`, `[while]`, `[repeat]`, `[switch]`: now utilize `preprocess_block()` such that you no longer have to write secondary shortcode tags for nested statements
- `[choose]`: utilizes the new `preprocess_block()` to temporarily replace the value of `Unprompted.Config.sanitize_after` to `{"\\n":"|"}` which should allow the following syntax to select a random line from another file: `[choose][file some_file][/choose]`
- `[chance]`, `[do]`, `[for]`, `[while]`, `[set]`: now sanitize the content per the new `Unprompted.Config.syntax.sanitize_block` rules
- `[chance]`, `[do]`, `[for]`, `[while]`, `[set]`: support `_raw` to disable content sanitization
- New function `shortcode_var_is_true()`: allows shortcodes to check if a given variable key is found in pargs or set to True in kwargs (still needs to be implemented across most shortcodes)
- `[sets]`: supports advanced expressions
- Unprompted now includes extra generation paramters in the output window
- You can disable the above behavior by setting `Unprompted.Config.stable_diffusion.show_extra_generation_params` to false
- New config setting `Unprompted.Config.log_contexts`: a comma-delimited string that dictates which types of log messages to include in the console (only shows `ERROR` and `RESULT` messages by default, but can be extended to show `DEBUG` or `ALL`)
- Debug message displaying startup load time
- Simple `unprompted_dry.bat` that activates a given conda environment and launches `unprompted_dry.py` (you will need to edit it for your own setup)

### Changed
- `[zoom_enhance]`: fixed bug with manual mask behavior
- `[zoom_enhance]`: updated Wizard shortcode generation for compatibility with new syntax
- `[get]`: the `_before` and `_after` arguments no longer update the variable's stored value
- Bodysnatcher: updated template for compatibility with new syntax
- img2img_folder: updated template for compatibility with new syntax
- txt2img2img: update template for compatibility with new syntax
- Fixed an issue that prevented `controlnet_x_pixel_perfect` variables from working correctly
- Moved `import` calls of various Stable Diffusion shortcodes into the `run()` block to prevent issues with the standalone `unprompted_dry.py`

### Removed
- `Unprompted.Config.debug` in favor of the new `Unprompted.Config.log_contexts`
- Shortcodes that allow nested statements without use of secondary shortcode tags will no longer parse those secondary tags, unfortunately this means some templates will have to be updated for compatibility
- Outdated `choose_weighted` example template

</details>

<br>
<details><summary>👴🏼 Older Versions</summary>
<details><summary>8.3.1 - 22 April 2023</summary>

### About

Over the last couple days, I have been experimenting with changes to the adaptive scaling features of `[zoom_enhance]`. I believe it will produce more consistent results across different resolutions, but you should take a backup of the current shortcode if you're happy with its performance - many of the default settings have changed, and I will likely continue finetuning it over the next few weeks. Your feedback is appreciated!

### Changed
- `[zoom_enhance]`: rewrote most of the adaptive scaling calculations
- `[zoom_enhance]`: introduced several try-catch blocks for better exception handling
- `[zoom_enhance]`: fixed a couple issues with `show_original`
- `[zoom_enhance]`: fixed an issue that caused the shortcode to call Unprompted's `process()` routine a second time

</details>

<details><summary>8.3.0 - 21 April 2023</summary>

### Added
- New shortcode `[color_correct]`: provides the same automatic color grading features as Bodysnatcher, but in the form of a standalone block
- `[color_correct]`: supports the `source` argument, which is a string that processes the initial image with `[txt2mask]` and uses the resulting masked image as a source for color correction, as opposed to the entire image
- `[txt2mask]`: implemented [CLIP Surgery](https://github.com/xmed-lab/CLIP_Surgery) as a new method type ("clip_surgery") which optionally supports Segment Anything (dev comment: this is better than `clipseg` at certain tasks but worse at others - `clipseg` is still default for the time being)
- `[txt2mask]`: new argument `stamp` that pastes a temporary PNG onto the init image before running mask processing, useful for redacting a portion of the image for example
- `[txt2mask]`: supports `stamp_method` to choose sizing and positioning logic
- `[txt2mask]`: supports `stamp_x` and `stamp_y` for precise positioning of the stamp
- `[txt2mask]`: supports `stamp_blur` radius to engage optional gaussian filter
- `[txt2mask]`: 10 basic stamps are included by default
- `[zoom_enhance]`: now supports `mask_method`
- `[template]`: any kwargs in the Wizard template block will be passed to the constructed `[file]` block
- `[file]`: experimental new argument `_bypass_if` that skips file processing if the value returns true (intended to be used with Wizard templates)
- `[get sd_model]` should now work as expected
- Bodysnatcher: new option `background_mode` that inverts the mask and disables the zoom_enhance step
- Bodysnatcher: new setting `stamp`

### Changed
- `[zoom_enhance]`: the `color_correct_method` default value is now `none`
- `[zoom_enhance]`: fix for adaptive CFG scaling
- `[zoom_enhance]`: minor tweaks to the adaptive scaling algorithm
- `[zoom_enhance]`: speculative fix for an issue with batch processing, which may also resolve an infinite loop that could occur with Bodysnatcher
- `[txt2mask]`: the "sam" `method` has been renamed to "grounded_sam"
- `[txt2mask]`: fixed a crash related to switching back and forth between `method` types
- Moved legacy shortcodes into their own `legacy` folder
- Fixed a crash related to empty shortcode arguments
- Updated the manual

</details>

<details><summary>8.2.0 - 18 April 2023</summary>

### Added
- `[substring]`: you can now pass strings into the `start` and `end` arguments and it will find the index of those strings within the content
- `[zoom_enhance]`: included `negative_mask` in the Wizard UI

### Changed
- `[txt2mask]`: setting `method="sam"` will attempt to install the required GroundingDINO library automatically, YMMV
- `[array]`: fixed crash related to `_shuffle`
- Unprompted will now store downloaded models into `models` rather than `lib_unprompted`
- On startup, Unprompted will move its models to the new location

</details>

<details><summary>8.1.0 - 17 April 2023</summary>

### Added
- You can now use `[set]` to manage various ControlNet settings
- Bodysnatcher: new setting `use_optimized_inference_settings`
- Bodysnatcher: new setting `use_controlnet_preset`
- `[zoom_enhance]`: implements the `color-matcher` library for higher quality swaps
- `[zoom_enhance]`: supports `color_correct_method` to choose from different grading algorithms, or disable color correction by setting this to `none`
- `[zoom_enhance]`: supports `color_correct_strength` which is an integer that determines how many times to run the `color_correct_method`
- `[zoom_enhance]`: the `adaptive_hires` feature will now ajdust CFG scale and apply a bit of sharpening
- Wizard UI `number` elements can now specify `_minimum` and `_maximum` value range (however, this isn't supported by Gradio yet)
- Specified default values for Wizard UI `slider` elements to prevent crashing

### Changed
- `[zoom_enhance]`: speculative fix for final image not showing up in the output window
- `[zoom_enhance]`: the `use_workaround` parg has been renamed to `show_original`
- `[zoom_enhance]`: hotfix for broken txt2img mode
- `[case]`: fixed an issue with default case always firing
- Bodysnatcher: decreased the default value of `zoom_enhance_denoising_max` from 0.35 to 0.30
- Bodysnatcher: debug images are no longer saved by default, but you can toggle them in the UI

</details>

<details><summary>8.0.0 - 16 April 2023</summary>

### Added
- New `Bodysnatcher` GUI template
- New option `Unprompted.Config.beta_features` to opt into unfinished doodads
- Unprompted now creates a copy of the `p` object at the beginning of the `process()` routine named `Unprompted.p_copy`, which allows for greater compatibility with extensions that hijack the inference pipeline (e.g. ControlNet)
- With the help of the above change, `[zoom_enhance]` is now compatible with ControlNet
- The `[zoom_enhance]` shortcode now applies a sharpening filter to the final image as determined by the `sharpen_amount` arg
- The `[zoom_enhance]` shortcode now supports manual mask behavior `mode` similar to `[txt2mask]`
- The `[zoom_enhance]` shortcode seeks to improve support with `Only Masked` mode by scaling up some settings to account for your original image resolution
- The `[zoom_enhance]` shortcode supports `bypass_adaptive_hires` to disable the above behavior
- The `[zoom_enhance]` shortcode now supports `hires_size_max` which limits the adaptive resolution to avoid OOM errors (defaults to 1024)
- Wizard Templates now support `[wizard_ui_accordion]` to group a collection of settings into a collapsible menu
- Wizard Template UI elements now support `_info` for showing descriptive text
- New `Known Issues` section in the manual
- The `[txt2mask]` shortcode now supports the Segment Anything Model with GroundingRINO (set `method="sam"`), although you need to install the latter manually--it doesn't work with pip at the time of writing--and I'm not particularly impressed by its results compared to clipseg (after installing manually: you'll need to move GroundingRINO into your `venv` folder and replace any `import groundingrino` calls with relative imports e.g. `import ...utils.something`)
- CSS style for prose hyperlinks so I can actually see the darn things

### Changed
- Wizard Functions have been renamed to Wizard Templates
- The `[zoom_enhance]` shortcode now runs the native `process_images_inner()` function as opposed to piggybacking the `[img2img]` shortcode
- The `[zoom_enhance]` `save` parg has been renamed to `debug`
- Increased the `[zoom_enhance]` `mask_size_max` default value from 0.3 to 0.5
- A bit of UI polish
- Fixed a crash related to calling `Unprompted.parse_alt_tags()` with an empty string
- Fixed typo related to Wizard Template radio buttons
- Fixed CSS padding of list elements in the latest version of WebUI
- Fixed CSS spacing between `<detail>` elements
- Fixed Wizard Template radio button default value
- Fixed an issue with nested Wizard UI event listeners
- Wizard UI values are updated on Gradio's unfocus event due to the unreliable nature of the `change()` event as demonstrated here: https://github.com/gradio-app/gradio/issues/3876
- Improved logging in various places
- Wizard Templates are now explicitly loaded as `utf8` (compatible with emoji 😎)

### Removed
- The `settings` placeholder UI files for the time being, although I would like to implement a UI for `config_user.json` eventually



</details>

<details><summary>7.9.1 - 17 March 2023</summary>

### Changed
- Hotfix for `[zoom_enhance]` "Advanced Options" menu

</details>

<details><summary>7.9.0 - 17 March 2023</summary>

### Added
- New `match_main_seed` setting that synchronizes the Unprompted seed with the WebUI seed
- The `[txt2mask]` shortcode will now cache its model to improve performance (for reference, this saves about 3 seconds per run on my 3090)
- New `[txt2mask]` setting `unload_model` to disable the above behavior
- The `[zoom_enhance]` Wizard UI now includes `unload_model`
- New `[zoom_enhance]` setting `upscale_method`
- The `[zoom_enhance]` default upscaling method is now Nearest Neighbor which should result in a more accurate final image
- New `[zoom_enhance]` setting `downscale_method` which controls the resample filter used with the final image
- The `[zoom_enhance]` default downscaling method is now Lanczos, which should result in sharper images

### Changed
- Fixed an issue related to `[img2img]` and a previously interrupted generation
- The `[zoom_enhance]` shortcode does a better job of ensuring that img2img settings are correct
- Most of the `[zoom_enhance]` Wizard settings have been moved into an "Advanced Options" accordion menu
- Fixed a CSS issue related to the promo box and the newest version of the WebUI

</details>

<details><summary>7.8.0 - 13 March 2023</summary>

### Added
- The `[zoom_enhance]` shortcode now accepts multiple values for `replacement` and `negative_replacement`, using `Unprompted.Config.syntax.delimiter` (vertical pipe by default)
- The `[zoom_enhance]` shortcode now supports `mask_sort_method` which determines the order of multiple matching regions, defaults to `left-to-right`
- The `[zoom_enhance]` shortcode will now adjust CFG scale dynamically, in the same fashion as denoising strength
- The `[zoom_enhance]` Wizard GUI now lets you override `denoising_strength` and `cfg_scale` with arbitary values, bypassing the "dynamic" mechanism
- Every `[zoom_enhance]` argument now supports advanced expressions
- Improved console logging for `[zoom_enhance]`

### Changed
- The `[img2img]` shortcode temporarily bypasses `alwayson_scripts` to avoid errors with many extensions
- Fixed an issue related to `[zoom_enhance]` not responding after a previously interrupted generation or error
- Fixed a minor issue related to the `[zoom_enhance]` sigmoid curve evaluation
- Speculative fix for an issue related to `[txt2mask]` on non-CUDA devices

</details>

<details><summary>7.7.2 - 13 March 2023</summary>

### Added
- The `[zoom_enhance]` shortcode now supports experimental `use_workaround` to hopefully resolve issues with output window

</details>

<details><summary>7.7.1 - 13 March 2023</summary>

### Changed
- Fixed a few typos in the `[zoom_enhance]` shortcode

</details>

<details><summary>7.7.0 - 12 March 2023</summary>

### Added
- New `[zoom_enhance]` shortcode for automatically fixing issues with low-resolution details like faces or hands
- The `[after]` shortcode now supports `allow_dupe_index` when you want to run the same `after` content in batch mode
- The `[txt2mask]` and `[img2img]` shortcodes now support `return_image` which lets you call them directly in the source of other shortcodes
- Shortcodes can now declare custom `wizard_prepend` and `wizard_append` values in the event that they need to be called in an unusual way

### Changed
- Fixed an issue with `[img2img]` when used from the img2img tab

</details>

<details><summary>7.6.0 - 25 February 2023</summary>

### Added
- New `img2img_folder.txt` template function
- The `[info]` shortcode now supports `sentence_count`
- The `[info]` shortcode now supports `filename`
- The `[after]` shortcode now stores a self-referential `after_index` variable
- The `[length]` shortcode can now accept `[array]` variables directly

### Changed
- Fixed a crash related to setting index values with `[array]`
- Fixed a crash when sending an empty string to `parse_advanced()`
- Fixed a crash related to `[img2img]` when using multiple `[after]` blocks
- Fixed a few mistakes in the Manual

</details>

<details><summary>7.5.9 - 15 February 2023</summary>

### About

The `[controlnet]` shortcode is now considered a "legacy" feature as it is generally less robust than [Mikubill's dedicated ControlNet extension](https://github.com/Mikubill/sd-webui-controlnet). I have decided to re-allocate my energy into other aspects of Unprompted as I prefer to work on features that are not amply represented in the SD community.

### Added
- The `[controlnet]` shortcode now supports the `openpose_hands` argument

### Removed
- Unnecessary Gradio files from ControlNet library

</details>

<details><summary>7.5.8 - 14 February 2023</summary>

### Changed

- Fixed a startup crash that could occur when a ControlNet model was listed as previously selected

</details>

<details><summary>7.5.7 - 13 February 2023</summary>

### Changed

- Fixed `[controlnet]` save button

</details>

<details><summary>7.5.6 - 13 February 2023</summary>

### Added
- The `[controlnet]` shortcode now supports the Canny, HED Boundary, and Segementation Map models
- Implemented Wizard UI for the `[controlnet]` shortcode

### Changed
- Fixed a syntax issue related to sliders and the Wizard Shortcode generator

</details>

<details><summary>7.5.5 - 13 February 2023</summary>

### Added
- The `[controlnet]` shortcode now supports the Normal Map model

### Changed

- Fixed another memory leak related to `[controlnet]`

</details>

<details><summary>7.5.4 - 13 February 2023</summary>

### Added
- The `[controlnet]` shortcode now supports the Depth model

### Changed
- The `[controlnet]` ETA is no longer mistakenly assigned to denoising strength
- Potentially fixed memory leak related to `[controlnet]`

</details>

<details><summary>7.5.3 - 13 February 2023</summary>

### Added
- The `[controlnet]` shortcode now supports face restoration 

### Changed
- Fixed bug causing `[controlnet]` to run inadvertently

</details>

<details><summary>7.5.2 - 13 February 2023</summary>

### Added
- The `[controlnet]` shortcode now supports Scribble and M-LSD Line models with the `model` argument

</details>

<details><summary>7.5.1 - 13 February 2023</summary>

### Changed

- The `[controlnet]` shortcode now expects its models to be in the `Stable-diffusion` directory like a normal model

</details>

<details><summary>7.5.0 - 13 February 2023</summary>

### About
The new features in this release are still under development and may or may not work as intended.

### Added
- New WIP `[controlnet]` shortcode, only supports "pose2image" at the moment
- New WIP `[pix2pix_zero]` shortcode
- New WIP setting to enable compatibility with extra networks such as Lora, not yet functional

### Changed
- Moved the `pez_open_clip` dependency into the `stable_diffusion` subfolder

</details>

<details><summary>7.4.0 - 10 February 2023</summary>

### Added
- The `[img2pez]` shortcode now accepts multiple image paths and will optimize a single prompt across all of them
- The `[img2pez]` shortcode now supports `free_memory`
- The `[img2pez]` shortcode log now outputs the best candidates in realtime, courtesy of @bakkot

### Changed
- Reduced the `[img2pez]` default value for `iterations` from 3000 to 200 (thank you to @bakkot for the suggested optimizations)
- Increased the `[img2pez]` default value for `prompt_length` from 8 to 16
- The `template_directory` setting changed from `./templates` to `templates` for Linux compatibility, may also help with colab setups
- The `[...nyms]` shortcodes will now perform a download check for the required `wordnet` package
- Fixed Usage section in README.md
- Fixed a few filepaths in `templates/common/examples/human/main.txt`
- Rewrote the Wizard Shortcode generator function to fix a few issues

</details>

<details><summary>7.3.0 - 8 February 2023</summary>

### Added
- The `[img2pez]` shortcode now supports all settings from the Hard Prompts Made Easy method
- The `[img2pez]` shortcode now supports `image_path` if you wish to use something other than the initial img2img image
- Full Wizard GUI compatibility for `[img2pez]`

### Changed
- The `parse_filepath()` function has been updated to support choosing a random file from a directory

</details>

<details><summary>7.2.0 - 8 February 2023</summary>

### Added
- New `[img2pez]` shortcode (Hard Prompts Made Easy)

</details>

<details><summary>7.1.0 - 7 February 2023</summary>

### Added
- Added [pattern](https://github.com/NicolasBizzozzero/pattern) package to install.py for additional language processing features
- New `[article]` shortcode
- New `[pluralize]` shortcode
- New `[singularize]` shortcode
- New `[conjugate]` shortcode
- New `[autocorrect]` shortcode
- The `txt2img2img` template is now available as a Wizard Function

### Changed
- Updated the `[img2img]` shortcode for compatibility with the latest A1111 WebUI
- Updated the look of generated result text
- Updated the promo panel with info about the new DemonCrawl Avatar Generator

</details>

<details><summary>7.0.0 - 28 January 2023</summary>

### Added
- Added [NLTK](https://github.com/nltk/nltk) to install.py to enable natural language processing features
- New `[synonyms]` shortcode
- New `[antonyms]` shortcode
- New `[hypernyms]` shortcode
- New `[hyponyms]` shortcode
- The `[txt2mask]` shortcode now supports the optional `sketch_color` argument
- The `[txt2mask]` shortcode now supports the optional `sketch_alpha` argument
- The above arguments provide compatibility with Inpaint Sketch mode, albeit with some workarounds for A1111 limitations

### Changed
- The `[switch]` shortcode now supports advanced expressions
- Rewrote Wizard function generator for better layout handling
- Fixed issue with `[for]`
- Fixed issue with Unprompted seed locking the main seed
- Fixed issue with dropdown and radio Wizard UI delimiters
- Fixed SyntaxWarning related to Wizard function generator

</details>

<details><summary>6.0.0 - 25 January 2023</summary>

### Added
- You can now change the active SD checkpoint with `[set sd_model]`
- New `[instance2mask]` shortcode by WeberSamuel (PR #48)
- New `[invert_mask]` shortcode by WeberSamuel (PR #48)
- New `[enable_multi_images]` shortcode by WeberSamuel (PR #48)
- The `[txt2mask]` shortcode now supports GPU (PR #48)
- New `[txt2mask]` arguments: `neg_precision`, `neg_padding`, and `neg_smoothing` by WeberSamuel (PR #48)
- The `[txt2mask]` argument `show` will also append a segmentation mask (PR #48)
- New UI option `Unprompted Seed` allows you to reproduce images that feature shortcodes with randomness, such as `[choose]` 

### Changed
- Wizard Function default values are no longer written to ui-config.json
- Fixed `[img2img]` syntax for compatibility with latest A1111
- Fixed a rounding issue with Wizard shortcode number fields
- The Manual and Starter Guide have been reorganized into collapsible sections
- Moved all included templates into `templates\common` for simplicity

</details>

<details><summary>5.2.0 - 24 January 2023</summary>

### Added
- The `[set]` shortcode now supports the `_choices` argument which accepts an array of valid values
- The `[set]` shortcode now supports the Wizard UI `_placeholder` argument
- The `[sets]` shortcode has been rewritten to pass off its arguments to `[set]`, which means it now supports all current and future system arguments of `[set]`
- Wizard Functions now support `dropdown`, `radio` and `slider` as valid `_ui` types
- Wizard Function textboxes show the `[set]` content as a placeholder
- Wizard Functions will now include a gr.Label title element by default
- The Wizard shortcode parser now supports `[base_dir]` which is useful for linking to files within the template directory (note that [this function is broken](https://github.com/gradio-app/gradio/issues/3009) in the version of Gradio that A1111 currently uses)
- Updated the manual

### Changed
- Renamed the `lib` folder to `lib_unprompted` in order to resolve import calls conflicting with other extensions, possibly due to a flaw in the A1111 extension framework (more research needed)

</details>

<details><summary>5.1.0 - 23 January 2023</summary>

### Added
- The Wizard now includes Function mode, which houses custom UIs for your `[file]` templates
- New `example_function.txt` to demonstrate the basics of the Wizard Function mode
- The Wizard auto-include option is now determined on a per-shortcode or function basis

### Changed
- Several fixes and workarounds to ensure compatibility with latest version of A1111 WebUI

### Removed
- `Config.ui.wizard_autoinclude` temporarily removed for logistical reasons
- CLIPSeg weights no longer included with this repo (the txt2mask shortcode will automatically download the weights if necessary)

</details>

<details><summary>5.0.0 - 2 January 2023</summary>

### Added
- New shortcode `[array]` which can be used to manage groups or lists of values
- The `[txt2mask]` `padding` argument now supports negative values
- The `[txt2mask]` `smoothing` argument now supports advanced expressions
- The `[choose]` `_weighted` argument now supports floats
- The `[get]` function can return formatted lists, including those created by `[array]`
- New config `ui` settings for customizing the open state of accordion menus
- New button in the About tab to quickly open your templates folder
- The `[eval]` shortcode now supports a `sigmoid()` distribution curve function
- New function `is_system_arg()` to simplify the skipping of certain shortcode arguments

### Changed
- Rewrote the `[txt2mask]` `padding` implementation (PR #38 - thank you, @credman0!)
- The `[txt2mask]` default value of `smoothing` has changed from 0 to 20
- No longer need to specify entire sub-dictionary blocks in `config_user.json` to apply partial changes, thanks to flatdict library
- The `[config]` shortcode also supports the flatdict library mentioned above
- Workaround for Gradio checkbox value being overwritten by A1111 stock config
</details>

<details><summary>4.3.1 - 29 December 2022</summary>

### Changed
- Fixed issue with `[choose]`

### Removed
- Unnecessary Javascript file
</details>

<details><summary>4.3.0 - 27 December 2022</summary>

### Added
- New Wizard panel, an experimental GUI shortcode builder
- New config section `ui` for adjusting the default appearance of the extension
- The `[choose]` shortcode now supports `_weighted` for a more convenient approach to weighing the list of options

### Changed
- Minor interface improvements
- Fixed an issue related to txt2mask in the new version of A1111 WebUI
- Fixed an issue related to the postprocess() routine in the new version of A1111 WebUI

</details>

<details><summary>4.2.1 - 23 December 2022</summary>

### Changed
- Fixed an issue related to `[switch]`

</details>

<details><summary>4.2.0 - 22 December 2022</summary>

### Added
- New shortcode `[file2mask]` that allows you to modify or replace your img2img mask with arbitrary files
- New shortcode `[filelist]` that returns a delimited string containing the full paths of all files in a given path
- New shortcode `[length]` that returns the number of items in a delimited string
- The `[txt2mask]` shortcode utilizes the new refined CLIPseg weights
- The `[txt2mask]` shortcode now supports `legacy_weights` which will fallback to the old weights
- The `[txt2mask]` shortcode now supports `smoothing` which lets you define the sharpness of your mask selection
- The `[txt2mask]` shortcode now supports `size_var` which lets you store the percentage of the canvas that your text selection occupies
- The `[get]` shortcode can now return multiple variables
- The `[get]` shortcode allows you to specify a separator when returning multiple variables via `_sep`
- The `[file]` shortcode now supports `_encoding` which lets you change the expected encoding type

### Changed
- Improved error handling for the `[file]` shortcode
- Minor improvements to the Manual and Readme
</details>

<details><summary>4.1.0 - 14 December 2022</summary>

### Added
- New `after()` routine that allows Unprompted to modify the outcome of a generation
- New shortcode `[after]` that allows you to process text post-generation
- New shortcode `[img2img]`, which is used inside of `[after]` for appending an img2img task to the output, effectively replacing my old txt2img2img script
- New shortcode `[img2img_autosize]` that automatically adjusts the width and height parameters in img2img mode based on the proportions of the input image
- New shortcode `[init_image]` that loads an image from the given filepath for use with img2img
- New config options `templates.default` and `templates.default_negative` that let you apply certain shortcodes to every run
- The `[txt2mask]` shortcode now supports `show` which will append the final image mask to your generation output
- The `[txt2mask]` shortcode now supports advanced expressions

### Changed
- Fixed an issue with advanced expressions and multi-word string values
</details>

<details><summary>4.0.0 - 11 December 2022</summary>

### Added
- New shortcode `[txt2mask]` which is a port of my script by the same name
- Collapsible menus to docs
- "Enabled" checkbox in the extension UI as a convenient way of bypassing Unprompted
- The extension now features inline resources, including the announcements, changelog, manual and starter guide

### Changed
- Redesigned the extension interface
- The Dry Run feature has been decoupled from the WebUI's "Generate" button, meaning it no longer generates a dummy image
- The `[choose]` delimiter is now specified in the config as `syntax.delimiter`

### Removed
- Custom CSS and Javascript for handling the collapsible advertisement in favor of native Gradio elements
</details>

<details><summary>3.0.0 - 10 December 2022</summary>

### Added
- The `[info]` shortcode now supports `clip_count`

### Changed
- Fixed an issue with the negative prompt in batch sizes greater than 2

### Removed
- The `[chance]` shortcode no longer supports `_probability` as the first argument now automatically accepts expressions and secondary shortcode tags
</details>

<details><summary>2.0.2 - 7 December 2022</summary>

### Changed
- Overhauled Github README.md
- Possibly fixed compatibility issue with Dynamic Prompts
</details>

<details><summary>2.0.1 - 7 December 2022</summary>

### Changed
- The `[file]` shortcode will throw a soft error if the provided filepath is not valid, rather than completely aborting Unprompted (Issue #23)
- Fixed a string truncation issue related to the sanitization filter (Issue #26)
</details>

<details><summary>2.0.0 - 7 December 2022</summary>

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
</details>

<details><summary>1.2.0 - 2 December 2022</summary>

### Added
- New `[sets]` atomic shortcode for setting multiple variables at once

### Changed
- `[eval]` can now read user variables
</details>

<details><summary>1.1.0 - 2 December 2022</summary>

### Added
- New `[for]` shortcode, as in for loops
- New `[casing]` shortcode powered by @dmlls casefy library
- The `[if]` and `[while]` shortcodes now support advanced expressions via simpleeval, e.g. `[if "var_a==10 and var_b<=50"]`
- The `[if]` and `[while]` shortcodes now support `!=` as an operator type for `_is`
</details>

<details><summary>1.0.0 - 1 December 2022</summary>

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
</details>

<details><summary>0.10.0 - 30 November 2022</summary>

### Added
- New `[replace]` shortcode

### Changed
- Replaced `n_temp` and `n_final` config settings with `sanitize_before` and `sanitize_after` that let you define any number of characters to modify before/after processing
- Tab character (`\t`) is now ignored by default, which will hopefully make it easier to format complex templates for readability
- All string sanitization logic has been moved into the `process_string()` function
- Fixed an issue with `negative_prompt` logic
</details>

<details><summary>0.9.0 - 29 November 2022</summary>

### Added
- Updated `negative_prompt` to support the latest version of Automatic1111's WebUI, which permits batch support for negative prompts
</details>

<details><summary>0.8.0 - 13 November 2022</summary>

### Added
- New system variable `batch_index` for making decisions based on the progress into a batch run
- The `[choose]` shortcode now accepts `_case` which bypasses the random selection with a given number or variable
</details>

<details><summary>0.7.0 - 11 November 2022</summary>

### Added
- New `[config]` shortcode
- The `[choose]` delimiter is now specified in config.json (defaults to `|`)
- New `parse_filepath(string, context)` function in shared.py that supports both relative and absolute path handling
- Merged `.gitignore` PR (thank you @MaikoTan!)
</details>

<details><summary>0.6.0 - 6 November 2022</summary>

### Added
- New `[elif]` shortcode
- The `[repeat]` shortcode now accepts floats, e.g. 4.6 has a 60% chance of repeating 5 times instead of 4
- The `[repeat]` shortcode now supports `_sep` which is a string delimiter to insert after each output, excluding the final output
- New `autocast()` function in shared.py that will convert a variable to str, int, or float automatically
- New `templates/examples` for snippets of code that demonstrate cool ways of combining shortcodes you may not have considered

### Changed
- Fixed an issue with `[repeat]` outputting its content once more than intended
</details>

<details><summary>0.5.1 - 5 November 2022</summary>

### Changed
- Fixed an issue with `[set]` converting to float in situations where int is preferred
</details>

<details><summary>0.5.0 - 5 November 2022</summary>

### Added
- Button for dismissing the ad
- The ad will be dismissed automatically if you purchase the Fantasy Template Pack
</details>

<details><summary>0.4.0 - 4 November 2022</summary>

### Added
- Config option `batch_support` which, if enabled, will generate random prompts for every image in a batch as opposed to using the same prompt for the entire batch
</details>

<details><summary>0.3.0 - 4 November 2022</summary>

### Added
- Support for infinite nesting of secondary shortcode tags
- New shortcode `[while]` for looping content until the condition returns false
- `[chance]` now supports `_sides` which determines the upper bound of the chance roll (default is 100)

### Changed
- The `[if]` `_operator` argument has been renamed to `_is` for readability
</details>

<details><summary>0.2.0 - 4 November 2022</summary>

### Added
- New shortcode `[##]` for multiline comments
- Documentation for `config.json`
- `[if]` now supports `_any` which flips from "and" to "or" multivar processing
- `[if]` now supports `_operator` which determines the comparison logic for your arguments

### Changed
- Overhauled codebase in order to load as an A1111 extension rather than a script, please re-review the installation instructions!
- Renamed `DOCUMENTATION.md` to `MANUAL.md`
</details>

<details><summary>0.1.1 - 2 November 2022</summary>

### Added
- `[get]` now supports `_before` and `_after` arguments
- `[set]` now supports secondary shortcode tags

### Changed
- `[file]` now strips leading and trailing newline characters
</details>

<details><summary>0.1.0 - 1 November 2022</summary>

### Added
- Added `[switch]` and `[case]` shortcodes
- Added `[repeat]` shortcode
- Added `is_equal()` function to Unprompted object that checks for loose equality of two variables

### Changed
- Fixed `_append` and `_prepend` behavior of `[set]` when used with int values
</details>

<details><summary>0.0.1 - 31 October 2022</summary>

### Added
- Initial release
</details>
</details>