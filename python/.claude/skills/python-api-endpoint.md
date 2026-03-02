---
name: python-api-endpoint
description: Create new FastAPI endpoints following project conventions with proper schemas, validation, and tests.
triggers:
  - "create endpoint"
  - "add route"
  - "new API"
  - "add endpoint"
tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# Python API Endpoint Creator Skill

## When Triggered

Create a new FastAPI endpoint following the project's architectural conventions.

## Steps

1. **Understand the requirement**: What resource/action does this endpoint handle?

2. **Create the Pydantic schemas** in `src/app/api/v1/schemas/`:
   ```python
   from pydantic import BaseModel, Field

   class CreateItemRequest(BaseModel):
       name: str = Field(..., min_length=1, max_length=255)
       description: str | None = None

   class ItemResponse(BaseModel):
       id: int
       name: str
       description: str | None
       created_at: datetime

       model_config = ConfigDict(from_attributes=True)
   ```

3. **Create the business logic** in `src/app/core/`:
   - Service functions/classes with full type hints
   - Custom exceptions for domain errors
   - No framework dependencies in core logic

4. **Create the route** in `src/app/api/v1/routes/`:
   ```python
   from fastapi import APIRouter, Depends, status

   router = APIRouter(prefix="/items", tags=["items"])

   @router.post("/", status_code=status.HTTP_201_CREATED, response_model=ItemResponse)
   async def create_item(
       request: CreateItemRequest,
       service: ItemService = Depends(get_item_service),
   ) -> ItemResponse:
       return await service.create(request)
   ```

5. **Register the router** in the appropriate `__init__.py` or `main.py`

6. **Create tests**:
   - Unit tests for business logic in `tests/unit/`
   - Integration tests for the endpoint in `tests/integration/`
   - Use `httpx.AsyncClient` with `ASGITransport` for API tests

7. **Run quality gates**:
   ```bash
   uv run ruff check --fix <new files>
   uv run ruff format <new files>
   uv run mypy <new files>
   uv run pytest <test files> -v
   ```

## Key Conventions

- Endpoints are **thin controllers** — delegate to service layer
- Always use proper HTTP status codes (201, 204, 404, 422)
- All request/response bodies use Pydantic BaseModel
- Use `Depends()` for dependency injection
- Use `APIRouter` with prefix and tags
- Return type hint must match `response_model`
