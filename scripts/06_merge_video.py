import os, json, subprocess, glob

W, H      = 1920, 1080
FPS       = 30
CHARACTER = "assets/character.mp4"
BG_MUSIC  = "assets/bg_music.mp3"

with open("output/script.json", encoding="utf-8") as f:
    script = json.load(f)

os.makedirs("output/segments", exist_ok=True)
os.makedirs("output/final",    exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def run(cmd, label=""):
    print(f"    ▶ {label}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"      ⚠️ {r.stderr[-500:]}")
    return r.returncode == 0

def probe_duration(path):
    r = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", path
    ], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 5.0

def probe_size(path):
    """Returns (width, height) of video/image"""
    r = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0", path
    ], capture_output=True, text=True)
    try:
        parts = r.stdout.strip().split(",")
        return int(parts[0]), int(parts[1])
    except:
        return W, H

def safe_txt(t):
    return (t or "")[:45] \
        .replace("'", "").replace(":", "") \
        .replace("\\", "").replace("[", "") \
        .replace("]", "").replace(",", "") \
        .replace('"', "").replace(";", "")

def file_ok(path):
    return os.path.exists(path) and os.path.getsize(path) > 1000

# ─────────────────────────────────────────────────────────────────────────────
# VERIFY CHARACTER VIDEO EXISTS
# ─────────────────────────────────────────────────────────────────────────────

char_exists = file_ok(CHARACTER)
if char_exists:
    cw, ch = probe_size(CHARACTER)
    print(f"✅ Character video found: {CHARACTER} ({cw}x{ch})")
else:
    print(f"⚠️ Character video NOT found at {CHARACTER} — will skip character overlay")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — BACKGROUND CLIP
# Video/image loops to fill exact audio duration
# ─────────────────────────────────────────────────────────────────────────────

def make_bg(scene, audio_dur):
    sid    = scene["id"]
    effect = scene.get("effect", "none")
    vp     = f"output/media/scene_{sid}.mp4"
    ip     = f"output/media/scene_{sid}.jpg"
    out    = f"output/segments/bg_{sid}.mp4"

    if file_ok(out):
        return out

    dur    = audio_dur + 0.5
    frames = int(dur * FPS) + 10

    # Professional color grade
    grade = (
        "eq=contrast=1.15:brightness=0.03:saturation=1.35:gamma=0.95,"
        "unsharp=5:5:0.8:3:3:0.4"
    )

    # Ken Burns / motion effects
    if effect == "zoom_in":
        ken = (
            f"zoompan=z='zoom+0.0005':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s={W}x{H}:fps={FPS}"
        )
    elif effect == "zoom_out":
        ken = (
            f"zoompan=z='if(lte(zoom,1.0),1.3,max(1.001,zoom-0.0005))':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s={W}x{H}:fps={FPS}"
        )
    elif effect == "slide_left":
        ken = (
            f"scale={W*2}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H}:'min(t*40,iw-{W})':0,fps={FPS}"
        )
    elif effect == "slide_right":
        ken = (
            f"scale={W*2}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H}:'max(0,iw-{W}-t*40)':0,fps={FPS}"
        )
    else:
        ken = (
            f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},fps={FPS}"
        )

    if file_ok(vp):
        run([
            "ffmpeg",
            "-stream_loop", "-1", "-i", vp,
            "-t", str(dur),
            "-vf", (
                f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                f"crop={W}:{H},fps={FPS},{grade}"
            ),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-an", "-y", out
        ], f"BG video  s{sid} [{effect}]")

    elif file_ok(ip):
        run([
            "ffmpeg",
            "-loop", "1", "-i", ip,
            "-t", str(dur),
            "-vf", f"scale=7680:-2,{ken},{grade}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-an", "-y", out
        ], f"BG image  s{sid} [{effect}]")

    else:
        # Gradient black fallback
        run([
            "ffmpeg", "-f", "lavfi",
            "-i", f"color=c=0x0d0d1a:s={W}x{H}:r={FPS}",
            "-t", str(dur),
            "-c:v", "libx264", "-y", out
        ], f"BG black  s{sid}")

    return out

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — CHARACTER CLIP
# Loop character video to fill audio duration, mute its audio
# ─────────────────────────────────────────────────────────────────────────────

def make_char(sid, audio_dur):
    out = f"output/segments/char_{sid}.mp4"

    if file_ok(out):
        return out

    # Get character dimensions
    cw, ch = probe_size(CHARACTER)

    # Scale to 340px wide keeping aspect ratio
    scale_h = int(340 * ch / cw) if cw > 0 else 480
    # Make height even number
    if scale_h % 2 != 0:
        scale_h += 1

    run([
        "ffmpeg",
        "-stream_loop", "-1",
        "-i", CHARACTER,
        "-t", str(audio_dur + 0.5),
        "-vf", f"scale=340:{scale_h}",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-an",                          # mute character audio
        "-y", out
    ], f"Character  s{sid}  {audio_dur:.1f}s")

    return out

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — PROFESSIONAL COMPOSITE
# bg + vignette + character (bottom-right) + text overlay + audio
# ─────────────────────────────────────────────────────────────────────────────

def compose(scene, bg_path, char_path, audio_path, audio_dur):
    sid      = scene["id"]
    use_char = (
        scene.get("use_character", True)
        and char_exists
        and char_path
        and file_ok(char_path)
    )
    txt  = safe_txt(scene.get("text_overlay", ""))
    out  = f"output/segments/final_{sid}.mp4"

    if file_ok(out):
        return out

    # Alternate character position: bottom-right / bottom-left
    if sid % 3 == 0:
        char_x = "W-w-50"
        char_y = "H-h-50"
    elif sid % 3 == 1:
        char_x = "50"
        char_y = "H-h-50"
    else:
        char_x = "W-w-50"
        char_y = "H-h-50"

    # Professional text overlay with shadow
    txt_filter = ""
    if txt:
        txt_filter = (
            # Shadow
            f"drawtext=text='{txt}':"
            f"fontsize=62:fontcolor=black@0.7:"
            f"x=(w-text_w)/2+3:y=h*0.83+3,"
            # Main text
            f"drawtext=text='{txt}':"
            f"fontsize=62:fontcolor=white:"
            f"x=(w-text_w)/2:y=h*0.83:"
            f"box=1:boxcolor=black@0.45:boxborderw=14"
        )

    # Vignette for cinematic feel
    vignette = "vignette=PI/5"

    if use_char:
        # 3 inputs: bg, character, audio
        fc = (
            # Vignette on bg
            f"[0:v]{vignette}[bg];"
            # Character overlay
            f"[1:v][bg]overlay={char_x}:{char_y}[ov]"
        )
        if txt_filter:
            fc += f";[ov]{txt_filter}[v]"
        else:
            fc += ";[ov]copy[v]"

        run([
            "ffmpeg",
            "-i", bg_path,
            "-i", char_path,
            "-i", audio_path,
            "-filter_complex", fc,
            "-map", "[v]",
            "-map", "2:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(audio_dur),
            "-y", out
        ], f"Compose+char  s{sid}")

    else:
        # 2 inputs: bg, audio
        if txt_filter:
            fc      = f"[0:v]{vignette},{txt_filter}[v]"
            map_arg = ["-filter_complex", fc, "-map", "[v]"]
        else:
            fc      = f"[0:v]{vignette}[v]"
            map_arg = ["-filter_complex", fc, "-map", "[v]"]

        run([
            "ffmpeg",
            "-i", bg_path,
            "-i", audio_path,
            *map_arg,
            "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(audio_dur),
            "-y", out
        ], f"Compose  s{sid}")

    return out

# ─────────────────────────────────────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────────────────────────────────────

segments  = []
total_dur = 0.0

for scene in script["scenes"]:
    sid        = scene["id"]
    audio_path = f"output/audio/scene_{sid}.mp3"

    if not file_ok(audio_path):
        print(f"  ⏩ Scene {sid} — no audio, skipping")
        continue

    # Audio is master clock — NEVER trimmed
    audio_dur = probe_duration(audio_path)
    use_char  = scene.get("use_character", True)

    print(f"\n🎬 Scene {sid}  |  audio={audio_dur:.2f}s  |  effect={scene.get('effect','none')}  |  char={use_char and char_exists}")

    bg   = make_bg(scene, audio_dur)
    char = make_char(sid, audio_dur) if (char_exists and use_char) else None
    seg  = compose(scene, bg, char, audio_path, audio_dur)

    if file_ok(seg):
        actual = probe_duration(seg)
        segments.append(seg)
        total_dur += actual
        diff = abs(actual - audio_dur)
        status = "✅" if diff < 0.5 else "⚠️"
        print(f"  {status} Done  seg={actual:.2f}s  audio={audio_dur:.2f}s  diff={diff:.2f}s")
    else:
        print(f"  ❌ FAILED scene {sid}")

print(f"\n📊 Segments ready : {len(segments)}")
print(f"📊 Total duration : {total_dur:.1f}s = {total_dur/60:.1f} min")

# ─────────────────────────────────────────────────────────────────────────────
# CONCAT ALL SEGMENTS
# ─────────────────────────────────────────────────────────────────────────────

concat_txt = "output/concat.txt"
with open(concat_txt, "w") as f:
    for s in segments:
        f.write(f"file '{os.path.abspath(s)}'\n")

raw = "output/final/raw.mp4"
run([
    "ffmpeg", "-f", "concat", "-safe", "0",
    "-i", concat_txt,
    "-c", "copy",
    "-y", raw
], "Concatenate all segments")

# ─────────────────────────────────────────────────────────────────────────────
# FINAL — professional grade + bg music + cinematic bars + fade
# ─────────────────────────────────────────────────────────────────────────────

final = "output/final/final_video.mp4"

# Cinematic black bars (2.35:1 aspect)
bars = (
    f"drawbox=x=0:y=0:w={W}:h=45:color=black:t=fill,"
    f"drawbox=x=0:y={H-45}:w={W}:h=45:color=black:t=fill"
)

# Opening + closing fade
fades = "fade=t=in:st=0:d=1"

final_vf = f"{bars},{fades}"

if file_ok(BG_MUSIC):
    run([
        "ffmpeg",
        "-i", raw,
        "-stream_loop", "-1", "-i", BG_MUSIC,
        "-filter_complex", (
            "[0:a]volume=1.0[va];"
            f"[1:a]volume=0.06,atrim=0:{int(total_dur)}[mu];"
            "[va][mu]amix=inputs=2:duration=first[a];"
            f"[0:v]{final_vf}[v]"
        ),
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-y", final
    ], "Final + BG music + cinematic bars")
else:
    run([
        "ffmpeg", "-i", raw,
        "-vf", final_vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-y", final
    ], "Final + cinematic bars (no music)")

final_dur = probe_duration(final)
print(f"\n✅ FINAL VIDEO READY!")
print(f"   Path     : {final}")
print(f"   Duration : {final_dur:.1f}s = {final_dur/60:.1f} min")