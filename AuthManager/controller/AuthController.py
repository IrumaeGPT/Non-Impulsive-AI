from fastapi import APIRouter,Depends
from AuthManager.service.AuthService import joinProcess,loginProcess
from model.User import User,UserLoginRequest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util.jwtUtil import verify_token

router = APIRouter()

@router.get("/test")
async def testName():
    return "tester user"

@router.post("/join")
async def joinUser(user: User):
    response = joinProcess(user)
    return response

@router.post("/login")
async def login(request: UserLoginRequest):
    response = loginProcess(request.userId,request.password)
    return response

@router.get("/authuser")
async def authTest( a = Depends(verify_token)):
    return "Hello user?"
    


