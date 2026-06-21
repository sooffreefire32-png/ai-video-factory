from moviepy import *
import os

def render_video(visual_assets_paths, voiceover_path, music_path, timeline, output_path, character_video_path):
    final_clips = []
    
    # Target resolution
    W, H = 1920, 1080

    print("Loading assets for rendering...")
    
    asset_idx = 0
    for item in timeline:
        try:
            if item["type"] == "scene_image":
                path = visual_assets_paths[asset_idx]
                asset_idx += 1
                
                # Check if it's a video or image based on extension
                if path.lower().endswith(('.mp4', '.avi', '.mov')):
                    clip = VideoFileClip(path).resized(width=W)
                    if clip.h > H:
                        clip = clip.cropped(y_center=clip.h/2, height=H)
                    clip = clip.subclipped(0, min(clip.duration, item["duration"]))
                else:
                    clip = ImageClip(path, duration=item["duration"]).resized(width=W)
                    if clip.h > H:
                        clip = clip.cropped(y_center=clip.h/2, height=H)
                    else:
                        clip = clip.resized(height=H)
                
                final_clips.append(clip)
                
            elif item["type"] == "character_video":
                if os.path.exists(character_video_path):
                    clip = VideoFileClip(character_video_path).resized(width=W)
                    if clip.h > H:
                        clip = clip.cropped(y_center=clip.h/2, height=H)
                    clip = clip.subclipped(0, min(clip.duration, item["duration"]))
                    final_clips.append(clip)
        except Exception as e:
            print(f"Error processing clip {item}: {e}")
            continue

    if not final_clips:
        print("No clips to render!")
        return

    # Concatenate all video clips
    video_clip = concatenate_videoclips(final_clips, method="compose")

    # Load voiceover audio
    voiceover_audio = AudioFileClip(voiceover_path)

    # Sync video duration with voiceover
    if video_clip.duration < voiceover_audio.duration:
        video_clip = video_clip.with_duration(voiceover_audio.duration)
    else:
        video_clip = video_clip.subclipped(0, voiceover_audio.duration)

    # Add background music
    if music_path and os.path.exists(music_path):
        music_audio = AudioFileClip(music_path)
        if music_audio.duration < video_clip.duration:
            n_loops = int(video_clip.duration / music_audio.duration) + 1
            music_audio = concatenate_audioclips([music_audio] * n_loops).with_duration(video_clip.duration)
        else:
            music_audio = music_audio.subclipped(0, video_clip.duration)
        
        final_audio = CompositeAudioClip([
            voiceover_audio.with_volume_scaled(1.0), 
            music_audio.with_volume_scaled(0.2)
        ])
    else:
        final_audio = voiceover_audio

    final_video = video_clip.with_audio(final_audio)

    # Write the final video file
    print(f"Starting final render to {output_path}...")
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    print(f"Final video rendered to {output_path}")
