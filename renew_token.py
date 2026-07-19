"""
renew_token.py
Refresca el token de acceso de larga duración de Instagram (dura 60 días,
se puede renovar después de las primeras 24h) y actualiza el secret
IG_ACCESS_TOKEN en GitHub para que el resto de los workflows lo usen
sin intervención manual.

Requiere estas variables de entorno (ver README.md, sección 8):
- IG_ACCESS_TOKEN : token actual (ya existe como secret del repo)
- GH_PAT          : Personal Access Token de GitHub con permiso para
                     escribir secrets de este repo (scope "repo" clásico,
                     o fine-grained con "Secrets: write")
- GITHUB_REPOSITORY: lo inyecta GitHub Actions automáticamente ("owner/repo")

Documentación oficial del refresh:
https://developers.facebook.com/docs/instagram-platform/reference/refresh_access_token/
"""

import os
import sys
from base64 import b64encode

import requests
from nacl import encoding, public

IG_REFRESH_URL = "https://graph.instagram.com/refresh_access_token"


def refresh_ig_token(current_token):
    resp = requests.get(
        IG_REFRESH_URL,
        params={"grant_type": "ig_refresh_token", "access_token": current_token},
        timeout=30,
    )
    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError(f"No se pudo refrescar el token: {data}")
    return data["access_token"], data.get("expires_in")


def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    """Encripta un valor como lo exige la API de Secrets de GitHub (sealed box de libsodium)."""
    pk = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(pk)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


def update_github_secret(repo, pat, secret_name, secret_value):
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github+json",
    }

    key_resp = requests.get(
        f"https://api.github.com/repos/{repo}/actions/secrets/public-key",
        headers=headers,
        timeout=30,
    )
    key_resp.raise_for_status()
    key_data = key_resp.json()

    encrypted_value = encrypt_secret(key_data["key"], secret_value)

    put_resp = requests.put(
        f"https://api.github.com/repos/{repo}/actions/secrets/{secret_name}",
        headers=headers,
        json={"encrypted_value": encrypted_value, "key_id": key_data["key_id"]},
        timeout=30,
    )
    put_resp.raise_for_status()


def main():
    current_token = os.environ.get("IG_ACCESS_TOKEN")
    gh_pat = os.environ.get("GH_PAT")
    repo = os.environ.get("GITHUB_REPOSITORY")

    if not current_token:
        sys.exit("Falta IG_ACCESS_TOKEN en el entorno.")
    if not gh_pat:
        sys.exit(
            "Falta GH_PAT en el entorno (Personal Access Token con permiso "
            "de 'Secrets: write' sobre este repo). Ver README.md sección 8."
        )
    if not repo:
        sys.exit("Falta GITHUB_REPOSITORY (normalmente lo inyecta GitHub Actions).")

    new_token, expires_in = refresh_ig_token(current_token)
    update_github_secret(repo, gh_pat, "IG_ACCESS_TOKEN", new_token)

    days = round(expires_in / 86400, 1) if expires_in else "desconocidos"
    print(f"✅ Token renovado. Válido por ~{days} días más. Secret IG_ACCESS_TOKEN actualizado en {repo}.")


if __name__ == "__main__":
    main()
