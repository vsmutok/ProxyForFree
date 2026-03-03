from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from api.routes import router
from core.config import API_AUTH_ENABLED, API_PASS, API_USER

# ---------- Optional HTTP Basic Auth ----------
# Uses API_USER / API_PASS from .env.
# Set API_AUTH_ENABLED=1 in .env to require authentication.
security = HTTPBasic(auto_error=False)
_security_dependency = Security(security)


def verify_credentials(credentials: HTTPBasicCredentials | None = _security_dependency):
    if not API_AUTH_ENABLED:
        return
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )
    if credentials.username != API_USER or credentials.password != API_PASS:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


app = FastAPI(
    title="ProxyForFree API",
    description="REST API for managing proxy servers via OpenVPN + 3proxy",
    version="1.0.0",
    dependencies=[Depends(verify_credentials)],
)

app.include_router(router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": "ProxyForFree API"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
