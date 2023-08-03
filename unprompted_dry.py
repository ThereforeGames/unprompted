# Unprompted by Therefore Games. All Rights Reserved.
# https://patreon.com/thereforegames
# https://github.com/ThereforeGames/unprompted

from lib_unprompted.shared import Unprompted

# Main object
Unprompted = Unprompted()


def do_unprompted(string):
	# Reset vars
	Unprompted.shortcode_user_vars = {}

	# TODO: We may want to declare our own log level for the result message
	Unprompted.log.info(Unprompted.start(string))

	# Cleanup routines
	Unprompted.cleanup()


while True:
	try:
		command = input("(INPUT) Unprompted string:")
		do_unprompted(command)
	except Exception as e:
		Unprompted.log.exception("Exception occurred.")