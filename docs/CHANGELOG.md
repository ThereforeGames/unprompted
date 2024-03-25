# Changelog
All notable changes to this project will be documented in this file.

For more details on new features, please check the [Manual](./MANUAL.md).

<details open><summary>10.8.0 - 25 March 2024</summary>

### Added
- `[gpt]`: Now supports `tokenizer` kwarg to load a separate model as the tokenizer
- `[gpt]`: Now supports `transformers_class` kwarg to specify the methods of inference, defaults to `auto`
- `[gpt]`: Now supports `prefix` and `affix` kwargs to include extra strings in the returned result
- `[gpt]`: Catch exception when there are issues with the `model` or `tokenizer`
- `[replace]`: Now supports delimited values in `_from` and `_to` kwargs
- Magic Spice preset `booru_spice_v2`: Updated syntax for better compatiblity with Animagine XL 3.1
- Magic Spice preset `photo_spice_v2`: Updated GPT model to SuperPrompt
- Magic Spice preset `allspice_v2`: Updated GPT model to SuperPrompt
- New config setting `Config.ui.wizard_prepends`: Determines whether the Wizard's autoincludes are prepended or appended to your prompt (defaults to true; prepend)
- New txt2img preset `dpm_lightning_8step_merged_v1`: Compatible only with Forge UI, use with models that have prebaked Lightning lora

### Fixed
- `photo_spice_v2`: Fixed an issue with the `do_fluff` variable
- `[zoom_enhance]`: Fixed a possible crash due to unused `scipy` package
- `[img2img]`: Fixed an issue with Forge WebUI

</details>

<details><summary>10.7.0 - 6 March 2024</summary>

### Added
- New shortcode `[autotone]`: Adjusts the black point of the image to enhance contrast (should be placed inside an `[after]` block)
- New free template Magic Spice v0.0.1: Produces high-quality images regardless of the simplicity of your prompt, using ideas from Fooocus and elsewhere
- `[faceswap]`: Now supports the `gender_bonus` kwarg to boost facial similarity score when source and target genders are equal (compatible with insightface pipeline only)
- `[faceswap]`: Now supports the `age_influence` kwarg to penalize facial similarity score based on the difference of ages between source and target faces (compatible with insightface pipeline only)
- `[faceswap]`: Now supports the `prefer_gpu` kwarg to run inference on the video card if possible
- `[faceswap]`: The `make_embedding` option will now save gender and age values into the blended embedding
- `[faceswap]`: The insightface analyser is now properly cached, improving inference time significantly
- `[gpt]`: Now supports the `instruction` kwarg to help steer models that are capable of following instruction-response format prompts
- Added a customized `insightface_cuda` package that swaps hardcoded CPU references to CUDA equivalents
- Wizard UI now supports `_lines` and `_max_lines` to specify number of rows in a textbox UI element
- Unprompted now detects if you're using the Forge WebUI
- New txt2img preset `restart_fast_v1`
- New txt2img preset `dpm_lightning_8step_v1`: Uses the new Lightning sampler and Lora in Forge WebUI for super fast SDXL inference
- New helper function `str_to_rgb()`
- Facelift template banner image

### Changed
- `[gpt]`: The default GPT-2 model is now `LykosAI/GPT-Prompt-Expansion-Fooocus-v2`
- `[gpt]`: Renamed the `cache` parg to `unload` to match naming convention of other shortcodes
- Facelift template now defaults to the `fast_v1` preset

### Fixed
- The `wizard_generate_shortcode()` and `wizard_generate_template()` methods will no longer escape special HTML characters in the prompt
- `[after]`: Fixed compatibility issue with Forge WebUI
- `[faceswap]`: The `export_embedding` parg will now bypass the cache to avoid errors
- The `get_local_file_dir()` method now uses the `unprompted_dir` variable in case Unprompted is not in the usual `extensions` directory

### Removed
- Developer presets

</details>

<details><summary>10.6.0 - 1 December 2023</summary>

### Added
- New settings `Config.ui.wizard_shortcodes`, `Config.ui.wizard_templates`, `Config.ui.wizard_capture`: Allows you to disable certain Wizard tabs in order to improve WebUI performance
- `[max]` and `[min]`: Supports the `_key` parg to return the key of the max/min value instead of the value itself
- `[max]` and `[min]`: Can now parse values given as a list separated by `Config.syntax.delimiter`
- `[get]`: Supports the `_key` kwarg to return the names of requested variables instead of their values
- `[get]`: Supports the `_regex` kwarg to return the values of matching variables

### Changed
- `[set]`: Now parses the value of the first parg, allowing you to use shortcodes in evaluating the variable name
- `[get]`: The default value of `_sep` is now `Config.syntax.delimiter` instead of space

### Fixed
- `[faceswap]`: Fixed `embedding_path` processing

</details>

<details><summary>10.5.0 - 25 November 2023</summary>

### About
This update introduces global variables, several image processing shortcodes and improvements to some included templates and presets. The image features were motivated by Unprompted's integration with [BooruDatasetTagManager](https://github.com/starik222/BooruDatasetTagManager/pull/89) (my own PR.) For example, you can use `[image_info]` to assess image quality and influence the results of the Autotagger. Enjoy!

### Added
- New shortcode `[resize]`: Resizes the image to the given dimensions, works with the SD image by default
- `[resize]` can be toggled to peform a crop instead
- New shortcode `[image_info]`: Returns various types of metadata about the image, including quality assessment via the pyiqa toolbox
- New shortcode `[cast]`: Converts the content to a given datatype
- New config setting `globals`: Allows you to create variables in key/value format that will be available to all templates and shortcodes
- New config setting `Syntax.global_prefix`: The prefix for global variables, defaults to `global_`
- `[get]`: Automatically runs variables through the parser if they begin with `Unprompted.Config.syntax.global_prefix`, which means that global variables can be initialized to complex values such as function names or other shortcodes
- `[get]`: New parg `_read_only`, use with `_parse` in order to prevent the parser from writing the result back to the variable (which is the new default behavior of `_parse`)
- `[txt2mask]`: New kwarg `aspect_var` which returns the aspect ratio of the mask 
- Regional Prompter Buddy v0.1.0: Now references `global_subject` for default `subject_a`
- Regional Prompter Buddy v0.1.0: Adjusted default settings to improve speed of workflows
- Bodysnatcher v1.5.0: New setting `max_image_size` size to limit the dimensions of the output image
- Bodysnatcher v1.5.0: New setting `mask_informs_size` which uses the mask aspect ratio to determine the inpainting dimensions
- Bodysnatcher v1.5.0: New setting `mask_size_limit` to cap the dimensions of the aforementioned feature
- Bodysnatcher v1.5.0: New setting `mask_padding` to adjust the padding applied by `[txt2mask]`
- Bodysnatcher v1.5.0: Now references `global_subject`, `global_prefix`, and `global_class` for default values
- Bodysnatcher v1.5.0: Now uses the new `vivarium_v3` preset by default
- Bodysnatcher v1.5.0: Minor UI updates
- `viviarum_v3` ControlNet preset: Now uses the `reference` model at a low strength to help preserve lighting
- `vivarium_v3` ControlNet preset: Adjusts denoising strength depending on whether an inpainting model is active
- `vivarium_v3` ControlNet preset: Now references `global_negative_prompt` for inference
- `vivarium_v3` ControlNet preset: No longer specifies `mask_method` as I find the preset equally effective with or without it, albeit in different ways - try both!
- `best_quality_v4` Facelift preset: Now prefers the `TGHQFace8x_500k` ESRGAN model, as the `4xFaceUpDAT` model is throwing errors in the current WebUI
- ControlNet image variables can now take a PIL object in addition to a filepath
- New `Reload Unprompted` button in the WebUI
- Warning message about the (presently significant) limitations of Gradio's dynamic refresh capabilities and temporarily disabled some refresh features

### Fixed
- `[round]`: Fixed error with rounding ints
- The `Unprompted.current_image()` method now takes care to update the size of `image_mask` if needed

</details>

<details><summary>10.4.2 - 20 November 2023</summary>

### Fixed
- `[max]`: Fixed an issue with float values

</details>

<details><summary>10.4.1 - 20 November 2023</summary>

### Changed
- Tweaked `shared.py` import statements to make importing Unprompted from other locations a bit easier
- Updated `requirements.txt`

</details>

<details><summary>10.4.0 - 10 November 2023</summary>

### Added
- `[faceswap]`: New kwarg `visibility` to control the alpha value of the swapped face, defaults to 1.0
- `[faceswap]`: New parg `export_embedding` that will save a file of the averaged faces to the given filepath (in safetensors format)
- `[faceswap]`: New kwarg `embedding_path` that allows you to specify a filepath for the exported embedding
- `[faceswap]`: You can load a composite face embedding by passing it in the first parg, this is only compatible with the `insightface` pipeline
- Facelift preset `make_embedding`: Generates a composite face embedding from the given face filepaths
- Facelift preset `best_quality_v3`: Reduces the visibility of the faceswap slightly in order to maintain some of the original textures
- Facelift preset `best_quality_v3`: Now prefers the `4xFaceUpDAT` ESRGAN model
- Facelift v0.1.1: The `faces` upload window now shows safetensors files in addition to images
- Bodysnatcher v1.4.4: Minor UI updates
- Bodysnatcher preset `vivarium_v2`: Adjusted inference settings and enabled `[txt2mask]` support
- Wizard UI type `file`: The `_file_types` kwarg now supports delimited values

### Changed
- Regional Prompter Buddy v0.0.4: Reduced default `flip_chance` to 0
- Regional Prompter Buddy v0.0.4: Disabled `base_prompt` by default to match default setting in Regional Prompter

### Fixed
- Wizard: Fixed a crash that could occur while parsing shortcodes inside of a `[wizard]` block
- Updated "Getting Started" guide for compatibility with current `[overrides]` syntax

</details>

<details><summary>10.3.1 - 5 November 2023</summary>

### Fixed
- `[config]`: Hotfix for inline JSON parsing

</details>

<details><summary>10.3.0 - 5 November 2023</summary>

### Added
- `Config.syntax.cleanup_extra_spaces`: Determines default behavior of the `process_string()` function with regard to trimming extra spaces (not thoroughly tested; setting this to false may cause issues with certain shortcodes)
- Unprompted will print the contents of the `p` object if your logger is set to `DEBUG`
- Bodysnatcher v1.4.3: Supports `keep_hands` and `keep_feet` even when `mask_mode` is "none"

### Changed
- `[faceswap]`: Improved caching of the face object when adding or changing face filepaths
- `[log]` and `[logs]`: The default logging context is now inherited from `Config.logging.level`
- `[while]`: Added `preprocess_block()` to delay execution of inner content until expression is evaluated as true
- Bodysnatcher v1.4.3: Sets `inpainting_mask_invert` to true when `mask_mode` is "none"
- Bodysnatcher v1.4.3: Adjusted interrogation syntax

### Fixed
- `[img2img]`: Removed unnecessary loop through samplers
- `[upscale]`: Fixed shortcode not working when `models` value did not include a delimiter

</details>

<details><summary>10.2.3 - 29 October 2023</summary>

### Fixed
- Fixed a batch processing issue that could cause the negative prompt to repeat itself

</details>

<details><summary>10.2.2 - 29 October 2023</summary>

### Fixed
- Additional fixes for hires variables not syncing properly with batch process

</details>

<details><summary>10.2.1 - 28 October 2023</summary>

### Added
- New ControlNet preset `vivarium_v1`: Uses the `instruct_p2p` model and opinionated inference settings for a quick and fairly accurate bodyswap
- Bodysnatcher v1.4.2: Added option to disable `[txt2mask]` feature

### Fixed
- Fixed an issue related to the hires prompt not updating correctly for the first image in a batch

</details>

<details><summary>10.2.0 - 27 October 2023</summary>

### Added
- New shortcode `[tags]`: Assigns arbitrary metatags that can be used in conjunction with a filter for bypassing the content
- New shortcode `[filter_tags]`: Bypasses the content of `[tags]` blocks that do not match the given filter
- New shortcode `[logs]`: Atomic version of `[log]` that allows you print multiple messages at once
- Blue badge with the number of active Wizard scripts, similar to ControlNet
- New setting `Config.syntax.not_operator`: Allows you to change the character used for the "not" operator, defaults to `!` (currently only used for tags)
- New guide: "Using Metatags with Your `[choose]` Blocks"

### Changed
- Wizard "auto-include" string now contains name of the current script or shortcode
- Shuffle the Unprompted promo on UI load
- Minor CSS improvements

### Fixed
- `[override]`: Fixed a syntax error
- Fixed an error related to setting `batch_count` > 1 with hires fix enabled

</details>

<details><summary>10.1.5 - 18 October 2023</summary>

### Fixed
- Wizard UI: Fixed an issue related to block shortcode content
- `[txt2mask]`: Fixed a crash that could occur with the `show` parg
- `[color_correct]`: Fixed missing Wizard UI

</details>

<details><summary>10.1.4 - 17 October 2023</summary>

### Fixed
- `[zoom_enhance]`: Additional fixes for the `bypass_adaptive_hires` parg

</details>

<details><summary>10.1.3 - 16 October 2023</summary>

### Changed
- `[interrogate]`: Now caches the image and caption to speed up future calls to the same image
- Bodysnatcher v1.4.1: Moved the interrogation result to the back of the prompt

### Fixed
- `[zoom_enhance]`: Fixed an error related to the `bypass_adaptive_hires` parg
- The Wizard parser no longer escapes quotation marks
- The Wizard parser will automatically convert brackets into nested alt tags for compatibility with `[call]` arguments
- The Wizard parser will automatically convert double quotes to single quotes

</details>

<details><summary>10.1.2 - 14 October 2023</summary>

### Fixed
- `[get]`: Fixed the `_var` kwarg

</details>

<details><summary>10.1.1 - 14 October 2023</summary>

### Fixed
- Resolved an issue with the negative prompt not updating correctly in some batch processing scenarios as well as for Style presets

</details>

<details><summary>10.1.0 - 13 October 2023</summary>

### Added
- New shortcode `[upscale]`: Enhances a given image using one the WebUI's upscaler methods
- New shortcode `[interrogate]`: Generates a caption for the given image using various techniques
- `[civitai]`: Now supports `_words` parg to include the activation text in your prompt, also writing it to the companion JSON file 
- Facelift v0.1.0: Upgraded preset `best_quality_v2` which now applies `[upscale]` as a final step
- New helper method `ensure()`: Converts a variable to a datatype if it isn't already that datatype
- Bodysnatcher v1.4.0: Optionally interrogate the starting image
- ControlNet model variables may now refer to the name presets in `Config.stable_diffusion.controlnet.sd1_models`; you can adjust these to match your own filenames
- The CN config has a place for SDXL models too, although I haven't added any entries there yet
- Updated img2img preset `full_denoise_v3`: Reduced the CFG scale and disabled mask blur

### Changed
- The setting `Config.stable_diffusion.controlnet_name` has been renamed to `Config.stable_diffusion.controlnet.extension`

### Fixed
- The template editor will correctly parse files with emojis now

</details>

<details><summary>10.0.2 - 13 October 2023</summary>

### Added
- `[else]`: Now supports `debug` parg to print diagnostic information
- New img2img preset: `subtle_v1`
- Updated ControlNet preset `photo_general` and renamed to `magic_mirror_v2`
- Updated ControlNet preset `photo_fast` and renamed to `quickshot_v2`

### Changed
- `[faceswap]`: Lowered the default value of `minimum_similarity` from 0 to -1000
- Renamed ControlNet preset `photo_inpainting_v1` to `fidelity_v1`
- Renamed ControlNet preset `photo_face` to `face_doctor_v1`
- Facelift v0.0.2: Now defaults to the `best_quality` preset
- Bodysnatcher v1.3.5: Updated the default `prefix` from "photo of" to "high detail RAW photo of"
- Bodysnatcher v1.3.5: No longer runs `[img2img_autosize]` when you are on `Only masked` mode
- Bodysnatcher v1.3.5: Now applies 5px of negative mask padding when using the `Keep original hands` option, which can significantly improve blending of new image
- Bodysnatcher v1.3.5: The Zoom Enhance features are now disabled by default, as Facelift is a better fit with Bodysnatcher
- Bodysnatcher v1.3.5: Updated the default `inference_preset` to `subtle_v1`
- Bodysnatcher v1.3.5: Updated documentation
- Updated credits in `README.md`

### Fixed
- `[else]`: Fixed a potential issue related to nested conditional logic
- `[faceswap]`: Speculative workaround for an issue related to insightface and a missing Cython dependency
- Replaced a few instances of `[file]` with `[call]` in the stock templates
- Bodysnatcher v1.3.5: Fixed an error that would occur when `Keep hands` was disabled but `Keep feet` was enabled

### Removed
- `requirements.txt` from ghost package to resolve Github security warnings

</details>

<details><summary>10.0.1 - 11 October 2023</summary>

### Fixed
- `[civitai]`: Fixed an issue related to the shorthand syntax and the `query` kwarg

</details>

<details><summary>10.0.0 - 11 October 2023</summary>

### About
**Important:** This is a major update with changes to batch processing that may affect pre-existing templates. Please read the changelog carefully.

### Added
- New premium template Beautiful Soul: A highly expressive character generator for the A1111 WebUI. With thousands of wildcards and direct ControlNet integration, this is by far our most powerful Unprompted template to date. Available at half price until November 11th!
- New template Facelift v0.0.1: An all-in-one solution for performing faceswaps by combining different models and postprocessing techniques
- New shortcode `[faceswap]`: Replaces the face with that of an arbitrary image using various pipelines, including InsightFace (same tech as Roop extension)
- New shortcode `[restore_faces]`: Improves the quality of faces using various models, including a custom GPEN implementation exclusive to Unprompted
- New shortcode `[civitai]`: Downloads a file using the Civitai API (unless it's already on your system) and automatically adds it to your prompt with correct formatting
- New shortcode `[overrides]`: Allows you to force the value of specific variable(s) using inline kwargs (`[override]` is now a block shortcode instead)
- New config setting `Config.formats.default_encoding` for various file operations (defaults to `uft8`)
- New config setting `Config.debug_requirements`: Set to true in `config_user.json` to potentially fix issues with missing dependencies
- New class method `Unprompted.parse_arg()`: Formats a parg or kwarg by the key, casting to a given datatype as specified (this will gradually replace other methods of processing shortcode args)
- New class method `Unprompted.current_image()`: Gets or sets the current image with support for txt2img, img2img, batch processing, and the `[after]` routine
- New class method `Unprompted.escape_tags()`: Escapes the bracket characters in a string
- `[get]`: Now supports `_escape` to remove square brackets, useful when used inside of an expression
- `[get]`: Now supports `_parse` to run the requested variable through the shortcode parser before returning
- `[set]`: Now supports `_defer` which bypasses shortcode parsing of the content, allowing you to instead parse the variable with `[get _parse]`.
- `[set]`: Now supports `_show_label` to control whether the label is visible in the Gradio Wizard UI (defaults to True)
- Inference presets for txt2img: `dpm_3m_v1`, `euler_a_v1`, `restart_v1`, and `variety_hour_v1`
- Various enhancements for `download_file()` helper method
- The Wizard now supports Gradio File, Image, Row, and Column blocks
- The Wizard now supports multiselect dropdown values for both shortcode and template UIs
- Print "main routine completed" message to the console

### Changed
- `[after]`: Now has dedicated batch support, which eliminates the need to implement batch support on a per-shortcode basis
- `[after]`: Replaced `allow_dupe_index` with `dupe_index_mode` that can be set to `skip`, `concat`, `append`, or `replace`
- `[call]`: Now evaluates secondary tags in kwarg values
- `[override]`: Converted to a block shortcode that forces the value of the first parg to become the result of the content
- `[color_correct]`: Updated batch support
- `[if]`: Updated truthy check such that string variables will evaluate to true, e.g. `[sets var="something"][if var]this is true![/if]`
- `[wizard accordion]`: renamed to `[wizard]` that reads a block type from the first parg, either `accordion`, `row`, or `column`
- Bodysnatcher v1.3.4: Replaced `[file]` blocks with `[call]`
- Regional Prompter Buddy v0.0.3: The `split_negatives` option will add extra terms to further differentiate the two subjects
- Migrated helper functions to a standalone `lib_unprompted.helpers` module in accordance with Python standard practices
- Updated img2img inference presets: `general_v2` and `full_denoise_v2`, moved them from `inference` folder to `img2img`
- `Unprompted.Config.txt_format` renamed to `Unprompted.Config.formats.txt`
- Minor improvements to the extension UI layout
- Improved parser error message about unclosed tag

### Fixed
- `[img2img_autosize]`: Fixed a crash that would occur when using the Wizard to auto-include this shortcode
- `[if]`: Will return false if the provided key doesn't exist as a user variable
- `[set]`: Fixed compatibility issue with `_remember` and Wizard UI elements
- Fixed the "Generate Shortcode" button for Wizard Templates appearing outside of its tab
- Improved flexibility of the backtick escape character such that it should work with any subsequent character
- Resolved error related to the `simple` and `verbose` modes of the Capture tab

### Removed
- Legacy function `shortcode_string_log()`
- `[zoom_enhance]` no longer implements its own batch support, instead now relies on that of the `[after]` block

</details>

<br>
<details><summary>👴🏼 Older Versions</summary>
<details><summary>9.16.1 - 7 September 2023</summary>

### Fixed
- `[img2img]`: Fixed missing parameters for default WebUI scripts `seed` and `refiner`
</details>

<details><summary>9.16.0 - 7 September 2023</summary>

### Added
- `[get]` and `[set]`: Now support `_external` kwarg to read/write a specific variable into an external file
- `[get]` and `[sets]`: Now support `_all_external` kwarg to read/write all variables into an external file
- `[set]`: You can now set `_ui="none"` in conjunction with `_new` to avoid adding this block to the Wizard UI
- `[call]`: Replaced filepath handling with the updated `Unprompted.parse_filepath()` method, which now supports absolute paths
- `[call]`: Now supports `_suppress_errors` to avoid writing errors to console
- Helper function `str_with_ext()` that formats a filepath string to include an extension if it's missing one
- Helper function `create_load_json()` that creates the requested json file before trying to load it, if necessary

### Changed
- `[##]`: Now correctly nullifies any shortcodes in the content, including those with malformed syntax

### Fixed
- `[img2img]`: Fixed an issue with this shortcode and the After routine in WebUI v1.6.0
- Fixed an issue with batch_count > 1 in the latest WebUI
- Fixed an issue related to Wizard auto-includes and blank prompts
- Fixed a couple issues related to deactivating extra networks in batch processing
- Speculative fix for an issue with nested if/else logic

</details>

<details><summary>9.15.2 - 31 August 2023</summary>

### Changed
- `[img2img]`: Updated for compatibility with WebUI v1.6.0
- `[zoom_enhance]`: Lowered the default `cfg_min` and `cfg_max` values for the new DPM++ 3M samplers to 2.0 and 5.0
- `[zoom_enhance]`: Improved support for `discard` mask mode
- Unprompted Template Editor: Updated for compatibility with WebUI v1.6.0
- Tested compatibility with WebUI v1.6.0 and updated compatibility blurb as such

### Fixed
- `[zoom_enhance]`: Fixed alignment issue related to `countour_padding`
- Wizard Templates: Fixed an issue related to HTML escape sequences with spaces
- Bodysnatcher 1.3.3: Now uses mask mode `discard` with `[zoom_enhance]` to ensure compatibility with `[txt2mask]`
- Bodysnatcher 1.3.3: Temporarily switched `[zoom_enhance]` to `_alt` mode as a workaround for ControlNet compatibility issue

</details>

<details><summary>9.15.1 - 8 August 2023</summary>

### Added
- Github form templates for bug reports and feature requests

### Fixed
- Fixed a potential crash related to the `[base_dir]` shortcode of the Wizard UI

</details>

<details><summary>9.15.0 - 7 August 2023</summary>

### Added
- Refresh buttons for Wizard Templates and Shortcodes
- Regional Prompter Buddy v0.0.2: New setting `region_delimiter` which lets you customize the term that separates each region (defaults to `BREAK`, but you may want to switch it to `AND` for Latent Couple)
- Regional Prompter Buddy v0.0.2: New setting `prompt_style` which determines the overall prompt structure, try setting it to `Basic` if you want to use this template without another extension
- New config setting `logging.deprecated_warnings`: Turn this off if you don't wish to see console messages about the use of deprecated or legacy code

### Changed
- Updated documentation

### Fixed
- `[img2pez]`: Workaround for conflict between `optim_utils.py` and WebUI batch processing

</details>

<details><summary>9.14.0 - 3 August 2023</summary>

### About
Unprompted v9.14.0 introduces support for custom functions, greatly improves flexibility of `[else]` statements, and perhaps most exciting of all: implements `[gpt]` for text autocompletion and summarization. Enjoy!

### Added
- New shortcode `[gpt]`: Autocompletes the content with a given GPT model (similar to "Magic Prompt" from Dynamic Prompts)
- New shortcode `[function]`: Contains arbitrary code that you can call at will
- New shortcode `[call]`: Allows you to execute a specific `[function]` or filepath
- `[else]`: Now supports `id` kwarg which lets you tie specific if/else statements together (thus the `[else]` block can appear anywhere in the script) - do this by matching the if block's `_else_id` kwarg with the else block's `id` kwarg
- `[call]`: Compatible with `[else]` if a function fails, if the filepath doesn't exist, or if either return the term `_false`
- New config setting `subdirectories.models`: determines the folder within your Unprompted directory to store various model files in
- New manual category: "For Programmers"

### Changed
- `[else]`: Improved comprehension of nested if/else statements
- `[file]`: Now considered a legacy shortcode in favor of `[call]`, but will remain available for a while due to widespread use
- Separated processing flow into new methods for the Unprompted object: `start()`, `cleanup()` and `after()`

### Fixed
- `[get]`: Fixed a crash related to the `_default` kwarg

</details>

<details><summary>9.13.3 - 1 August 2023</summary>

### Added
- `[zoom_enhance]`: Now supports `upscale_min` which is the minimum area that a selected mask must occupy in order to be eligible for enhancement, defaults to 0.03 (which is what it was previously hardcoded to)

### Changed
- `[zoom_enhance]`: The `upscale_min` value is specifically compared against the size of a 512x512 canvas
- `[zoom_enhance]`: Updated debug image names and log messages for clarity

### Fixed
- `[zoom_enhance]`: Fixed alignment issue related to using the `_alt` parg in txt2img mode

</details>

<details><summary>9.13.2 - 1 August 2023</summary>

### Added
- New special variable `sd_vae`: allows you to change the vae file programmatically, similar to `sd_model`

### Changed
- Unprompted will warn you if you try to `[get]` or `[set]` a deprecated variable
- Unprompted will warn you if you haven't renamed the extension folder for compatibility with other scripts
- The `populate_stable_diffusion_vars()` method has been renamed to `update_user_vars()`
- Updated documentation

### Fixed
- The `p_copy` object was not functioning correctly in the latest versions of the WebUI, so it has been replaced with direct modifications to the main `p` object instead, hopefully fixing recent issues with `[img2img]` and `[zoom_enhance]`
- Generating a shortcode with the Wizard no longer strips lora tags from text fields (escapes HTML characters)
- `[zoom_enhance]`: Fixed multiple issues that prevented the use of this shortcode outside of an after block (now you can!)

### Removed
- Retired the `log_error()`function in favor of `log.exception` which preserves the shortcode name as the logger id

</details>

<details><summary>9.13.1 - 30 July 2023</summary>

### Fixed
- Fixed an issue with updating Extra Networks during batch processing

</details>

<details><summary>9.13.0 - 30 July 2023</summary>

### About
This update improves compatibility with `batch_size`. You can now mix `batch_size` and `batch_count` to your heart's content, and Unprompted will parse each prompt independently. Give it a try!

### Added
- New shortcode `[seed]`: Allows you to call the `random.seed()` method at will, setting it to the `p.seed` value by default
- New config setting `stable_diffusion.batch_size_method`: allows you to determine how Unprompted will handle tasks where `batch_size` > 1
- New special variable `batch_size_index`: Returns the batch_size counter of the current process, e.g. if your batch_size is 4 this will return 0 to 3
- New proxy variable `batch_count_index`: Returns the same thing as `batch_index`, which may be removed in a future update as the name lacks specificity

### Changed

- Config setting `stable_diffusion.batch_method` renamed to `stable_diffusion.batch_count_method`
- The `stable_diffusion.batch_count_method` value of `legacy` has been renamed to `safe` for clarity
- The `stable_diffusion.batch_count_method` value of `none` has been renamed to `unify` for clarity
- Tested compatibility with WebUI v1.5.1 and updated compatibility blurb as such

</details>

<details><summary>9.12.0 - 30 July 2023</summary>

### Added
- New template `Regional Prompter Buddy v0.0.1`: This is an experimental template that streamlines and optimizes the prompt for use with the [Regional Prompter](https://github.com/hako-mikan/sd-webui-regional-prompter) extension (thank you to @hako-mikan for helping make this possible)
- `[after]`: Now handles the bypassing of specific extensions that have known compatibility issues
- `[after]`: Supports `allow_unsafe_scripts` parg to bypass the bypasser
- New config setting `logging.improve_alignment`: responsible for handling separation space between columns of console messages

### Changed
- Clipdrop SDXL Styles v0.0.2: Negative prompt terms will be appended to your existing negative prompt, rather than overwriting it
- The default label of a Wizard UI element has been changed from "Setting" to the variable name in titlecase format
- Added top border to Wizard "autoinclude" UI element
- Further improvements to formatting of console messages

### Fixed
- `[after]`: Bypasses the Regional Prompter extension as it was causing errors with additional img2img tasks
- `[zoom_enhance]`: It is now possible to chain together `[zoom_enhance]` blocks, at least in txt2img mode
- Fixed an issue with `single_seed` variable
- Fixed crash related to SDXL and hires fix

</details>

<details><summary>9.11.0 - 28 July 2023</summary>

### Added
- New Wizard template `Clipdrop SDXL Styles`: Clipdrop recently disclosed their prompt pre-processing terms for various SDXL presets (comic book, fantasy, etc) so I have adapted them to a simple Wizard UI
- `[img2img]`: Can now process multiple init images (better batch support)
- `[img2img]`: Now supports `batch_test` expression
- `[unset]`: Now supports pattern matching with `*` to delete multiple variables from memory, useful if you need to disable ControlNet for the `[after]` block e.g. `[unset cn_* controlnet_*]`
- `[zoom_enhance]`: Now supports `no_sync` parg which prevents updates to the `p` object, may help to ensure compatibility with other extensions

### Changed
- Adjusted a few console messages

### Fixed
- `[txt2mask]`: Fixed an issue with updating the `mode` variable at the end of the process
- Bodysnatcher v1.3.2: Unsets the ControlNet units for `[after]` processing

</details>

<details><summary>9.10.0 - 27 July 2023</summary>

### About
Unprompted v9.10.0 overhauls the logger and brings quality-of-life improvements for the newly-released SDXL. Congratulations to Stability AI for their incredible work!

### Added
- New example template `sdxl_refiner` that automatically refines the image via img2img (this is not the most efficient means of using the refiner, but I believe it's the best that A1111 supports at the time of writing)
- `[zoom_enhance]`: The default values of `upscale_width` and `upscale_height` will automatically become 1024 if you have an SDXL model loaded (otherwise 512)
- New special variable `sd_base`: returns the base type of the selected checkpoint, i.e. `sd1`, `sd2`, `sdxl` or `none`
- The logger has been implemented anew using Python's `logging` module
- The format and colors of the new logger are adopted from ControlNet to help ensure a consistent-looking console
- New setting `Config.stable_diffusion.controlnet_name` if for some reason your environment expects it to be something other than `sd-webui-controlnet`
- New setting `Config.logging.colors`: A dictionary of escape sequences that correspond to colors for the various logging levels
- New setting `Config.logging.format`: String that defines the structure of a log message
- New setting `Config.logging.file`: An optional filepath for writing log messages to disk
- New setting `Config.logging.filemode`: If writing log messages to disk, you can specify filemode `a` to append messages to the file or `w` to overwrite the existing file
- New setting `Config.logging.level`: This defines the lowest-priority messages you wish to see in your console, set it to `DEBUG` for verbose output
- New setting `Config.logging.use_colors`: Set to false if you hate colors

### Changed
- Hardcoded references to ControlNet location have been replaced with path returned by `modules.extensions`, which may allow CN variables to work with third-party forks of the WebUI (which are nevertheless considered unsupported by this extension - try them at your own risk)

### Fixed
- Template Editor: No longer creates an entire Unprompted object, as it only needed the object for its config-parsing capabilities

### Removed
- `[pix2pix_zero]`: This shortcode presented a dependency conflict with the `ultralytics` package required by [txt2mask]. I have decided to simply remove this shortcode given its legacy status.
- Config setting `log_contexts` superceded by the new setting `logging.level`
- The log contexts `SETUP` and `RESULT` do not have direct equivalents in the new logger and have been replaced with `INFO` level messages

</details>

<details><summary>9.9.0 - 25 July 2023</summary>

### Added
- `[array]`: Now accepts variable names as kwargs for updating array indexes dynamically, as in the case of a `[for]` loop
- New example template `batch_seeds_custom_step_size` that allows you to override the WebUI's behavior of incrementing the seed by 1 in a batch process

### Fixed
- Ensured compatibility with WebUI v1.5.0
- Hotfix for `batch_index` user variable handling

</details>

<details><summary>9.8.3 - 24 July 2023</summary>

### Changed
- Stable Diffusion variables will be synchronized with your Unprompted variables whenever an img2img task is called, including `[zoom_enhance]` and `[img2img]`
- Optimized `Unprompted.update_stable_diffusion_vars()` performance

</details>

<details><summary>9.8.2 - 24 July 2023</summary>

### Fixed
- Updated the batch processing code to fix compatibility with Extra Networks as well as the `templates.default` setting
- `[zoom_enhance]`: Fixed handling of `batch_index` when `batch_size` > 1

</details>

<details><summary>9.8.1 - 23 July 2023</summary>

### Fixed
- Hotfix for `sd_model` handling
- Hotfix for `batch_size` > 1 crash
- Updated documentation

</details>

<details><summary>9.8.0 - 22 July 2023</summary>

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
- Wizard Templates now support `[wizard accordion]` to group a collection of settings into a collapsible menu
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