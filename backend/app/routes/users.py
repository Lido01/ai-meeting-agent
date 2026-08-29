
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


@router.post("/", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    print("===== CREATE USER START =====")

    print("Received user:", user.email)

    # --------------------------------------------------------
    # STEP 1: Check existing user
    # --------------------------------------------------------

    print("Checking existing user...")

    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    print("Existing user:", existing_user)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # --------------------------------------------------------
    # STEP 2: Hash password
    # --------------------------------------------------------

    print("Starting password hash...")

    hashed_password = pwd_context.hash(
        user.password
    )

    print("Password hash completed.")

    # --------------------------------------------------------
    # STEP 3: Create database object
    # --------------------------------------------------------

    print("Creating User object...")

    new_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        password_hash=hashed_password
    )

    print("User object created.")

    # --------------------------------------------------------
    # STEP 4: Add to session
    # --------------------------------------------------------

    print("Adding user to database session...")

    db.add(new_user)

    print("User added to session.")

    # --------------------------------------------------------
    # STEP 5: Commit
    # --------------------------------------------------------

    print("Starting database commit...")

    db.commit()

    print("Database commit completed.")

    # --------------------------------------------------------
    # STEP 6: Refresh
    # --------------------------------------------------------

    print("Refreshing user...")

    db.refresh(new_user)

    print("User refresh completed.")

    print("===== CREATE USER SUCCESS =====")

    return new_user
