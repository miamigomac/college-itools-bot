"""
generate_calendar.py
Prepara automáticamente entradas nuevas para content_calendar.csv:
elige temas del currículum MINEDUC (curriculum_topics.json, exportado
desde college-backend), genera la imagen de marca con image_generator.py
y arma el caption/hashtags con caption_helper.py.

Cubre los tipos que se pueden generar sin grabar nada (post, carousel,
story_photo). Los reels/historias en video necesitan footage real de
la app y quedan fuera de este script — se agregan a mano en el CSV.

Uso:
    python generate_calendar.py --weeks 2
    python generate_calendar.py --weeks 2 --start-date 2026-07-22

Las imágenes generadas quedan en generated_media/ y el media_url que
se escribe en el CSV apunta al raw.githubusercontent.com del repo
(asume que este mismo commit se va a pushear a GitHub).
"""

import argparse
import csv
import os
import random
import re
import json
from datetime import date, datetime, timedelta

from caption_helper import generate_caption, generate_hashtags
from image_generator import generate_post_image

CALENDAR_FILE = "content_calendar.csv"
TOPICS_FILE = "curriculum_topics.json"
MEDIA_DIR = "generated_media"
FIELDNAMES = ["date", "time", "type", "media_url", "caption", "hashtags", "status"]
REPO_RAW_BASE = "https://raw.githubusercontent.com/miamigomac/college-itools-bot/main"

PILLAR_WEIGHTS = [
    ("aprendizaje", 35),
    ("apoderados", 25),
    ("vida_familiar", 25),
    ("comunidad", 15),
]

# día de semana (0=lunes) -> (hora, tipo)
WEEKLY_SLOTS = [
    (1, "19:30", "post"),       # martes
    (3, "19:30", "post"),       # jueves
    (5, "11:00", "carousel"),   # sábado
    (6, "18:00", "story_photo"),  # domingo
]


def slug(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9áéíóúñ]+", "-", text)
    return text.strip("-")[:40]


def load_topics():
    with open(TOPICS_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_calendar():
    with open(CALENDAR_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_calendar(rows):
    with open(CALENDAR_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def pick_pillar():
    pillars, weights = zip(*PILLAR_WEIGHTS)
    return random.choices(pillars, weights=weights, k=1)[0]


def make_topic_caption(topic, pillar):
    body = (
        f'En College iTools tu hijo puede repasar "{topic["tema"]}" '
        f'({topic["asignatura"]}, {topic["grado"]}) jugando, siguiendo el '
        f"currículum MINEDUC."
    )
    caption = generate_caption(body, pillar=pillar)
    hashtags = generate_hashtags(["general", pillar])
    return caption, hashtags


def make_carousel_caption(topics, pillar):
    lista = "\n".join(f"• {t['tema']} ({t['asignatura']}, {t['grado']})" for t in topics)
    body = f"Esta semana te proponemos repasar jugando:\n\n{lista}"
    caption = generate_caption(body, pillar=pillar)
    hashtags = generate_hashtags(["general", pillar])
    return caption, hashtags


def build_rows(start_date, weeks, topics):
    available = topics.copy()
    random.shuffle(available)

    def next_topic():
        if not available:
            available.extend(topics)
            random.shuffle(available)
        return available.pop()

    rows = []
    for week in range(weeks):
        for weekday, time_str, media_type in WEEKLY_SLOTS:
            days_ahead = (weekday - start_date.weekday()) % 7
            slot_date = start_date + timedelta(days=days_ahead + week * 7)
            pillar = pick_pillar()

            if media_type == "carousel":
                chosen = [next_topic() for _ in range(3)]
                caption, hashtags = make_carousel_caption(chosen, pillar)
                filenames = []
                for i, topic in enumerate(chosen):
                    fname = f"{slot_date.isoformat()}-carousel-{i}-{slug(topic['tema'])}.png"
                    out_path = os.path.join(MEDIA_DIR, fname)
                    generate_post_image(
                        topic["asignatura"], topic["grado"], topic["tema"], pillar, out_path,
                    )
                    filenames.append(fname)
                media_url = "|".join(f"{REPO_RAW_BASE}/{MEDIA_DIR}/{fn}" for fn in filenames)
            else:
                topic = next_topic()
                fname = f"{slot_date.isoformat()}-{media_type}-{slug(topic['tema'])}.png"
                out_path = os.path.join(MEDIA_DIR, fname)
                generate_post_image(
                    topic["asignatura"], topic["grado"], topic["tema"], pillar, out_path,
                )
                media_url = f"{REPO_RAW_BASE}/{MEDIA_DIR}/{fname}"
                if media_type == "story_photo":
                    caption, hashtags = "", ""
                else:
                    caption, hashtags = make_topic_caption(topic, pillar)

            rows.append({
                "date": slot_date.isoformat(),
                "time": time_str,
                "type": media_type,
                "media_url": media_url,
                "caption": caption,
                "hashtags": hashtags,
                "status": "pending",
            })

    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weeks", type=int, default=2)
    parser.add_argument("--start-date", type=str, default=None,
                         help="YYYY-MM-DD, por defecto mañana")
    args = parser.parse_args()

    start_date = (
        datetime.strptime(args.start_date, "%Y-%m-%d").date()
        if args.start_date else date.today() + timedelta(days=1)
    )

    topics = load_topics()
    existing_rows = load_calendar()

    # Descarta filas "draft" con placeholder (generadas a mano antes de
    # tener este pipeline) — se reemplazan por contenido real.
    kept_rows = [r for r in existing_rows if r["status"].strip().lower() != "draft"]

    new_rows = build_rows(start_date, args.weeks, topics)
    save_calendar(kept_rows + new_rows)

    print(f"Agregadas {len(new_rows)} filas nuevas desde {start_date.isoformat()} "
          f"({args.weeks} semana(s)). Filas descartadas por ser 'draft': "
          f"{len(existing_rows) - len(kept_rows)}.")


if __name__ == "__main__":
    main()
