import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

# --- Configuration ---
SECRET_KEY = "a_very_secret_key_that_should_be_in_a_config_file"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Setup ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
router = APIRouter()

# --- Pydantic Models ---
class User(BaseModel):
    id: str
    email: str
    name: str
    role: str
    permissions: list[str]

class TokenData(BaseModel):
    username: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str

class UserRegistration(BaseModel):
    email: str
    password: str
    name: str


class AuthManager:
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    # In a real app, this would look up the user in the database
    def get_user(self, username: str):
        if username == "testuser":
            return {"username": "testuser", "hashed_password": self.get_password_hash("testpassword")}
        return None

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

auth_manager = AuthManager()

# --- API Endpoints ---
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_manager.get_user(form_data.username)
    if not user or not auth_manager.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_manager.create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Dependencies ---
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = auth_manager.get_user(username)
    if user is None:
        raise credentials_exception
    # In a real app, you'd return a proper user model here
    return {"name": user.get("username"), "email": f"{user.get('username')}@example.com"}

@router.post("/register", response_model=Token)
async def register_user(user_data: UserRegistration):
    # In a real app, you'd save the user to the database
    # Here we just pretend it was successful
    access_token = auth_manager.create_access_token(data={"sub": user_data.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout_user():
    # In a real app, you might invalidate a token here
    return {"message": "Logout successful"}

@router.post("/verify")
async def verify_token(user: dict = Depends(get_current_user)):
    # get_current_user already validates the token
    return {"valid": True, "user": user}

@router.post("/refresh", response_model=Token)
async def refresh_token(user: dict = Depends(get_current_user)):
    # The user is valid, so issue a new token
    access_token = auth_manager.create_access_token(data={"sub": user.get("email")})
    return {"access_token": access_token, "token_type": "bearer"}
