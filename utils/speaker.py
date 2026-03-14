import pyttsx3

class AgentSpeaker:
    def __init__(self):
        # Initialize the offline text-to-speech engine
        self.engine = pyttsx3.init()
        
        # Slow down the reading speed slightly so it's easier to understand
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', 175) 

    def speak(self, text: str):
        """Speaks the text aloud and blocks the script until finished reading."""
        try:
            print(f"🔊 Announcing: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"⚠️ Audio system failed to speak: {e}")