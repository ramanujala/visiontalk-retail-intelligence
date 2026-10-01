from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exceptions import (
    VisionTalkException,
    visiontalk_exception_handler,
    http_exception_handler,
    global_exception_handler
)
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.stores import router as stores_router
from app.api.v1.images import router as images_router
from app.api.v1.detections import router as detections_router
from app.api.v1.ocr import router as ocr_router
from app.api.v1.evidence import router as evidence_router
from app.api.v1.expected_products import router as expected_products_router
from app.api.v1.expected_actual import router as expected_actual_router
from app.api.v1.compliance_rules import router as compliance_rules_router
from app.api.v1.compliance import router as compliance_router
from app.api.v1.llm import router as llm_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
app.add_exception_handler(VisionTalkException, visiontalk_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include API Routers
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(stores_router, prefix=settings.API_V1_STR)
app.include_router(images_router, prefix=settings.API_V1_STR)
app.include_router(detections_router, prefix=settings.API_V1_STR)
app.include_router(ocr_router, prefix=settings.API_V1_STR)
app.include_router(evidence_router, prefix=settings.API_V1_STR)
app.include_router(expected_products_router, prefix=settings.API_V1_STR)
app.include_router(expected_actual_router, prefix=settings.API_V1_STR)
app.include_router(compliance_rules_router, prefix=settings.API_V1_STR)
app.include_router(compliance_router, prefix=settings.API_V1_STR)
app.include_router(llm_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "message": "Welcome to VisionTalk Retail Intelligence API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }
