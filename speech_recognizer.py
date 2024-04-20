import os
import threading
import time
from threading import Thread

import azure.cognitiveservices.speech as speechsdk

speech_region = os.getenv("SPEECH_REGION")
speech_key = os.getenv("SPEECH_KEY")

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
speech_config.speech_recognition_language = "en-US"


# for intentrecognition https://github.com/Azure-Samples/cognitive-services-speech-sdk/blob/master/quickstart/python/intent-recognition/quickstart.py
class SpeechRecognizer:
    def __init__(self, file_path: str) -> None:
        audio_config = speechsdk.audio.AudioConfig(filename=file_path)
        self.is_converting = False
        self.speech_text = []
        self.speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )

    def _stop_cb(self, evt):
        print("CLOSING on {}".format(evt))
        self.speech_recognizer.stop_continuous_recognition()
        self.is_converting = False

    def _update_recognized_text(self, evt):
        self.speech_text.append(evt.result.text)

    @property
    def converted_text(self):
        return self.speech_text

    def convert(self):
        self.speech_recognizer.start_continuous_recognition()
        while self.is_converting:
            time.sleep(0.5)

    def start_converting(self):
        if self.is_converting:
            return
        self.is_converting = True
        self.speech_text = []
        # speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
        self.speech_recognizer.recognized.connect(
            lambda evt: self._update_recognized_text(evt)
        )
        self.speech_recognizer.session_started.connect(
            lambda evt: print("SESSION STARTED: {}".format(evt))
        )
        self.speech_recognizer.session_stopped.connect(
            lambda evt: print("SESSION STOPPED {}".format(evt))
        )
        self.speech_recognizer.canceled.connect(
            lambda evt: print("CANCELED {}".format(evt))
        )
        self.speech_recognizer.session_stopped.connect(lambda evt: self._stop_cb(evt))
        self.speech_recognizer.canceled.connect(lambda evt: self._stop_cb(evt))
        Thread(target=self.convert).start()
