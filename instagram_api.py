"""
instagram_api.py
Wrapper para publicar contenido en Instagram usando la API OFICIAL
de Meta con "Instagram Login" (Instagram API with Instagram business
login). Requiere que la cuenta sea Profesional (Empresa o Creador).
NO requiere una Página de Facebook: se autentica directo con la cuenta
de Instagram y usa el host graph.instagram.com.

Documentación oficial:
https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/content-publishing
"""

import time
import requests
from config import IG_USER_ID, ACCESS_TOKEN

GRAPH_API_VERSION = "v21.0"
BASE_URL = f"https://graph.instagram.com/{GRAPH_API_VERSION}"


class InstagramAPIError(Exception):
    pass


def _post(endpoint, params):
    url = f"{BASE_URL}/{endpoint}"
    params = {**params, "access_token": ACCESS_TOKEN}
    resp = requests.post(url, params=params, timeout=60)
    data = resp.json()
    if "error" in data:
        raise InstagramAPIError(data["error"])
    return data


def _get(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    params = {**(params or {}), "access_token": ACCESS_TOKEN}
    resp = requests.get(url, params=params, timeout=30)
    data = resp.json()
    if "error" in data:
        raise InstagramAPIError(data["error"])
    return data


def _wait_until_ready(container_id, timeout=180, interval=5):
    """Espera a que un contenedor de video/reel/historia en video termine de procesarse."""
    elapsed = 0
    while elapsed < timeout:
        status = _get(container_id, {"fields": "status_code"})
        code = status.get("status_code")
        if code == "FINISHED":
            return True
        if code == "ERROR":
            raise InstagramAPIError(f"Error procesando el contenedor {container_id}")
        time.sleep(interval)
        elapsed += interval
    raise InstagramAPIError("Tiempo de espera agotado procesando el video")


def _publish(creation_id):
    result = _post(f"{IG_USER_ID}/media_publish", {"creation_id": creation_id})
    return result.get("id")


def publish_photo_post(image_url, caption=""):
    """Publica una foto en el feed. image_url debe ser una URL pública."""
    container = _post(f"{IG_USER_ID}/media", {
        "image_url": image_url,
        "caption": caption,
    })
    return _publish(container["id"])


def publish_carousel(image_urls, caption=""):
    """Publica un carrusel (entre 2 y 10 imágenes/videos)."""
    if not (2 <= len(image_urls) <= 10):
        raise ValueError("Un carrusel necesita entre 2 y 10 elementos")

    children_ids = []
    for url in image_urls:
        item = _post(f"{IG_USER_ID}/media", {
            "image_url": url,
            "is_carousel_item": "true",
        })
        children_ids.append(item["id"])

    container = _post(f"{IG_USER_ID}/media", {
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
        "caption": caption,
    })
    return _publish(container["id"])


def publish_reel(video_url, caption="", cover_url=None):
    """Publica un Reel. video_url debe ser una URL pública (mp4)."""
    params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
    }
    if cover_url:
        params["cover_url"] = cover_url

    container = _post(f"{IG_USER_ID}/media", params)
    _wait_until_ready(container["id"])
    return _publish(container["id"])


def publish_story_photo(image_url):
    """Publica una historia con una imagen."""
    container = _post(f"{IG_USER_ID}/media", {
        "image_url": image_url,
        "media_type": "STORIES",
    })
    return _publish(container["id"])


def publish_story_video(video_url):
    """Publica una historia con un video."""
    container = _post(f"{IG_USER_ID}/media", {
        "video_url": video_url,
        "media_type": "STORIES",
    })
    _wait_until_ready(container["id"])
    return _publish(container["id"])
