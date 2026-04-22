# SPUT

Sistema Flask para gestion de ordenes tecnicas.

## Desarrollo local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python init_db.py
python app.py
```

## VPS

Ver `VPS_DEPLOY.md`.

## Importante

No subir `.env`, backups, bases de datos ni documentos generados con datos reales.
