# main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import pandas as pd
import os
from typing import List
import hashlib
import json 

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_FILE = "data/user/infor.csv"
SEARCH_OUTPUTS_DIR = "search_outputs" 

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TopicCreate(BaseModel):
    email: EmailStr
    topic: str

class TopicDelete(BaseModel):
    email: EmailStr
    topic: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['email', 'password', 'topic'])
        df.to_csv(CSV_FILE, index=False)

def read_csv() -> pd.DataFrame:
    init_csv()
    return pd.read_csv(CSV_FILE)

def write_csv(df: pd.DataFrame):
    df.to_csv(CSV_FILE, index=False)

def user_exists(email: str) -> bool:
    df = read_csv()
    return email in df['email'].values

def verify_password(email: str, password: str) -> bool:
    df = read_csv()
    user_row = df[df['email'] == email]
    if user_row.empty:
        return False
    stored_password = user_row.iloc[0]['password']
    return stored_password == hash_password(password)

@app.get("/")
async def root():
    return {"message": "Topic Manager API"}

@app.post("/register")
async def register(user: UserRegister):
    try:
        if user_exists(user.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        df = read_csv()
        hashed_password = hash_password(user.password)
        new_row = pd.DataFrame({
            'email': [user.email],
            'password': [hashed_password],
            'topic': ['']
        })
        df = pd.concat([df, new_row], ignore_index=True)
        write_csv(df)
        return {"message": "User registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/login")
async def login(user: UserLogin):
    try:
        if not user_exists(user.email) or not verify_password(user.email, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return {"message": "Login successful", "email": user.email}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/topics/{email}")
async def get_topics(email: str) -> List[str]:
    try:
        if not user_exists(email):
            raise HTTPException(status_code=404, detail="User not found")
        df = read_csv()
        user_topics = df[df['email'] == email]['topic'].tolist()
        topics = [topic for topic in user_topics if topic and str(topic).strip() and str(topic) != 'nan']
        return topics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get topics: {str(e)}")

@app.post("/topics")
async def add_topic(topic_data: TopicCreate):
    try:
        if not user_exists(topic_data.email):
            raise HTTPException(status_code=404, detail="User not found")
        if not topic_data.topic.strip():
            raise HTTPException(status_code=400, detail="Topic cannot be empty")
        df = read_csv()
        new_row = pd.DataFrame({
            'email': [topic_data.email],
            'password': [df[df['email'] == topic_data.email].iloc[0]['password']],
            'topic': [topic_data.topic.strip()]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        write_csv(df)
        return {"message": "Topic added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add topic: {str(e)}")

@app.delete("/topics")
async def delete_topic(topic_data: TopicDelete):
    try:
        if not user_exists(topic_data.email):
            raise HTTPException(status_code=404, detail="User not found")
        df = read_csv()
        condition = (df['email'] == topic_data.email) & (df['topic'] == topic_data.topic)
        if not df[condition].empty:
            df = df[~condition]
            write_csv(df)
            return {"message": "Topic deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Topic not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete topic: {str(e)}")


@app.get("/papers/{topic}")
async def get_papers_for_topic(topic: str):
    """
    Lấy thông tin các paper liên quan đến một topic.
    Tên file được chuyển đổi từ tên topic. Vd: '3D Object Detection' -> '3D-Object-Detection.json'
    """
    try:
        filename = topic + ".json"
        
        print(f"Searching for file: {filename}")
        file_path = os.path.join(SEARCH_OUTPUTS_DIR, filename)
        print(f"Looking for file: {file_path}")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Data for topic '{topic}' not found.")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error reading data file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/data")
async def get_all_data():
    try:
        df = read_csv()
        return df.to_dict('records')
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8077) # Thay đổi port nếu cần