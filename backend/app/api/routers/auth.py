"""Router de autenticação: registo, login, refresh, logout (JWT em cookies httpOnly)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.deps import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User, Role
from app.schemas.user import (
    UserCreate,
    UserRead,
    LoginRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# Nome do cookie de acesso
ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"


def _cookie_secure() -> bool:
    """Cookies só exigem HTTPS em produção; em local/teste continuam testáveis."""

    return settings.ENVIRONMENT == "production"


def _set_access_token_cookie(response: Response, token: str) -> None:
    """Define o cookie de acesso com HttpOnly, Secure (em produção) e SameSite=Lax."""

    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=token,
        httponly=True,
        secure=_cookie_secure(),
        samesite="lax",
        path="/",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def _set_refresh_token_cookie(response: Response, token: str) -> None:
    """Define o cookie de refresh, restrito ao prefixo /auth."""

    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=token,
        httponly=True,
        secure=_cookie_secure(),
        samesite="lax",
        path="/auth",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
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

    # O registo público nunca atribui privilégios. Papéis elevados só podem
    # ser concedidos por um administrador autenticado (PATCH /users/{id}).
    requested_role = user_in.role
    if requested_role != Role.STUDENT:
        logger.warning(
            "registo público tentou papel elevado=%s; forçado para student",
            requested_role,
        )

    new_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=Role.STUDENT,
        institution_id=user_in.institution_id,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    logger.info("utilizador registado id=%s role=student", new_user.id)
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
        logger.warning("tentativa de login falhada")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou palavra-passe incorretos",
        )
    if not user.is_active:
        logger.warning("tentativa de login de utilizador desativado id=%s", user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utilizador desativado",
        )

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    _set_access_token_cookie(response, access_token)
    _set_refresh_token_cookie(response, refresh_token)
    logger.info("login com sucesso id=%s", user.id)

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
    _set_refresh_token_cookie(response, new_refresh)
    logger.info("refresh de token id=%s", user.id)

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
    response.delete_cookie(key=REFRESH_TOKEN_COOKIE, path="/auth")
    logger.info("logout efetuado")
    return None
