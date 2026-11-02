"""Cria uma conta de utilizador diretamente na base de dados.

Operação de operador (requer acesso ao shell/contentor), não é uma API pública.
Se ``--password`` for omitido, é gerada uma palavra-passe aleatória e impressa
uma única vez.

Exemplos:
    python -m scripts.create_user --email admin@escola.pt --role admin
    python -m scripts.create_user --email prof@escola.pt --role teacher --name "Ana"
"""

from __future__ import annotations

import argparse
import asyncio
import secrets
import sys

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal, engine
from app.models.school import Teacher
from app.models.user import Role, User

VALID_ROLES = (Role.ADMIN, Role.TEACHER, Role.COORDINATOR, Role.STUDENT)


async def create_user(
    email: str,
    password: str,
    role: str,
    full_name: str | None,
    institution_id: str | None,
    skip_existing: bool = False,
) -> bool:
    """Cria o utilizador. Devolve True se criou, False se já existia."""

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none() is not None:
            if skip_existing:
                print(f"= {email} já existe, ignorado")
                return False
            raise SystemExit(f"ERRO: já existe uma conta para {email}")

        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=role,
            institution_id=institution_id,
        )
        db.add(user)
        await db.flush()

        # Docentes precisam do perfil Teacher para indisponibilidades/contestações.
        if role == Role.TEACHER:
            db.add(Teacher(user_id=user.id, institution_id=institution_id))

        await db.commit()
        print(f"+ {email} criado (role={role}, id={user.id})")
        return True


async def _main(args: argparse.Namespace) -> int:
    generated = args.password is None
    password = args.password or secrets.token_urlsafe(12)

    if len(password) < 6:
        print("ERRO: a palavra-passe deve ter pelo menos 6 caracteres", file=sys.stderr)
        return 2

    try:
        created = await create_user(
            email=args.email.strip(),
            password=password,
            role=args.role,
            full_name=args.name,
            institution_id=args.institution,
            skip_existing=args.if_not_exists,
        )
    finally:
        await engine.dispose()

    if created and generated:
        print(f"  palavra-passe gerada: {password}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria uma conta de utilizador.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", help="se omitida, é gerada uma aleatória")
    parser.add_argument("--role", choices=VALID_ROLES, default=Role.STUDENT)
    parser.add_argument("--name", dest="name", default=None)
    parser.add_argument("--institution", default=None)
    parser.add_argument(
        "--if-not-exists",
        action="store_true",
        help="não falha se o email já existir (usado pelo seed)",
    )
    raise SystemExit(asyncio.run(_main(parser.parse_args())))


if __name__ == "__main__":
    main()
