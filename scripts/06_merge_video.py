import os, json, subprocess, glob

W, H = 1920, 1080
FPS  = 25
CHARACTER = "assets/character.mp4"
BG_MUSIC  = "assets/bg_music.mp3"

with open("output/script.json") as f:
    script = json.load(f)

os.makedirs("output/segments", exist_ok=True)
os.makedirs("output/final",    exist_ok=True)

# ── helpers ───────────────────────────────────────────────────────────────────

def run(cmd, label=""):
    print(f"  🎬 {label}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"     ⚠️  {r.stderr[-300:]}")
    return r.returncode == 0

def duration_of(path):
    r = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", path
    ], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 5.0

def safe_text(t):
    return (t or "")[:45].replace("'","").replace(":","").replace("\\","")

# ── background clip ───────────────────────────────────────────────────────────

def make_bg(scene, dur):
    sid    = scene["id"]
    effect = scene.get("effect", "none")
    vp     = f"output/media/scene_{sid}.mp4"
    ip     = f"output/media/scene_{sid}.jpg"
    out    = f"output/segments/bg_{sid}.mp4"

    base_vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},fps={FPS}"
    )

    # Ken Burns / motion effects
    if effect == "zoom_in":
        ken = (
            f",zoompan=z='zoom+0.0008':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={int(dur*FPS)}:s={W}x{H}"
        )
    elif effect == "zoom_out":
        ken = (
            f",zoompan=z='if(lte(zoom,1.0),1.4,max(1.001,zoom-0.0008))':"
            f"d={int(dur*FPS)}:s={W}x{H}"
        )
    elif effect == "slide_left":
        ken = f",crop={W}:{H}:'if(lte(t*30,iw-{W}),t*30,iw-{W})':0"
    elif effect == "slide_right":
        ken = f",crop={W}:{H}:'if(lte(t*30,iw-{W}),iw-{W}-t*30,0)':0"
    else:
        ken = ""

    if os.path.exists(vp):
        run([
            "ffmpeg", "-stream_loop", "-1", "-i", vp,
            "-t", str(dur + 1),
            "-vf", base_vf + ken,
            "-c:v", "libx264", "-preset", "fast",
            "-an", "-y", out
        ], f"BG video {sid}")
    elif os.path.exists(ip):
        run([
            "ffmpeg", "-loop", "1", "-i", ip,
            "-t", str(dur + 1),
            "-vf", f"scale=8000:-1{ken},scale={W}:{H},fps={FPS}",
            "-c:v", "libx264", "-preset", "fast",
            "-an", "-y", out
        ], f"BG image {sid}")
    else:
        run([
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=black:s={W}x{H}:r={FPS}",
            "-t", str(dur + 1),
            "-c:v", "libx264", "-y", out
        ], f"BG black {sid}")

    return out

# ── character overlay (NO chroma key — simple corner overlay) ─────────────────

def make_char(sid, dur):
    out = f"output/segments/char_{sid}.mp4"
    run([
        "ffmpeg",
        "-stream_loop", "-1", "-i", CHARACTER,
        "-t", str(dur + 1),
        "-vf", "scale=420:-1",   # sirf resize
        "-c:v", "libx264", "-preset", "ultrafast",
        "-an", "-y", out
    ], f"Character {sid}")
    return out

# ── compose one segment ───────────────────────────────────────────────────────

def compose(scene, bg, char, audio):
    sid      = scene["id"]
    use_char = (
        scene.get("use_character", True)
        and char
        and os.path.exists(CHARACTER)
    )
    txt = safe_text(scene.get("text_overlay", ""))
    out = f"output/segments/final_{sid}.mp4"

    grade = "eq=contrast=1.1:brightness=0.02:saturation=1.25"

    text_filter = (
        f",drawtext=text='{txt}':"
        f"fontsize=58:fontcolor=white:"
        f"x=(w-text_w)/2:y=h*0.82:"
        f"box=1:boxcolor=black@0.6:boxborderw=10"
    ) if txt else ""

    if use_char:
        # Background + character overlay bottom-right corner
        fc = (
            f"[0:v]{grade}[bg];"
            f"[1:v]scale=420:-1[ch];"
            f"[bg][ch]overlay=W-w-40:H-h-40[ov]"
        )
        if txt:
            fc += (
                f";[ov]drawtext=text='{txt}':"
                f"fontsize=58:fontcolor=white:"
                f"x=(w-text_w)/2:y=h*0.82:"
                f"box=1:boxcolor=black@0.6:boxborderw=10[v]"
            )
        else:
            fc += ";[ov]copy[v]"

        run([
            "ffmpeg",
            "-i", bg, "-i", char, "-i", audio,
            "-filter_complex", fc,
            "-map", "[v]", "-map", "2:a",
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-shortest", "-y", out
        ], f"Compose+char {sid}")
    else:
        run([
            "ffmpeg",
            "-i", bg, "-i", audio,
            "-filter_complex",
            f"[0:v]{grade}{text_filter}[v]",
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-shortest", "-y", out
        ], f"Compose {sid}")

    return out

# ── main loop ─────────────────────────────────────────────────────────────────

segments = []
for scene in script["scenes"]:
    sid   = scene["id"]
    audio = f"output/audio/scene_{sid}.mp3"

    if not os.path.exists(audio):
        print(f"  ⏩ Skip {sid} — no audio")
        continue

    dur  = duration_of(audio)
    bg   = make_bg(scene, dur)
    char = (
        make_char(sid, dur)
        if scene.get("use_character", True) and os.path.exists(CHARACTER)
        else None
    )
    seg = compose(scene, bg, char, audio)

    if os.path.exists(seg):
        segments.append(seg)
        print(f"  ✅ Segment {sid} done ({dur:.1f}s)")

# ── concat all segments ───────────────────────────────────────────────────────

concat_txt = "output/concat.txt"
with open(concat_txt, "w") as f:
    for s in segments:
        f.write(f"file '{os.path.abspath(s)}'\n")

raw = "output/final/raw.mp4"
run([
    "ffmpeg", "-f", "concat", "-safe", "0",
    "-i", concat_txt, "-c", "copy", "-y", raw
], "Concatenate all segments")

# ── final grade + optional background music ───────────────────────────────────

final = "output/final/final_video.mp4"

if os.path.exists(BG_MUSIC):
    run([
        "ffmpeg", "-i", raw,
        "-stream_loop", "-1", "-i", BG_MUSIC,
        "-filter_complex",
        (
            "[0:a]volume=1.0[va];"
            "[1:a]volume=0.08[mu];"
            "[va][mu]amix=inputs=2:duration=first[a];"
            "[0:v]fade=t=in:st=0:d=1,"
            "eq=contrast=1.1:brightness=0.02:saturation=1.3[v]"
        ),
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-y", final
    ], "Final grade + bg music")
else:
    run([
        "ffmpeg", "-i", raw,
        "-vf",
        "fade=t=in:st=0:d=1,eq=contrast=1.1:brightness=0.02:saturation=1.3",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-y", final
    ], "Final grade only")

print(f"\n✅ Final video: {final}")
print(f"   Duration: {duration_of(final)/60:.1f} minutes")