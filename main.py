import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.routes import myrouts, users
from src.db.connectdb import get_db
from src.routes import auth
from src.conf.dburl import config
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]

app = FastAPI()
app.include_router(auth.routs)
app.include_router(users.router, prefix='/api')
app.include_router(myrouts.routs)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])


@app.on_event('startup')
async def startup():
    r = await redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0, password=config.REDIS_PASSWORD)
    await FastAPILimiter.init(r)


@app.get('/')
def index():
    return {'message': 'Todo Application'}


@app.get('/api/healthchecker')
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text('SELECT 1'))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail='Error connecting to DB')
        return {'message': 'Welcome to fastAPI'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='Error connecting to DB')
