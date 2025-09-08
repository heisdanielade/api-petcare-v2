# 🦴 PetCare Tracker API

**PamiętamPsa** or **PamPsa** shortened (Polish for *"I remember the dog"*) is a backend REST API built with **FastAPI** that allows users to manage their pets, receive notifications, and track key pet care activities. Designed with simplicity and real-life usability in mind, this project supports modern authentication and a growing feature set.

---

## Features

- **User Authentication** (JWT-based login & registration)
- **Pet Management** – Add, view, edit, and delete pet profiles
- **Reminder System** *(in progress)* – Schedule and manage care-related reminders
- **Email Notifications** – Triggered on user registration, pet addition, etc.
- **Pet Health Records** *(planned)* – Log health events and medical history
- **Production-ready stack** with PostgreSQL and security best practices

---

## Tech Stack

| Layer           | Technology                             |
|-----------------|----------------------------------------|
| Language        | Python, Bash (startup script)          |
| Backend         | FastAPI (with built-in OpenAPI docs)   |
| Database        | PostgreSQL (with Alembic migrations)   |
| Validation      | Pydantic                               |
| Security        | JWT, slowapi (rate limiting)           |
| Deployment      | Docker, Render                         |

---

## API Overview

The API is versioned and documented with Swagger UI, which provides a visual interface to explore and test endpoints.
> 🔐 Access to Swagger docs is restricted based on user roles.


Frontend URL: [pamietampsa.app](https://pamietampsa.netlify.app/)


### Example Endpoints
| Method | Endpoint           | Description                   |
|--------|--------------------|-------------------------------|
| POST   | `/v1/auth/signup`  | Register a new user           |
| POST   | `/v1/auth/login`   | Authenticate user, get token  |
| POST   | `/v1/user/me`      | Authenticated user details    |
| GET    | `/v1/pets/all`     | Get current user's pets       |
| POST   | `/v1/pets/add`     | Add a new pet                 |
| PUT    | `/v1/pets/{id}`    | Update existing pet           |
| DELETE | `/v1/pets/{id}`    | Delete pet                    |

---

## Additional

- All protected endpoints require a **Bearer JWT token** in the `Authorization` header.

- To protect public endpoints from abuse, this API applies rate limiting. If this limit is exceeded, requests return HTTP **429 Too Many Requests**.

---

## Email Notifications

Email events currently include:
- Successful user registration
- New pet added

Planned:
- Reminders for pet care
- Health record logs and alerts

---

## Work in Progress
This is an actively developed backend. Coming soon:

- Complete Reminders CRUD + Notification Triggers

- OAuth2.0 (Google & Facebook)

- Pet Health Record Management


### Contributing
Kindly contact me for the possibility of collaborating/contributing, I look forward to hearing from you!

---

Developed by **[heisdanielade](https://github.com/heisdanielade)**

---
