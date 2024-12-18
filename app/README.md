# FastAPI Clinic Management System

## Overview
This project is a web-based clinic management system built with FastAPI and PostgreSQL. It includes user authentication, role-based access control, and CRUD operations for managing services, doctors, and appointments.

## Requirements
- Docker
- Docker Compose

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Build and run the application:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   Open your browser and navigate to `http://localhost:8000`.

4. **Initialize the database:**
   You can run the SQL script located in `app/init_db.sql` to set up the database schema.

## API Endpoints
- **User Registration:** `POST /register`
- **User Login:** `POST /login`
- **Services CRUD:** 
  - Create: `POST /services`
  - Read: `GET /services`
  - Update: `PUT /services/{service_id}`
  - Delete: `DELETE /services/{service_id}`
- **Doctors CRUD:** 
  - Create: `POST /doctors`
  - Read: `GET /doctors`
  - Update: `PUT /doctors/{doctor_id}`
  - Delete: `DELETE /doctors/{doctor_id}`
- **Appointments CRUD:** 
  - Create: `POST /appointments`
  - Read: `GET /appointments`
  - Update: `PUT /appointments/{appointment_id}`
  - Delete: `DELETE /appointments/{appointment_id}`

## Testing the Application

1. **Build and Run the Application:**
   - Open your terminal and navigate to the project directory.
   - Run the following command to build and start the application using Docker:
     ```bash
     docker-compose up --build
     ```

2. **Access the Application:**
   - Open your web browser and navigate to `http://localhost:8000`.
   - You should see a welcome message indicating that the FastAPI application is running.

3. **Interact with the API:**
   - You can use tools like **Postman** or **cURL** to test the API endpoints.
   - Alternatively, you can access the interactive API documentation provided by FastAPI at `http://localhost:8000/docs`. This will allow you to test the endpoints directly from your browser.

4. **Testing User Registration:**
   - Use the `POST /register` endpoint to create a new user. Provide a JSON body with the username, password, and role ID.
   - Example request body:
     ```json
     {
       "username": "testuser",
       "password": "securepassword",
       "role_id": 1
     }
     ```

5. **Testing User Login:**
   - Use the `POST /login` endpoint to log in with the created user credentials.
   - Example request body:
     ```json
     {
       "username": "testuser",
       "password": "securepassword"
     }
     ```

6. **Testing CRUD Operations:**
   - Use the respective endpoints for services, doctors, and appointments to create, read, update, and delete records.
   - Refer to the API documentation for the exact request formats and required parameters.

7. **Check Database:**
   - You can connect to the PostgreSQL database using a database client (like pgAdmin or DBeaver) to verify that the data is being stored correctly.
   - Use the credentials specified in the `docker-compose.yml` file to connect to the database.

## Notes
- Ensure that the PostgreSQL service is running and accessible.
- Modify the environment variables in `docker-compose.yml` as needed for your setup.
