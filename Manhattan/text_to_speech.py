import pyttsx3

#Later will be migrated to Piper TTS
def audio(extracted_text: object) -> object:
    engine = pyttsx3.init()
    engine.setProperty('rate', 120)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(extracted_text)
    engine.runAndWait()
    if engine._inLoop:
        engine.endLoop()
