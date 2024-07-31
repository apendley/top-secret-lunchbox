# Most of this code came from todbot's excellent eighties_dystopia example at
# https://github.com/todbot/circuitpython-synthio-tricks/tree/main/examples/eighties_dystopia
# 
# I just packaged it up into this class so I could abuse it more easily across the game.
# 

###################################################### 
# Midi note mapping
######################################################
# A0  A#0  B0  C1  C#1  D1  D#1  E1  F1  F#1  G1  G#1
# 21  22   23  24  25   26  27   28  29  30   31  32

# A1  A#1  B1  C2  C#2  D2  D#2  E2  F2  F#2  G2  G#2
# 33  34   35  36  37   38  39   40  41  42   43  44

# A2  A#2  B2  C3  C#3  D3  D#3  E3  F3  F#3  G3  G#3
# 45  46   47  48  49   50  51   52  53  54   55  56

# A3  A#3  B3  C4  C#4  D4  D#4  E4  F4  F#4  G4  G#4
# 57  58   59  60  61   62  63   64  65  66   67  68

# A4  A#4  B4  C5  C#5  D5  D#5  E5  F5  F#5  G5  G#5
# 69  70   71  72  73   74  75   76  77  78   79  80

# A5  A#5  B5  C6  C#6  D6  D#6  E6  F6  F#6  G6  G#6
# 81  82   83  84  85   86  87   88  89  90   91  92

import synthio
import random
import ulab.numpy as numpy

class EightiesDystopia:
    DEFAULT_NOTES = (31, 32, 33)
    DEFAULT_NOTE_DURATION = 9000    

    def __init__(self, synth):
        self._synth = synth
        self._is_playing = False

        # Note pool
        self._notes = self.DEFAULT_NOTES
        self._note_duration = self.DEFAULT_NOTE_DURATION

        # how many voices for each note
        self._num_voices = 5

        # filter lowest frequency
        self._lpf_basef = 600

        # filter q
        self._lpf_resonance = 1.5

        # our oscillator waveform
        self._wave_saw = numpy.linspace(30000, -30000, num=512, dtype=numpy.int16)
        self._amp_env = synthio.Envelope(attack_level=1, sustain_level=1)        

        # set up the voices (aka "Notes" in synthio-speak) w/ initial values
        self._voices = []
        for i in range(self._num_voices):
            note = synthio.Note(frequency=0, envelope=self._amp_env, waveform=self._wave_saw)
            self._voices.append(note)

        # the LFO that modulates the filter cutoff
        self._lfo_filtermod = synthio.LFO(rate=0.05, scale=2000, offset=2000)

    def play(self, notes=None, note_duration=None):
        if notes is None:
            notes = self.DEFAULT_NOTES

        if note_duration is None:
            note_duration = self.DEFAULT_NOTE_DURATION

        self._notes = notes
        self._note_duration = note_duration

        if self._is_playing:
            # Force note switch on the next update
            self._next_note_time = 0
            return

        self._next_note_time = self._note_duration

        # we can't attach this directly to a filter input, so stash it in the blocks runner
        self._synth.blocks.append(self._lfo_filtermod)

        self._note = random.choice(self._notes)
        self._next_filtermod_time = 0

        # start the voices playing
        self._set_notes(self._note)
        self._synth.press(self._voices)
        self._is_playing = True

    def skip_to_next_note(self):
        # Force note switch on the next update
        self._next_note_time = 0

    def stop(self):
        if not self._is_playing:
            return

        # Free filtermod resources
        self._synth.release(self._voices)
        self._synth.blocks.remove(self._lfo_filtermod)
        self._is_playing = False

    def update(self, dt):
        if not self._is_playing:
            return

        # continuosly update filter, no global filter, so update each voice's filter
        for v in self._voices:
            v.filter = self._synth.low_pass_filter(self._lpf_basef + self._lfo_filtermod.value, self._lpf_resonance)

        self._next_filtermod_time += dt

        if self._next_filtermod_time >= 1000:
            self._next_filtermod_time = 0

            # randomly modulate the filter frequency ('rate' in synthio) to make more dynamic
            self._lfo_filtermod.rate = 0.01 + random.random() / 8
            # print("filtermod", self._lfo_filtermod.rate)

        # No point in changing notes if there's only one
        if len(self._notes) > 1:
            self._next_note_time -= dt    

            if self._next_note_time <= 0:
                self._next_note_time = self._note_duration

                # pick new note, but not one we're currently playing
                self._note = random.choice([n for n in self._notes if n != self._note])
                self._set_notes(self._note)
                # print("note", self._note, ["%3.2f" % v.frequency for v in self._voices] )

    # set all the voices to the "same" frequency (with random detuning)
    # zeroth voice is sub-oscillator, one-octave down
    def _set_notes(self, n):
        for voice in self._voices:
            # more valid if we move up the scale
            voice.frequency = synthio.midi_to_hz(n + random.uniform(0, 0.4))

        # bass note one octave down
        self._voices[0].frequency = self._voices[0].frequency/2