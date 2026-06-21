from gtts import gTTS
import os

def generate_voice(text, path, lang='en'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(path)
        print(f'Voice generated and saved to {path}')
    except Exception as e:
        print(f'Error generating voice with gTTS: {e}')
        # Fallback or error handling if gTTS fails
        with open(path.replace(".mp3", ".txt"), "w") as f:
            f.write(text)
        print('Saved text to file as a fallback.')
