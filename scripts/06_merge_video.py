import os, json, subprocess, glob

W, H      = 1920, 1080
FPS       = 30
CLIP_DUR  = 4
CHARACTER = "assets/character.mp4"
BG_MUSIC  = "assets/bg_music.mp3"

with open("output/script.json", encoding="utf-8") as f:
    script = json.load(f)

os.makedirs("output/segments", exist_ok=True)
os.makedirs("output/final",    exist_ok=True)
os.makedirs("output/clips",    exist_ok=True)

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

def probe_wh(path):
    r = subprocess.run([
        "ffprobe", "-v", "quiet", "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0", path
    ], capture_output=True, text=True)
    try:
        w, h = r.stdout.strip().split(",")
        return int(w), int(h)
    except:
        return W, H

def file_ok(path):
    return os.path.exists(path) and os.path.getsize(path) > 1000

def safe_txt(t):
    return (t or "")[:45] \
        .replace("'","").replace(":","").replace("\\","") \
        .replace("[","").replace("]","").replace(",","") \
        .replace('"',"").replace(";","")

# ── Check character ───────────────────────────────────────────────────────────

char_exists = file_ok(CHARACTER)
char_scale  = "scale=340:-2"

if char_exists:
    cw, ch = probe_wh(CHARACTER)
    sh     = int(340 * ch / cw) if cw > 0 else 480
    if sh % 2 != 0: sh += 1
    char_scale = f"scale=340:{sh}"
    print(f"✅ Character: {cw}x{ch} → 340x{sh}")
else:
    print(f"⚠️ Character not found: {CHARACTER}")

# ── Make one 4-sec quick cut from a source clip ───────────────────────────────

CUT_EFFECTS = ["zoom_in", "zoom_out", "slide_left", "zoom_in", "slide_right", "zoom_out"]

def make_cut(src, effect, out):
    if file_ok(out):
        return out

    grade = "eq=contrast=1.12:brightness=0.02:saturation=1.3"
    t     = str(CLIP_DUR + 0.5)

    if effect == "zoom_in":
        ken = (
            f"zoompan=z='zoom+0.0008':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={CLIP_DUR*FPS}:s={W}x{H}:fps={FPS}"
        )
    elif effect == "zoom_out":
        ken = (
            f"zoompan=z='if(lte(zoom,1.0),1.3,max(1.001,zoom-0.0008))':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={CLIP_DUR*FPS}:s={W}x{H}:fps={FPS}"
        )
    elif effect == "slide_left":
        ken = (
            f"scale={W*2}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H}:'min(t*50,iw-{W})':0,fps={FPS}"
        )
    elif effect == "slide_right":
        ken = (
            f"scale={W*2}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H}:'max(0,iw-{W}-t*50)':0,fps={FPS}"
        )
    else:
        ken = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}"

    if src.endswith(".mp4"):
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{grade}"
        run([
            "ffmpeg", "-stream_loop", "-1", "-i", src,
            "-t", t, "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-an", "-y", out
        ], f"cut video [{effect}]")
    else:
        run([
            "ffmpeg", "-loop", "1", "-i", src,
            "-t", t, "-vf", f"scale=7680:-2,{ken},{grade}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-an", "-y", out
        ], f"cut image [{effect}]")

    return out if file_ok(out) else None

# ── Make background for one scene (multiple quick cuts) ───────────────────────

def make_scene_bg(scene, audio_dur):
    sid = scene["id"]
    out = f"output/segments/bg_{sid}.mp4"

    if file_ok(out):
        return out

    # Collect available sources
    sources = []
    for idx in range(6):
        vp = f"output/media/scene_{sid}_clip_{idx}.mp4"
        ip = f"output/media/scene_{sid}_clip_{idx}.jpg"
        if file_ok(vp):   sources.append(vp)
        elif file_ok(ip): sources.append(ip)

    # Old format fallback
    if not sources:
        for ext in [".mp4", ".jpg"]:
            p = f"output/media/scene_{sid}{ext}"
            if file_ok(p):
                sources.append(p)
                break

    if not sources:
        run([
            "ffmpeg", "-f", "lavfi",
            "-i", f"color=c=0x0d0d1a:s={W}x{H}:r={FPS}",
            "-t", str(audio_dur + 0.5),
            "-c:v", "libx264", "-y", out
        ], f"BG black s{sid}")
        return out

    # How many cuts needed
    num_cuts = max(1, int(audio_dur / CLIP_DUR) + 1)
    cut_paths = []

    for i in range(num_cuts):
        src    = sources[i % len(sources)]
        effect = CUT_EFFECTS[i % len(CUT_EFFECTS)]
        c_out  = f"output/clips/s{sid}_c{i}.mp4"
        result = make_cut(src, effect, c_out)
        if result:
            cut_paths.append(result)

    if not cut_paths:
        run([
            "ffmpeg", "-f", "lavfi",
            "-i", f"color=c=0x0d0d1a:s={W}x{H}:r={FPS}",
            "-t", str(audio_dur + 0.5), "-c:v", "libx264", "-y", out
        ], f"BG fallback s{sid}")
        return out

    concat_f = f"output/clips/cc_{sid}.txt"
    with open(concat_f, "w") as f:
        for cp in cut_paths:
            f.write(f"file '{os.path.abspath(cp)}'\n")

    run([
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", concat_f,
        "-t", str(audio_dur + 0.5),
        "-c:v", "libx264", "-preset", "fast",
        "-an", "-y", out
    ], f"BG concat s{sid} ({len(cut_paths)} cuts @ {CLIP_DUR}s)")

    return out

# ── Character clip ────────────────────────────────────────────────────────────

def make_char(sid, audio_dur):
    out = f"output/segments/char_{sid}.mp4"
    if file_ok(out):
        return out
    run([
        "ffmpeg",
        "-stream_loop", "-1", "-i", CHARACTER,
        "-t", str(audio_dur + 0.5),
        "-vf", char_scale,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-an", "-y", out
    ], f"Char s{sid}")
    return out

# ── Compose: bg + char + text + audio ─────────────────────────────────────────

def compose(scene, bg_path, char_path, audio_path, audio_dur):
    sid      = scene["id"]
    use_char = (
        scene.get("use_character", True)
        and char_exists
        and char_path
        and file_ok(char_path)
    )
    txt = safe_txt(scene.get("text_overlay", ""))
    out = f"output/segments/final_{sid}.mp4"

    if file_ok(out):
        return out

    char_x = "W-w-50" if sid % 2 == 0 else "50"
    char_y = "H-h-50"

    vignette = "vignette=PI/5"

    txt_f = ""
    if txt:
        txt_f = (
            f"drawtext=text='{txt}':"
            f"fontsize=64:fontcolor=black@0.75:"
            f"x=(w-text_w)/2+3:y=h*0.83+3,"
            f"drawtext=text='{txt}':"
            f"fontsize=64:fontcolor=white:"
            f"x=(w-text_w)/2:y=h*0.83:"
            f"box=1:boxcolor=black@0.4:boxborderw=16"
        )

    if use_char:
        fc  = f"[0:v]{vignette}[bg];[1:v][bg]overlay={char_x}:{char_y}[ov]"
        fc += f";[ov]{txt_f}[v]" if txt_f else ";[ov]copy[v]"
        run([
            "ffmpeg",
            "-i", bg_path, "-i", char_path, "-i", audio_path,
            "-filter_complex", fc,
            "-map", "[v]", "-map", "2:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(audio_dur), "-y", out
        ], f"Compose+char s{sid}")
    else:
        fc      = f"[0:v]{vignette},{txt_f}[v]" if txt_f else f"[0:v]{vignette}[v]"
        map_arg = ["-filter_complex", fc, "-map", "[v]"]
        run([
            "ffmpeg",
            "-i", bg_path, "-i", audio_path,
            *map_arg, "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(audio_dur), "-y", out
        ], f"Compose s{sid}")

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
        print(f"  ⏩ s{sid} no audio")
        continue

    audio_dur = probe_duration(audio_path)
    num_cuts  = max(1, int(audio_dur / CLIP_DUR))
    use_char  = scene.get("use_character", True)

    print(f"\n🎬 s{sid}  audio={audio_dur:.1f}s  cuts≈{num_cuts}  char={use_char and char_exists}")

    bg   = make_scene_bg(scene, audio_dur)
    char = make_char(sid, audio_dur) if (char_exists and use_char) else None
    seg  = compose(scene, bg, char, audio_path, audio_dur)

    if file_ok(seg):
        actual = probe_duration(seg)
        segments.append(seg)
        total_dur += actual
        print(f"  ✅ s{sid} done  {actual:.1f}s")
    else:
        print(f"  ❌ s{sid} FAILED")

print(f"\n📊 Segments : {len(segments)}")
print(f"📊 Total    : {total_dur:.0f}s = {total_dur/60:.1f} min")

# ── Concat ─────────────────────────────────────────────────────────────────────

concat_txt = "output/concat.txt"
with open(concat_txt, "w") as f:
    for s in segments:
        f.write(f"file '{os.path.abspath(s)}'\n")

raw = "output/final/raw.mp4"
run([
    "ffmpeg", "-f", "concat", "-safe", "0",
    "-i", concat_txt, "-c", "copy", "-y", raw
], "Concat all segments")

# ── Final: cinematic bars + music + fade ──────────────────────────────────────

final    = "output/final/final_video.mp4"
bars     = (
    f"drawbox=x=0:y=0:w={W}:h=42:color=black:t=fill,"
    f"drawbox=x=0:y={H-42}:w={W}:h=42:color=black:t=fill"
)
final_vf = f"{bars},fade=t=in:st=0:d=1.2"

if file_ok(BG_MUSIC):
    run([
        "ffmpeg", "-i", raw,
        "-stream_loop", "-1", "-i", BG_MUSIC,
        "-filter_complex", (
            "[0:a]volume=1.0[va];"
            f"[1:a]volume=0.06,atrim=0:{int(total_dur)}[mu];"
            "[va][mu]amix=inputs=2:duration=first[a];"
            f"[0:v]{final_vf}[v]"
        ),
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", "-y", final
    ], "Final + music + bars")
else:
    run([
        "ffmpeg", "-i", raw, "-vf", final_vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", "-y", final
    ], "Final + bars")

fd = probe_duration(final)
print(f"\n✅ DONE!  {fd:.0f}s = {fd/60:.1f} min")
print(f"   → output/final/final_video.mp4")