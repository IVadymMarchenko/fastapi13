from fastapi import APIRouter, HTTPException, Query, Depends, status, BackgroundTasks, Request
import random
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository import functionuser
from src.db.connectdb import get_db
from src.schemas.user import UserSchema, UserResponse, TokenUpdate, RequestEmail
from src.services.auth import auth_service
from src.contacts.models import User
from src.services.email import send_email

routs = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@routs.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    exist_user = await functionuser.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exist')
    body.password = auth_service.get_password_hash(body.password)
    new_user = await functionuser.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    # TODO send email
    return new_user


@routs.post('/login', response_model=TokenUpdate)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await functionuser.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid email')
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='email not confirmed')
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid password')
    access_token = await auth_service.create_access_token(data={'sub': user.email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': user.email})
    await functionuser.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@routs.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await functionuser.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='verification error')
    if user.confirmed:
        return {'message': 'Your email already confirmed'}
    await functionuser.confirmed_email(email, db)
    return {'message': 'Your email confirmed'}


@routs.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    user = await functionuser.get_user_by_email(body.email, db)
    if user.confirmed:
        return {'message': 'Your email already confirmed'}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {'message': 'Check email '}

# @routs.post('/reset_password')
# async def resset_password(body:RequestEmail,bt:BackgroundTasks,db:AsyncSession=Depends(get_db)):
#     user=await functionuser.get_user_by_email(body.email,db)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='user not found')

