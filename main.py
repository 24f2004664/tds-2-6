from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import time


app = FastAPI()

EMAIL = "24f2004664@ds.study.iitm.ac.in"

ALLOWED_ORIGIN = "https://app-1rqf55.example.com"

RATE_LIMIT = 11
WINDOW = 10

rate_buckets = {}


# Middleware 2: strict CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        ALLOWED_ORIGIN
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware 3: rate limiter
@app.middleware("http")
async def rate_limit(request: Request, call_next):

    client_id = request.headers.get(
        "X-Client-Id",
        "default"
    )

    now = time.time()

    bucket = rate_buckets.setdefault(
        client_id,
        []
    )

    bucket[:] = [
        t for t in bucket
        if now - t < WINDOW
    ]

    if len(bucket) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={
                "detail": "rate limit exceeded"
            }
        )

    bucket.append(now)

    return await call_next(request)



# Middleware 1: request context
@app.middleware("http")
async def request_context(request: Request, call_next):

    request_id = request.headers.get(
        "X-Request-ID"
    )

    if not request_id:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response



@app.get("/")
def home():
    return {
        "status": "ok"
    }


@app.get("/ping")
def ping(request: Request):

    return {
        "email": EMAIL,
        "request_id": request.state.request_id
    }
