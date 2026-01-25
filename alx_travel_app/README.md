# ALX Travel App – Asynchronous Email Notifications

## Project Overview

This project extends the **ALX Travel App** by introducing **asynchronous background task processing** using **Celery** with **RabbitMQ** as the message broker.  
The main goal is to ensure that **email notifications** (booking and payment confirmations) are sent **without blocking** the main request–response cycle.

This improves application performance, scalability, and user experience.

---

## Key Features

- Asynchronous background task processing using **Celery**
- **RabbitMQ** (running in Docker) as the message broker
- Booking confirmation emails sent asynchronously
- Payment confirmation emails sent asynchronously after successful Chapa payment verification
- Django REST Framework–based API
- Non-blocking request handling

---

## Technology Stack

- **Django** – Backend framework
- **Django REST Framework** – API layer
- **Celery** – Background task queue
- **RabbitMQ** – Message broker (Dockerized)
- **SMTP / Django Email Backend** – Email delivery
- **Docker** – RabbitMQ container

---

## Asynchronous Workflow Explanation

### Booking Creation Flow

1. A booking is created via the **Booking API endpoint**.
2. The booking is saved to the database.
3. A Celery task is triggered using `.delay()`.
4. Celery sends a **booking confirmation email** in the background.
5. The API responds immediately without waiting for the email to send.

### Payment Confirmation Flow

1. A payment is initiated using the Chapa API.
2. Payment verification is performed after completion.
3. On successful verification:
   - Payment status is updated
   - Booking status is confirmed
   - A Celery task sends a **payment confirmation email** asynchronously

---

## Project Structure (Relevant Files)

```text
alx_travel_app/
├── alx_travel_app/
│   ├── celery.py
│   ├── settings.py
│   └── __init__.py
├── listings/
│   ├── tasks.py
│   ├── views.py
│   └── models.py
├── manage.py
└── README.md
Celery Configuration
Celery is configured in alx_travel_app/celery.py and integrated with Django settings.

RabbitMQ is used as the message broker.

python
Copy code
CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672//"
RabbitMQ (Docker Setup)
RabbitMQ runs inside a Docker container with ports exposed to the host.

Example command used:

bash
Copy code
docker run -d \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management
RabbitMQ Management UI:

arduino
Copy code
http://localhost:15672
Login:

makefile
Copy code
username: guest
password: guest
Email Backend
For testing and development, the Django console email backend is used:

python
Copy code
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
Emails are printed to the terminal when tasks execute.

How to Run the Project Locally
1️⃣ Start RabbitMQ (Docker)
bash
Copy code
docker start rabbitmq
2️⃣ Activate Virtual Environment
bash
Copy code
source venv/bin/activate
3️⃣ Start Celery Worker
bash
Copy code
celery -A alx_travel_app worker -l info
Expected output:

nginx
Copy code
Connected to amqp://guest@localhost:5672//
celery@hostname ready.
4️⃣ Start Django Server
bash
Copy code
python manage.py runserver
Testing Asynchronous Emails
Booking Confirmation Email
Create a booking via the API endpoint:

bash
Copy code
POST /api/bookings/
The API responds immediately.

Celery processes the email task in the background.

Email content appears in the Django console.

Note: Creating a booking via Django Admin does not trigger the API view logic.
Booking confirmation emails are triggered when bookings are created through the API.

Payment Confirmation Email
Initiate payment using the payment endpoint.

Verify payment via the verification endpoint.

On successful verification:

Payment status updates

Booking is confirmed

Payment confirmation email is sent asynchronously via Celery

Why Asynchronous Processing Is Used
In real-world booking platforms (e.g., Airbnb, Booking.com):

Sending emails synchronously slows down responses

Background processing ensures faster user feedback

Celery allows the system to scale efficiently

This project demonstrates industry-standard asynchronous task handling.

Status
Celery integrated successfully


Author
Alexander Edim
Backend Engineer | ALX Backend & ProDev Programs

