from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.services.user_service import authenticate_user, create_user, create_token_for_user, get_user_by_email

router = APIRouter()

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    user = create_user(db, email, password)
    access_token = create_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}
