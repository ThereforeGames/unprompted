from modules import script_callbacks
from modules import shared


def on_ui_settings():
	section = "unprompted", "Unprompted"
	shared.opts.add_option(key="unprompted_rerun_extra_networks", info=shared.OptionInfo(False, label="Re-process extra networks after Unprompted is finished (WIP - this is not yet functional!)", section=section))

def initialize():
	script_callbacks.on_ui_settings(on_ui_settings)
