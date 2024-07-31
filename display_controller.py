# Compatibility with both CircuitPython 8.x.x and 9.x.x.
# Remove after 8.x.x is no longer a supported release.
try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire

import displayio
import adafruit_displayio_ssd1306
from switchboard_renderer import SwitchboardRenderer

class DisplayController:
    WIDTH = 128
    HEIGHT = 64

    def __init__(self, spi_bus, command, chip_select, reset):
        self._display_bus = FourWire(spi_bus, 
                                     command=command, 
                                     chip_select=chip_select, 
                                     reset=reset,
                                     baudrate=24_000_000)

        self.display = adafruit_displayio_ssd1306.SSD1306(self._display_bus, 
                                                          width=DisplayController.WIDTH, 
                                                          height=DisplayController.HEIGHT)

        # Main display group/context
        self.main_group = displayio.Group()
        self.display.root_group = self.main_group

        # To help with switchboard UI rendering
        self._switchboard_renderer = SwitchboardRenderer()
        self._is_switchboard_renderer_active = False

    @property
    def switchboard_renderer(self):
        return self._switchboard_renderer

    @property
    def is_switchboard_renderer_active(self):
        return self._is_switchboard_renderer_active        

    def set_switchboard_renderer_active(self, active):
        if active == self._is_switchboard_renderer_active:
            return

        self._is_switchboard_renderer_active = active

        if active:
            self._switchboard_renderer.add_to_group(self.main_group)
        else:
            self._switchboard_renderer.remove_from_group(self.main_group)