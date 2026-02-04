"""
Carousel Generator for THE17PROJECT
Generates swipeable carousel posts (static images) for Instagram

Design specs:
- 1080x1920px (9:16 portrait format - same as reels)
- Dark background matching video aesthetic
- Bebas Neue font (same as videos)
- ALL TEXT CENTERED on every slide
- THE17PROJECT branding
"""

import os
import random
from PIL import Image, ImageDraw, ImageFont
from life_path_database import get_life_path_data, get_all_life_paths


class CarouselGenerator:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.fonts_dir = os.path.join(self.base_dir, "fonts")
        self.output_dir = os.path.join(self.base_dir, "output", "carousels")
        os.makedirs(self.output_dir, exist_ok=True)

        # 9:16 portrait format (same as reels)
        self.size = (1080, 1920)

        # Color scheme (matching video aesthetic)
        self.colors = {
            'background': (15, 15, 30),           # Dark blue-black
            'primary_text': (255, 255, 255),      # White
            'accent': (147, 112, 219),            # Purple (brand color)
            'secondary_accent': (255, 200, 0),    # Yellow/Orange
            'muted': (150, 150, 170),             # Muted gray
            'highlight': (255, 100, 150),         # Pink
        }

        self._ensure_fonts()

    def _ensure_fonts(self):
        """Ensure fonts are available"""
        self.font_bebas = os.path.join(self.fonts_dir, "BebasNeue-Regular.ttf")
        self.font_montserrat = os.path.join(self.fonts_dir, "Montserrat-Bold.ttf")

    def _get_font(self, size):
        """Get font with specified size"""
        try:
            return ImageFont.truetype(self.font_bebas, size)
        except:
            try:
                return ImageFont.truetype(self.font_montserrat, size)
            except:
                return ImageFont.load_default()

    def _create_base_image(self):
        """Create base image with gradient background"""
        img = Image.new('RGB', self.size, self.colors['background'])
        draw = ImageDraw.Draw(img)

        # Add subtle gradient effect
        for y in range(self.size[1]):
            ratio = y / self.size[1]
            r = int(15 + (10 * ratio))
            g = int(15 + (5 * ratio))
            b = int(30 + (15 * ratio))
            draw.line([(0, y), (self.size[0], y)], fill=(r, g, b))

        return img, draw

    def _add_watermark(self, draw):
        """Add THE17PROJECT watermark at bottom"""
        font = self._get_font(32)
        text = "The17Project"

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.size[0] - text_width) // 2
        y = self.size[1] - 80

        draw.text(
            (x, y),
            text,
            font=font,
            fill=self.colors['accent'],
            stroke_width=1,
            stroke_fill=(0, 0, 0)
        )

    def _add_slide_indicator(self, draw, current, total):
        """Add slide indicator dots"""
        dot_radius = 8
        dot_spacing = 24
        total_width = (total * dot_radius * 2) + ((total - 1) * dot_spacing)
        start_x = (self.size[0] - total_width) // 2
        y = self.size[1] - 140

        for i in range(total):
            x = start_x + i * (dot_radius * 2 + dot_spacing)
            color = self.colors['accent'] if i == current - 1 else self.colors['muted']
            draw.ellipse(
                [x, y, x + dot_radius * 2, y + dot_radius * 2],
                fill=color
            )

    def _draw_text_centered(self, draw, text, y, font, color, stroke=True):
        """Draw text horizontally centered at given y position"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.size[0] - text_width) // 2

        if stroke:
            draw.text((x, y), text, font=font, fill=color, stroke_width=2, stroke_fill=(0, 0, 0))
        else:
            draw.text((x, y), text, font=font, fill=color)

        return bbox[3] - bbox[1]  # Return text height

    def _draw_wrapped_text_centered(self, draw, text, y, font, color, max_width=900, line_spacing=15):
        """Draw wrapped text, all lines centered"""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        total_height = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (self.size[0] - text_width) // 2

            draw.text((x, y + total_height), line, font=font, fill=color, stroke_width=2, stroke_fill=(0, 0, 0))
            total_height += text_height + line_spacing

        return total_height

    def _draw_bullet_list_centered(self, draw, items, start_y, font, color, max_items=5):
        """Draw a centered bullet list"""
        line_height = font.size + 20
        y = start_y

        for item in items[:max_items]:
            text = f"• {item.upper()}"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]

            # Center the bullet point text
            x = (self.size[0] - text_width) // 2

            draw.text((x, y), text, font=font, fill=color, stroke_width=1, stroke_fill=(0, 0, 0))
            y += line_height

        return y

    # =========================================================================
    # LIFE PATH BREAKDOWN CAROUSEL (10 slides)
    # =========================================================================

    def generate_life_path_breakdown(self, life_path_number):
        """Generate 10-slide Life Path Breakdown carousel"""
        lp_data = get_life_path_data(life_path_number)
        if not lp_data:
            print(f"   ❌ No data found for Life Path {life_path_number}")
            return None

        slides = []
        carousel_dir = os.path.join(self.output_dir, f"LP{life_path_number}_breakdown")
        os.makedirs(carousel_dir, exist_ok=True)

        # Generate each slide
        slides.append(self._slide_cover(life_path_number, lp_data, 1, 10))
        slides.append(self._slide_core_traits(life_path_number, lp_data, 2, 10))
        slides.append(self._slide_strengths(life_path_number, lp_data, 3, 10))
        slides.append(self._slide_challenges(life_path_number, lp_data, 4, 10))
        slides.append(self._slide_careers(life_path_number, lp_data, 5, 10))
        slides.append(self._slide_compatibility(life_path_number, lp_data, 6, 10))
        slides.append(self._slide_purpose(life_path_number, lp_data, 7, 10))
        slides.append(self._slide_shadow(life_path_number, lp_data, 8, 10))
        slides.append(self._slide_growth(life_path_number, lp_data, 9, 10))
        slides.append(self._slide_cta(life_path_number, 10, 10))

        # Save slides
        slide_paths = []
        for i, slide in enumerate(slides, 1):
            path = os.path.join(carousel_dir, f"slide_{i:02d}.png")
            slide.save(path, "PNG", quality=95)
            slide_paths.append(path)
            print(f"   ✅ Saved slide {i}/10")

        return {
            'type': 'life_path_breakdown',
            'life_path_number': life_path_number,
            'slide_paths': slide_paths,
            'carousel_dir': carousel_dir
        }

    def _slide_cover(self, lp_num, lp_data, slide_num, total):
        """Slide 1: Cover - everything centered"""
        img, draw = self._create_base_image()

        # Center point for vertical layout
        center_y = self.size[1] // 2

        # "LIFE PATH" label
        label_font = self._get_font(60)
        self._draw_text_centered(draw, "LIFE PATH", center_y - 280, label_font, self.colors['muted'])

        # Big number with glow
        number_font = self._get_font(300)
        number = str(lp_num)
        bbox = draw.textbbox((0, 0), number, font=number_font)
        num_width = bbox[2] - bbox[0]
        num_x = (self.size[0] - num_width) // 2

        # Glow effect
        for offset in range(12, 0, -2):
            draw.text((num_x, center_y - 200), number, font=number_font,
                     fill=(*self.colors['accent'][:3], int(60 * (1 - offset/12))),
                     stroke_width=offset + 3, stroke_fill=(0, 0, 0, 30))

        draw.text((num_x, center_y - 200), number, font=number_font,
                 fill=self.colors['accent'], stroke_width=4, stroke_fill=(0, 0, 0))

        # Name (The Leader, etc.)
        name_font = self._get_font(70)
        name = lp_data.get('name', f'Life Path {lp_num}').upper()
        self._draw_text_centered(draw, name, center_y + 150, name_font, self.colors['primary_text'])

        # "THE COMPLETE GUIDE"
        guide_font = self._get_font(40)
        self._draw_text_centered(draw, "THE COMPLETE GUIDE", center_y + 240, guide_font, self.colors['secondary_accent'])

        # Swipe instruction
        swipe_font = self._get_font(32)
        self._draw_text_centered(draw, "SWIPE FOR YOUR BREAKDOWN →", center_y + 400, swipe_font, self.colors['muted'])

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)

        return img

    def _slide_core_traits(self, lp_num, lp_data, slide_num, total):
        """Slide 2: Core Traits - centered"""
        img, draw = self._create_base_image()

        # Header section
        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(80)
        self._draw_text_centered(draw, "CORE TRAITS", 280, title_font, self.colors['primary_text'])

        # Traits list - centered
        traits = lp_data.get('core_traits', {}).get('positive', [])[:6]
        if traits:
            trait_font = self._get_font(42)
            self._draw_bullet_list_centered(draw, traits, 450, trait_font, self.colors['primary_text'], max_items=6)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)

        return img

    def _slide_strengths(self, lp_num, lp_data, slide_num, total):
        """Slide 3: Strengths - centered"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(80)
        self._draw_text_centered(draw, "YOUR STRENGTHS", 280, title_font, self.colors['primary_text'])

        # Key characteristics
        chars = lp_data.get('key_characteristics', [])[:5]
        if chars:
            char_font = self._get_font(38)
            self._draw_bullet_list_centered(draw, chars, 450, char_font, self.colors['primary_text'], max_items=5)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)

        return img

    def _slide_challenges(self, lp_num, lp_data, slide_num, total):
        """Slide 4: Challenges - centered"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(80)
        self._draw_text_centered(draw, "CHALLENGES", 280, title_font, self.colors['highlight'])

        challenges = lp_data.get('challenges', [])[:5]
        if challenges:
            chal_font = self._get_font(38)
            self._draw_bullet_list_centered(draw, challenges, 450, chal_font, self.colors['primary_text'], max_items=5)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)

        return img

    def _slide_careers(self, lp_num, lp_data, slide_num, total):
        """Slide 5: Career Paths - centered"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(80)
        self._draw_text_centered(draw, "IDEAL CAREERS", 280, title_font, self.colors['secondary_accent'])

        careers = lp_data.get('career_paths', [])[:6]
        if careers:
            career_font = self._get_font(44)
            self._draw_bullet_list_centered(draw, careers, 450, career_font, self.colors['primary_text'], max_items=6)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)

        return img

    def _slide_compatibility(self, lp_num, lp_data, slide_num, total):
        """Slide 6: Compatibility - centered"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(80)
        self._draw_text_centered(draw, "COMPATIBILITY", 280, title_font, self.colors['primary_text'])

        compatibility = lp_data.get('compatibility', {})
        y = 450

        # Best matches
        best = compatibility.get('best', [])
        if best:
            label_font = self._get_font(45)
            self._draw_text_centered(draw, "BEST MATCHES", y, label_font, self.colors['highlight'])
            y += 70

            match_font = self._get_font(60)
            match_text = "  ".join([str(m) for m in best])
            self._draw_text_centered(draw, match_text, y, match_font, self.colors['primary_text'])
            y += 120

        # Challenging
        challenging = compatibility.get('challenging', [])
        if challenging:
            label_font = self._get_font(45)
            self._draw_text_centered(draw, "CHALLENGING", y, label_font, self.colors['secondary_accent'])
            y += 70

            match_font = self._get_font(60)
            match_text = "  ".join([str(m) for m in challenging])
            self._draw_text_centered(draw, match_text, y, match_font, self.colors['primary_text'])
            y += 120

        # Neutral
        neutral = compatibility.get('neutral', [])
        if neutral:
            label_font = self._get_font(45)
            self._draw_text_centered(draw, "NEUTRAL", y, label_font, self.colors['muted'])
            y += 70

            match_font = self._get_font(60)
            match_text = "  ".join([str(m) for m in neutral])
            self._draw_text_centered(draw, match_text, y, match_font, self.colors['primary_text'])

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)

        return img

    def _slide_purpose(self, lp_num, lp_data, slide_num, total):
        """Slide 7: Life Purpose - centered"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(80)
        self._draw_text_centered(draw, "YOUR PURPOSE", 280, title_font, self.colors['primary_text'])

        # Purpose text - wrapped and centered
        purpose = lp_data.get('life_purpose', '')
        if purpose:
            purpose_font = self._get_font(46)
            self._draw_wrapped_text_centered(draw, purpose.upper(), 480, purpose_font,
                                            self.colors['secondary_accent'], max_width=900)

        # Archetype
        archetype = lp_data.get('archetype', '')
        if archetype:
            arch_font = self._get_font(38)
            self._draw_text_centered(draw, f"THE {archetype.upper()}", 900, arch_font, self.colors['muted'])

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)

        return img

    def _slide_shadow(self, lp_num, lp_data, slide_num, total):
        """Slide 8: Shadow Work - centered"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(80)
        self._draw_text_centered(draw, "SHADOW WORK", 280, title_font, self.colors['highlight'])

        subtitle_font = self._get_font(35)
        self._draw_text_centered(draw, "WATCH OUT FOR THESE", 380, subtitle_font, self.colors['muted'])

        negatives = lp_data.get('core_traits', {}).get('negative', [])[:5]
        if negatives:
            neg_font = self._get_font(40)
            self._draw_bullet_list_centered(draw, negatives, 500, neg_font, self.colors['primary_text'], max_items=5)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)

        return img

    def _slide_growth(self, lp_num, lp_data, slide_num, total):
        """Slide 9: Growth Tips - centered"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(80)
        self._draw_text_centered(draw, "GROWTH TIPS", 280, title_font, self.colors['secondary_accent'])

        # Generate tips from challenges
        challenges = lp_data.get('challenges', [])[:4]
        tips = []
        for challenge in challenges:
            if 'learning' in challenge.lower():
                tips.append(challenge.replace('Learning to', 'Practice').strip())
            elif 'managing' in challenge.lower():
                tips.append(challenge.replace('Managing', 'Work on managing').strip())
            elif 'avoiding' in challenge.lower():
                tips.append(challenge.replace('Avoiding', 'Consciously avoid').strip())
            else:
                tips.append(f"Focus on: {challenge}")

        if tips:
            tip_font = self._get_font(38)
            self._draw_bullet_list_centered(draw, tips, 450, tip_font, self.colors['primary_text'], max_items=4)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)

        return img

    def _slide_cta(self, lp_num, slide_num, total):
        """Slide 10: CTA - everything centered"""
        img, draw = self._create_base_image()

        center_y = self.size[1] // 2

        # Question
        q_font = self._get_font(55)
        self._draw_text_centered(draw, "WHAT'S YOUR", center_y - 300, q_font, self.colors['muted'])

        # Life Path Number
        lp_font = self._get_font(90)
        self._draw_text_centered(draw, "LIFE PATH NUMBER?", center_y - 200, lp_font, self.colors['primary_text'])

        # Calculate CTA
        calc_font = self._get_font(45)
        self._draw_text_centered(draw, "CALCULATE YOURS FREE", center_y - 40, calc_font, self.colors['secondary_accent'])

        # Link in bio (Instagram-friendly)
        link_font = self._get_font(75)
        self._draw_text_centered(draw, "🔗 LINK IN BIO", center_y + 50, link_font, self.colors['accent'])

        # Website name for visual reference
        site_font = self._get_font(38)
        self._draw_text_centered(draw, "SEVENTHLIFEPATH.COM", center_y + 140, site_font, self.colors['muted'])

        # Save reminder
        save_font = self._get_font(40)
        self._draw_text_centered(draw, "💾 SAVE THIS FOR LATER", center_y + 260, save_font, self.colors['highlight'])

        # Follow CTA
        follow_font = self._get_font(32)
        self._draw_text_centered(draw, "FOLLOW @THE17PROJECT", center_y + 360, follow_font, self.colors['muted'])

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)

        return img


    # =========================================================================
    # LIFE PATH COMPATIBILITY CAROUSEL (6 slides)
    # =========================================================================

    def generate_compatibility_carousel(self, lp1, lp2):
        """Generate 6-slide compatibility carousel for two Life Paths"""
        lp1_data = get_life_path_data(lp1)
        lp2_data = get_life_path_data(lp2)

        if not lp1_data or not lp2_data:
            print(f"   ❌ No data found for Life Path {lp1} or {lp2}")
            return None

        slides = []
        carousel_dir = os.path.join(self.output_dir, f"LP{lp1}_LP{lp2}_compatibility")
        os.makedirs(carousel_dir, exist_ok=True)

        # Determine compatibility level
        compat_level = self._get_compatibility_level(lp1, lp2, lp1_data)

        slides.append(self._compat_cover(lp1, lp2, lp1_data, lp2_data, compat_level, 1, 6))
        slides.append(self._compat_overview(lp1, lp2, lp1_data, lp2_data, compat_level, 2, 6))
        slides.append(self._compat_strengths(lp1, lp2, lp1_data, lp2_data, 3, 6))
        slides.append(self._compat_challenges(lp1, lp2, lp1_data, lp2_data, 4, 6))
        slides.append(self._compat_tips(lp1, lp2, compat_level, 5, 6))
        slides.append(self._slide_cta(lp1, 6, 6))

        slide_paths = []
        for i, slide in enumerate(slides, 1):
            path = os.path.join(carousel_dir, f"slide_{i:02d}.png")
            slide.save(path, "PNG", quality=95)
            slide_paths.append(path)
            print(f"   ✅ Saved slide {i}/6")

        return {
            'type': 'life_path_compatibility',
            'lp1': lp1,
            'lp2': lp2,
            'slide_paths': slide_paths,
            'carousel_dir': carousel_dir
        }

    def _get_compatibility_level(self, lp1, lp2, lp1_data):
        """Determine compatibility level between two Life Paths"""
        compat = lp1_data.get('compatibility', {})
        if lp2 in compat.get('best', []):
            return 'excellent'
        elif lp2 in compat.get('challenging', []):
            return 'challenging'
        else:
            return 'neutral'

    def _compat_cover(self, lp1, lp2, lp1_data, lp2_data, compat_level, slide_num, total):
        """Compatibility cover slide"""
        img, draw = self._create_base_image()
        center_y = self.size[1] // 2

        # Title
        title_font = self._get_font(50)
        self._draw_text_centered(draw, "COMPATIBILITY GUIDE", center_y - 350, title_font, self.colors['muted'])

        # Numbers side by side
        num_font = self._get_font(200)
        combo_text = f"{lp1}  +  {lp2}"
        self._draw_text_centered(draw, combo_text, center_y - 250, num_font, self.colors['accent'])

        # Names
        name_font = self._get_font(45)
        name1 = lp1_data.get('name', f'Life Path {lp1}').upper()
        name2 = lp2_data.get('name', f'Life Path {lp2}').upper()
        self._draw_text_centered(draw, f"{name1}  &  {name2}", center_y + 50, name_font, self.colors['primary_text'])

        # Compatibility rating
        level_colors = {
            'excellent': self.colors['highlight'],
            'neutral': self.colors['secondary_accent'],
            'challenging': self.colors['accent']
        }
        level_text = {
            'excellent': '💚 HIGHLY COMPATIBLE',
            'neutral': '💛 NEUTRAL MATCH',
            'challenging': '🔥 CHALLENGING BUT GROWTH'
        }
        level_font = self._get_font(50)
        self._draw_text_centered(draw, level_text[compat_level], center_y + 180, level_font, level_colors[compat_level])

        swipe_font = self._get_font(32)
        self._draw_text_centered(draw, "SWIPE TO LEARN MORE →", center_y + 350, swipe_font, self.colors['muted'])

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _compat_overview(self, lp1, lp2, lp1_data, lp2_data, compat_level, slide_num, total):
        """Compatibility overview slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp1} + {lp2}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "THE DYNAMIC", 280, title_font, self.colors['primary_text'])

        # Dynamic description based on archetypes
        arch1 = lp1_data.get('archetype', '').split()[0] if lp1_data.get('archetype') else 'Person'
        arch2 = lp2_data.get('archetype', '').split()[0] if lp2_data.get('archetype') else 'Person'

        desc_font = self._get_font(42)
        descriptions = {
            'excellent': f"THE {arch1.upper()} AND {arch2.upper()} CREATE NATURAL HARMONY",
            'neutral': f"THE {arch1.upper()} AND {arch2.upper()} CAN BUILD UNDERSTANDING",
            'challenging': f"THE {arch1.upper()} AND {arch2.upper()} PUSH EACH OTHER TO GROW"
        }
        self._draw_wrapped_text_centered(draw, descriptions[compat_level], 450, desc_font,
                                        self.colors['secondary_accent'], max_width=900)

        # Key traits comparison
        trait_font = self._get_font(36)
        y = 700
        self._draw_text_centered(draw, f"LP {lp1}: {', '.join(lp1_data.get('core_traits', {}).get('positive', [])[:3]).upper()}", y, trait_font, self.colors['muted'])
        y += 60
        self._draw_text_centered(draw, f"LP {lp2}: {', '.join(lp2_data.get('core_traits', {}).get('positive', [])[:3]).upper()}", y, trait_font, self.colors['muted'])

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _compat_strengths(self, lp1, lp2, lp1_data, lp2_data, slide_num, total):
        """Compatibility strengths slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LP {lp1} + LP {lp2}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "RELATIONSHIP STRENGTHS", 280, title_font, self.colors['highlight'])

        # Generate strengths based on traits
        traits1 = lp1_data.get('core_traits', {}).get('positive', [])[:3]
        traits2 = lp2_data.get('core_traits', {}).get('positive', [])[:3]

        strengths = [
            f"{lp1} brings {traits1[0] if traits1 else 'unique energy'}",
            f"{lp2} brings {traits2[0] if traits2 else 'unique energy'}",
            "Together: balance & growth",
            "Mutual respect potential"
        ]

        trait_font = self._get_font(40)
        self._draw_bullet_list_centered(draw, strengths, 450, trait_font, self.colors['primary_text'], max_items=4)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _compat_challenges(self, lp1, lp2, lp1_data, lp2_data, slide_num, total):
        """Compatibility challenges slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LP {lp1} + LP {lp2}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "WATCH OUT FOR", 280, title_font, self.colors['secondary_accent'])

        # Generate challenges based on negative traits
        neg1 = lp1_data.get('core_traits', {}).get('negative', [])[:2]
        neg2 = lp2_data.get('core_traits', {}).get('negative', [])[:2]

        challenges = []
        if neg1:
            challenges.append(f"{lp1}'s {neg1[0]} tendencies")
        if neg2:
            challenges.append(f"{lp2}'s {neg2[0]} tendencies")
        challenges.append("Communication differences")
        challenges.append("Different life priorities")

        chal_font = self._get_font(40)
        self._draw_bullet_list_centered(draw, challenges[:4], 450, chal_font, self.colors['primary_text'], max_items=4)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _compat_tips(self, lp1, lp2, compat_level, slide_num, total):
        """Compatibility tips slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LP {lp1} + LP {lp2}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "TIPS FOR SUCCESS", 280, title_font, self.colors['primary_text'])

        tips_by_level = {
            'excellent': [
                "Appreciate your natural flow",
                "Don't take harmony for granted",
                "Keep communication open",
                "Grow together intentionally"
            ],
            'neutral': [
                "Focus on understanding differences",
                "Find common ground actively",
                "Respect each other's needs",
                "Build bridges through patience"
            ],
            'challenging': [
                "See friction as growth opportunity",
                "Practice active listening",
                "Celebrate your differences",
                "Commit to understanding"
            ]
        }

        tips_font = self._get_font(40)
        self._draw_bullet_list_centered(draw, tips_by_level[compat_level], 450, tips_font, self.colors['highlight'], max_items=4)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    # =========================================================================
    # LIFE PATH CAREER DEEP DIVE CAROUSEL (6 slides)
    # =========================================================================

    def generate_career_carousel(self, life_path_number):
        """Generate 6-slide Career Deep Dive carousel"""
        lp_data = get_life_path_data(life_path_number)
        if not lp_data:
            print(f"   ❌ No data found for Life Path {life_path_number}")
            return None

        slides = []
        carousel_dir = os.path.join(self.output_dir, f"LP{life_path_number}_career")
        os.makedirs(carousel_dir, exist_ok=True)

        slides.append(self._career_cover(life_path_number, lp_data, 1, 6))
        slides.append(self._career_strengths(life_path_number, lp_data, 2, 6))
        slides.append(self._career_ideal(life_path_number, lp_data, 3, 6))
        slides.append(self._career_avoid(life_path_number, lp_data, 4, 6))
        slides.append(self._career_success(life_path_number, lp_data, 5, 6))
        slides.append(self._slide_cta(life_path_number, 6, 6))

        slide_paths = []
        for i, slide in enumerate(slides, 1):
            path = os.path.join(carousel_dir, f"slide_{i:02d}.png")
            slide.save(path, "PNG", quality=95)
            slide_paths.append(path)
            print(f"   ✅ Saved slide {i}/6")

        return {
            'type': 'life_path_career',
            'life_path_number': life_path_number,
            'slide_paths': slide_paths,
            'carousel_dir': carousel_dir
        }

    def _career_cover(self, lp_num, lp_data, slide_num, total):
        """Career carousel cover"""
        img, draw = self._create_base_image()
        center_y = self.size[1] // 2

        label_font = self._get_font(50)
        self._draw_text_centered(draw, "LIFE PATH", center_y - 280, label_font, self.colors['muted'])

        num_font = self._get_font(250)
        self._draw_text_centered(draw, str(lp_num), center_y - 150, num_font, self.colors['accent'])

        title_font = self._get_font(80)
        self._draw_text_centered(draw, "CAREER GUIDE", center_y + 120, title_font, self.colors['secondary_accent'])

        name_font = self._get_font(45)
        name = lp_data.get('name', '').upper()
        self._draw_text_centered(draw, name, center_y + 220, name_font, self.colors['primary_text'])

        swipe_font = self._get_font(32)
        self._draw_text_centered(draw, "FIND YOUR IDEAL PATH →", center_y + 380, swipe_font, self.colors['muted'])

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _career_strengths(self, lp_num, lp_data, slide_num, total):
        """Career strengths slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "WORK STRENGTHS", 280, title_font, self.colors['primary_text'])

        chars = lp_data.get('key_characteristics', [])[:5]
        char_font = self._get_font(38)
        self._draw_bullet_list_centered(draw, chars, 450, char_font, self.colors['highlight'], max_items=5)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _career_ideal(self, lp_num, lp_data, slide_num, total):
        """Ideal careers slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "IDEAL CAREERS", 280, title_font, self.colors['secondary_accent'])

        careers = lp_data.get('career_paths', [])[:6]
        career_font = self._get_font(44)
        self._draw_bullet_list_centered(draw, careers, 450, career_font, self.colors['primary_text'], max_items=6)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _career_avoid(self, lp_num, lp_data, slide_num, total):
        """Careers to avoid slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "AVOID THESE", 280, title_font, self.colors['highlight'])

        # Generate based on challenges
        challenges = lp_data.get('challenges', [])
        avoid = []
        for c in challenges[:4]:
            if 'routine' in c.lower() or 'repetitive' in c.lower():
                avoid.append("Highly repetitive roles")
            elif 'independence' in c.lower() or 'freedom' in c.lower():
                avoid.append("Micro-managed positions")
            elif 'patience' in c.lower():
                avoid.append("Slow-paced environments")
            else:
                avoid.append("Roles limiting growth")

        avoid = list(set(avoid))[:4] or ["Misaligned environments", "Energy-draining roles", "Unfulfilling positions", "Limiting opportunities"]

        avoid_font = self._get_font(40)
        self._draw_bullet_list_centered(draw, avoid, 450, avoid_font, self.colors['primary_text'], max_items=4)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _career_success(self, lp_num, lp_data, slide_num, total):
        """Career success tips slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "SUCCESS TIPS", 280, title_font, self.colors['primary_text'])

        archetype = lp_data.get('archetype', '').lower()
        tips = [
            "Align work with your purpose",
            "Use your natural strengths",
            "Seek growth opportunities",
            "Build meaningful connections"
        ]

        tips_font = self._get_font(40)
        self._draw_bullet_list_centered(draw, tips, 450, tips_font, self.colors['secondary_accent'], max_items=4)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    # =========================================================================
    # LIFE PATH LOVE CAROUSEL (6 slides)
    # =========================================================================

    def generate_love_carousel(self, life_path_number):
        """Generate 6-slide Love & Relationships carousel"""
        lp_data = get_life_path_data(life_path_number)
        if not lp_data:
            print(f"   ❌ No data found for Life Path {life_path_number}")
            return None

        slides = []
        carousel_dir = os.path.join(self.output_dir, f"LP{life_path_number}_love")
        os.makedirs(carousel_dir, exist_ok=True)

        slides.append(self._love_cover(life_path_number, lp_data, 1, 6))
        slides.append(self._love_style(life_path_number, lp_data, 2, 6))
        slides.append(self._love_needs(life_path_number, lp_data, 3, 6))
        slides.append(self._love_compatibility(life_path_number, lp_data, 4, 6))
        slides.append(self._love_tips(life_path_number, lp_data, 5, 6))
        slides.append(self._slide_cta(life_path_number, 6, 6))

        slide_paths = []
        for i, slide in enumerate(slides, 1):
            path = os.path.join(carousel_dir, f"slide_{i:02d}.png")
            slide.save(path, "PNG", quality=95)
            slide_paths.append(path)
            print(f"   ✅ Saved slide {i}/6")

        return {
            'type': 'life_path_love',
            'life_path_number': life_path_number,
            'slide_paths': slide_paths,
            'carousel_dir': carousel_dir
        }

    def _love_cover(self, lp_num, lp_data, slide_num, total):
        """Love carousel cover"""
        img, draw = self._create_base_image()
        center_y = self.size[1] // 2

        label_font = self._get_font(50)
        self._draw_text_centered(draw, "LIFE PATH", center_y - 280, label_font, self.colors['muted'])

        num_font = self._get_font(250)
        self._draw_text_centered(draw, str(lp_num), center_y - 150, num_font, self.colors['highlight'])

        title_font = self._get_font(80)
        self._draw_text_centered(draw, "IN LOVE", center_y + 120, title_font, self.colors['primary_text'])

        name_font = self._get_font(45)
        name = lp_data.get('name', '').upper()
        self._draw_text_centered(draw, name, center_y + 220, name_font, self.colors['accent'])

        swipe_font = self._get_font(32)
        self._draw_text_centered(draw, "YOUR RELATIONSHIP GUIDE →", center_y + 380, swipe_font, self.colors['muted'])

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _love_style(self, lp_num, lp_data, slide_num, total):
        """Love style slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "YOUR LOVE STYLE", 280, title_font, self.colors['highlight'])

        traits = lp_data.get('core_traits', {}).get('positive', [])[:4]
        style = [f"You love with {t}" for t in traits]

        style_font = self._get_font(40)
        self._draw_bullet_list_centered(draw, style, 450, style_font, self.colors['primary_text'], max_items=4)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _love_needs(self, lp_num, lp_data, slide_num, total):
        """Love needs slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "YOU NEED", 280, title_font, self.colors['secondary_accent'])

        chars = lp_data.get('key_characteristics', [])[:3]
        needs = [
            "Partner who understands you",
            "Space for independence",
            "Emotional support",
            "Shared growth"
        ]

        needs_font = self._get_font(40)
        self._draw_bullet_list_centered(draw, needs, 450, needs_font, self.colors['primary_text'], max_items=4)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _love_compatibility(self, lp_num, lp_data, slide_num, total):
        """Love compatibility slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "BEST MATCHES", 280, title_font, self.colors['primary_text'])

        compat = lp_data.get('compatibility', {})
        y = 450

        best = compat.get('best', [])
        if best:
            label_font = self._get_font(40)
            self._draw_text_centered(draw, "💚 MOST COMPATIBLE", y, label_font, self.colors['highlight'])
            y += 70
            match_font = self._get_font(70)
            match_text = "  ".join([str(m) for m in best])
            self._draw_text_centered(draw, match_text, y, match_font, self.colors['primary_text'])
            y += 140

        challenging = compat.get('challenging', [])
        if challenging:
            label_font = self._get_font(40)
            self._draw_text_centered(draw, "🔥 CHALLENGING", y, label_font, self.colors['secondary_accent'])
            y += 70
            match_font = self._get_font(70)
            match_text = "  ".join([str(m) for m in challenging])
            self._draw_text_centered(draw, match_text, y, match_font, self.colors['primary_text'])

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _love_tips(self, lp_num, lp_data, slide_num, total):
        """Love tips slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(50)
        self._draw_text_centered(draw, f"LIFE PATH {lp_num}", 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "RELATIONSHIP TIPS", 280, title_font, self.colors['primary_text'])

        challenges = lp_data.get('challenges', [])[:2]
        tips = [
            "Communicate openly",
            "Balance independence & togetherness",
            "Work on patience",
            "Appreciate differences"
        ]

        tips_font = self._get_font(40)
        self._draw_bullet_list_centered(draw, tips, 450, tips_font, self.colors['highlight'], max_items=4)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    # =========================================================================
    # ANGEL NUMBER CAROUSEL (5 slides)
    # =========================================================================

    def generate_angel_number_carousel(self, angel_number):
        """Generate 5-slide Angel Number meaning carousel"""
        from angel_numbers_db import get_angel_number_meaning

        meaning = get_angel_number_meaning(angel_number)
        if not meaning:
            print(f"   ❌ No data found for Angel Number {angel_number}")
            return None

        slides = []
        carousel_dir = os.path.join(self.output_dir, f"AN{angel_number}")
        os.makedirs(carousel_dir, exist_ok=True)

        slides.append(self._angel_cover(angel_number, meaning, 1, 5))
        slides.append(self._angel_meaning(angel_number, meaning, 2, 5))
        slides.append(self._angel_action(angel_number, meaning, 3, 5))
        slides.append(self._angel_affirmation(angel_number, meaning, 4, 5))
        slides.append(self._angel_cta(angel_number, 5, 5))

        slide_paths = []
        for i, slide in enumerate(slides, 1):
            path = os.path.join(carousel_dir, f"slide_{i:02d}.png")
            slide.save(path, "PNG", quality=95)
            slide_paths.append(path)
            print(f"   ✅ Saved slide {i}/5")

        return {
            'type': 'angel_number',
            'angel_number': angel_number,
            'slide_paths': slide_paths,
            'carousel_dir': carousel_dir
        }

    def _angel_cover(self, number, meaning, slide_num, total):
        """Angel number cover slide"""
        img, draw = self._create_base_image()
        center_y = self.size[1] // 2

        label_font = self._get_font(50)
        self._draw_text_centered(draw, "ANGEL NUMBER", center_y - 280, label_font, self.colors['muted'])

        # Big number with glow
        num_font = self._get_font(280)
        bbox = draw.textbbox((0, 0), number, font=num_font)
        num_width = bbox[2] - bbox[0]
        num_x = (self.size[0] - num_width) // 2

        for offset in range(12, 0, -2):
            draw.text((num_x, center_y - 200), number, font=num_font,
                     fill=self.colors['accent'], stroke_width=offset + 3, stroke_fill=(0, 0, 0, 30))

        draw.text((num_x, center_y - 200), number, font=num_font,
                 fill=self.colors['accent'], stroke_width=4, stroke_fill=(0, 0, 0))

        title_font = self._get_font(55)
        self._draw_text_centered(draw, "WHAT IT MEANS", center_y + 150, title_font, self.colors['secondary_accent'])

        swipe_font = self._get_font(32)
        self._draw_text_centered(draw, "SWIPE TO DISCOVER →", center_y + 350, swipe_font, self.colors['muted'])

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _angel_meaning(self, number, meaning, slide_num, total):
        """Angel number meaning slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(60)
        self._draw_text_centered(draw, number, 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "THE MESSAGE", 290, title_font, self.colors['primary_text'])

        meaning_text = meaning.get('meaning', 'A powerful message from the universe')
        meaning_font = self._get_font(42)
        self._draw_wrapped_text_centered(draw, meaning_text.upper(), 480, meaning_font,
                                        self.colors['secondary_accent'], max_width=900)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _angel_action(self, number, meaning, slide_num, total):
        """Angel number action slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(60)
        self._draw_text_centered(draw, number, 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "TAKE ACTION", 290, title_font, self.colors['highlight'])

        action = meaning.get('action', 'Trust the process and stay aligned')
        action_font = self._get_font(42)
        self._draw_wrapped_text_centered(draw, action.upper(), 480, action_font,
                                        self.colors['primary_text'], max_width=900)

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _angel_affirmation(self, number, meaning, slide_num, total):
        """Angel number affirmation slide"""
        img, draw = self._create_base_image()

        header_font = self._get_font(60)
        self._draw_text_centered(draw, number, 200, header_font, self.colors['accent'])

        title_font = self._get_font(70)
        self._draw_text_centered(draw, "AFFIRMATION", 290, title_font, self.colors['primary_text'])

        # Generate affirmation from meaning
        meaning_text = meaning.get('meaning', '')
        if 'abundance' in meaning_text.lower():
            affirmation = "I AM OPEN TO RECEIVING ABUNDANCE"
        elif 'love' in meaning_text.lower():
            affirmation = "I AM WORTHY OF DEEP LOVE"
        elif 'change' in meaning_text.lower():
            affirmation = "I EMBRACE POSITIVE CHANGE"
        elif 'spiritual' in meaning_text.lower():
            affirmation = "I TRUST MY SPIRITUAL PATH"
        else:
            affirmation = "I AM ALIGNED WITH MY HIGHEST PURPOSE"

        aff_font = self._get_font(50)
        self._draw_wrapped_text_centered(draw, affirmation, 500, aff_font,
                                        self.colors['secondary_accent'], max_width=900)

        reminder_font = self._get_font(35)
        self._draw_text_centered(draw, "REPEAT THIS WHEN YOU SEE " + number, 800, reminder_font, self.colors['muted'])

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img

    def _angel_cta(self, number, slide_num, total):
        """Angel number CTA slide"""
        img, draw = self._create_base_image()
        center_y = self.size[1] // 2

        q_font = self._get_font(55)
        self._draw_text_centered(draw, "SEEING", center_y - 300, q_font, self.colors['muted'])

        num_font = self._get_font(150)
        self._draw_text_centered(draw, number, center_y - 180, num_font, self.colors['accent'])

        q2_font = self._get_font(55)
        self._draw_text_centered(draw, "EVERYWHERE?", center_y - 30, q2_font, self.colors['muted'])

        link_font = self._get_font(60)
        self._draw_text_centered(draw, "🔗 LINK IN BIO", center_y + 100, link_font, self.colors['highlight'])

        site_font = self._get_font(35)
        self._draw_text_centered(draw, "SEVENTHLIFEPATH.COM", center_y + 180, site_font, self.colors['muted'])

        save_font = self._get_font(38)
        self._draw_text_centered(draw, "💾 SAVE FOR WHEN YOU SEE IT", center_y + 300, save_font, self.colors['secondary_accent'])

        follow_font = self._get_font(32)
        self._draw_text_centered(draw, "FOLLOW @THE17PROJECT", center_y + 400, follow_font, self.colors['muted'])

        self._add_watermark(draw)
        self._add_slide_indicator(draw, slide_num, total)
        return img


# ============================================================================
# CAPTION GENERATORS
# ============================================================================

def generate_carousel_caption(carousel_type, life_path_number=None, lp2=None, angel_number=None):
    """Generate Instagram caption for carousel post"""
    if carousel_type == 'life_path_breakdown':
        from life_path_database import get_life_path_data
        lp_data = get_life_path_data(life_path_number)
        name = lp_data.get('name', f'Life Path {life_path_number}') if lp_data else f'Life Path {life_path_number}'

        caption = f"""Life Path {life_path_number}: {name} - THE COMPLETE GUIDE 🔮

Swipe through for your complete breakdown 👉

✨ Core Traits
💪 Strengths & Weaknesses
💼 Ideal Careers
❤️ Compatibility
🎯 Life Purpose
🌑 Shadow Work
📈 Growth Tips

Save this for later 🔖

👇 What's YOUR Life Path Number?
📍 Link in bio to calculate

#lifepath{life_path_number} #numerology #lifepathguide #spiritualgrowth #selfdiscovery"""

    elif carousel_type == 'life_path_compatibility':
        from life_path_database import get_life_path_data
        lp1_data = get_life_path_data(life_path_number)
        lp2_data = get_life_path_data(lp2)
        name1 = lp1_data.get('name', '') if lp1_data else ''
        name2 = lp2_data.get('name', '') if lp2_data else ''

        caption = f"""Life Path {life_path_number} + {lp2} Compatibility 💕

{name1} meets {name2}...

Swipe to discover:
✨ Your relationship dynamic
💪 Strengths together
⚡ Challenges to navigate
💡 Tips for success

Tag someone with this combo! 👇

Save for your relationships 🔖

#lifepath{life_path_number} #lifepath{lp2} #compatibility #numerology #relationships #soulmate"""

    elif carousel_type == 'life_path_career':
        from life_path_database import get_life_path_data
        lp_data = get_life_path_data(life_path_number)
        name = lp_data.get('name', '') if lp_data else ''

        caption = f"""Life Path {life_path_number} Career Guide 💼

{name}'s path to success...

Swipe for:
💪 Your work strengths
✨ Ideal career paths
🚫 What to avoid
🎯 Success tips

What's your career? Drop it below! 👇

#lifepath{life_path_number} #careeradvice #numerology #dreamjob #findyourpurpose"""

    elif carousel_type == 'life_path_love':
        from life_path_database import get_life_path_data
        lp_data = get_life_path_data(life_path_number)
        name = lp_data.get('name', '') if lp_data else ''

        caption = f"""Life Path {life_path_number} in Love ❤️

How {name} loves...

Swipe to discover:
💕 Your love style
🔥 What you need
💚 Best matches
💡 Relationship tips

Tag your partner! 👇

#lifepath{life_path_number} #lovelanguage #numerology #relationships #soulmate #dating"""

    elif carousel_type == 'angel_number':
        caption = f"""Angel Number {angel_number} 🔮

The universe is speaking to you...

Swipe to learn:
✨ What it means
🎯 Action to take
💫 Affirmation to use

Seeing {angel_number} everywhere? Save this! 🔖

Comment {angel_number} if you've seen it lately 👇

#angelnumber{angel_number} #angelnumbers #spirituality #numerology #universe #signs"""

    else:
        caption = """Numerology Quick Guide 📚

Swipe through to learn more 👉

Save for later 🔖

#numerology #lifepath #spiritualgrowth #selfawareness"""

    return caption


# ============================================================================
# CAROUSEL ROTATION SYSTEM
# ============================================================================

def get_all_carousel_specs():
    """
    Get all possible carousel specifications for rotation.
    Returns list of dicts with carousel type and parameters.

    Total: 9 + 36 + 9 + 9 + 278 = 341 unique carousels
    """
    specs = []

    # 1. Life Path Breakdowns (9)
    for lp in range(1, 10):
        specs.append({
            'type': 'life_path_breakdown',
            'life_path_number': lp,
            'id': f'LP{lp}_breakdown'
        })

    # 2. Life Path Compatibility (36 unique pairs)
    for lp1 in range(1, 10):
        for lp2 in range(lp1 + 1, 10):  # Only unique pairs, no duplicates
            specs.append({
                'type': 'life_path_compatibility',
                'lp1': lp1,
                'lp2': lp2,
                'id': f'LP{lp1}_LP{lp2}_compat'
            })

    # 3. Life Path Career (9)
    for lp in range(1, 10):
        specs.append({
            'type': 'life_path_career',
            'life_path_number': lp,
            'id': f'LP{lp}_career'
        })

    # 4. Life Path Love (9)
    for lp in range(1, 10):
        specs.append({
            'type': 'life_path_love',
            'life_path_number': lp,
            'id': f'LP{lp}_love'
        })

    # 5. Angel Number carousels (all available)
    from angel_numbers_db import get_all_angel_numbers
    for an in get_all_angel_numbers():
        specs.append({
            'type': 'angel_number',
            'angel_number': an,
            'id': f'AN{an}'
        })

    return specs


def get_next_carousel(posted_ids=None):
    """
    Get the next carousel to post based on what's already been posted.
    Uses rotation to cycle through all carousels before repeating.

    Args:
        posted_ids: Set of carousel IDs that have already been posted

    Returns:
        dict: Carousel spec to generate next
    """
    if posted_ids is None:
        posted_ids = set()

    all_specs = get_all_carousel_specs()

    # Find unposted carousels
    unposted = [s for s in all_specs if s['id'] not in posted_ids]

    # If all posted, reset cycle
    if not unposted:
        print(f"   ♻️  All {len(all_specs)} carousels posted! Starting new cycle...")
        unposted = all_specs

    # Prioritize variety: rotate through types
    # Order: breakdown -> compatibility -> career -> love -> angel_number
    type_order = ['life_path_breakdown', 'life_path_compatibility',
                  'life_path_career', 'life_path_love', 'angel_number']

    for ctype in type_order:
        type_carousels = [s for s in unposted if s['type'] == ctype]
        if type_carousels:
            return type_carousels[0]

    # Fallback: return first unposted
    return unposted[0]


def generate_next_carousel(posted_ids=None):
    """
    Generate the next carousel in rotation.

    Args:
        posted_ids: Set of carousel IDs already posted

    Returns:
        dict: Result with carousel info and slide paths
    """
    spec = get_next_carousel(posted_ids)
    generator = CarouselGenerator()

    print(f"\n📊 Generating carousel: {spec['id']}")
    print(f"   Type: {spec['type']}")

    if spec['type'] == 'life_path_breakdown':
        result = generator.generate_life_path_breakdown(spec['life_path_number'])
    elif spec['type'] == 'life_path_compatibility':
        result = generator.generate_compatibility_carousel(spec['lp1'], spec['lp2'])
    elif spec['type'] == 'life_path_career':
        result = generator.generate_career_carousel(spec['life_path_number'])
    elif spec['type'] == 'life_path_love':
        result = generator.generate_love_carousel(spec['life_path_number'])
    elif spec['type'] == 'angel_number':
        result = generator.generate_angel_number_carousel(spec['angel_number'])
    else:
        print(f"   ❌ Unknown carousel type: {spec['type']}")
        return None

    if result:
        result['carousel_id'] = spec['id']
        result['spec'] = spec

        # Generate caption
        if spec['type'] == 'life_path_breakdown':
            result['caption'] = generate_carousel_caption('life_path_breakdown', spec['life_path_number'])
        elif spec['type'] == 'life_path_compatibility':
            result['caption'] = generate_carousel_caption('life_path_compatibility', spec['lp1'], spec['lp2'])
        elif spec['type'] == 'life_path_career':
            result['caption'] = generate_carousel_caption('life_path_career', spec['life_path_number'])
        elif spec['type'] == 'life_path_love':
            result['caption'] = generate_carousel_caption('life_path_love', spec['life_path_number'])
        elif spec['type'] == 'angel_number':
            result['caption'] = generate_carousel_caption('angel_number', angel_number=spec['angel_number'])

    return result


def get_carousel_stats():
    """Get statistics about carousel content availability"""
    all_specs = get_all_carousel_specs()

    stats = {
        'total': len(all_specs),
        'life_path_breakdown': len([s for s in all_specs if s['type'] == 'life_path_breakdown']),
        'life_path_compatibility': len([s for s in all_specs if s['type'] == 'life_path_compatibility']),
        'life_path_career': len([s for s in all_specs if s['type'] == 'life_path_career']),
        'life_path_love': len([s for s in all_specs if s['type'] == 'life_path_love']),
        'angel_number': len([s for s in all_specs if s['type'] == 'angel_number']),
    }

    stats['days_of_content'] = stats['total']  # 1 carousel per day

    return stats


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("THE17PROJECT - CAROUSEL GENERATOR")
    print("=" * 70)

    lp_num = int(sys.argv[1]) if len(sys.argv) > 1 else 8

    generator = CarouselGenerator()

    print(f"\n📊 Generating Life Path {lp_num} Breakdown Carousel (9:16 format)...")
    result = generator.generate_life_path_breakdown(lp_num)

    if result:
        print(f"\n✅ Carousel generated successfully!")
        print(f"   Directory: {result['carousel_dir']}")
        print(f"   Slides: {len(result['slide_paths'])}")
        print(f"   Format: 1080x1920 (9:16 portrait)")

        caption = generate_carousel_caption('life_path_breakdown', lp_num)
        print(f"\n📝 Caption preview:")
        print("-" * 40)
        print(caption[:300] + "...")
    else:
        print("\n❌ Carousel generation failed")
