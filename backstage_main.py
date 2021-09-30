# -*- coding: utf-8 -*-

from fastapi import Depends, FastAPI

from backstage.routers import testfunc_router, celery_router, root_router

app = FastAPI()
prefix = "/api"
app.include_router(root_router.router, prefix=prefix)
app.include_router(testfunc_router.router, prefix=prefix)
app.include_router(celery_router.router, prefix=prefix)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run('backstage_main:app', host="0.0.0.0", port=8000, reload=False)
