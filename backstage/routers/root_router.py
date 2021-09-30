# -*- coding: utf-8 -*-
import time

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World!"}


@router.post("/demo")
async def demo():
    time.sleep(1)
    return {"code": 2000, "msg": "success", "data": {"confidence": time.time(), "class_index": 1}}


@router.get("/demo")
async def demo():
    time.sleep(1)
    return {"code": 2000, "msg": "success", "data": {"confidence": time.time(), "class_index": 1}}
