from fastapi import APIRouter, HTTPException, File, UploadFile, Response, Security
from fastapi.params import Depends
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.databases.postgres_orm import get_session
from app.databases.repositories_orm.user import create_user, create_path_preview, save_image_preview
from app.databases.repositories_sql.user import get_user, get_image_user_db
from app.security.crypt import hash_password, verify_password
from app.security.jwt import create_access_token, create_refresh_token
from app.schemas.schema_user import CreateUserRequest, DataUserResponse, LoginUserRequest, PreviewImageUserResponse
from app.static import access_security, refresh_security
from app.utils import get_user_id

router = APIRouter(prefix="/user", tags=["Catalog"])


@router.post("/signup", response_model=DataUserResponse, status_code=201)
async def sign_up(data: CreateUserRequest, session: AsyncSession = Depends(get_session)):
    try:
        user = await create_user(session, data.username, data.email, hash_password(data.password))
        access_token = create_access_token(user.id, user.username)
        refresh_token = create_refresh_token(user.id, user.username)
        return DataUserResponse(
            username=user.username,
            email=user.email,
            access_token=access_token,
            refresh_token=refresh_token
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Логин или почта уже заняты")


@router.post("/signin", response_model=DataUserResponse)
async def sign_in(data: LoginUserRequest):
    result_db = await get_user(data.login)

    if result_db is None:
        raise HTTPException(status_code=400, detail="Такой пользователь не зарегистрирован")

    elif not verify_password(data.password, result_db["password"]):
        raise HTTPException(status_code=400, detail="Не правильный пароль")

    username: str = result_db["username"]
    email: str = result_db["email"]
    access_token = create_access_token(result_db['id'], username)
    refresh_token = create_refresh_token(result_db['id'], username)

    return DataUserResponse(
        username=username,
        email=email,
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/change_preview", status_code=201)
async def change_preview(
        image: UploadFile = File(...),
        credentials: JwtAuthorizationCredentials = Security(access_security),
        session: AsyncSession = Depends(get_session)
):
    user_id: int = credentials.subject["id"]

    path_preview = await save_image_preview(image, user_id)

    if not await create_path_preview(session, user_id, path_preview):
        raise HTTPException(status_code=500, detail="Error in server")

    return Response(status_code=201)


@router.post("/get_image_user", response_model=PreviewImageUserResponse)
async def get_image_user(username: str):
    user_id = await get_user_id(username)

    return await get_image_user_db(user_id)


@router.post("/update_token", response_model=DataUserResponse)
async def update_token(credentials: JwtAuthorizationCredentials = Security(refresh_security)):
    username: str = credentials.subject["username"]

    result_db = await get_user(username)
    if result_db is None:
        raise HTTPException(status_code=500, detail="User not found")

    email: str = result_db["email"]
    access_token = create_access_token(result_db['id'], username)
    refresh_token = create_refresh_token(result_db['id'], username)

    return DataUserResponse(
        username=username,
        email=email,
        access_token=access_token,
        refresh_token=refresh_token
    )
