# UserMoney

A FastAPI-based backend service for managing user accounts and financial transactions.

## Features

- User Authentication
- Account Management
- CORS Support
- Request Logging
- Secure API Endpoints

## Tech Stack

- FastAPI (Python web framework)
- MongoDB (Database)
- Pydantic (Data validation)
- JWT Authentication
- Email Validation

## Project Structure

```
.
├── app/
│   ├── api/         # API routes and endpoints
│   ├── core/        # Core application settings
│   ├── models/      # Database models
│   ├── schemas/     # Pydantic schemas
│   ├── services/    # Business logic
│   ├── database.py  # Database configuration
│   └── main.py      # Application entry point
├── requirements.txt # Project dependencies
└── .gitignore      # Git ignore file
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To run the application in development mode:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation at: `http://localhost:8000/docs`
- ReDoc documentation at: `http://localhost:8000/redoc`

## Environment Variables

The application requires certain environment variables to be set. Create a `.env` file in the root directory with the following variables:

- `MONGODB_URL`: MongoDB connection string
- `SECRET_KEY`: Secret key for JWT token generation
- `EMAIL_USERNAME`: Your email account username 
- `EMAIL_PASSWORD`: Your app-specific password
- `EMAIL_HOST`: SMTP server host
- `EMAIL_PORT`: SMTP server port
