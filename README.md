# Backend Take Home (FastAPI + pytest)

This project follows the assignment requirements from the image:

- 3 endpoints:
  - `GET /contacts/{contact_id}`: get object by ID
  - `POST /contacts`: add object
  - `DELETE /contacts/{contact_id}`: delete object
- Request logging middleware
- Validation for add/delete requests
- Dependency injection via a service class (`ContactProcessor`)
- Unit tests with pytest

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run tests

```bash
pytest -q
```
