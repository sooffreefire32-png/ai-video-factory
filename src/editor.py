from moviepy.editor import *
import os

def render_video(generated_images_paths, voiceover_path, music_path, timeline, output_path, character_video_path):
    final_clips = []
    audio_clips = []

    # Load voiceover audio
    voiceover_audio = AudioFileClip(voiceover_path)
    audio_clips.append(voiceover_audio)

    current_video_duration = 0

    for item in timeline:
        if item["type"] == "scene_image":
            # Find the corresponding generated image
            # This assumes generated_images_paths are in the order they appear in the timeline
            # A more robust solution would map scene content to image paths
            image_clip = ImageClip(generated_images_paths.pop(0), duration=item["duration"])
            image_clip = image_clip.set_fps(24) # Set FPS for smooth transitions
            final_clips.append(image_clip)
            current_video_duration += item["duration"]
        elif item["type"] == "character_video":
            character_clip = VideoFileClip(character_video_path)
            # Ensure character clip duration matches timeline item duration
            character_clip = character_clip.subclip(0, min(character_clip.duration, item["duration"]))
            final_clips.append(character_clip)
            current_video_duration += item["duration"]

    # Concatenate all video clips
    video_clip = concatenate_videoclips(final_clips, method="compose")

    # Ensure video duration matches voiceover duration
    if video_clip.duration < voiceover_audio.duration:
        # If video is shorter, extend the last clip or loop some clips
        # For simplicity, let\'s just extend the last clip for now
        last_clip = final_clips[-1]
        extension_duration = voiceover_audio.duration - video_clip.duration
        extended_last_clip = last_clip.set_duration(last_clip.duration + extension_duration)
        final_clips[-1] = extended_last_clip
        video_clip = concatenate_videoclips(final_clips, method="compose")
    elif video_clip.duration > voiceover_audio.duration:
        # If video is longer, trim it to voiceover duration
        video_clip = video_clip.subclip(0, voiceover_audio.duration)

    # Add background music
    if music_path and os.path.exists(music_path):
        music_audio = AudioFileClip(music_path)
        # Loop music if it\'s shorter than the video
        if music_audio.duration < video_clip.duration:
            music_audio = music_audio.fx(vfx.loop, duration=video_clip.duration)
        else:
            music_audio = music_audio.subclip(0, video_clip.duration)
        
        # Mix voiceover and background music (adjust volumes as needed)
        final_audio = CompositeAudioClip([voiceover_audio.set_duration(video_clip.duration).volumex(1.0), music_audio.volumex(0.3)])
    else:
        final_audio = voiceover_audio.set_duration(video_clip.duration)

    final_video = video_clip.set_audio(final_audio)

    # Write the final video file
    final_video.write_videofile(output_path, fps=24, codec="libx264")
    print(f"Final video rendered to {output_path}")
