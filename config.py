import os
from dotenv import load_dotenv

load_dotenv()

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")

if not IG_USER_ID or not ACCESS_TOKEN:
    raise EnvironmentError(
        "Faltan variables de entorno. Copia .env.example a .env "
        "y completa IG_USER_ID e IG_ACCESS_TOKEN (ver README.md)."
    )
