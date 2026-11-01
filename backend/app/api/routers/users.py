"""Router de utilizadores: listar (admin), obter perfil (me), atualizar."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user, require_role
from app.models.user import User, Role
from app.schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def _get_institution_id(current_user: User) -> str | None:
    """Extrai institution_id do utilizador atual."""
    return current_user.institution_id


@router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_user)):
    """Devolve o perfil do utilizador autenticado."""

    return current_user


@router.get("/", response_model=list[UserRead])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """Lista todos os utilizadores da instituição do admin (apenas admin)."""

    institution_id = current_user.institution_id
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador sem institution_id",
        )

    result = await db.execute(select(User).where(User.institution_id == institution_id))
    return result.scalars().all()


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """Atualiza um utilizador (apenas admin da mesma instituição)."""

    institution_id = current_user.institution_id
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador sem institution_id",
        )

    result = await db.execute(select(User).where(User.id == user_id, User.institution_id == institution_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilizador não encontrado",
        )

    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user