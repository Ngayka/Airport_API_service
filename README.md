# ✈️ Airport API Service

A RESTful API for booking flight tickets. 
Built with Django, Django REST Framework, PostgreSQL, and JWT authentication. Users can register, authenticate, view flights, book tickets, and track their orders. 
Admins can manage data through the admin panel.

---

## 🚀 Technologies Used

- Python 3.12
- Django 5.2
- Django REST Framework
- PostgreSQL
- Docker & Docker Compose
- Simple JWT (for authentication)
- drf-spectacular (for OpenAPI/Swagger docs)
- Custom user model
- Django admin interface

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/airport-api-service.git
cd airport-api-service
```
### 2️⃣ Create a `.env` file

Create a `.env` file in the project root with your environment variables

3️⃣ Run the project with Docker
```
docker-compose up --build
```
4️⃣ Getting Access
```
POST /api/user/register/
Content-Type: application/json

{
  "email": "your_email@example.com",
  "password": "your_password"
}
```
Get access and refresh tokens
```
POST /api/user/token/
Content-Type: application/json

{
  "email": "your_email@example.com",
  "password": "your_password"
}
```
## API Features

### User Management
- User registration and profile management
- JWT-based authentication (access & refresh tokens)

### Flights & Airplanes
- List, create, update, and delete flights
- Manage airplanes and airplane types

### Ticket Booking
- Create, update, view, and delete tickets
- Validation to ensure seat availability and no double booking

### Orders
- Create orders containing multiple tickets
- View order details with related tickets and flight info

### Admin Interface
- Django admin panel for managing flights, tickets, orders, airplanes, airplane types, airports, routes, and users

### Filtering & Validation
- Filter flights by route and departure time
- Backend validation for ticket seat and row limits

### Docker Support
- Dockerized setup with PostgreSQL database for easy deployment
