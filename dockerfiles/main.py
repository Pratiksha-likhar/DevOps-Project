from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
import os
import time


app = FastAPI(title="Employee Management API")


class Employee(BaseModel):
    name: str
    department: str
    salary: float


def get_connection():

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


def initialize_database():

    for attempt in range(10):

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    salary DECIMAL(10,2) NOT NULL
                )
            """)

            connection.commit()

            cursor.close()
            connection.close()

            print("MySQL database initialized")
            return

        except Exception as e:

            print(f"MySQL not ready. Attempt {attempt + 1}/10")

            if attempt == 9:
                raise e

            time.sleep(5)


@app.on_event("startup")
def startup_event():

    initialize_database()


@app.get("/health")
def health():

    return {
        "status": "UP"
    }


@app.get("/employees")
def get_employees():

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM employees")

    employees = cursor.fetchall()

    cursor.close()
    connection.close()

    return employees


@app.post("/employees")
def create_employee(employee: Employee):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO employees
        (name, department, salary)
        VALUES (%s, %s, %s)
        """,
        (
            employee.name,
            employee.department,
            employee.salary
        )
    )

    connection.commit()

    employee_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return {
        "message": "Employee created successfully",
        "id": employee_id
    }