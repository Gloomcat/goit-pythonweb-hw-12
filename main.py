from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from src.api import contacts, utils, auth, users

app = FastAPI()

# CORS settings
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handles RateLimitExceeded exceptions by returning a 429 response.

    Args:
        request (Request): The incoming request.
        exc (RateLimitExceeded): The exception raised when the rate limit is exceeded.

    Returns:
        JSONResponse: A response indicating the client has made too many requests.
    """
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests."},
    )


# Include API routers
app.include_router(contacts.router, prefix="/api")
app.include_router(utils.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
