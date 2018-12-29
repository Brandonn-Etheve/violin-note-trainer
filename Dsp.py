from scipy import signal
import threading

import pyaudio  # package portaudio-devel
import numpy as np
import matplotlib.pyplot as plt
from drawnow import drawnow


class Dsp:


    def __init__(self):
        self.notes_name = ["do0", "do0# / ré0b", "ré0", "ré0# / mi0b", "mi0", "fa0", "fa0# / sol0b", "sol0", "sol0# / la0b",
                      "la0", "la0# / si0b", "si0", "do1", "do1# / ré1b", "ré1", "ré1# / mi1b", "mi1", "fa1",
                      "fa1# / sol1b", "sol1", "sol1# / la1b", "la1", "la1# / si1b", "si1", "do2", "do2# / ré2b", "ré2",
                      "ré2# / mi2b", "mi2", "fa2", "fa2# / sol2b", "sol2", "sol2# / la2b", "la2", "la2# / si2b", "si2",
                      "do3", "do3# / ré3b", "ré3", "ré3# / mi3b", "mi3", "fa3", "fa3# / sol3b", "sol3", "sol3# / la3b",
                      "la3", "la3# / si3b", "si3", "do4", "do4# / ré4b", "ré4", "ré4# / mi4b", "mi4", "fa4",
                      "fa4# / sol4b", "sol4", "sol4# / la4b", "la4", "la4# / si4b", "si4", "do5", "do5# / ré5b", "ré5",
                      "ré5# / mi5b", "mi5", "fa5", "fa5# / sol5b", "sol5", "sol5# / la5b", "la5", "la5# / si5b", "si5",
                      "do6", "do6# / ré6b", "ré6", "ré6# / mi6b", "mi6", "fa6", "fa6# / sol6b", "sol6", "sol6# / la6b",
                      "la6", "la6# / si6b", "si6", "do7", "do7# / ré7b", "ré7", "ré7# / mi7b", "mi7", "fa7",
                      "fa7# / sol7b", "sol7", "sol7# / la7b", "la7", "la7# / si7b", "si7", "do8", "do8# / ré8b", "ré8",
                      "ré8# / mi8b", "mi8", "fa8", "fa8# / sol8b", "sol8", "sol8# / la8b", "la8", "la8# / si8b", "si8",
                      "do9", "do9# / ré9b", "ré9", "ré9# / mi9b", "mi9", "fa9", "fa9# / sol9b", "sol9", "sol9# / la9b",
                      "la9", "la9# / si9b", "si9"]

        self.notes_frequency = [32.7, 34.65, 36.71, 38.89, 41.2, 43.65, 46.25, 49, 51.91, 55, 58.27, 61.74, 65.41, 69.3,
                           73.42, 77.78, 82.41, 87.31, 92.5, 98, 103.8, 110, 116.5, 123.5, 130.8, 138.6, 146.8, 155.6,
                           164.8, 174.6, 185, 196, 207.7, 220, 233.1, 246.9, 261.6, 277.2, 293.7, 311.1, 329.6, 349.2,
                           370, 392, 415.3, 440, 466.2, 493.9, 523.3, 554.4, 587.3, 622.3, 659.3, 698.5, 740, 784,
                           830.6, 880, 932.3, 987.8, 1046.5, 1108.7, 1174.7, 1244.5, 1318.5, 1396.9, 1480, 1568, 1661.2,
                           1760, 1864.7, 1975.5, 2093, 2217.5, 2349.3, 2489, 2637, 2793.8, 2960, 3136, 3322.4, 3520,
                           3729.3, 3951.1, 4186, 4434.9, 4698.6, 4978, 5274, 5587.7, 5919.9, 6271.9, 6644.9, 7040,
                           7458.6, 7902.1, 8372, 8869.8, 9397.3, 9956.1, 10548, 11175, 11840, 12544, 13290, 14080,
                           14917, 15804, 16744, 17740, 18795, 19912, 21096, 22351, 23680, 25088, 26580, 28160, 29834,
                           31609]

        self.num_samples = 16384  # number of data points to read at a time
        self.RATE = 44100  # time resolution of the recording device (Hz)

        self.p = pyaudio.PyAudio()  # start the PyAudio class
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.RATE, input=True,
                        frames_per_buffer=self.num_samples)  # uses default input device

        self.frequency = []
        f = 0
        self.f_step = self.RATE / self.num_samples

        for i in range(0, int(self.num_samples / 2)):
            self.frequency.append(f)
            f += self.f_step

        self.on = True
        self.process = True

        self.note = ""
        self.note_index = 0
        self.note_right = ""
        self.note_left = ""

        self.closeness = 0
        self.strongestFrequency = 0
        self.intensity = 0
        self.targetFrequency = 0
        self.targetFrequency_right = 0
        self.targetFrequency_left = 0
        self.frequencies_intensities = []


        self.thread1 = threading.Thread(target=self.processAudio, args=())
        self.thread1.setDaemon(False)
        self.thread1.start()



    def find_nearest_index(self, array, value):
        array = np.asarray(array)
        return (np.abs(array - value)).argmin()

    def get_closeness(self, index, value):
        if value > self.notes_frequency[index] :
            output = abs(self.notes_frequency[index + 1] - value)
            output = (output * 100) / (self.notes_frequency[index + 1] - self.notes_frequency[index])
            output = abs(100-output)

        else:
            output = abs(self.notes_frequency[index - 1] - value)
            output = (output * 100) / (self.notes_frequency[index] - self.notes_frequency[index - 1])
            output = abs(100-output)*-1

        return output


    def make_fig(self):
        # plt.scatter(x, y)  # I think you meant this
        plt.xlim((150, 600))
        plt.plot(self.frequency, self.frequencies_intensities)

    #
    def get_first_strongestFrequency_intensity_index(self, min_intensity):
        for i in range(1,len(self.frequencies_intensities)-1):
            if self.frequencies_intensities[i] > min_intensity:
                for j in range(i, len(self.frequencies_intensities) - 1):
                    if self.frequencies_intensities[j] < min_intensity:
                        return round((i+j)/2)



    def processAudio(self):
        # create a numpy array holding a single read of audio data
        note_number = len(self.notes_name)

        while self.on:
            if self.process:
                data = np.fromstring(self.stream.read(self.num_samples), dtype=np.int16)
                data_fft = np.fft.fft(data)
                # data_fft = data
                data_fft = data_fft[0:int(self.num_samples / 2)]
                self.frequencies_intensities = np.abs(data_fft)
                self.frequencies_intensities /= 32767
                # drawnow(self.make_fig)

                strongestFrequency_intensity_index = self.get_first_strongestFrequency_intensity_index(0.1)

                if strongestFrequency_intensity_index is not None:

                    self.strongestFrequency = self.frequency[strongestFrequency_intensity_index]
                    self.intensity = self.frequencies_intensities[strongestFrequency_intensity_index]
                    self.note_index = self.find_nearest_index(self.notes_frequency, self.strongestFrequency)
                    self.note = self.notes_name[self.note_index]
                    self.closeness = self.get_closeness(self.note_index, self.strongestFrequency)
                    if self.note_index > 0:
                        self.note_left = self.notes_name[self.note_index-1]
                        self.targetFrequency_left = self.notes_frequency[self.note_index-1]
                    else:
                        self.note_left = "--"
                        self.targetFrequency_left = 0

                    if self.note_index < note_number-1:
                        self.note_right = self.notes_name[self.note_index+1]
                        self.targetFrequency_right = self.notes_frequency[self.note_index+1]

                    else:
                        self.note_right = "--"
                        self.targetFrequency_right = 0

                    self.targetFrequency = self.notes_frequency[self.note_index]
                # if strongestFrequency_intensity > 400:
                # print(current_milli_time()-start)
                # plt.plot(frequencies)
                # plt.show()
                # print(data)

    def __del__(self):
        # close the stream gracefully
        self.on = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

