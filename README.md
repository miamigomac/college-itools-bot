# Bot de Instagram — college.itools

Herramienta lista para usar que publica posts, carruseles, reels e
historias en tu cuenta de Instagram usando la **API oficial de Meta**
(Instagram Graph API). No es un bot "no oficial" que simule la app:
por eso necesita una configuración inicial en Meta for Developers,
pero a cambio no arriesga que te suspendan la cuenta.

## Qué incluye

| Archivo | Para qué sirve |
|---|---|
| `instagram_api.py` | Funciones para publicar fotos, carruseles, reels e historias |
| `scheduler.py` | Revisa `content_calendar.csv` y publica lo que esté programado |
| `caption_helper.py` | Genera captions y hashtags con plantillas (sin costo, sin API extra) |
| `image_generator.py` | Genera las imágenes de los posts con la identidad visual de College iTools |
| `generate_calendar.py` | Arma filas nuevas del calendario a partir de `curriculum_topics.json` (temas MINEDUC) + genera sus imágenes |
| `curriculum_topics.json` | Snapshot de temas por asignatura/grado, exportado de `college-backend` |
| `content_calendar.csv` | Tu calendario de contenido |
| `generated_media/` | Imágenes generadas por `generate_calendar.py`, servidas vía raw.githubusercontent.com |
| `.github/workflows/scheduler.yml` | Corre el scheduler automáticamente cada 30 min, gratis, en GitHub |
| `.github/workflows/generate_content.yml` | Corre `generate_calendar.py` el 1 y 15 de cada mes para mantener el calendario cargado |
| `strategy_guide.md` | Guía de estrategia de contenido para la cuenta |

## 1. Configuración inicial (una sola vez)

Este bot usa la **Instagram API with Instagram Login** (no la vía
clásica de Facebook Login/Página). Es decir: te autenticas directo
con tu cuenta de Instagram Profesional (Empresa o Creador), sin pasar
por una Página de Facebook ni por Graph API Explorer. Por eso todas
las llamadas van a `graph.instagram.com` (ver `instagram_api.py` y
`renew_token.py`), no a `graph.facebook.com`.

1. Entra a [developers.facebook.com](https://developers.facebook.com) → **Mis apps** → **Crear app** → tipo **"Empresa"**.
2. Dentro de la app, agrega el producto **"Instagram"** (Instagram API setup) y configura el **"Instagram business login"**: agrega tu cuenta de Instagram y define una **redirect URI** (puede ser cualquier URL tuya, incluso `https://localhost/`, solo se usa para recibir el `code`).
3. Autoriza tu cuenta abriendo esta URL en el navegador (reemplaza `TU_APP_ID` y `TU_REDIRECT_URI`):
   ```
   https://www.instagram.com/oauth/authorize
     ?client_id=TU_APP_ID
     &redirect_uri=TU_REDIRECT_URI
     &response_type=code
     &scope=instagram_business_basic,instagram_business_content_publish
   ```
   Al autorizar, te redirige a `TU_REDIRECT_URI?code=...#_`. Copia ese `code` (sin el `#_` final).
4. Cambia el `code` por un **token de acceso de corta duración** (esta llamada también te devuelve tu `IG_USER_ID` en el campo `user_id`):
   ```
   POST https://api.instagram.com/oauth/access_token
     client_id=TU_APP_ID
     client_secret=TU_APP_SECRET
     grant_type=authorization_code
     redirect_uri=TU_REDIRECT_URI
     code=EL_CODE_DEL_PASO_ANTERIOR
   ```
5. Convierte ese token en uno de **larga duración (60 días)**:
   ```
   GET https://graph.instagram.com/access_token
     ?grant_type=ig_exchange_token
     &client_secret=TU_APP_SECRET
     &access_token=TU_TOKEN_CORTO
   ```

6. Copia `.env.example` a `.env` y completa ambos valores (`IG_USER_ID` del paso 4, `IG_ACCESS_TOKEN` del paso 5):
   ```
   cp .env.example .env
   ```

> ⚠️ El token expira cada 60 días — tendrás que repetir el paso 5
> periódicamente (o programar la renovación automática más adelante
> si quieres que te ayude con eso).

## 2. Instalación

```bash
cd college_itools_bot
pip install -r requirements.txt
```

## 3. Un detalle importante: las imágenes/videos necesitan URL pública

La API de Instagram **no acepta archivos subidos desde tu compu**,
solo URLs públicas. Opciones simples y gratuitas para hospedar tu
contenido:

- [Cloudinary](https://cloudinary.com) (plan gratuito, sube por API o por web)
- [imgbb.com](https://imgbb.com) para imágenes sueltas
- Un repositorio de GitHub público (usando el link "raw")
- Tu propio hosting o un bucket S3/Drive configurado como público

## 4. Generar contenido automáticamente (imágenes + captions)

`generate_calendar.py` arma filas nuevas del calendario solo, sin que
tengas que escribir cada caption ni conseguir imágenes a mano:

1. Elige temas de `curriculum_topics.json` (currículum MINEDUC de 3° a
   8° básico, exportado de `college-backend`), rotando entre los 4
   pilares de `strategy_guide.md`.
2. Genera la imagen de cada post/carrusel/historia con
   `image_generator.py` (Pillow, sin servicios externos), usando la
   misma identidad visual del backend: navy + dorado, fuentes Cinzel/Nunito.
3. Arma caption y hashtags con `caption_helper.py`.
4. Guarda las imágenes en `generated_media/` y escribe en el CSV una
   `media_url` apuntando a `raw.githubusercontent.com` de este mismo
   repo — por eso hace falta pushear el commit para que esas URLs
   queden accesibles antes de que el scheduler intente publicarlas.

```bash
python generate_calendar.py --weeks 2
# o desde una fecha específica:
python generate_calendar.py --weeks 2 --start-date 2026-08-01
```

Las filas quedan directo en `status: pending` (a diferencia de cuando
las cargás a mano, acá la imagen ya existe y es válida).

> ⚠️ Solo cubre `post`, `carousel` y `story_photo` — los **reels y
> las historias en video necesitan grabación real** de la app o de
> los niños usándola, así que esos los seguís cargando a mano en el
> CSV con tu propio material.

El workflow `.github/workflows/generate_content.yml` corre esto solo
el 1 y el 15 de cada mes (o manualmente desde Actions) para que el
calendario nunca se quede vacío.

## 5. Uso

### Publicar algo ahora mismo (sin esperar al calendario)

```python
from instagram_api import publish_photo_post, publish_reel, publish_story_photo

publish_photo_post("https://tu-hosting.com/imagen.jpg", caption="Mi primer post 🎉")
publish_story_photo("https://tu-hosting.com/historia.jpg")
publish_reel("https://tu-hosting.com/video.mp4", caption="Mi primer reel 🚀")
```

### Publicar por calendario (recomendado)

1. Abre `content_calendar.csv` y agrega filas con:
   - `date` (`YYYY-MM-DD`), `time` (`HH:MM`, 24h)
   - `type`: `post`, `carousel`, `reel`, `story_photo` o `story_video`
   - `media_url`: la URL pública (para carrusel, separa varias URLs con `|`)
   - `caption`, `hashtags`
   - `status`: déjalo en `pending`
2. Corre manualmente:
   ```bash
   python scheduler.py
   ```
3. O déjalo automático (ver sección 6).

### Generar captions/hashtags rápido

```bash
python caption_helper.py
```

## 6. Automatizarlo del todo (gratis, con GitHub Actions)

1. Sube esta carpeta a un repositorio de GitHub.
2. En el repo: **Settings → Secrets and variables → Actions** → agrega
   `IG_USER_ID` e `IG_ACCESS_TOKEN` como *secrets*.
3. Listo — el workflow en `.github/workflows/scheduler.yml` va a
   revisar tu calendario cada 30 minutos y publicar lo que corresponda,
   sin que tengas que prender tu compu.

(Alternativa sin GitHub: un cron job en tu propio servidor con
`*/30 * * * * cd /ruta/al/proyecto && python scheduler.py`.)

## 7. Límites que debes conocer

- Máx. **25 publicaciones** (posts + reels + carruseles combinados) por cuenta cada 24 h vía API.
- Las historias tienen su propio límite, más alto.
- Los videos/reels tardan unos segundos-minutos en procesarse antes de poder publicarse (el script ya espera esto automáticamente).

## 8. Próximos pasos que te puedo armar

- Reporte semanal de métricas (alcance, interacciones) leyendo el Graph API.
- Plantillas de imagen adicionales (historias en 9:16, distintos layouts).
- Integración con IA para redactar captions más elaborados.

Dime si quieres que agregue algo de esto.

## 9. Renovación automática del token

El token dura 60 días. `renew_token.py` lo refresca automáticamente y
actualiza el secret `IG_ACCESS_TOKEN` en GitHub, sin que tengas que
repetir el paso 5 de la configuración inicial a mano.

Corre el 1 y el 15 de cada mes vía
`.github/workflows/renew_token.yml` (bastante antes de los 60 días,
así hay margen si alguna corrida falla).

**Configuración (una sola vez):**

1. Crea un Personal Access Token de GitHub:
   **Settings de tu cuenta → Developer settings → Personal access
   tokens → Fine-grained tokens → Generate new token**.
   - Repository access: solo este repo (`college-itools-bot`).
   - Permissions → Repository permissions → **Secrets: Read and write**.
2. En el repo: **Settings → Secrets and variables → Actions** → agrega
   ese token como secret nuevo llamado `GH_PAT`.
3. Listo. También puedes forzar una renovación manual desde la pestaña
   **Actions → Renovar token de Instagram → Run workflow**.

> El refresh solo funciona si el token todavía no expiró. Si por algún
> motivo pasan los 60 días sin renovarlo, hay que repetir el paso 5 de
> la sección 1 a mano y volver a pegar el token en el secret
> `IG_ACCESS_TOKEN`.
