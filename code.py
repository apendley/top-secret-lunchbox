# First import only what we need so we can respond to being powered on ASAP.
# For now, we'll turn all of the switchboard LEDs blue
import board
import digitalio
import displayio
from led_controller import LEDController

# get rid of whatever is currently on the display
displayio.release_displays()

# Enable power to sound, neopixels, etc
ext_power = digitalio.DigitalInOut(board.EXTERNAL_POWER)
ext_power.switch_to_output(value=True)

# Set up led controller and draw initial LED state
led_controller = LEDController(board.EXTERNAL_NEOPIXELS)
led_controller.set_button_color((0, 0, 255))
led_controller.fill_switchboard_color((0, 0, 255))
led_controller.update()

# Now import everything else
import gc

from adafruit_ticks import ticks_ms, ticks_diff
from adafruit_debouncer import Debouncer

from adafruit_ht16k33.segments import Seg7x4

from audio_controller import AudioController
from display_controller import DisplayController

from switchboard import Switchboard

from device import Device
from application import Application
import scenes
from game_state import GameState

# Set up SPI and I2C busses
i2c = board.I2C()
spi = board.SPI()

# Set up OLED
display = DisplayController(spi, command=board.D6, chip_select=board.D5, reset=board.D9)

# Set up seven segment display
seven_seg = Seg7x4(i2c, auto_write=True)
seven_seg.auto_write = False

# set up switchboard
switchboard = Switchboard(board.D10, board.D11, board.D12, board.D13, board.A0,
                          board.A1, board.A2, board.A3, board.D24, board.D25)

# set up arcade button
arcade_button_io = digitalio.DigitalInOut(board.EXTERNAL_BUTTON)
arcade_button_io.direction = digitalio.Direction.INPUT
arcade_button_io.pull = digitalio.Pull.UP
arcade_button = Debouncer(arcade_button_io)

# Create game state
game_state = GameState()

# For easier testing
# game_state.set_puzzle_solved(0, True)
# game_state.set_puzzle_solved(1, True)
# game_state.set_puzzle_solved(2, True)
# game_state.set_puzzle_solved(3, True)
# game_state.set_puzzle_solved(4, True)

# Set up audio at the last possible moment, to prevent crackles during importing/setup
audio = AudioController(board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DATA)

# Now put everything together into the "device" object
device = Device(led_controller=led_controller,
                switchboard=switchboard,
                display_controller=display,
                seven_seg=seven_seg,
                audio_controller=audio,
                arcade_button=arcade_button,
                game_state=game_state)

# Finally, create the game object, set it up, and run it
application = Application(device)
application.goto_scene(scenes.BOOT)

# For easier testing
# application.goto_scene(scenes.MENU)
# application.goto_scene(scenes.COLOR_MATCH)
# application.goto_scene(scenes.SYMBOL_MATCH)
# application.goto_scene(scenes.REACTION_MATCH)
# application.goto_scene(scenes.FIND_SUM)
# application.goto_scene(scenes.GREMLIN)
# application.goto_scene(scenes.WIN_GAME)

# ----------------------------
# Debug info
# ----------------------------
frame_count = 0
frame_accum = 0
last_fps = 0

def debug_update_fps(dt):
    global frame_count, frame_accum, fps_text_area

    frame_count += 1
    frame_accum += dt

    if frame_accum >= 1000:
        avg_time = frame_accum / frame_count        
        last_fps = 1000 / avg_time

        print(f"avg time: {avg_time}ms", "  avg fps:", int(last_fps), "  free mem:", gc.mem_free())

        frame_count = 0
        frame_accum -= 1000

# ----------------------------
# Main loop
# ----------------------------
last_ticks = ticks_ms()

while True:
    now = ticks_ms()
    dt = ticks_diff(now, last_ticks)
    last_ticks = now

    # debug_update_fps(dt)
    application.update(dt)
