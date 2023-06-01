import pandas as pd
import re

from typing import List
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import engine,SessionLocal

from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app=FastAPI()

########データベース設定###
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

########オリジン間リソース共有###
origins = [
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://192.168.56.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
########オリジン間リソース共有###

@app.post("/students/",response_model=schemas.Student)
def create_student(student: schemas.StudentCreate,db: Session = Depends(get_db)):
    db_student = crud.get_student_by_id(db=db,id=student.id)
    if db_student:
        raise HTTPException(status_code=400,detail="id already registered")
    return crud.create_student(db=db, student=student)

@app.post("/upload_csv/")
def create_grades(file: UploadFile = File(...)):
    with open("temp.xlsx", "wb") as f:
        f.write(file.file.read())
    
    data = pd.read_excel("temp.xlsx")
    pattern = r'[\s_-]+'
    Sr_name_id_cleaned = data["受験者"].apply(lambda x: re.sub(pattern, '', str(x)))
    extracted_id = Sr_name_id_cleaned.str[:6]
    extracted_name = Sr_name_id_cleaned.str[6:]
    df_name_id_score = pd.DataFrame({'id': extracted_id, 'name': extracted_name, "score":data["得点"]})
    df_grade = df_name_id_score.assign(test_id=1)
    print(df_grade)
    df_grade.to_sql('grade', con=engine, if_exists='replace')

@app.get("/student/{id}")
async def read_item(id:str):
    return {"id": f"{id}","score":[10,20,30,40,50]}

@app.get("/average/")
async def read_average():
    return {"average":[15,23,33,45,60]}