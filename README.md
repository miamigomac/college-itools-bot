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
| `content_calendar.csv` | Tu calendario de contenido (lo editas tú) |
| `.github/workflows/scheduler.yml` | Corre el scheduler automáticamente cada 30 min, gratis, en GitHub |
| `strategy_guide.md` | Guía de estrategia de contenido para la cuenta |

## 1. Configuración inicial (una sola vez)

Como ya tienes tu cuenta como Empresa/Creador vinculada a una página
de Facebook, te faltan estos pasos:

1. Entra a [developers.facebook.com](https://developers.facebook.com) → **Mis apps** → **Crear app** → tipo **"Empresa"**.
2. Dentro de la app, agrega el producto **"Instagram Graph API"** (o **"Instagram"**, según cómo lo muestre el panel en este momento).
3. En **Configuración de la app → Básica**, vincula tu página de Facebook (la que está conectada a tu Instagram).
4. Ve a **Graph API Explorer** (developers.facebook.com/tools/explorer):
   - Selecciona tu app.
   - Selecciona los permisos: `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`, `business_management`.
   - Genera un **token de acceso de usuario**.
5. Convierte ese token en uno de **larga duración (60 días)**:
   ```
   GET https://graph.facebook.com/v21.0/oauth/access_token
     ?grant_type=fb_exchange_token
     &client_id=TU_APP_ID
     &client_secret=TU_APP_SECRET
     &fb_exchange_token=TU_TOKEN_CORTO
   ```
6. Obtén tu **IG_USER_ID**:
   ```
   GET https://graph.facebook.com/v21.0/me/accounts?access_token=TU_TOKEN
   ```
   Copia el `id` de tu página, luego:
   ```
   GET https://graph.facebook.com/v21.0/{page-id}?fields=instagram_business_account&access_token=TU_TOKEN
   ```
   El valor de `instagram_business_account.id` es tu `IG_USER_ID`.

7. Copia `.env.example` a `.env` y completa ambos valores:
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

## 4. Uso

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
3. O déjalo automático (ver sección 5).

### Generar captions/hashtags rápido

```bash
python caption_helper.py
```

## 5. Automatizarlo del todo (gratis, con GitHub Actions)

1. Sube esta carpeta a un repositorio de GitHub.
2. En el repo: **Settings → Secrets and variables → Actions** → agrega
   `IG_USER_ID` e `IG_ACCESS_TOKEN` como *secrets*.
3. Listo — el workflow en `.github/workflows/scheduler.yml` va a
   revisar tu calendario cada 30 minutos y publicar lo que corresponda,
   sin que tengas que prender tu compu.

(Alternativa sin GitHub: un cron job en tu propio servidor con
`*/30 * * * * cd /ruta/al/proyecto && python scheduler.py`.)

## 6. Límites que debes conocer

- Máx. **25 publicaciones** (posts + reels + carruseles combinados) por cuenta cada 24 h vía API.
- Las historias tienen su propio límite, más alto.
- Los videos/reels tardan unos segundos-minutos en procesarse antes de poder publicarse (el script ya espera esto automáticamente).

## 7. Próximos pasos que te puedo armar

- Renovación automática del token cada 60 días.
- Reporte semanal de métricas (alcance, interacciones) leyendo el Graph API.
- Generación de imágenes/carruseles con diseño automático.
- Integración con IA para redactar captions más elaborados.

Dime si quieres que agregue algo de esto.
