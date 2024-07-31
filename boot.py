import board
import digitalio
import storage

# Top left jack to bottom right jack (D10 -> D25)
jack_output = digitalio.DigitalInOut(board.D10)
jack_output.direction = digitalio.Direction.OUTPUT
jack_output.value = False

jack_input = digitalio.DigitalInOut(board.D25)
jack_input.direction = digitalio.Direction.INPUT
jack_input.pull = digitalio.Pull.UP

input_valid_1 = (jack_input.value == False)
jack_input.deinit()
jack_output.deinit()

# Top right jack to bottom left jack (A1 -> A0)
jack_output = digitalio.DigitalInOut(board.A1)
jack_output.direction = digitalio.Direction.OUTPUT
jack_output.value = False

jack_input = digitalio.DigitalInOut(board.A0)
jack_input.direction = digitalio.Direction.INPUT
jack_input.pull = digitalio.Pull.UP

input_valid_2 = (jack_input.value == False)

# Enter edit mode if connections are valid
is_edit_mode = input_valid_1 and input_valid_2

if not is_edit_mode:
    storage.disable_usb_drive()
