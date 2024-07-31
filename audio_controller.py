import audiobusio
import audiocore
import audiomixer
import synthio
import random
from helper import clamp
from eighties_dystopia import EightiesDystopia

class AudioController:
    def __init__(self, pin_clock, pin_word_select, pin_data):
        self.audio = audiobusio.I2SOut(pin_clock, pin_word_select, pin_data)
        self.synth = synthio.Synthesizer(channel_count=1, sample_rate=22050)

        self._mixer = audiomixer.Mixer(voice_count=2,
                                       channel_count=1, 
                                       sample_rate=22050, 
                                       buffer_size=1024*7)

        self.audio.play(self._mixer)
        self._mixer.voice[0].play(self.synth)

        # Initialize internal property to avoid updating mixer, since we're about to do it right after this anyway
        self._main_volume = 1.0

        # Initialize using public properties to update mixer
        self.synth_volume = self.default_synth_volume
        self.wave_volume = 0.25

        # Plug/unplug sfx. Two additional pitch-shifted versions are used 
        # for each effect and will be chosen from randomly to help prevent monotony 
        # since these SFX are used *a lot*.
        self._plug_sfx = [
            "audio/maximize_003_lo.wav",
            "audio/maximize_003.wav",
            "audio/maximize_003_hi.wav"
        ]

        self._unplug_sfx = [
            "audio/minimize_003_lo.wav",
            "audio/minimize_003.wav",
            "audio/minimize_003_hi.wav"
        ]

        # Eighties dystopia soundtrack control
        self._eighties_dystopia = EightiesDystopia(self.synth)

    def update(self, dt):
        self._eighties_dystopia.update(dt)

    @property
    def main_volume(self):
        return self._main_volume

    @main_volume.setter
    def main_volume(self, v):
        self._main_volume = clamp(v, 0.0, 1.0)
        self.synth_volume = self._synth_volume
        self.wave_volume = self._wave_volume

    @property
    def default_synth_volume(self):
        return 0.05

    @property
    def low_synth_volume(self):
        return 0.02

    @property
    def synth_volume(self):
        return self._synth_volume

    @synth_volume.setter
    def synth_volume(self, v):
        self._synth_volume = v
        self._mixer.voice[0].level = v * self._main_volume

    @property
    def wave_volume(self):
        return self._wave_volume

    @wave_volume.setter
    def wave_volume(self, v):
        self._wave_volume = v
        self._mixer.voice[1].level = v * self._main_volume

    @property
    def is_playing_wave_file(self):
        return self._mixer.voice[1].playing

    def play_wave_file(self, filename, loop=False):
        file = open(filename, "rb")
        wav = audiocore.WaveFile(file)
        self._mixer.voice[1].play(wav, loop=loop)

    def stop_wave_file(self):
        if self._mixer.voice[1].playing:
            self._mixer.voice[1].stop()

    def play_connection_sfx(self):
        index = random.randrange(0, len(self._plug_sfx))
        self.play_wave_file(self._plug_sfx[index])

    def play_disconnection_sfx(self):
        index = random.randrange(0, len(self._unplug_sfx))
        self.play_wave_file(self._unplug_sfx[index])

    @property
    def eighties_dystopia(self):
        return self._eighties_dystopia