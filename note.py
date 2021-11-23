import numpy as np
import simpleaudio
class Harmonic:
    def __init__(self, multiple, magnitude):
        self.multiple = multiple
        self.magnitude = magnitude

class Instrument:
    sample_rate = 44100
    max_time = 5
    def __init__(self, harmonics=[], attack=0.0, decay=0.0, sustain=1.0, release=0.0):
        self.__attack = attack
        self.__decay = decay
        self.__sustain = sustain
        self.__release = release
        self.harmonics = harmonics
        self._generate_time_vector()
        self.generate_envelope()

    def generate_envelope(self):
        self.attack_slope = np.linspace(0,1, int(self.__attack*self.sample_rate))
        self.decay_slope = np.linspace(1,self.__sustain, int(self.__decay*self.sample_rate))
        self.release_slope = np.linspace(self.__sustain,0, int(self.__release*self.sample_rate))

    def _generate_time_vector(self):
        self._time = np.linspace(0,self.max_time, int(self.max_time*self.sample_rate))

    def add_harmonic(self, harmonic):
        self.harmonics.append(harmonic)

    def set_attack(self, attack):
        self.__attack = attack
        self.generate_envelope()

    def set_decay(self, decay):
        self.__decay = decay
        self.generate_envelope()

    def set_sustain(self, sustain):
        self.__sustain = sustain
        self.generate_envelope()

    def set_release(self, release):
        self.__release = release
        self.generate_envelope()

    def note(self, freq_hz, time_s, volume_db):
        if time_s > self.max_time:
            self.max_time = time_s + self.__release
            self._generate_time_vector()

        t = self._time[:int((time_s+self.__release)*self.sample_rate)]
        f = np.cos(2*np.pi*freq_hz*t)                                                     
        for mult, mag in self.harmonics:
            f = f + mag * np.cos(2*np.pi*freq_hz*mult*t)

        f = f * 10**(volume_db/10)

        attack_samps = f[:len(self.attack_slope)]
        decay_samps = f[len(self.attack_slope):len(self.attack_slope)+len(self.decay_slope)]
        sustain_samps = f[len(self.attack_slope) + len(self.decay_slope):int(self.sample_rate*time_s)]
        release_samps = f[int(self.sample_rate*time_s):]
        #print(f'{len(f)}')
        #print(f'{len(attack_samps)}, {len(decay_samps)}, {len(sustain_samps)}, {len(release_samps)}')
        A = attack_samps * self.attack_slope[:len(attack_samps)]
        D = decay_samps * self.decay_slope[:len(decay_samps)]
        S = sustain_samps * self.__sustain
        R = release_samps[:len(self.release_slope)] * self.release_slope[:len(release_samps)]
        return np.concatenate([A,D,S,R])

if __name__ == "__main__":
    x = Instrument([(1.006, 1.0), (2,0.9), (3,0.7), (5,0.5), (9,0.5)], 0.05, 0.1, 0.9, 0.5)

    A = x.note(400, 1.5, 0)
    Cs = x.note(500, 1.5, 0)
    E = x.note(600, 1.5, 0)
    O = x.note(800, 1.5, 0)
    G = x.note(700, 1.5, 0)
    B = x.note(900, 1.5, 0)
    C = x.note(1100, 1.5, 0)
    note = A + Cs + E + O
    note *= 32767 / max(abs(note))
    note = note.astype(np.int16)
    play = simpleaudio.play_buffer(note, 1, 2, 44100)
    play.wait_done()
