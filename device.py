
class Device:
    def __init__(self, 
                 led_controller, 
                 switchboard, 
                 display_controller,
                 seven_seg,
                 audio_controller,
                 arcade_button,
                 game_state):
        self.led_controller = led_controller
        self.switchboard = switchboard
        self.display_controller = display_controller
        self.seven_seg = seven_seg
        self.audio_controller = audio_controller
        self.arcade_button = arcade_button
        self.game_state = game_state