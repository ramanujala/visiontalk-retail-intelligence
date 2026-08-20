# Development Guidelines — VisionTalk Retail Intelligence

## 1. Code Quality & Architecture Standards

### 1.1 Python / FastAPI Guidelines
- **Python Version**: Python 3.11+ required.
- **Type Hints**: Mandatory strictly typed code using Python `typing` module and `Pydantic v2` schemas.
- **Async Usage**: Use `async def` for I/O bound endpoints (DB queries, file saving, API calls); use standard synchronous functions or thread pools for heavy CPU vision processing (`cv2`, `ultralytics`).
- **Code Style**: Format with `black`, sort imports with `isort`, check quality with `flake8` / `ruff`.

### 1.2 Frontend / React Guidelines
- **Framework**: React 18 with TypeScript.
- **Styling**: Vanilla CSS with CSS Modules and dynamic tokens (vibrant dark modern theme, glassmorphism, responsive cards). No arbitrary inline styles.
- **State Management**: React Hooks and lightweight stores (Zustand) where needed.
- **Safety**: Strict TypeScript typing without `any` overrides.

---

## 2. Git & Version Control Protocol

### 2.1 Branching Strategy
- `master` / `main`: Production-ready, fully tested code.
- Feature commits must be semantic and atomic.

### 2.2 Commit Message Convention
```text
feat(cv): add bounding box coordinate normalization utility
fix(ocr): resolve null pointer when price tag text is empty
docs(arch): update database ER diagram in DATA_MODEL.md
test(api): add pytest unit test for /images/upload endpoint
refactor(evidence): modularize spatial coordinate indexing logic
```

### 2.3 Pre-Commit Checklist
Before committing any changes:
1. Run `pytest` to verify backend tests pass clean.
2. Check `git status` and `git diff` to ensure no unexpected files or `.env` secrets are modified.
3. Confirm documentation (`docs/*`) is updated if API endpoints, database schemas, or business logic changed.

---

## 3. Security & Environment Protection

- **No Hardcoded Secrets**: Secrets (JWT secret, DB password, API keys) must be loaded from environment variables via `app/core/config.py`.
- **Environment Files**: `.env.example` must contain template variable names. `.env` MUST be listed in `.gitignore` and NEVER committed.
- **Input Sanitation**: All file uploads, query parameters, and OCR string payloads are sanitized before processing.

---

## 4. Phase Execution & Testing Strictness

- Each phase in `docs/ROADMAP.md` MUST be executed independently.
- **No Unexecuted Claims**: Never claim tests passed or metrics reached unless commands were actually run and verified with empirical outputs.
- Maintain tests for all new functions added in backend and computer vision modules.
