import os

def create_shorts():

    cmd = """
ffmpeg -i output/video.mp4 -ss 00:01:00 -t 00:00:30 -vf scale=1080:1920 output/shorts.mp4
"""

    os.system(cmd)