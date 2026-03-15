import speech_recognition as sr

class AgentListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Adjust threshold dynamically for background noise
        self.recognizer.energy_threshold = 300 

    def listen_for_objective(self) -> str:
        """Listens to the microphone and returns the spoken text as a string."""
        with sr.Microphone() as source:
            print("\n🎤 Microphone is live. Please speak your objective...")
            
            # Briefly listen to the room to calibrate for background noise
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            try:
                # Listen for the user's voice
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                print("⏳ Processing speech...")
                
                # Convert the audio to text
                text = self.recognizer.recognize_google(audio)
                print(f"✅ Heard: '{text}'")
                return text
                
            except sr.WaitTimeoutError:
                print("⚠️ No speech detected.")
                return "Error: No speech detected."
            except sr.UnknownValueError:
                print("⚠️ Could not understand the audio.")
                return "Error: Could not understand audio."
            except Exception as e:
                print(f"⚠️ Microphone error: {e}")
                return f"Error: {e}"