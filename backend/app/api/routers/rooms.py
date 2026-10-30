"""Router de salas de aula: CRUD completo."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user, require_role
from app.models.school import Room, Role
from app.schemas.school import RoomCreate, RoomRead, RoomUpdate

router = APIRouter(prefix="/schools/rooms", tags=["schools"])


@router.post("/", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_in: RoomCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN, Role.COORDINATOR)),
):
    """Cria uma nova sala."""

    room = Room(**room_in.model_dump())
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


@router.get("/", response_model=list[RoomRead])
async def list_rooms(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Lista todas as salas."""

    result = await db.execute(select(Room))
    return result.scalars().all()


@router.get("/{room_id}", response_model=RoomRead)
async def get_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Obtém uma sala pelo ID."""

    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala não encontrada",
        )
    return room


@router.put("/{room_id}", response_model=RoomRead)
async def update_room(
    room_id: int,
    room_in: RoomUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN, Role.COORDINATOR)),
):
    """Atualiza uma sala."""

    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala não encontrada",
        )

    update_data = room_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room, field, value)

    await db.commit()
    await db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN)),
):
    """Remove uma sala."""

    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala não encontrada",
        )

    await db.delete(room)
    await db.commit()
