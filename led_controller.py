import neopixel
import helper

class LEDController:

    # Make the switchboard LEDs less eye-blistering by default
    DEFAULT_SWITCHBOARD_BRIGHTNESS = 32

    # The arcade button LED uses a different color order than the switchboard LEDs
    def grb_to_rgb(color):
        return (color[1], color[0], color[2])    

    def __init__(self, pin_name):
        self._strip = neopixel.NeoPixel(pin_name, 11, pixel_order=neopixel.RGB, brightness=1.0, auto_write=False)
        self._strip.show()
        self._needs_sync = False

    def update(self):
        if self._needs_sync:
            self._strip.show()
            self._needs_sync = False            

    def set_button_color(self, color):
        color = LEDController.grb_to_rgb(color)
        scaled_color = helper.gamma8(color)
        self._strip[0] = scaled_color
        self._needs_sync = True

    def set_switchboard_color(self, switchboard_index, color, brightness=DEFAULT_SWITCHBOARD_BRIGHTNESS):
        if switchboard_index < 5:
            switchboard_index = 4 - switchboard_index

        led_index = switchboard_index + 1
        scaled_color = helper.color_scale(color, brightness)
        scaled_color = helper.gamma8(scaled_color)
        self._strip[led_index] = scaled_color
        self._needs_sync = True

    def fill_switchboard_color(self, color, brightness=DEFAULT_SWITCHBOARD_BRIGHTNESS):
        scaled_color = helper.color_scale(color, brightness)
        scaled_color = helper.gamma8(scaled_color)

        for led_index in range(1, 11):
            self._strip[led_index] = scaled_color

        self._needs_sync = True