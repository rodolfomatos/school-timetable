"""Router de turmas: CRUD completo."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user, require_role
from app.models.school import Class
from app.models.user import Role, User
from app.schemas.school import ClassCreate, ClassRead, ClassUpdate

router = APIRouter(prefix="/schools/classes", tags=["schools"])


def _get_institution_id(current_user: User) -> str | None:
    """Extrai institution_id do utilizador atual."""
    return current_user.institution_id


@router.post("/", response_model=ClassRead, status_code=status.HTTP_201_CREATED)
async def create_class(
    class_in: ClassCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.ADMIN, Role.COORDINATOR)),
):
    """Cria uma nova turma."""

    institution_id = current_user.institution_id
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador sem institution_id",
        )

    class_obj = Class(**class_in.model_dump(), institution_id=institution_id)
    db.add(class_obj)
    await db.commit()
    await db.refresh(class_obj)
    return class_obj


@router.get("/", response_model=list[ClassRead])
async def list_classes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todas as turmas da instituição do utilizador."""

    institution_id = current_user.institution_id
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador sem institution_id",
        )

    result = await db.execute(select(Class).where(Class.institution_id == institution_id))
    return result.scalars().all()


@router.get("/{class_id}", response_model=ClassRead)
async def get_class(
    class_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtém uma turma pelo ID."""

    institution_id = current_user.institution_id
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador sem institution_id",
        )

    result = await db.execute(select(Class).where(Class.id == class_id, Class.institution_id == institution_id))
    class_obj = result.scalar_one_or_none()
    if class_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turma não encontrada",
        )
    return class_obj


@router.put("/{class_id}", response_model=ClassRead)
async def update_class(
    class_id: int,
    class_in: ClassUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.ADMIN, Role.COORDINATOR)),
):
    """Atualiza uma turma."""

    institution_id = current_user.institution_id
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador sem institution_id",
        )

    result = await db.execute(select(Class).where(Class.id == class_id, Class.institution_id == institution_id))
    class_obj = result.scalar_one_or_none()
    if class_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turma não encontrada",
        )

    update_data = class_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(class_obj, field, value)

    await db.commit()
    await db.refresh(class_obj)
    return class_obj


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(
    class_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """Remove uma turma."""

    institution_id = current_user.institution_id
    if not institution_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador sem institution_id",
        )

    result = await db.execute(select(Class).where(Class.id == class_id, Class.institution_id == institution_id))
    class_obj = result.scalar_one_or_none()
    if class_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turma não encontrada",
        )

    await db.delete(class_obj)
    await db.commit()