"""
Video Generator for THE17PROJECT reels
- Bebas Neue font (tall condensed ALL CAPS)
- White fill + THIN BLACK outline (2-3px)
- FORCED 2-line split: Line 1 WHITE, Line 2 DARK YELLOW/ORANGE
- Text positioned in LOWER THIRD
- THE17PROJECT watermark BELOW each text phrase
- Source watermark (bottom left, barely visible)
"""

import os
import requests
import random
import glob
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import VideoClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.AudioClip import CompositeAudioClip
import moviepy.video.fx.all as vfx
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from video_sources import VideoSourceManager

# 150+ VIDEO SEARCH TERMS
VIDEO_QUERIES = [
    # Spiritual & Mystical (15)
    "spiritual awakening", "divine light rays", "mystical energy", "sacred geometry", "cosmic consciousness",
    "ethereal glow", "spiritual journey", "enlightenment meditation", "universal energy", "metaphysical symbols",
    "astral projection", "third eye opening", "chakra alignment", "aura energy field", "divine guidance",
    # Space & Cosmos (15)
    "galaxy nebula", "stars universe", "cosmic dust", "milky way night", "space timelapse",
    "planet earth orbit", "moon phases", "solar system", "asteroid field", "black hole",
    "supernova explosion", "constellation stars", "deep space", "cosmic rays", "interstellar clouds",
    # Nature Abstract (15)
    "ocean waves sunset", "mountain peak clouds", "waterfall flowing", "forest canopy light", "desert sand dunes",
    "aurora borealis", "lightning storm", "rainbow prism", "crystal formation", "ice glaciers",
    "volcanic lava", "canyon landscape", "river flowing", "lake reflection", "sunrise timelapse",
    # Water & Elements (15)
    "underwater bubbles", "ocean deep blue", "water droplets", "waves crashing", "rain falling",
    "ice crystals", "water surface", "ocean current", "tidal waves", "splash slow motion",
    "water ripples", "aquatic life", "coral reef", "jellyfish floating", "whale swimming",
    # Fire & Light (15)
    "fire flames", "candle burning", "bonfire night", "torch fire", "sunset golden hour",
    "sunrise dawn", "light beams", "sun rays forest", "golden light", "lens flare",
    "sparkle glitter", "fireworks", "light trails", "neon glow", "bioluminescence",
    # Sky & Clouds (15)
    "clouds timelapse", "storm clouds", "blue sky", "sunset clouds", "cirrus clouds",
    "cumulus clouds", "dramatic sky", "sky aerial view", "cloud formations", "overcast sky",
    "clear sky stars", "twilight sky", "dusk atmosphere", "heaven clouds", "skyscape panorama",
    # Abstract & Artistic (15)
    "ink water abstract", "paint swirls", "smoke patterns", "particle effects", "light painting",
    "motion blur", "kaleidoscope", "fractal patterns", "geometric shapes", "color gradient",
    "texture closeup", "prism refraction", "holographic effect", "digital art motion", "abstract flow",
    # Symbolic Objects (15)
    "chain links", "rope knot", "compass direction", "hourglass time", "clock mechanism",
    "key lock", "mirror reflection", "candle meditation", "incense smoke", "crystal ball",
    "feather floating", "leaf falling", "flower blooming", "tree branches", "wooden texture",
    # Human Silhouettes (15)
    "person silhouette sunset", "meditation silhouette", "yoga pose backlight", "walking figure shadow", "hands reaching sky",
    "person jumping", "dance silhouette", "runner motion blur", "hiker mountain back", "prayer hands",
    "open arms freedom", "shadow figure", "person beach distant", "crowd silhouette", "human back view",
    # Cityscapes & Urban (15)
    "city lights night", "skyscraper timelapse", "traffic light trails", "building architecture", "urban skyline",
    "bridge structure", "street night blur", "neon signs", "city rain", "rooftop view",
    "urban aerial", "metropolis night", "modern architecture", "glass building reflection", "city bokeh",
    # Textures & Patterns (15)
    "marble texture", "gold particles", "diamond sparkle", "silk fabric", "sand texture",
    "wood grain", "stone surface", "metal texture", "glass shatter", "paper texture",
    "leather surface", "concrete pattern", "rust oxidation", "ice texture", "wave patterns",
    # Motion & Energy (15)
    "energy waves", "electromagnetic field", "sound waves", "vibration frequency", "pulse rhythm",
    "flow motion", "spinning rotation", "swirling vortex", "ripple effect", "expansion growth",
    "transformation change", "dynamic movement", "speed motion", "acceleration fast", "momentum energy",
    # Spiritual Symbols (15)
    "lotus flower", "mandala pattern", "zen garden", "yin yang symbol", "infinity symbol",
    "sacred circle", "triangle pyramid", "spiral pattern", "tree of life", "eye symbol",
    "angel wings", "dove flying", "butterfly transformation", "phoenix rising", "dragon symbol",
    # Time & Seasons (15)
    "autumn leaves", "winter snow", "spring bloom", "summer sun", "seasons change",
    "day to night", "moon cycle", "tide change", "growth timelapse", "decay transformation",
    "clock timelapse", "sundial shadow", "calendar pages", "hourglass sand", "time passage"
]

class VideoGenerator:
    def __init__(self):
        self.video_sources = VideoSourceManager()
        self.output_dir = "output"
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.fonts_dir = os.path.join(self.base_dir, "fonts")
        self.music_dir = os.path.join(self.base_dir, "music")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.fonts_dir, exist_ok=True)
        self.size = (1080, 1920)
        self.fps = 30

        # Download Bebas Neue font if not exists
        self._ensure_font()

    def _ensure_font(self):
        """Download Bebas Neue Bold font if missing"""
        font_path = os.path.join(self.fonts_dir, "BebasNeue-Regular.ttf")

        if not os.path.exists(font_path):
            print("   📥 Downloading Bebas Neue font...")
            try:
                font_url = "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf"
                response = requests.get(font_url, timeout=30)
                with open(font_path, 'wb') as f:
                    f.write(response.content)
                print("   ✅ Font downloaded")
            except Exception as e:
                print(f"   ⚠️  Font download failed: {e}")

    def wrap_text_smart(self, text, max_width=900, font_size=52):
        """
        Wrap text into EXACTLY 2 lines that fit within max width
        FIXED FONT SIZE - no shrinking for consistency
        Returns (lines, font_size) - list of 2 lines and the font size
        """
        from PIL import ImageFont, Image, ImageDraw

        # Load font for measurement
        font_path = os.path.join(self.fonts_dir, "BebasNeue-Regular.ttf")
        if not os.path.exists(font_path):
            font_path = os.path.join(self.fonts_dir, "Montserrat-Bold.ttf")

        # FIXED font size - no auto-reduction for consistent look
        font = ImageFont.truetype(font_path, font_size)

        # ALL CAPS
        text_upper = text.upper()
        words = text_upper.split()

        # If very short (1-3 words), split evenly
        if len(words) <= 3:
            mid = len(words) // 2
            if mid == 0:
                # Only 1 word - put on first line, leave second empty
                return ([text_upper, ''], font_size)
            line1 = ' '.join(words[:mid]) if mid > 0 else ''
            line2 = ' '.join(words[mid:])
            return ([line1, line2], font_size)

        # Try to split into 2 lines naturally
        # Start from middle and find best split point
        total_words = len(words)
        best_split = total_words // 2

        # Try splits around the midpoint to find one that fits
        for offset in range(0, max(total_words // 2, 1)):
            for direction in [0, 1, -1]:  # Try middle first, then +offset, then -offset
                if direction == 0:
                    split_point = best_split
                elif direction == 1:
                    split_point = best_split + offset
                else:
                    split_point = best_split - offset

                if split_point <= 0 or split_point >= total_words:
                    continue

                line1 = ' '.join(words[:split_point])
                line2 = ' '.join(words[split_point:])

                # Measure both lines
                temp_img = Image.new('RGB', (1, 1))
                temp_draw = ImageDraw.Draw(temp_img)

                bbox1 = temp_draw.textbbox((0, 0), line1, font=font)
                width1 = bbox1[2] - bbox1[0]

                bbox2 = temp_draw.textbbox((0, 0), line2, font=font)
                width2 = bbox2[2] - bbox2[0]

                # Both lines must fit within max width
                if width1 <= max_width and width2 <= max_width:
                    return ([line1, line2], font_size)

        # Fallback: force split at midpoint (fixed font size)
        mid = total_words // 2
        if mid == 0:
            mid = 1
        line1 = ' '.join(words[:mid])
        line2 = ' '.join(words[mid:])
        return ([line1, line2], font_size)

    def break_into_chunks(self, text, chunk_size=4):
        """
        Break text into smaller chunks for rapid display
        Each chunk will be 3-5 words for quick tempo changes
        """
        words = text.split()
        chunks = []

        i = 0
        while i < len(words):
            # Take 3-5 words per chunk (vary slightly for natural feel)
            import random
            actual_chunk_size = min(random.choice([3, 4, 4, 5]), len(words) - i)
            chunk = ' '.join(words[i:i + actual_chunk_size])
            chunks.append(chunk)
            i += actual_chunk_size

        return chunks

    def create_text_clips(self, content, voice_duration, voice_timings=None, text_color=(255, 200, 0)):
        """
        Create text clips synced with voice timing

        Args:
            text_color: RGB tuple for accent text color
        Breaks text into smaller chunks that change rapidly with speaker tempo
        """
        segments = [
            content['hook'],
            content['meaning'],
            content['action'],
            content['cta']
        ]

        text_clips = []

        if voice_timings:
            # Use precise voice timings for perfect sync
            print(f"   ✅ Using precise voice timings with rapid text changes")

            for i, timing in enumerate(voice_timings):
                # Break segment into smaller chunks (3-5 words each)
                chunks = self.break_into_chunks(timing['text'])

                # Distribute segment duration across chunks
                chunk_duration = timing['duration'] / len(chunks)

                for j, chunk in enumerate(chunks):
                    # Calculate timing for this chunk
                    chunk_start = timing['start'] + (j * chunk_duration)

                    # Smart wrap text to fit screen (returns lines and font size)
                    lines, font_size = self.wrap_text_smart(chunk)

                    # Create text clip for this chunk
                    text_clip = self._create_text_clip(
                        lines=lines,
                        duration=chunk_duration,
                        start_time=chunk_start,
                        font_size=font_size,
                        text_color=text_color
                    )

                    text_clips.append(text_clip)

            print(f"   ✅ Created {len(text_clips)} rapid text chunks (synced with speaker tempo)")
        else:
            # Fallback: Equal time distribution with chunks
            segment_duration = voice_duration / 4

            for i, segment in enumerate(segments):
                # Calculate segment timing
                segment_start = i * segment_duration

                # Break segment into smaller chunks
                chunks = self.break_into_chunks(segment)

                # Distribute segment duration across chunks
                chunk_duration = segment_duration / len(chunks)

                for j, chunk in enumerate(chunks):
                    # Calculate timing for this chunk
                    chunk_start = segment_start + (j * chunk_duration)

                    # Smart wrap text to fit screen (returns lines and font size)
                    lines, font_size = self.wrap_text_smart(chunk)

                    # Create text clip
                    text_clip = self._create_text_clip(
                        lines=lines,
                        duration=chunk_duration,
                        start_time=chunk_start,
                        font_size=font_size,
                        text_color=text_color
                    )

                    text_clips.append(text_clip)

            print(f"   ✅ Created {len(text_clips)} rapid text chunks (equal timing)")

        return text_clips

    def _create_text_clip(self, lines, duration, start_time, font_size=52, text_color=(255, 200, 0)):
        """
        Create text overlay that fits on screen
        Supports exactly 2 lines with alternating white/accent colors
        Uses FIXED font size for consistency across all text

        Args:
            text_color: RGB tuple for accent color (alternates with white)
        """
        def make_frame(t):
            # Create image
            img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Load font
            font_path = os.path.join(self.fonts_dir, "BebasNeue-Regular.ttf")
            if not os.path.exists(font_path):
                font_path = os.path.join(self.fonts_dir, "Montserrat-Bold.ttf")

            font = ImageFont.truetype(font_path, font_size)

            # Fade animation (shorter for rapid text changes)
            alpha = 255
            # Dynamic fade: 15% of duration, max 0.2s for rapid chunks
            fade_duration = min(0.2, duration * 0.15)
            if t < fade_duration:
                alpha = int(255 * (t / fade_duration))
            elif t > duration - fade_duration:
                alpha = int(255 * ((duration - t) / fade_duration))

            # Position text in lower third (adjust based on line count)
            line_height = 60  # Gap between Lines in a text block
            total_text_height = len(lines) * line_height

            # Center vertically in lower third
            y_start = 1400 - (total_text_height // 2)

            # Draw all lines with alternating colors
            for i, line in enumerate(lines):
                if not line:
                    continue

                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (1080 - text_width) // 2
                y = y_start + (i * line_height)

                # Alternate colors: odd lines = white, even lines = accent color
                if i % 2 == 0:
                    fill_color = (255, 255, 255, alpha)  # WHITE
                else:
                    fill_color = (*text_color, alpha)    # ACCENT COLOR (from parameter)

                draw.text(
                    (x, y),
                    line,
                    font=font,
                    fill=fill_color,
                    stroke_width=3,
                    stroke_fill=(0, 0, 0, alpha)
                )

            # Convert RGBA to RGB and extract alpha as separate mask
            # moviepy 1.0.3 requires explicit RGB + mask, not RGBA
            img_array = np.array(img)
            return img_array[:, :, :3]  # Return RGB only

        def make_mask(t):
            # Create same image to extract alpha channel
            img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            font_path = os.path.join(self.fonts_dir, "BebasNeue-Regular.ttf")
            if not os.path.exists(font_path):
                font_path = os.path.join(self.fonts_dir, "Montserrat-Bold.ttf")

            font = ImageFont.truetype(font_path, font_size)

            alpha = 255
            fade_duration = min(0.2, duration * 0.15)
            if t < fade_duration:
                alpha = int(255 * (t / fade_duration))
            elif t > duration - fade_duration:
                alpha = int(255 * ((duration - t) / fade_duration))

            # Same positioning logic as make_frame
            line_height = 60
            total_text_height = len(lines) * line_height
            y_start = 1400 - (total_text_height // 2)

            # Draw all lines with alternating colors (same as make_frame)
            for i, line in enumerate(lines):
                if not line:
                    continue

                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (1080 - text_width) // 2
                y = y_start + (i * line_height)

                # Alternate colors: odd lines = white, even lines = accent color
                if i % 2 == 0:
                    fill_color = (255, 255, 255, alpha)
                else:
                    fill_color = (*text_color, alpha)

                draw.text(
                    (x, y),
                    line,
                    font=font,
                    fill=fill_color,
                    stroke_width=3,
                    stroke_fill=(0, 0, 0, alpha)
                )

            # Extract and normalize alpha channel for mask (0-1 range)
            img_array = np.array(img)
            return img_array[:, :, 3] / 255.0  # Return alpha channel normalized

        # Create clip with proper duration and timing
        clip = VideoClip(make_frame, duration=duration)
        mask = VideoClip(make_mask, duration=duration, ismask=True)
        clip = clip.set_mask(mask)
        clip = clip.set_start(start_time)

        return clip

    def generate_video(self, content, voice_path, output_path, style_name, voice_timings=None, text_color=(255, 200, 0)):
        """
        Generate video reel with synced text

        Args:
            text_color: RGB tuple for the accent text color (default: yellow/orange)
        """

        voice_audio = AudioFileClip(voice_path)
        main_duration = voice_audio.duration

        print(f"   🎙️  Voice duration: {main_duration:.1f}s")
        if voice_timings:
            print(f"   🎯 Text will be synced with speaker timing")

        # Duration validation
        total_duration = main_duration + 2  # Add 2s end card
        if main_duration > 28:
            print(f"   ⚠️  WARNING: Voice is {main_duration:.1f}s (over 28s limit)")
            print(f"   ⚠️  Final reel will be ~{total_duration:.1f}s with end card")
            if total_duration > 35:
                print(f"   ❌ ERROR: Total duration {total_duration:.1f}s exceeds 35s hard limit")
                print(f"   ❌ Content is too long. Please regenerate with shorter content.")
                # Don't fail completely, but warn user
        elif total_duration <= 30:
            print(f"   ✅ Duration check passed: {total_duration:.1f}s total (under 30s target)")
        else:
            print(f"   ⚠️  Total duration {total_duration:.1f}s is between 30-35s (acceptable but not ideal)")

        query = random.choice(VIDEO_QUERIES)
        print(f"   Fetching: '{query}'")

        video_data = self.video_sources.fetch_multiple_videos(query, count=4)

        if not video_data:
            print(f"   ❌ No videos found")
            return None

        # Download video clips
        video_clips = []
        video_sources = []
        for i, video_info in enumerate(video_data[:4]):
            temp_path = f"{self.output_dir}/bg_temp_{i}.mp4"
            if self._download_video(video_info['url'], temp_path):
                video_clips.append(temp_path)
                video_sources.append(video_info['source'])

        if not video_clips:
            print(f"   ❌ Failed to download videos")
            return None

        print(f"   ✅ Downloaded {len(video_clips)} clips")

        try:
            # Create properly cropped video montage
            background = self._create_proper_montage(video_clips, main_duration)

            # Create text clips synced with voice timing (or equal distribution if no timings)
            text_clips = self.create_text_clips(content, main_duration, voice_timings, text_color)

            # Create static THE17PROJECT watermark (always visible)
            brand_watermark = self._create_static_brand_watermark(main_duration)
            print(f"   ✅ Added static THE17PROJECT watermark")

            # Create barely visible source watermark (bottom left)
            source_watermark = self._create_source_watermark(video_sources[0], main_duration)
            print(f"   ✅ Added source watermark (bottom left, barely visible)")

            # Composite: video + text + watermarks
            main_composite = CompositeVideoClip(
                [background] + text_clips + [brand_watermark, source_watermark],
                size=self.size
            )
            main_composite = main_composite.set_duration(main_duration)

            # Create 2-second end card
            print(f"   ✅ Creating 2-second end card...")
            end_card = self._create_end_card(text_color)
            end_card = end_card.set_start(main_duration)

            # Combine main video + end card
            total_duration = main_duration + 2  # Add 2 seconds for end card
            final_video = CompositeVideoClip(
                [main_composite, end_card],
                size=self.size
            ).set_duration(total_duration)

            # Add audio with music that covers full duration (including end card)
            print(f"   🎵 Mixing audio for {total_duration:.1f}s (voice + music)...")
            final_audio = self._mix_audio(voice_audio, total_duration)
            final_video = final_video.set_audio(final_audio)

            # Render HIGH QUALITY for Instagram (Slack will compress on upload)
            print(f"   ⏳ Rendering HIGH QUALITY video for Instagram...")
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                bitrate='6000k',  # 6Mbps video = HIGH QUALITY (~12-15MB for 20-25s)
                audio_bitrate='192k',  # High quality audio
                threads=4,
                preset='slow',  # Best quality compression
                logger='bar'  # Show progress bar
            )

            print(f"   ✅ Render complete!")

            # Cleanup
            for clip_path in video_clips:
                if os.path.exists(clip_path):
                    os.remove(clip_path)

            return output_path

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_proper_montage(self, video_clips, target_duration):
        """Create montage with proper aspect ratio (crop, don't squish)"""

        num_clips = len(video_clips)
        clip_duration = target_duration / num_clips

        print(f"   Creating montage: {num_clips} clips x {clip_duration:.1f}s each")

        processed_clips = []
        target_aspect = 9 / 16

        for i, clip_path in enumerate(video_clips):
            clip = VideoFileClip(clip_path)

            # CRITICAL: Convert to RGB (remove alpha channel if present)
            # moviepy 1.0.3 has issues compositing RGBA video clips
            def rgb_converter(frame):
                if len(frame.shape) == 3 and frame.shape[2] == 4:
                    return frame[:, :, :3]  # Strip alpha channel
                return frame

            clip = clip.fl_image(rgb_converter)
            clip_aspect = clip.w / clip.h

            # Fix aspect ratio - CROP, don't squish
            if abs(clip_aspect - target_aspect) > 0.01:
                if clip_aspect > target_aspect:
                    # Too wide - crop sides
                    new_width = int(clip.h * target_aspect)
                    x_center = clip.w / 2
                    clip = clip.fx(vfx.crop, x1=(x_center - new_width/2), x2=(x_center + new_width/2))
                else:
                    # Too tall - crop top/bottom
                    new_height = int(clip.w / target_aspect)
                    y_center = clip.h / 2
                    clip = clip.fx(vfx.crop, y1=(y_center - new_height/2), y2=(y_center + new_height/2))

            # Resize to exact dimensions
            clip = clip.fx(vfx.resize, newsize=self.size)

            # Extract segment
            if clip.duration >= clip_duration:
                start_time = max(0, (clip.duration - clip_duration) / 2)
                clip = clip.subclip(start_time, start_time + clip_duration)
            else:
                clip = clip.set_duration(clip_duration)

            # Set start time
            clip = clip.set_start(i * clip_duration)
            processed_clips.append(clip)

        final_montage = CompositeVideoClip(processed_clips, size=self.size)
        return final_montage.set_duration(target_duration)

    def _create_brand_watermark(self, duration):
        """Create THE17PROJECT watermark (below captions, one third from top)"""

        def make_frame(t):
            img = Image.new('RGBA', self.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Same font as main text, smaller
            font_path = os.path.join(self.fonts_dir, "BebasNeue-Regular.ttf")
            if not os.path.exists(font_path):
                font_path = os.path.join(self.fonts_dir, "Montserrat-Bold.ttf")

            font = ImageFont.truetype(font_path, 28)

            text = "The17Project"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]

            # Position below captions at one third of screen height
            x = (self.size[0] - text_width) // 2  # Horizontal center
            y = int(self.size[1] / 3) + 120  # One third + offset below captions

            # WHITE text with subtle BLACK outline
            draw.text(
                (x, y),
                text,
                font=font,
                fill=(255, 255, 255, 255),  # WHITE fill
                stroke_width=2,  # Subtle outline
                stroke_fill=(0, 0, 0, 255)  # BLACK stroke
            )

            # Convert RGBA to RGB (moviepy 1.0.3 compatibility)
            img_array = np.array(img)
            return img_array[:, :, :3]

        def make_mask(t):
            img = Image.new('RGBA', self.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            font_path = os.path.join(self.fonts_dir, "BebasNeue-Regular.ttf")
            if not os.path.exists(font_path):
                font_path = os.path.join(self.fonts_dir, "Montserrat-Bold.ttf")

            font = ImageFont.truetype(font_path, 28)

            text = "The17Project"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]

            x = (self.size[0] - text_width) // 2
            y = int(self.size[1] / 3) + 120

            draw.text(
                (x, y),
                text,
                font=font,
                fill=(255, 255, 255, 255),
                stroke_width=2,
                stroke_fill=(0, 0, 0, 255)
            )

            # Extract alpha channel for mask
            img_array = np.array(img)
            return img_array[:, :, 3] / 255.0

        clip = VideoClip(make_frame, duration=duration)
        mask = VideoClip(make_mask, duration=duration, ismask=True)
        return clip.set_mask(mask)

    def _create_static_brand_watermark(self, duration):
        """Create static THE17PROJECT watermark (always visible, no fade)"""

        def make_frame(t):
            img = Image.new('RGBA', self.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Load font
            font_path = os.path.join(self.fonts_dir, "BebasNeue-Regular.ttf")
            if not os.path.exists(font_path):
                font_path = os.path.join(self.fonts_dir, "Montserrat-Bold.ttf")

            watermark_font = ImageFont.truetype(font_path, 28)
            watermark = "The17Project"

            # Calculate position (centered, below text area in lower third)
            bbox = draw.textbbox((0, 0), watermark, font=watermark_font)
            w_width = bbox[2] - bbox[0]
            w_x = (1080 - w_width) // 2
            w_y = 1500  # Fixed position in lower third

            # Static - always full opacity (no alpha fade)
            draw.text(
                (w_x, w_y),
                watermark,
                font=watermark_font,
                fill=(255, 255, 255, 255),  # Full opacity white
                stroke_width=2,
                stroke_fill=(0, 0, 0, 255)  # Full opacity black outline
            )

            # Convert RGBA to RGB (moviepy 1.0.3 compatibility)
            img_array = np.array(img)
            return img_array[:, :, :3]

        def make_mask(t):
            img = Image.new('RGBA', self.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            font_path = os.path.join(self.fonts_dir, "BebasNeue-Regular.ttf")
            if not os.path.exists(font_path):
                font_path = os.path.join(self.fonts_dir, "Montserrat-Bold.ttf")

            watermark_font = ImageFont.truetype(font_path, 28)
            watermark = "The17Project"

            bbox = draw.textbbox((0, 0), watermark, font=watermark_font)
            w_width = bbox[2] - bbox[0]
            w_x = (1080 - w_width) // 2
            w_y = 1500

            draw.text(
                (w_x, w_y),
                watermark,
                font=watermark_font,
                fill=(255, 255, 255, 255),
                stroke_width=2,
                stroke_fill=(0, 0, 0, 255)
            )

            # Extract alpha channel for mask
            img_array = np.array(img)
            return img_array[:, :, 3] / 255.0

        clip = VideoClip(make_frame, duration=duration)
        mask = VideoClip(make_mask, duration=duration, ismask=True)
        return clip.set_mask(mask)

    def _create_source_watermark(self, source_name, duration):
        """Create barely visible source watermark (BOTTOM LEFT)"""

        def make_frame(t):
            img = Image.new('RGBA', self.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Small simple font
            font_path = os.path.join(self.fonts_dir, "Montserrat-Bold.ttf")
            font = ImageFont.truetype(font_path, 16)

            text = f"Source: {source_name}"

            # BOTTOM LEFT (barely visible)
            x = 15
            y = 1880

            # Semi-transparent white (barely visible)
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 100))

            # Convert RGBA to RGB (moviepy 1.0.3 compatibility)
            img_array = np.array(img)
            return img_array[:, :, :3]

        def make_mask(t):
            img = Image.new('RGBA', self.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            font_path = os.path.join(self.fonts_dir, "Montserrat-Bold.ttf")
            font = ImageFont.truetype(font_path, 16)

            text = f"Source: {source_name}"

            x = 15
            y = 1880

            draw.text((x, y), text, font=font, fill=(255, 255, 255, 100))

            # Extract alpha channel for mask
            img_array = np.array(img)
            return img_array[:, :, 3] / 255.0

        clip = VideoClip(make_frame, duration=duration)
        mask = VideoClip(make_mask, duration=duration, ismask=True)
        return clip.set_mask(mask)

    def _create_end_card(self, text_color=(255, 200, 0)):
        """
        Create 2-second end card - clean purple logo

        Args:
            text_color: RGB tuple for slogan text color
        """

        def make_frame(t):
            # Dark background
            img = Image.new('RGB', self.size, (15, 15, 30))
            draw = ImageDraw.Draw(img)

            # Load font
            font_path = os.path.join(self.fonts_dir, "BebasNeue-Regular.ttf")
            if not os.path.exists(font_path):
                font_path = os.path.join(self.fonts_dir, "Montserrat-Bold.ttf")

            # THE17PROJECT logo - large, clean purple
            logo_font = ImageFont.truetype(font_path, 110)
            logo_text = "The17Project"

            bbox = draw.textbbox((0, 0), logo_text, font=logo_font)
            text_width = bbox[2] - bbox[0]
            x = (self.size[0] - text_width) // 2
            y = 800

            # Simple PURPLE text with thin black outline
            draw.text(
                (x, y),
                logo_text,
                font=logo_font,
                fill=(147, 112, 219, 255),  # Medium purple
                stroke_width=2,  # Thin outline
                stroke_fill=(0, 0, 0, 255)  # Black outline
            )

            # Slogan below logo
            slogan_font = ImageFont.truetype(font_path, 35)
            slogan = "UNLOCK YOUR DIVINE MESSAGES"

            bbox2 = draw.textbbox((0, 0), slogan, font=slogan_font)
            slogan_width = bbox2[2] - bbox2[0]
            slogan_x = (self.size[0] - slogan_width) // 2
            slogan_y = 940

            # Accent color slogan text (matches reel text color)
            draw.text(
                (slogan_x, slogan_y),
                slogan,
                font=slogan_font,
                fill=(*text_color, 255)  # Matches reel text accent color
            )

            return np.array(img)

        return VideoClip(make_frame, duration=2)

    def fetch_background_music(self):
        """Fetch spiritual music from Pixabay Music API

        Note: Pixabay's public API primarily supports images/videos.
        For audio, this may not work reliably. Falls back to local music.
        """

        # Check if API key is available
        if not os.getenv('PIXABAY_API_KEY'):
            print(f"   ⚠️  PIXABAY_API_KEY not set, skipping Pixabay music")
            return None

        moods = ["meditation", "spiritual", "ambient", "calm", "peaceful"]
        mood = random.choice(moods)

        # Pixabay API endpoint (Note: may not reliably return audio)
        url = "https://pixabay.com/api/"
        params = {
            "key": os.getenv('PIXABAY_API_KEY'),
            "q": f"{mood} music",
            "audio_type": "music",
            "per_page": 20
        }

        try:
            print(f"   🎵 Trying to fetch {mood} music from Pixabay...")
            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            if data.get('hits'):
                track = random.choice(data['hits'])

                # Try different URL fields that might contain audio
                music_url = track.get('previewURL') or track.get('preview') or track.get('download')

                if not music_url:
                    print(f"   ⚠️  No valid audio URL found in response")
                    return None

                track_name = track.get('tags', 'background music')

                # Download to temp file
                temp_music_path = os.path.join(self.output_dir, "temp_music.mp3")
                print(f"   📥 Downloading: {track_name[:50]}...")

                music_response = requests.get(music_url, stream=True, timeout=60)

                # Check content type to verify it's audio
                content_type = music_response.headers.get('content-type', '')
                if 'audio' not in content_type and 'mpeg' not in content_type:
                    print(f"   ⚠️  Downloaded file is not audio (type: {content_type})")
                    return None

                with open(temp_music_path, 'wb') as f:
                    for chunk in music_response.iter_content(chunk_size=8192):
                        f.write(chunk)

                # Verify file size (audio should be reasonably sized)
                file_size = os.path.getsize(temp_music_path)
                if file_size < 10000:  # Less than 10KB is probably not valid audio
                    print(f"   ⚠️  Downloaded file too small ({file_size} bytes), not valid audio")
                    os.remove(temp_music_path)
                    return None

                print(f"   ✅ Music downloaded ({file_size // 1024}KB)")
                return temp_music_path
            else:
                print(f"   ⚠️  No results from Pixabay API")
                return None

        except Exception as e:
            print(f"   ⚠️  Pixabay fetch failed: {e}")
            return None

    def _mix_audio(self, voice_audio, total_duration):
        """Mix voice with background music (fetches from Pixabay)"""

        from moviepy.audio.AudioClip import AudioClip

        # Extend voice audio with silence to match total duration (end card needs silence)
        voice_duration = voice_audio.duration
        end_card_duration = total_duration - voice_duration

        if end_card_duration > 0:
            silence = AudioClip(lambda t: [0, 0], duration=end_card_duration)
            extended_voice = CompositeAudioClip([voice_audio, silence.set_start(voice_duration)])
        else:
            extended_voice = voice_audio

        # Try to fetch music from Pixabay first
        music_path = self.fetch_background_music()

        # Fall back to local music if Pixabay fails
        if not music_path:
            music_files = glob.glob(os.path.join(self.music_dir, "*.mp3")) + \
                          glob.glob(os.path.join(self.music_dir, "*.wav"))

            if music_files:
                music_path = random.choice(music_files)
                print(f"   ✅ Using local music: {os.path.basename(music_path)}")
            else:
                print(f"   ⚠️  No music available, using voice only")
                return extended_voice

        try:
            from moviepy.audio.AudioClip import AudioClip

            music_audio = AudioFileClip(music_path)

            # Loop music if needed to cover full duration (including end card)
            if music_audio.duration < total_duration:
                loops_needed = int(total_duration / music_audio.duration) + 1
                # Manually loop by concatenating clips
                music_clips = [music_audio] * loops_needed
                from moviepy.audio.AudioClip import concatenate_audioclips
                music_audio = concatenate_audioclips(music_clips)

            # Trim to exact duration
            music_audio = music_audio.subclip(0, total_duration)

            # Set music volume to 15% by wrapping get_frame
            original_get_frame = music_audio.get_frame

            def get_frame_lowvolume(t):
                return 0.15 * original_get_frame(t)

            music_audio_quiet = AudioClip(get_frame_lowvolume, duration=total_duration, fps=music_audio.fps)

            # Mix voice + music
            final_audio = CompositeAudioClip([extended_voice, music_audio_quiet])

            # Cleanup temp music file if it was from Pixabay
            if music_path and 'temp_music.mp3' in music_path and os.path.exists(music_path):
                try:
                    os.remove(music_path)
                except:
                    pass

            return final_audio

        except Exception as e:
            print(f"   ⚠️  Audio mixing failed: {e}")
            return extended_voice

    def _download_video(self, url, output_path):
        """Download video from URL"""
        try:
            response = requests.get(url, stream=True, timeout=60)
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"   ⚠️  Download failed: {e}")
            return False
