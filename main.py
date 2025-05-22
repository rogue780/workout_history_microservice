from fastapi import FastAPI, Depends, Form, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv
import os
import sqlite3
from typing import Optional, List
from datetime import datetime

load_dotenv()

DATABASE = "workouts.db"
app = FastAPI()
security = HTTPBasic()

def basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    username = os.getenv("BASIC_AUTH_USERNAME")
    password = os.getenv("BASIC_AUTH_PASSWORD")

    if not username and not password:
        return

    if credentials.username != username or credentials.password != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workout_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_entered TEXT,
        exercise TEXT,
        muscle_group TEXT,
        sets INTEGER,
        repetitions_per_set TEXT,
        weight_per_set TEXT,
        notes TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def get_conn():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def healthcheck():
    return {"status": "Workout History Microservice running"}

@app.post("/exercise_history", dependencies=[Depends(basic_auth)])
def log_exercise(
    exercise: str = Form(...),
    muscle_group: str = Form(...),
    sets: int = Form(...),
    repetitions_per_set: str = Form(...), # e.g. '10,8,6'
    weight_per_set: str = Form(...), # e.g. '135,155,175'
    notes: Optional[str] = Form(""),
    date_entered: Optional[str] = Form(None)
):
    print(f"Received data: exercise={exercise}, muscle_group={muscle_group}, sets={sets}, repetitions_per_set={repetitions_per_set}, weight_per_set={weight_per_set}, notes={notes}, date_entered={date_entered}")
    date_entered = date_entered or datetime.utcnow().isoformat()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO workout_history
    (date_entered, exercise, muscle_group, sets, repetitions_per_set, weight_per_set, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        date_entered, exercise, muscle_group, sets,
        repetitions_per_set, weight_per_set, notes
    ))
    exercise_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"Logged exercise with ID: {exercise_id}")
    return {"id": exercise_id, "message": "Exercise logged"}

@app.get("/exercise_history")
def get_exercise_history(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    print(f"Received data: start_date={start_date}, end_date={end_date}")

    conn = get_conn()
    cursor = conn.cursor()
    query = "SELECT * FROM workout_history WHERE 1=1"
    params: List[str] = []
    if start_date:
        query += " AND date(date_entered) >= date(?)"
        params.append(start_date)
    if end_date:
        query += " AND date(date_entered) <= date(?)"
        params.append(end_date)
    query += " ORDER BY date_entered ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    exercise_history = []
    for row in rows:
        exercise_history.append({
            "id": row["id"],
            "date_entered": row["date_entered"],
            "exercise": row["exercise"],
            "muscle_group": row["muscle_group"],
            "sets": row["sets"],
            "repetitions_per_set": [int(x) for x in row["repetitions_per_set"].split(",")],
            "weight_per_set": [float(x) for x in row["weight_per_set"].split(",")],
            "notes": row["notes"]
        })
    
    print(f"Returning data: {exercise_history}")

    return exercise_history

@app.delete("/exercise_history/{exercise_id}", dependencies=[Depends(basic_auth)])
def delete_exercise(exercise_id: int):
    print(f"Received request to delete exercise with ID: {exercise_id}")
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM workout_history WHERE id=?", (exercise_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Exercise not found")

    cursor.execute("DELETE FROM workout_history WHERE id=?", (exercise_id,))
    conn.commit()
    conn.close()
    print(f"Deleted exercise with ID: {exercise_id}")
    return {"message": "Exercise deleted", "id": exercise_id}