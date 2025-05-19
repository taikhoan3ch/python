# User Info API

A production-ready FastAPI application with clean architecture and proper separation of concerns.

## Project Structure

```
app/
├── api/
│   └── v1/
│       ├── endpoints/
│       │   └── users.py
│       └── api.py
├── core/
│   └── config.py
├── models/
│   └── user.py
├── schemas/
├── services/
├── utils/
└── main.py
```

## Features

- Clean Architecture
- API Versioning
- CORS Middleware
- Environment Configuration
- Type Hints and Validation
- OpenAPI Documentation
- Mock Database (Ready for real database integration)

## Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## API Endpoints

### Users
- GET `/api/v1/users/`: Get all users
- GET `/api/v1/users/{user_id}`: Get user by ID
- POST `/api/v1/users/`: Create new user
- PUT `/api/v1/users/{user_id}`: Update user
- DELETE `/api/v1/users/{user_id}`: Delete user

## Deployment to Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Railway will automatically detect the Python application and deploy it
4. The application will be available at the URL provided by Railway

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
SECRET_KEY=your-secret-key-here
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
``` 