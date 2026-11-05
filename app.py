
from fastapi import FastAPI, Response
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import joblib
import pandas as pd
import time

app = FastAPI(title="Employee Salary Prediction API")

model = joblib.load("salary_model/model.pkl")
preprocessor = joblib.load("salary_model/preprocessor.pkl")

REQUEST_COUNT = Counter(
    "salary_prediction_requests_total",
    "Total salary prediction requests"
)

SUCCESS_COUNT = Counter(
    "salary_prediction_success_total",
    "Successful salary predictions"
)

ERROR_COUNT = Counter(
    "salary_prediction_errors_total",
    "Failed salary predictions"
)

REQUEST_LATENCY = Histogram(
    "salary_prediction_request_duration_seconds",
    "Time taken for salary predictions"
)

class EmployeeData(BaseModel):
    Age: float
    Gender: str
    Education_Level: str
    Job_Title: str
    Years_of_Experience: float

@app.get("/")
def home():
    return {"message": "Employee Salary Prediction API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict")
def predict_salary(data: EmployeeData):
    REQUEST_COUNT.inc()
    start_time = time.time()

    try:
        input_data = pd.DataFrame([{
            "Age": data.Age,
            "Gender": data.Gender,
            "Education Level": data.Education_Level,
            "Job Title": data.Job_Title,
            "Years of Experience": data.Years_of_Experience
        }])

        processed_data = preprocessor.transform(input_data)
        prediction = model.predict(processed_data)

        SUCCESS_COUNT.inc()

        return {
            "predicted_salary": round(float(prediction[0]), 2)
        }

    except Exception:
        ERROR_COUNT.inc()
        raise

    finally:
        REQUEST_LATENCY.observe(time.time() - start_time)

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
