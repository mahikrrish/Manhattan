"""
speech_to_text.py

Speech recognition component for the Manhattan AI Assistant.

This module captures microphone audio, performs silence-based
recording termination, preprocesses the recorded waveform,
and generates text transcriptions using OpenAI Whisper.

Current Architecture:

    Microphone
        ↓
    SoundDevice InputStream
        ↓
    Chunk Collection
        ↓
    Silence Detection
        ↓
    NumPy Waveform Processing
        ↓
    Whisper Base
        ↓
    Transcribed Text

Author:
    Krishna Mahidhar

Project:
    Manhattan - Offline AI Assistant
"""

import time
import queue
import threading
import numpy as np
import sounddevice as sd
import whisper


class SpeechRecognition(threading.Thread):
    """
        Speech-to-Text (STT) module for the Manhattan AI Assistant.

        This class records audio from the system microphone, automatically
        terminates recording after a configurable period of silence, converts
        the captured audio into a Whisper-compatible waveform, and generates
        a text transcription using OpenAI Whisper.

        Features:
        - Real-time microphone recording
        - Silence-based recording termination
        - Automatic audio preprocessing
        - Direct ndarray-to-Whisper transcription
        - Basic microphone error handling

        Attributes:
            sample_rate (int):
                Recording sample rate in Hz. Whisper performs best at 16 kHz.

            channels (int):
                Number of microphone channels to record.

            attempt (int):
                Retry counter used during microphone initialization failures.

            model:
                Loaded Whisper model instance reused for all transcriptions.
        """
    def __init__(self):
        """
            Initialize the speech recognition module.

            Loads the Whisper Base model into memory and configures
            microphone recording parameters.

            Loading the model during initialization avoids the overhead
            of reloading the model for every transcription request.
            """
        threading.Thread.__init__(self)
        self.sample_rate = 16000
        self.channels = 1
        self.attempt = 1
        self.model = whisper.load_model('base')
    def run(self):
        """
            Entry point for the speech recognition thread.

            Starts the audio recording process and triggers the
            speech-to-text pipeline.

            Returns:
                None
            """
        self.record()
    def record(self):
        """
            Record microphone audio until prolonged silence is detected.

            Audio is captured in small chunks using a SoundDevice
            InputStream callback. Recording automatically stops when
            no speech activity is detected for the configured silence
            duration.

            Workflow:
                1. Initialize microphone stream.
                2. Continuously collect audio chunks.
                3. Monitor audio volume levels.
                4. Detect silence timeout.
                5. Combine all chunks into a single waveform.
                6. Convert waveform into Whisper-compatible format.
                7. Forward audio for transcription.

            Raises:
                sounddevice.PortAudioError:
                    Raised when microphone initialization fails or
                    audio devices are unavailable.

            Returns:
                None
            """
        q = queue.Queue()

        def callback(indata, frames, time, status):
            """
                SoundDevice callback executed whenever a new audio
                buffer is available.

                Parameters:
                    indata (numpy.ndarray):
                        Audio samples received from the microphone.

                    frames (int):
                        Number of frames contained in the current buffer.

                    time:
                        Timing information provided by SoundDevice.

                    status:
                        Stream status flags indicating underflow,
                        overflow, or other stream conditions.

                Returns:
                    None
                """
            q.put(indata.copy())

        silence_threshold = 100  # Volume below this is treated as silence
        silence_seconds = 10  # Stop recording after 10 sec inactivity
        if self.attempt == 1:
            print('Waiting for audio...')
        # add time, attempt count for performance to MySQL
        last_speech_time = time.time()
        try:
            audio_recording = sd.InputStream(samplerate=self.sample_rate, channels=self.channels,
                                             dtype='int16', callback=callback)
            recorded_chunks = []
            with audio_recording:
                while True:
                    try:
                        data = q.get(timeout=1)
                        recorded_chunks.append(data)
                    except queue.Empty:
                        continue
                    volume = np.abs(data).mean()
                    if volume > silence_threshold:
                        last_speech_time = time.time()
                    if time.time() - last_speech_time > silence_seconds:
                        print("Silence detected")
                        break
            print('Recording done')
            # add time again to record 'recording' end time to MySQL
            recording = np.concatenate(recorded_chunks, axis=0)
            self.transcription(recording.flatten().astype(np.float32)/32768.0)
            # write(self.filename, self.sample_rate, recording)
            # # add time to record  write end time to MySQL
            # print("done")
        except sd.PortAudioError as e:
            if 'Invalid number of channels' in str(e):
                if self.attempt <= 2:
                    self.channels = 1
                    self.attempt += 1
                    self.record()
            elif 'Device unavailable' in str(e):
                print(sd.query_devices('Audio device', 'input'))
    def transcription(self, recording):
        """
            Convert recorded audio into text using Whisper.

            The method accepts a normalized mono waveform stored
            as a NumPy ndarray and submits it directly to the
            Whisper Base model for transcription.

            Parameters:
                recording (numpy.ndarray):
                    One-dimensional float32 waveform normalized
                    to the range [-1.0, 1.0].

            Returns:
                str:
                    Whisper-generated transcription.

            Output:
                Prints the Whisper transcription result to the console.

            Notes:
                Audio must be preprocessed before calling this method:

                - Flattened to a 1-D waveform
                - Converted to float32
                - Normalized by dividing by 32768.0

                Example:

                recording.flatten().astype(np.float32) / 32768.0
            """
        result = self.model.transcribe(recording)
        return result['text']
