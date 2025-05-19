# User Info API

A simple FastAPI application that returns mock user information.

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
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## Deployment to Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Railway will automatically detect the Python application and deploy it
4. The application will be available at the URL provided by Railway

## API Endpoints

- GET `/`: Returns mock user information 