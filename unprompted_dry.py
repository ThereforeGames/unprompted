# Unprompted by Therefore Games. All Rights Reserved.
# https://patreon.com/thereforegames
# https://github.com/ThereforeGames/unprompted

from lib.shared import Unprompted

# Main object
Unprompted = Unprompted()

def do_unprompted(string):
	# Reset vars
	Unprompted.shortcode_user_vars = {}

	Unprompted.log(Unprompted.process_string(string),False,"RESULT")

	# Cleanup routines
	Unprompted.log("Entering cleanup routine...",False)
	for i in Unprompted.cleanup_routines:
		Unprompted.shortcode_objects[i].cleanup()

while True:
	try:
		command = input("(INPUT) Unprompted string:")
		do_unprompted(command)
	except ValueError: print("ValueError occurred.")
