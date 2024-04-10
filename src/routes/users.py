import cloudinary
import cloudinary.uploader
from sqlalchemy import select
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Depends
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.connectdb import get_db
from src.contacts.models import User
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.conf.dburl import config
from fastapi import FastAPI, APIRouter,status
from src.repository import functionuser
from src.services.email import send_password_email

router = APIRouter()
cloudinary.config(cloud_name=config.CLD_NAME, api_key=config.CLD_API_KEY, api_secret=config.CLD_API_SECRET, secure=True)


@router.get('/me', response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(user: User = Depends(auth_service.get_current_user),
                           db: AsyncSession = Depends(get_db)):
    return user


@router.patch('/avatar', response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(file: UploadFile = File(), user: User = Depends(auth_service.get_current_user),
                           db: AsyncSession = Depends(get_db)):
    public_id = f'Web16/{user.email}'
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    print(res)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill',
                                                              version=res.get('version'))
    user = await functionuser.update_avatar_url(user.email, res_url, db)
    return user


@router.get('/reset_password')
async def reset_password(email: str, db: AsyncSession = Depends(get_db)):
    query = select(User).filter(User.email == email)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким email не найден"
        )
    new_password = await functionuser.generate_password()
    user.password = auth_service.get_password_hash(new_password)
    await db.commit()
    await send_password_email(email, new_password)
    return {"message": "Новый пароль отправлен успешно"}
