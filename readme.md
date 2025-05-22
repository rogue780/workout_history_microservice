## Requirements
- Python 3.8+
---
## Install Dependencies
1. **Clone the repository:**  
```bash
git clone git@github.com:rogue780/workout_history_microservice.git
cd workout_history_microservice
```
2. **Set up a Python virtual environment:**
```bash
python -m venv venv
source venv/bin/activate
```
3. **Install Dependencies:**
```bash
pip install -r requirements.txt
```
## Configuration
1. **Authentication:**

```bash
cp .env.example .env
```

Modify .env

```dotenv
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=secret
```
To disable authentication, leave the values blank:
```dotenv
BASIC_AUTH_USERNAME=
BASIC_AUTH_PASSWORD=
```
## Running
```bash
uvicorn main:app --reload
```
The service runs at http://127.0.0.1:8000
## Documentation
Swagger: http://127.0.0.1:8000/docs  
Redoc: http://127.0.0.1:8000/redoc  

## Examples
### Curl
**Create New Workout Entry:**
```bash
curl -X POST "http://localhost:8000/exercise_history" \
-u admin:secret \
-d "exercise=Bench Press" \
-d "muscle_group=Chest" \
-d "sets=3" \
-d "repetitions_per_set=10,8,6" \
-d "weight_per_set=135,155,175" \
-d "notes=Focused on form" \
-d "date_entered=2025-05-01T09:30:00Z"
```
**Get All Workouts:**
```bash
curl "http://localhost:8000/exercise_history"
```
**Get Workouts with Date Filtering:**
```bash
curl "http://localhost:8000/exercise_history?start_date=2025-05-01&end_date=2025-05-08"
```
**Delete a Workout Entry:**
```bash
curl -X DELETE "http://localhost:8000/exercise_history/1" \
-u admin:secret
```

### Programmatically Requesting and Receiving Data (Python Examples)
**Retrieve Exercise History (Filtered by Date):**
```python
import requests

url = "http://127.0.0.1:8000/exercise_history"
auth = ('admin', 'secret')  # omit if authentication is disabled
params = {
    'start_date': '2025-05-01',
    'end_date': '2025-05-08'
}

response = requests.get(url, params=params, auth=auth)

if response.status_code == 200:
    workouts = response.json()
    for workout in workouts:
        print(workout)
else:
    print(f"Request failed with status code {response.status_code}")
```

**Example JSON Response:**
```json
[
  {
    "id": 1,
    "date_entered": "2025-05-01T09:30:00Z",
    "exercise": "Bench Press",
    "muscle_group": "Chest",
    "sets": 3,
    "repetitions_per_set": [10, 8, 6],
    "weight_per_set": [135, 155, 175],
    "notes": "Focused on form"
  },
  {
    "id": 2,
    "date_entered": "2025-05-03T14:45:00Z",
    "exercise": "Squats",
    "muscle_group": "Legs",
    "sets": 4,
    "repetitions_per_set": [12, 10, 8, 6],
    "weight_per_set": [185, 205, 225, 245],
    "notes": "Legs felt strong today"
  }
]
```

## Sequence Diagram

![image](https://raw.githubusercontent.com/rogue780/workout_history_microservice/refs/heads/main/sequence_diagram.png)

