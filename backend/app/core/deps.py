"""Dependências da aplicação: sessão de base de dados, utilizador atual, verificação de papel."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.school import Role


async def get_db() -> AsyncSession:
    """Fornece uma sessão de base de dados assíncrona por request."""

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_token_from_request(request: Request) -> str | None:
    """Extrai o token de acesso do cookie httpOnly ou do header Authorization."""

    # Primeiro tenta o cookie httpOnly
    token = request.cookies.get("access_token")
    if token:
        return token

    # Fallback para header Authorization: Bearer <token>
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1]

    return None


async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Retorna o utilizador autenticado a partir do token JWT (cookie ou header)."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = await get_token_from_request(request)
    if token is None:
        raise credentials_exception

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user


def require_role(*allowed_roles: Role):
    """Cria uma dependência que verifica se o utilizador tem um dos papéis permitidos."""

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente",
            )
        return current_user

    return role_checker
