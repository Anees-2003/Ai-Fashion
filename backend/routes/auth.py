import os
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime
from database import users_col
from services.auth_service import hash_password, verify_password, create_access_token, decode_token
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
security = HTTPBearer(auto_error=False)

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@aifashion.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@1234")


# ─── Pydantic Schemas ─────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ─── Dependency: get current user from JWT ──────────────

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


async def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = await get_current_user(credentials)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload


# ─── User Registration ────────────────────────────────────

@router.post("/auth/register", response_model=TokenResponse)
async def register(req: RegisterRequest):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    existing = await users_col.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered.")

    user_doc = {
        "name": req.name,
        "email": req.email,
        "password_hash": hash_password(req.password),
        "role": "user",
        "created_at": datetime.utcnow().isoformat(),
    }
    result = await users_col.insert_one(user_doc)
    user_id = str(result.inserted_id)

    token = create_access_token({"sub": user_id, "email": req.email, "name": req.name, "role": "user"})
    return {
        "access_token": token,
        "user": {"id": user_id, "name": req.name, "email": req.email, "role": "user"},
    }


# ─── User Login ───────────────────────────────────────────

@router.post("/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    user = await users_col.find_one({"email": req.email})
    if not user or not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    user_id = str(user["_id"])
    token = create_access_token({
        "sub": user_id,
        "email": user["email"],
        "name": user.get("name", ""),
        "role": user.get("role", "user"),
    })
    return {
        "access_token": token,
        "user": {"id": user_id, "name": user.get("name", ""), "email": user["email"], "role": user.get("role", "user")},
    }


# ─── Admin Login ─────────────────────────────────────────

@router.post("/auth/admin/login", response_model=TokenResponse)
async def admin_login(req: LoginRequest):
    if req.email != ADMIN_EMAIL or req.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin credentials.")

    token = create_access_token({"sub": "admin", "email": ADMIN_EMAIL, "name": "Admin", "role": "admin"})
    return {
        "access_token": token,
        "user": {"id": "admin", "name": "Admin", "email": ADMIN_EMAIL, "role": "admin"},
    }


# ─── Me (current user info) ───────────────────────────────

@router.get("/auth/me")
async def me(current_user: dict = Depends(get_current_user)):
    return current_user


# ─── Admin: All Users ─────────────────────────────────────

@router.get("/admin/users")
async def admin_get_users(admin: dict = Depends(require_admin)):
    users = []
    async for u in users_col.find({}, {"password_hash": 0, "_id": 1, "name": 1, "email": 1, "role": 1, "created_at": 1}).sort("created_at", -1):
        u["id"] = str(u.pop("_id"))
        users.append(u)
    return {"total": len(users), "users": users}


# ─── Admin: Stats ─────────────────────────────────────────

@router.get("/admin/stats")
async def admin_stats(admin: dict = Depends(require_admin)):
    from database import designs_col, uploads_col, recommendations_col, products_col
    return {
        "users": await users_col.count_documents({}),
        "designs": await designs_col.count_documents({}),
        "uploads": await uploads_col.count_documents({}),
        "recommendations": await recommendations_col.count_documents({}),
        "products": await products_col.count_documents({}),
    }
