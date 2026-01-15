# Sentinel Project

Sentinel is a robust, asynchronous notification service built with FastAPI. It handles notification requests (SMS and Email) by queuing them in Redis and processing them through dedicated workers, ensuring high availability and reliability.

##  Features

- **Asynchronous Processing**: Uses Redis Streams for reliable task queuing and processing.
- **Multi-Channel Support**: Supports both SMS (via Twilio) and Email (via SendGrid).
- **Scalable Workers**: Multiple workers (Alice, Bob, Catherine) can process notifications concurrently.
- **Database Persistence**: All notifications are logged in PostgreSQL for tracking and auditing.
- **Retry Logic**: Built-in support for retrying failed notifications.
- **Dockerized**: Easy deployment using Docker and Docker Compose.

##  Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/) with [SQLAlchemy](https://www.sqlalchemy.org/) (Async)
- **Task Queue**: [Redis Streams](https://redis.io/docs/data-types/streams/)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **External APIs**: [Twilio](https://www.twilio.com/) (SMS), [SendGrid](https://sendgrid.com/) (Email)
- **Containerization**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

##  Project Structure

```text
Sentinel Project/
├── alembic/              # Database migrations
├── app/
│   ├── configs/          # Configuration files
│   ├── db/               # Database session and schema definitions
│   ├── models/           # SQLAlchemy models
│   ├── redis/            # Redis logic and notification handlers
│   ├── routes/           # FastAPI API endpoints
│   ├── workers/          # Background worker scripts
│   └── main.py           # Application entry point
├── compose.yaml          # Docker Compose configuration
├── Dockerfile            # Docker image definition
└── requirements.txt      # Python dependencies
```

##  Getting Started

### Prerequisites

- Docker and Docker Compose installed on your machine.
- Python 3.10+ (if running locally without Docker).

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Somsahu20/Sentinel.git
   cd Sentinel
   ```


2. **Environment Variables**:
   Create a `.env` file in the root directory and populate it with your credentials:
   ```env
   DB_USER=your_db_user
   PASSWORD=your_db_password
   DB_NAME=sentinel_db
   DB_PORT=5432
   REDIS_HOST=redis-db
   SID=your_twilio_sid
   AUTHTOKEN=your_twilio_token
   PHONE=your_twilio_phone
   SEND_GRID_API=your_sendgrid_api_key
   EMAIL=your_verified_email
   ```

3. **Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```
   This will start the PostgreSQL database, Redis, the FastAPI application, and the background workers.

### API Documentation

Once the application is running, you can access the interactive API documentation at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🔄 How It Works

1. **API Request**: A client sends a POST request to `/notifications` with the message body, recipient, and channel (SMS/Email).
2. **Persistence**: The notification is saved to the PostgreSQL database with a `PENDING` status.
3. **Queuing**: The notification is pushed to a Redis Stream (`sentinel:notifications`).
4. **Worker Processing**: Background workers (like `worker-alice`) read tasks from the Redis Stream using consumer groups.
5. **Delivery**: The worker calls the appropriate external API (Twilio or SendGrid) to deliver the notification.
6. **Status Update**: Upon success or failure, the worker updates the notification status in the database.


