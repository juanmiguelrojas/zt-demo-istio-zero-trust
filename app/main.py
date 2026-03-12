# Zero Trust Demo (k3d + Istio)

## Run (high level)
1) Build + import image to k3d
2) Deploy insecure + show it is open
3) Deploy secure + apply mTLS STRICT + deny-by-default + allowlist

## Files
- app/: FastAPI app
-






@'
import os
import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI()

SERVICE_NAME = os.getenv("SERVICE_NAME", "unknown")
EXP_ID = os.getenv("EXP_ID", "exp-unknown")

USERS_URL = os.getenv("USERS_URL", "http://users:8000")
PAY_URL = os.getenv("PAY_URL", "http://pay:8000")


@app.get("/health")
def health():
    return {"ok": True, "service": SERVICE_NAME, "exp_id": EXP_ID}


@app.get("/admin")
def admin():
    return {"admin": True, "exp_id": EXP_ID}


@app.get("/users")
def users():
    return {"users": ["alice", "bob"], "service": SERVICE_NAME, "exp_id": EXP_ID}


@app.get("/pay")
def pay():
    return {"paid": True, "amount": 10, "service": SERVICE_NAME, "exp_id": EXP_ID}


@app.get("/gateway/users")
async def gateway_users():
    async with httpx.AsyncClient(timeout=3.0) as client:
        r = await client.get(f"{USERS_URL}/users")
    if r.status_code >= 400:
        raise HTTPException(status_code=502, detail="upstream users error")
    return {"upstream": "users", "status": r.status_code, "body": r.json(), "exp_id": EXP_ID}


@app.get("/gateway/pay")
async def gateway_pay():
    async with httpx.AsyncClient(timeout=3.0) as client:
        r = await client.get(f"{PAY_URL}/pay")
    if r.status_code >= 400:
        raise HTTPException(status_code=502, detail="upstream pay error")
    return {"upstream": "pay", "status": r.status_code, "body": r.json(), "exp_id": EXP_ID}
