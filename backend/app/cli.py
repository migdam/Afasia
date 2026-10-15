"""Command line for the people who run the server.

The app has no way to create admin or therapist accounts (anyone who signs
up is a patient), so staff accounts are made here, from the backend
directory, with the same settings as the server:

    python -m app.cli create-user --username ada --email ada@example.com --role admin
    python -m app.cli set-role tess therapist

create-user asks for the password, or reads one line from standard input
with --password-stdin. Passwords never go on the command line, where they
would end up in shell history.
"""
import argparse
import getpass
import sys

from .core.security import get_password_hash
from .db.database import SessionLocal, init_db
from .db.models import User, UserRole

MIN_PASSWORD_LENGTH = 12
ROLES = [role.value for role in UserRole]


def fail(message):
    print(message, file=sys.stderr)
    return 1


def read_password(from_stdin):
    if from_stdin:
        return sys.stdin.readline().rstrip("\n")
    password = getpass.getpass("Password: ")
    if password != getpass.getpass("Password again: "):
        raise ValueError("The passwords don't match.")
    return password


def create_user(args):
    try:
        password = read_password(args.password_stdin)
    except ValueError as error:
        return fail(str(error))
    if len(password) < MIN_PASSWORD_LENGTH:
        return fail(f"The password must be at least {MIN_PASSWORD_LENGTH} characters.")

    with SessionLocal() as db:
        taken = db.query(User).filter(
            (User.username == args.username) | (User.email == args.email)
        ).first()
        if taken:
            return fail("That username or email is already in use.")
        db.add(User(
            username=args.username,
            email=args.email,
            full_name=args.full_name,
            hashed_password=get_password_hash(password),
            role=UserRole(args.role),
        ))
        db.commit()
    print(f"Created {args.role} {args.username}.")
    return 0


def set_role(args):
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == args.username).first()
        if not user:
            return fail(f"There is no user called {args.username}.")
        user.role = UserRole(args.role)
        db.commit()
    print(f"{args.username} is now {args.role}.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m app.cli", description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create-user", help="create an account with a given role")
    create.add_argument("--username", required=True)
    create.add_argument("--email", required=True)
    create.add_argument("--full-name")
    create.add_argument("--role", choices=ROLES, required=True)
    create.add_argument("--password-stdin", action="store_true", help="read the password from standard input")
    create.set_defaults(handler=create_user)

    role = commands.add_parser("set-role", help="change an existing account's role")
    role.add_argument("username")
    role.add_argument("role", choices=ROLES)
    role.set_defaults(handler=set_role)

    args = parser.parse_args(argv)
    init_db()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
