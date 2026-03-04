import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path as PathParam, Request, status

from app.models import Contact, ContactCreate
from app.repository import ContactRepository
from app.services import ContactProcessor

logger = logging.getLogger("backend_assignment")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


def get_repository(request: Request) -> ContactRepository:
    return request.app.state.contact_repo


def get_contact_processor() -> ContactProcessor:
    return ContactProcessor()


def create_app(data_file: Path | None = None) -> FastAPI:
    data_path = data_file or Path(__file__).resolve().parents[1] / "data" / "contacts.json"

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Load hard-coded JSON once and keep everything in memory.
        app.state.contact_repo = ContactRepository.from_json_file(data_path)
        yield

    app = FastAPI(title="Backend Take Home", lifespan=lifespan)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        started_at = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.info(
            "%s %s -> %s (%.2fms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response

    @app.get("/")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/contacts/{contact_id}", response_model=Contact)
    def get_contact(
        contact_id: Annotated[int, PathParam(gt=0)],
        repository: ContactRepository = Depends(get_repository),
    ) -> Contact:
        contact = repository.get_by_id(contact_id)
        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact {contact_id} not found",
            )
        return contact

    @app.post("/contacts", response_model=Contact, status_code=status.HTTP_201_CREATED)
    def add_contact(
        payload: ContactCreate,
        repository: ContactRepository = Depends(get_repository),
        processor: ContactProcessor = Depends(get_contact_processor),
    ) -> Contact:
        processed_payload = processor.process(payload)
        return repository.add(processed_payload)

    @app.delete("/contacts/{contact_id}", response_model=Contact)
    def delete_contact(
        contact_id: Annotated[int, PathParam(gt=0)],
        repository: ContactRepository = Depends(get_repository),
    ) -> Contact:
        deleted_contact = repository.delete(contact_id)
        if deleted_contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact {contact_id} not found",
            )
        return deleted_contact

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "10000")),
    )
