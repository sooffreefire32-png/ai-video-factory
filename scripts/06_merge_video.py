import os, json, subprocess

W, H      = 1920, 1080
FPS       = 25
CHARACTER = "assets/character.mp4"
BG_MUSIC  = "assets/bg_music.mp3"

with open("output/script.json") as f:
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
        print(f"      ⚠️ {r.stderr[-400:]}")
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

def safe_txt(t):
    return (t or "")[:48] \
        .replace("'", "").replace(":", "") \
        .replace("\\", "").replace("[", "") \
        .replace("]", "").replace(",", "")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — background clip
# VIDEO loops to fill audio duration — audio NEVER touched
# ─────────────────────────────────────────────────────────────────────────────

def make_bg(scene, audio_dur):
    sid    = scene["id"]
    effect = scene.get("effect", "none")
    vp     = f"output/media/scene_{sid}.mp4"
    ip     = f"output/media/scene_{sid}.jpg"
    out    = f"output/segments/bg_{sid}.mp4"
    frames = int(audio_dur * FPS) + 5   # slight buffer, trimmed later by mux

    # Ken Burns effects — applied to images
    if effect == "zoom_in":
        ken = (
            f"zoompan=z='zoom+0.0006':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s={W}x{H}:fps={FPS}"
        )
    elif effect == "zoom_out":
        ken = (
            f"zoompan=z='if(lte(zoom,1.0),1.35,max(1.001,zoom-0.0006))':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s={W}x{H}:fps={FPS}"
        )
    elif effect == "slide_left":
        ken = (
            f"scale={W*2}:{H},"
            f"crop={W}:{H}:'min(t*50,{W})':0,"
            f"fps={FPS}"
        )
    elif effect == "slide_right":
        ken = (
            f"scale={W*2}:{H},"
            f"crop={W}:{H}:'max(0,{W}-t*50)':0,"
            f"fps={FPS}"
        )
    else:
        ken = (
            f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},fps={FPS}"
        )

    grade = "eq=contrast=1.12:brightness=0.02:saturation=1.3"

    if os.path.exists(vp):
        # Video: loop it so it's always longer than audio
        # -stream_loop -1 = infinite loop, -t cuts at audio_dur + buffer
        run([
            "ffmpeg",
            "-stream_loop", "-1", "-i", vp,
            "-t", str(audio_dur + 1),
            "-vf", (
                f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                f"crop={W}:{H},fps={FPS},{grade}"
            ),
            "-c:v", "libx264", "-preset", "fast",
            "-an", "-y", out
        ], f"BG video scene {sid} [{effect}]")

    elif os.path.exists(ip):
        # Image: -loop 1 repeats forever, -t sets exact length
        run([
            "ffmpeg",
            "-loop", "1", "-i", ip,
            "-t", str(audio_dur + 1),
            "-vf", f"scale=8000:-1,{ken},{grade}",
            "-c:v", "libx264", "-preset", "fast",
            "-an", "-y", out
        ], f"BG image scene {sid} [{effect}]")

    else:
        # Black fallback
        run([
            "ffmpeg", "-f", "lavfi",
            "-i", f"color=c=0x1a1a2e:s={W}x{H}:r={FPS}",
            "-t", str(audio_dur + 1),
            "-c:v", "libx264", "-y", out
        ], f"BG black scene {sid}")

    return out

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — character clip
# Loop to fill audio duration — no trim on audio side
# ─────────────────────────────────────────────────────────────────────────────

def make_char(sid, audio_dur):
    out = f"output/segments/char_{sid}.mp4"
    run([
        "ffmpeg",
        "-stream_loop", "-1", "-i", CHARACTER,
        "-t", str(audio_dur + 1),
        "-vf", "scale=380:-1",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-an", "-y", out
    ], f"Character scene {sid}")
    return out

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — composite
# -shortest is REMOVED — instead we use audio as the length driver
# Video is already longer than audio, so mux stops exactly at audio end
# ─────────────────────────────────────────────────────────────────────────────

def compose(scene, bg_path, char_path, audio_path, audio_dur):
    sid      = scene["id"]
    use_char = (
        scene.get("use_character", True)
        and char_path
        and os.path.exists(char_path)
        and os.path.exists(CHARACTER)
    )
    txt = safe_txt(scene.get("text_overlay", ""))
    out = f"output/segments/final_{sid}.mp4"

    # Character position alternates for variety
    char_pos = "W-w-40:H-h-40" if sid % 2 == 0 else "40:H-h-40"

    txt_f = (
        f"drawtext=text='{txt}':"
        f"fontsize=56:fontcolor=white:"
        f"x=(w-text_w)/2:y=h*0.83:"
        f"box=1:boxcolor=black@0.55:boxborderw=12"
    ) if txt else ""

    # -t audio_dur on OUTPUT: video side is longer, output stops at audio end
    # This means audio plays fully, video just stops when audio ends ✅
    out_duration = ["-t", str(audio_dur)]

    if use_char:
        fc_parts = [
            "[0:v]copy[bg]",
            "[1:v]scale=380:-1[ch]",
            f"[bg][ch]overlay={char_pos}[ov]",
        ]
        fc_parts.append(f"[ov]{txt_f}[v]" if txt_f else "[ov]copy[v]")
        fc = ";".join(fc_parts)

        run([
            "ffmpeg",
            "-i", bg_path,
            "-i", char_path,
            "-i", audio_path,
            "-filter_complex", fc,
            "-map", "[v]",
            "-map", "2:a",
            *out_duration,             # ← output trimmed to exact audio length
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            "-y", out
        ], f"Compose+char scene {sid}  {audio_dur:.2f}s")

    else:
        if txt_f:
            fc_arg = ["-filter_complex", f"[0:v]{txt_f}[v]", "-map", "[v]"]
        else:
            fc_arg = ["-map", "0:v"]

        run([
            "ffmpeg",
            "-i", bg_path,
            "-i", audio_path,
            *fc_arg,
            "-map", "1:a",
            *out_duration,             # ← output trimmed to exact audio length
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            "-y", out
        ], f"Compose scene {sid}  {audio_dur:.2f}s")

    return out

# ─────────────────────────────────────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────────────────────────────────────

segments    = []
total_dur   = 0
char_exists = os.path.exists(CHARACTER)

for scene in script["scenes"]:
    sid        = scene["id"]
    audio_path = f"output/audio/scene_{sid}.mp3"

    if not os.path.exists(audio_path):
        print(f"  ⏩ Scene {sid} — no audio, skipping")
        continue

    # Audio duration = master clock, never trimmed
    audio_dur = probe_duration(audio_path)
    print(f"\n🎬 Scene {sid}  audio={audio_dur:.2f}s  effect={scene.get('effect','none')}")

    bg   = make_bg(scene, audio_dur)
    char = (
        make_char(sid, audio_dur)
        if char_exists and scene.get("use_character", True)
        else None
    )
    seg = compose(scene, bg, char, audio_path, audio_dur)

    if os.path.exists(seg):
        actual = probe_duration(seg)
        segments.append(seg)
        total_dur += actual
        print(f"  ✅ Done  segment={actual:.2f}s  audio={audio_dur:.2f}s")
        # Warn if mismatch > 0.5s
        if abs(actual - audio_dur) > 0.5:
            print(f"  ⚠️  Mismatch! segment={actual:.2f}s vs audio={audio_dur:.2f}s")
    else:
        print(f"  ❌ Segment {sid} FAILED")

print(f"\n📊 Segments: {len(segments)}")
print(f"📊 Total: {total_dur/60:.1f} min")

# ─────────────────────────────────────────────────────────────────────────────
# CONCAT
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
# FINAL — bg music + fade (audio stream untouched)
# ─────────────────────────────────────────────────────────────────────────────

final = "output/final/final_video.mp4"

if os.path.exists(BG_MUSIC) and os.path.getsize(BG_MUSIC) > 10000:
    run([
        "ffmpeg",
        "-i", raw,
        "-stream_loop", "-1", "-i", BG_MUSIC,
        "-filter_complex", (
            # Narration full volume, music very low
            "[0:a]volume=1.0[va];"
            "[1:a]volume=0.06,apad[mu];"
            "[va][mu]amix=inputs=2:duration=first[a];"
            "[0:v]fade=t=in:st=0:d=0.8[v]"
        ),
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "21",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-y", final
    ], "Final + BG music + fade")
else:
    run([
        "ffmpeg", "-i", raw,
        "-vf", "fade=t=in:st=0:d=0.8",
        "-c:v", "libx264", "-preset", "medium", "-crf", "21",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-y", final
    ], "Final + fade (no music)")

final_dur = probe_duration(final)
print(f"\n✅ FINAL VIDEO READY!")
print(f"   Duration: {final_dur/60:.1f} minutes")