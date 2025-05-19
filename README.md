# Business Info API

A modern Python-based API for managing business information, built with FastAPI and PostgreSQL.

## Features

- RESTful API endpoints for business information
- Modern, responsive frontend with Tailwind CSS
- PostgreSQL database with SQLAlchemy ORM
- View count tracking for businesses
- Most viewed and recently added business listings

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following content:
```
POSTGRES_SERVER=localhost
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=business_info
```

5. Initialize the database:
```bash
alembic upgrade head
```

## Running the Application

1. Start the development server:
```bash
uvicorn app.main:app --reload
```

2. Access the application:
- Frontend: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## API Endpoints

- `GET /api/v1/businesses/most-requested`: Get the most viewed businesses
- `GET /api/v1/businesses/last-added`: Get recently added businesses
- `POST /api/v1/businesses/`: Create a new business
- `GET /api/v1/businesses/{business_id}`: Get business details

## Production Deployment

1. Set up a production PostgreSQL database
2. Update the `.env` file with production credentials
3. Use a production-grade ASGI server like Gunicorn:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

4. Set up a reverse proxy (e.g., Nginx) to handle SSL and static files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 