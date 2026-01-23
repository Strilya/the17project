"""
Voice Generator - Deep US narrator voice with audio effects
"""

import os
from dotenv import load_dotenv
from google.cloud import texttospeech

class VoiceGenerator:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Get credentials path and convert to absolute if relative
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if creds_path:
            if not os.path.isabs(creds_path):
                # Convert relative path to absolute (relative to project root)
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                creds_path = os.path.join(project_root, creds_path)

            # Set the absolute path
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path

        self.client = texttospeech.TextToSpeechClient()
        
        # Deep US male voice
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-D",  # Deepest US male
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.90,  # 20% slower for better caption readability
            pitch=-8.5,  # Deep Morgan Freeman-style
            volume_gain_db=3.0,  # Strong presence
            effects_profile_id=["large-home-entertainment-class-device"]  # Bass/richness
        )
    
    def generate_speech(self, text, output_path):
        """Generate deep US narrator voice"""

        synthesis_input = texttospeech.SynthesisInput(text=text)

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=self.voice,
            audio_config=self.audio_config
        )

        with open(output_path, 'wb') as out:
            out.write(response.audio_content)

        print(f"   ✅ Deep US voice generated")
        return output_path

    def generate_segmented_speech(self, content, output_path):
        """
        Generate speech with separate segments for perfect text sync
        Returns timing information for each segment
        """
        from moviepy.audio.io.AudioFileClip import AudioFileClip
        from moviepy.audio.AudioClip import concatenate_audioclips, AudioClip
        import os

        segments = [
            content['hook'],
            content['meaning'],
            content['action'],
            content['cta']
        ]

        segment_files = []
        segment_durations = []

        # Generate each segment separately
        for i, segment_text in enumerate(segments):
            temp_path = f"output/temp_voice_segment_{i}.mp3"

            synthesis_input = texttospeech.SynthesisInput(text=segment_text)

            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )

            with open(temp_path, 'wb') as out:
                out.write(response.audio_content)

            segment_files.append(temp_path)

        # Load segments and calculate timings
        audio_clips = []
        current_time = 0.0
        timings = []

        # Pause between segments for better caption readability
        PAUSE_DURATION = 0.5

        for i, segment_file in enumerate(segment_files):
            clip = AudioFileClip(segment_file)
            segment_duration = clip.duration

            # Record timing for this segment
            timings.append({
                'text': segments[i],
                'start': current_time,
                'duration': segment_duration,
                'end': current_time + segment_duration
            })

            audio_clips.append(clip)
            segment_durations.append(segment_duration)

            # Add pause between segments (except after last one)
            if i < len(segment_files) - 1:
                silence = AudioClip(lambda t: [0, 0], duration=PAUSE_DURATION)
                audio_clips.append(silence)
                current_time += segment_duration + PAUSE_DURATION
            else:
                current_time += segment_duration

        # Concatenate all segments
        final_audio = concatenate_audioclips(audio_clips)
        final_audio.write_audiofile(output_path, codec='mp3', logger=None)

        # Cleanup temp files
        for temp_file in segment_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        # Close clips
        for clip in audio_clips:
            clip.close()

        total_duration = current_time

        print(f"   ✅ Segmented voice generated ({len(timings)} segments, {total_duration:.1f}s total)")
        print(f"   ⏱️  Segment timings:")
        for i, timing in enumerate(timings):
            print(f"      Segment {i+1}: {timing['start']:.1f}s - {timing['end']:.1f}s ({timing['duration']:.1f}s)")

        return output_path, timings

