# -*- coding: utf-8 -*-

from fastapi import Depends, FastAPI

from backstage.routers import testfunc_router, celery_router

app = FastAPI()
app.include_router(testfunc_router.router)
app.include_router(celery_router.router)


@app.get("/")
async def root():
    return {"message": "Hello World!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run('backstage_main:app', host="0.0.0.0", port=8000, reload=False)
