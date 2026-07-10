"""
scheduler.py
Revisa content_calendar.csv y publica automáticamente el contenido
programado para "ahora" (o antes). Pensado para correr por cron o
GitHub Actions cada 15-30 minutos.

Uso manual:
    python scheduler.py
"""

import csv
from datetime import datetime
from zoneinfo import ZoneInfo

# Las fechas/horas del calendario se interpretan en hora local de Chile.
TZ = ZoneInfo("America/Santiago")

from instagram_api import (
    publish_photo_post,
    publish_carousel,
    publish_reel,
    publish_story_photo,
    publish_story_video,
    InstagramAPIError,
)

CALENDAR_FILE = "content_calendar.csv"
FIELDNAMES = ["date", "time", "type", "media_url", "caption", "hashtags", "status"]


def load_calendar():
    with open(CALENDAR_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_calendar(rows):
    with open(CALENDAR_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def build_caption(row):
    caption = row.get("caption", "").strip()
    hashtags = row.get("hashtags", "").strip()
    if hashtags:
        caption = f"{caption}\n\n{hashtags}" if caption else hashtags
    return caption


def publish_row(row):
    media_type = row["type"].strip().lower()
    caption = build_caption(row)
    media_url = row["media_url"].strip()

    if media_type == "post":
        return publish_photo_post(media_url, caption)
    if media_type == "carousel":
        urls = [u.strip() for u in media_url.split("|") if u.strip()]
        return publish_carousel(urls, caption)
    if media_type == "reel":
        return publish_reel(media_url, caption)
    if media_type == "story_photo":
        return publish_story_photo(media_url)
    if media_type == "story_video":
        return publish_story_video(media_url)

    raise ValueError(f"Tipo de contenido desconocido: '{media_type}'")


def run():
    now = datetime.now(TZ)
    rows = load_calendar()
    changed = False

    for row in rows:
        if row["status"].strip().lower() != "pending":
            continue

        try:
            scheduled = datetime.strptime(f"{row['date']} {row['time']}", "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        except ValueError:
            print(f"⚠️  Fecha/hora inválida en fila: {row}")
            continue

        if scheduled <= now:
            try:
                media_id = publish_row(row)
                row["status"] = f"published:{media_id}"
                print(f"✅ Publicado ({row['type']}) - id {media_id}")
            except InstagramAPIError as e:
                row["status"] = "error"
                print(f"❌ Error publicando fila {row}: {e}")
            changed = True

    if changed:
        save_calendar(rows)
    else:
        print("Nada pendiente para publicar en este momento.")


if __name__ == "__main__":
    run()
