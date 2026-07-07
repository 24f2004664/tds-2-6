from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import time


app = FastAPI()

EMAIL = "24f2004664@ds.iitm.ac.in"

RATE_LIMIT = 11
WINDOW = 10

requests = {}


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app-1rqf55.example.com"
    ],
    allow_origin_regex=r"https://.*\.example\.com",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def middleware(request: Request, call_next):

    # Request ID
    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid.uuid4())
    )

    request.state.request_id = request_id


    # Skip OPTIONS
    if request.method != "OPTIONS":

        client = request.headers.get(
            "X-Client-Id",
            "default"
        )

        now = time.time()

        bucket = requests.setdefault(
            client,
            []
        )

        bucket[:] = [
            x for x in bucket
            if now - x < WINDOW
        ]

        if len(bucket) >= RATE_LIMIT:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "rate limit exceeded"
                }
            )
            response.headers["X-Request-ID"] = request_id
            return response

        bucket.append(now)


    response = await call_next(request)

    response.headers[
        "X-Request-ID"
    ] = request_id

    return response



@app.get("/")
def root():
    return {
        "ok": True
    }


@app.get("/ping")
def ping(request: Request):

    return {
        "email": EMAIL,
        "request_id": request.state.request_id
    }
