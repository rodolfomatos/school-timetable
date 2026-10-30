"""Router de autenticação: registo, login, refresh, logout (JWT em cookies httpOnly)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.db.session import AsyncSessionLocal
from app.models.user import User, Role
from app.schemas.user import (
    UserCreate,
    UserRead,
    LoginRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# Nome do cookie de acesso
ACCESS_TOKEN_COOKIE = "access_token"


def _set_access_token_cookie(response: Response, token: str) -> None:
    """Define o cookie de acesso com HttpOnly, Secure e SameSite=Lax."""

    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=token,
        httponly=True,
        secure=False,  # True em produção com HTTPS
        samesite="lax",
        path="/",
        max_age=30 * 60,  # 30 minutos
    )


def _clear_access_token_cookie(response: Response) -> None:
    """Remove o cookie de acesso."""

    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE,
        path="/",
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Regista um novo utilizador. Por defeito, o papel é 'student'."""

    # Verifica se o email já existe
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registado",
        )

    # Apenas um admin pode criar outro admin
    role = user_in.role
    if role == Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível criar utilizadores com papel admin via registo público",
        )

    new_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=role,
        institution_id=user_in.institution_id,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=UserRead)
async def login(
    response: Response,
    login_in: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Autentica um utilizador e define o cookie de acesso httpOnly."""

    result = await db.execute(select(User).where(User.email == login_in.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou palavra-passe incorretos",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utilizador desativado",
        )

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    _set_access_token_cookie(response, access_token)

    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        institution_id=user.institution_id,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/refresh", response_model=UserRead)
async def refresh(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Renova o token de acesso a partir do cookie de refresh."""

    # O refresh token também deve vir como cookie httpOnly em produção;
    # aqui aceitamos tanto via header Authorization (Bearer) quanto via cookie.
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            refresh_token = auth_header.split(" ", 1)[1]

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresh não encontrado",
        )

    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresh inválido",
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilizador não encontrado ou desativado",
        )

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    new_refresh = create_refresh_token({"sub": str(user.id)})

    _set_access_token_cookie(response, access_token)
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/auth",
        max_age=7 * 24 * 60 * 60,  # 7 dias
    )

    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        institution_id=user.institution_id,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    """Limpa os cookies de autenticação."""

    _clear_access_token_cookie(response)
    response.delete_cookie(key="refresh_token", path="/auth")
    return None
