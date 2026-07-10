"""
caption_helper.py
Generador simple de captions y sets de hashtags para "college.itools".
No necesita conexión ni API keys: usa plantillas y bancos de
hashtags predefinidos que puedes editar a tu gusto.

Uso:
    from caption_helper import generate_caption, generate_hashtags

    caption = generate_caption("Notion tiene una plantilla gratis para organizar tus materias", pillar="apps")
    hashtags = generate_hashtags(["general", "apps"])
"""

import random

HOOKS = [
    "¿Sabías que existe una herramienta que te resuelve esto? 👀",
    "Guarda este post, lo vas a necesitar en época de exámenes 📌",
    "Esto me hubiera ahorrado tantas horas en la u 😅",
    "La herramienta que todo estudiante necesita conocer 🚀",
    "3 minutos leyendo esto = horas ahorradas después 🙌",
]

CTAS = [
    "¿Ya la conocías? Cuéntame en los comentarios 👇",
    "Guárdalo para cuando lo necesites 💾",
    "Comparte esto con ese amigo que anda saturado de tareas 🙏",
    "Sígueme para más tips como este 📚",
    "¿Qué otra herramienta quieres que reseñe? Dímelo abajo 👇",
]

HASHTAG_BANKS = {
    "general": ["#college", "#universidad", "#estudiantes", "#tips", "#productividad"],
    "apps": ["#appsutiles", "#tecnologia", "#estudiar", "#organizacion", "#collegetools"],
    "estudio": ["#studytips", "#tecnicasdeestudio", "#examenes", "#apuntes", "#motivacion"],
    "vida_universitaria": ["#viduniversitaria", "#universidad", "#estudiantes", "#collegelife"],
}


def generate_caption(topic, pillar="general", hook=None, cta=None):
    """Arma un caption con estructura hook -> contenido -> llamado a la acción."""
    hook = hook or random.choice(HOOKS)
    cta = cta or random.choice(CTAS)
    return f"{hook}\n\n{topic}\n\n{cta}"


def generate_hashtags(pillars, extra=None, limit=20):
    """Combina hashtags de uno o más 'pilares' de contenido, sin duplicados."""
    tags = []
    for p in pillars:
        tags.extend(HASHTAG_BANKS.get(p, []))
    if extra:
        tags.extend(extra)

    seen = set()
    unique = [t for t in tags if not (t in seen or seen.add(t))]
    return " ".join(unique[:limit])


if __name__ == "__main__":
    caption = generate_caption(
        topic="Notion tiene una plantilla gratis para organizar todas tus materias del semestre.",
        pillar="apps",
    )
    hashtags = generate_hashtags(["general", "apps"])
    print(caption)
    print()
    print(hashtags)
