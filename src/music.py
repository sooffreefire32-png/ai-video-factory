def pick_music(script):

    text = script.lower()

    if "crime" in text or "murder" in text:
        return "assets/music.mp3"

    if "ghost" in text or "dark" in text:
        return "assets/music.mp3"

    return "assets/music.mp3"