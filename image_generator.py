"""
image_generator.py
Genera imágenes de posts para Instagram (1080x1080) con la identidad
visual de College iTools (mismos colores/fuentes que _ficha_assets del
backend: navy + dorado, Cinzel para títulos, Nunito para texto).

No depende de ningún servicio externo ni de college-backend en
producción: usa las fuentes locales en assets/fonts/ y arma todo con
Pillow.

Uso:
    from image_generator import generate_post_image
    generate_post_image(
        asignatura="Matemática", grado="5° Básico", tema="Fracciones",
        pillar="aprendizaje", out_path="generated_media/ejemplo.png",
    )
"""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

SIZE = 1080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "assets", "fonts")

NAVY = (15, 23, 42)
NAVY_DARK = (11, 18, 32)
CARD = (30, 41, 59)
BORDER = (51, 65, 85)
TEXT_LIGHT = (241, 245, 249)
TEXT_MUTED = (148, 163, 184)
GOLD = (245, 196, 0)

ACCENT_BY_ASIGNATURA = {
    "Matemática": (56, 189, 248),       # azul
    "Lenguaje": (155, 89, 245),         # violeta
    "Ciencias Naturales": (45, 190, 145),  # verde-teal
    "Historia": (245, 158, 11),         # ámbar
    "Inglés": (236, 72, 153),           # rosa
}

TAGLINE_BY_PILLAR = {
    "aprendizaje": "Repasa el currículum MINEDUC jugando",
    "apoderados": "15 minutos al día, sin pelear por el celular",
    "vida_familiar": "College iTools · aprender jugando",
    "comunidad": "Cuéntanos tu experiencia",
}


def _font(name, size, variation=None):
    path = os.path.join(FONT_DIR, name)
    font = ImageFont.truetype(path, size)
    if variation:
        font.set_variation_by_name(variation)
    return font


def _wrap_to_width(draw, text, font, max_width, max_lines=4):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip() + "…"
    return lines


def generate_post_image(asignatura, grado, tema, pillar, out_path):
    accent = ACCENT_BY_ASIGNATURA.get(asignatura, GOLD)
    tagline = TAGLINE_BY_PILLAR.get(pillar, TAGLINE_BY_PILLAR["aprendizaje"])

    img = Image.new("RGB", (SIZE, SIZE), NAVY)
    draw = ImageDraw.Draw(img)

    # Degradado sutil de fondo (navy -> navy_dark) de arriba a abajo.
    for y in range(SIZE):
        t = y / SIZE
        r = int(NAVY[0] + (NAVY_DARK[0] - NAVY[0]) * t)
        g = int(NAVY[1] + (NAVY_DARK[1] - NAVY[1]) * t)
        b = int(NAVY[2] + (NAVY_DARK[2] - NAVY[2]) * t)
        draw.line([(0, y), (SIZE, y)], fill=(r, g, b))

    # Barra de acento superior.
    draw.rectangle([(0, 0), (SIZE, 14)], fill=accent)

    # Marca "COLLEGE ITOOLS" arriba.
    brand_font = _font("Cinzel-Variable.ttf", 42, "Black")
    draw.text((80, 70), "COLLEGE ITOOLS", font=brand_font, fill=GOLD)

    # Píldora con asignatura + grado.
    pill_font = _font("Nunito-Variable.ttf", 34, "ExtraBold")
    pill_text = f"{asignatura.upper()} · {grado.upper()}"
    pill_w = draw.textlength(pill_text, font=pill_font) + 64
    pill_h = 70
    pill_x, pill_y = 80, 170
    draw.rounded_rectangle(
        [(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)],
        radius=pill_h // 2, fill=accent,
    )
    draw.text(
        (pill_x + 32, pill_y + pill_h / 2), pill_text,
        font=pill_font, fill=NAVY, anchor="lm",
    )

    # Título (tema) centrado en el medio del canvas.
    title_font = _font("Nunito-Variable.ttf", 84, "ExtraBold")
    max_width = SIZE - 160
    lines = _wrap_to_width(draw, tema, title_font, max_width, max_lines=4)

    line_height = 100
    total_h = line_height * len(lines)
    start_y = (SIZE - total_h) / 2 + 20

    for i, line in enumerate(lines):
        draw.text(
            (SIZE / 2, start_y + i * line_height), line,
            font=title_font, fill=TEXT_LIGHT, anchor="ma",
        )

    # Línea decorativa bajo el título.
    deco_y = start_y + total_h + 20
    draw.rectangle(
        [(SIZE / 2 - 60, deco_y), (SIZE / 2 + 60, deco_y + 6)], fill=accent,
    )

    # Tagline inferior + marca de agua sutil.
    tagline_font = _font("Nunito-Variable.ttf", 36, "SemiBold")
    draw.text(
        (SIZE / 2, SIZE - 130), tagline,
        font=tagline_font, fill=TEXT_MUTED, anchor="ma",
    )

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    generate_post_image(
        asignatura="Matemática", grado="5° Básico", tema="Fracciones Equivalentes",
        pillar="aprendizaje", out_path="generated_media/_preview.png",
    )
    print("Imagen de prueba generada en generated_media/_preview.png")
