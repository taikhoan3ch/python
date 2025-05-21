# FastAPI Backend with Modular Monolith Architecture

A robust FastAPI backend application with JWT authentication, role-based authorization, and dynamic table creation capabilities.

## Features

- JWT Authentication with role-based authorization
- PostgreSQL database with dynamic table creation
- RESTful API with OpenAPI documentation
- Modular monolith architecture
- Alembic database migrations
- Temporary HTML UI for API testing
- Railway deployment ready

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- JWT (PyJWT)
- bcrypt
- HTML + Fetch API
- Bootstrap

## Project Structure

```
project/
├── app/
│   ├── core/               # Configs, JWT auth, DB connection
│   ├── modules/            # Modular components
│   ├── api/                # OpenAPI route groups
│   ├── services/           # Shared business logic
│   ├── static/             # HTML UI
│   ├── main.py             # App entrypoint
├── alembic/                # Database migrations
├── tests/                  # Unit tests
├── requirements.txt
├── .env
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the development server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Temporary UI

Access the temporary HTML UI at:
- Login: http://localhost:8000/static/index.html
- Setup: http://localhost:8000/static/setup.html
- Users: http://localhost:8000/static/users.html
- Companies: http://localhost:8000/static/companies.html
- Products: http://localhost:8000/static/products.html
- Items: http://localhost:8000/static/items.html

## Deployment

The application is configured for deployment on Railway:

1. Connect your GitHub repository to Railway
2. Add the following environment variables:
   - DATABASE_URL
   - SECRET_KEY
   - ALGORITHM
3. Deploy the application

## License

MIT 