import time
import queue
import threading
from scipy.io.wavfile import write
import numpy as np
import sounddevice as sd
import whisper


class stt(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sample_rate = 44100
        self.filename = r'D:\Excel Datasets\Manhattan\recording.wav'
        self.channels = 1
    def run(self):
        self.record()
    def record(self):
        q = queue.Queue()

        def callback(indata, frames, time, status):
            q.put(indata.copy())

        SILENCE_THRESHOLD = 100 # Volume below this is treated as silence
        SILENCE_SECONDS = 10 # Stop recording after 10 sec inactivity
        print('Waiting for audio...')
        last_speech_time = time.time()
        audio_recording = sd.InputStream(samplerate=self.sample_rate, channels=self.channels, dtype='int16', callback=callback)
        recorded_chunks = []
        with audio_recording:
            while True:
                try:
                    data = q.get(timeout=1)
                    recorded_chunks.append(data)
                except queue.Empty:
                    continue
                volume = np.abs(data).mean()
                if volume > SILENCE_THRESHOLD:
                    last_speech_time = time.time()
                if time.time() - last_speech_time > SILENCE_SECONDS:
                    print("Silence detected")
                    break
        print('Recording done')
        recording = np.concatenate(recorded_chunks, axis=0)
        write(self.filename, self.sample_rate, recording)
        print("done")
st = stt()
st.run()
