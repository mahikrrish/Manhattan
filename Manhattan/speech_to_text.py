import time
import queue
import threading
from scipy.io.wavfile import write
import numpy as np
import sounddevice as sd
# model = Model(r'D:\Excel Datasets\Manhattan\vosk-model-en-us-0.42-gigaspeech')
# def recognition():
#     """
#         Offline Speech Recognition using Vosk and SoundDevice.
#
#         ```
#         Purpose
#         -------
#         Captures audio from the system microphone, detects speech,
#         converts speech to text using the Vosk speech recognition model,
#         and stops recording after a configurable period of silence.
#
#         Design Decisions
#         ----------------
#
#         1. Vosk
#            - Fully offline speech recognition.
#            - No internet connection required.
#            - Chosen over cloud APIs for privacy and local execution.
#
#         2. SoundDevice
#            - Replaces PyAudio.
#            - Easier installation on modern Python versions.
#            - Works directly with microphone devices.
#
#         3. FRAME_RATE = 16000
#            - Most Vosk models are trained for 16 kHz audio.
#            - Using 16 kHz improves recognition compatibility and accuracy.
#            - Must match both the recognizer and microphone stream.
#
#         4. blocksize = 8000
#            - Audio is processed in chunks.
#            - 8000 samples at 16000 Hz represents approximately
#              0.5 seconds of audio.
#            - Large enough for efficient processing while still
#              providing responsive recognition.
#
#         5. SILENCE_THRESHOLD = 100
#            - Average audio volume below this value is considered silence.
#            - Determined experimentally.
#            - May require adjustment depending on microphone sensitivity
#              and ambient noise.
#
#         6. SILENCE_SECONDS = 10
#            - Recording automatically stops after 10 seconds
#              without detected speech.
#            - Prevents infinite listening loops.
#            - Intended as a user inactivity timeout.
#
#         Recognition Flow
#         ----------------
#
#         Microphone
#             ↓
#         SoundDevice Stream
#             ↓
#         Audio Queue
#             ↓
#         Volume Analysis
#             ↓
#         Silence Detection
#             ↓
#         Vosk Recognition
#             ↓
#         Final Text Output
#
#         Queue Usage
#         -----------
#         SoundDevice callback threads should remain lightweight.
#
#         The callback only pushes audio data into a Queue.
#
#         The main thread:
#             - retrieves audio from the Queue
#             - performs recognition
#             - performs silence detection
#
#         This prevents microphone dropouts and callback blocking.
#
#         Silence Detection Logic
#         -----------------------
#
#         If:
#             volume > SILENCE_THRESHOLD
#
#         then:
#             last_speech_time = current time
#
#         If:
#             current_time - last_speech_time > SILENCE_SECONDS
#
#         then:
#             stop listening
#
#         This allows:
#             - normal pauses during speech
#             - automatic termination after user finishes speaking
#
#         Model Loading
#         -------------
#
#         The Vosk model is loaded globally:
#
#             model = Model(...)
#
#         instead of inside recognition()
#
#         Reason:
#             Vosk models are large and expensive to load.
#             Loading once during application startup significantly
#             improves response time.
#
#         Future Improvements
#         -------------------
#
#         Possible enhancements:
#
#         - Dynamic silence threshold calibration
#         - Voice activity detection (VAD)
#         - Wake-word support
#         - Streaming partial results to GUI
#         - Automatic punctuation restoration
#         - Whisper/Faster-Whisper backend option
#         - Multiple language support
#
#         Returns
#         -------
#         str
#             Recognized speech converted to text.
#         """
#     FRAME_RATE = 16000 # Vosk recommended sample rate
#     print('Starting Model')
#
#     rec = KaldiRecognizer(model, FRAME_RATE)
#     rec.SetWords(True)
#     print('Recognizer Activated')
#
#     q = queue.Queue()
#
#     def callback(indata, frames, time, status):
#         q.put(bytes(indata))
#     SILENCE_THRESHOLD = 100 # Volume below this is treated as silence
#     SILENCE_SECONDS = 10 # Stop recording after 10 sec inactivity
#     with sd.RawInputStream(
#         samplerate=FRAME_RATE,
#         blocksize=8000,
#         dtype="int16",
#         channels=1,
#         callback=callback
#     ):
#         print('Waiting for audio...')
#         last_speech_time = time.time()
#         text = ''
#         while True:
#             try:
#                 data = q.get(timeout=1)
#             except queue.Empty:
#                 continue
#             audio = np.frombuffer(data, dtype=np.int16)
#             volume = np.abs(audio).mean()
#             if volume > SILENCE_THRESHOLD:
#                 last_speech_time = time.time()
#             if time.time() - last_speech_time > SILENCE_SECONDS:
#                 print("Silence detected")
#                 break
#             if rec.AcceptWaveform(data):
#                 result = json.loads(rec.Result())
#                 text += ' ' + result["text"] + ' '
#     final_text = json.loads(rec.FinalResult())
#     text += ' ' + final_text['text']
#     return text.strip()

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
st.record()
