"""
caption_helper.py
Generador simple de captions y sets de hashtags para "college.itools".
Audiencia real: apoderados/padres de niños de 3° a 8° básico (currículum
MINEDUC) — ver strategy_guide.md. No necesita conexión ni API keys: usa
plantillas y bancos de hashtags predefinidos que puedes editar a tu gusto.

Uso:
    from caption_helper import generate_caption, generate_hashtags

    caption = generate_caption("15 minutos al día repasando matemáticas de 5° básico jugando", pillar="aprendizaje")
    hashtags = generate_hashtags(["general", "aprendizaje"])
"""

import random

HOOKS = [
    "¿Y si el tiempo de pantalla de tu hijo sirviera para aprender? 🎮📚",
    "Guarda este post, te va a servir en la próxima prueba 📌",
    "Esto le hubiera ahorrado muchas peleas por el celular a más de un apoderado 😅",
    "La herramienta que todo apoderado de básica necesita conocer 🚀",
    "3 minutos leyendo esto = menos peleas por el celular después 🙌",
]

CTAS = [
    "¿Ya la conocías? Cuéntanos en los comentarios 👇",
    "Guárdalo para cuando lo necesites 💾",
    "Comparte esto con ese apoderado que anda saturado con las tareas 🙏",
    "Síguenos para más tips como este 📚",
    "¿Qué otro ramo quieres que reforcemos jugando? Dinos abajo 👇",
]

HASHTAG_BANKS = {
    "general": ["#collegeitools", "#educación", "#edtech", "#colegio"],
    "aprendizaje": ["#MINEDUC", "#aprenderjugando", "#currículum", "#educaciónchile"],
    "apoderados": ["#apoderados", "#padres", "#tiempodepantalla", "#crianza"],
    "comunidad": ["#profesores", "#testimonios", "#comunidadeducativa"],
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
        topic="College iTools tiene ejercicios de matemáticas de 5° básico alineados al currículum MINEDUC, en formato de juego.",
        pillar="aprendizaje",
    )
    hashtags = generate_hashtags(["general", "aprendizaje"])
    print(caption)
    print()
    print(hashtags)
