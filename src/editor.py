import os

def render_video(images, voice, music):

    img_inputs = " ".join([f"-i {i}" for i in images])

    cmd = f"""
ffmpeg -y {img_inputs} -i {voice} -i {music} -i assets/character.mp4 \
-filter_complex "
[2:a]volume=0.3[bg];
[1:a][bg]amix=inputs=2:duration=longest[a];
[0:v]concat=n={len(images)}:v=1:a=0[v];
[3:v]scale=600:340[char];
[v][char]overlay=W-w-20:H-h-20
" \
-map "[a]" output/video.mp4
"""

    os.system(cmd)