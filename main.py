from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from twilio.rest import Client
from dotenv import load_dotenv
from datetime import datetime,timedelta
from db import dbConnect
import random
import os
import jwt

load_dotenv() 

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    name:str
    mobile:str

class Login(BaseModel):
    mobile:str  
    otp:int  
    
twilio_client = Client(
    os.getenv("TWILIO_SID"),os.getenv("TWILIO_AUTH_TOKEN")
)  
@app.post("/createUser")
def CreateUser(Data:User):
   try:
        user = dbConnect()
        otp = random.randint(100000,900000)
        
        otpExpiresAt = datetime.now() + timedelta(minutes = 2)
        isUserExist = user.find_one({"mobile":Data.mobile})
        if isUserExist:
            isUserExist["_id"] = str(isUserExist["_id"])
            if isUserExist["otpExpiresAt"] < datetime.now():
                user.update_one({"mobile":isUserExist["mobile"]},{
                    "$set":{
                        "name":Data.name,
                        "mobile":Data.mobile,
                        "otp":otp,
                        "otpExpiresAt":otpExpiresAt
                    }
                })
                twilio_client.messages.create(
                body = f"Your otp is {otp}",
                from_ = os.getenv("TWILIO_PHONE"),
                to = f"+91{Data.mobile}"
                )
                update_user = user.find_one({"mobile":Data.mobile})
                update_user["_id"] = str(update_user["_id"])
                return {"message":"New otp send because old otp expire","userData":update_user}
            return {"message":"User already exist and otp is valid","userData":isUserExist}
        newUser = {
        "name":Data.name,
        "mobile":Data.mobile,
        "otp":otp,
        "otpExpiresAt":otpExpiresAt
        }
        twilio_client.messages.create(
            body = f"Your otp is {otp}",
            from_ = os.getenv("TWILIO_PHONE"),
            to = f"+91{Data.mobile}"
        )
        result = user.insert_one(newUser)
        newUser["_id"] = str(result.inserted_id)
        return {"message":"user created sucessfully","userData":newUser}
   except Exception as error:
       print("error occure",error)
    
    
@app.post("/loginUser")
def home(Data:Login):
   try:
        users = dbConnect()
        userExist = users.find_one({"mobile":Data.mobile})
        if not userExist:
            return {"message":"User Not found"}
        if userExist["otpExpiresAt"] < datetime.now():
         return {"message":"Otp expire.Please request new one"}
        if userExist["otp"] != Data.otp:
            return {"message":"Invalid otp"}
        token = jwt.encode({"mobile": Data.mobile, "exp": datetime.utcnow() + timedelta(hours=1)},os.getenv("KEY"), algorithm="HS256")
        return {"message":"User logiin sucessfully","token":token}
   except Exception as error:
       print("error occure",error)
       
@app.post("/logout")
def logout():
    try:
        return{"message":"User logout sucessfully?"}
    except Exception as error:
       print("error occure",error)
             