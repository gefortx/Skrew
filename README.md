# Skrew

Skrew is a lightweight web application for creating and sharing skating sessions with other skaters.

The project uses **HTML, CSS, and JavaScript** for the frontend and **FastAPI + SQLite** for the backend. It also includes user authentication using **JWT tokens** and password hashing.

## 🚀 Features

* User registration and login
* JWT-based authentication
* Password hashing with bcrypt
* Protected session creation
* User-specific session ownership
* Public session feed
* SQLite database
* FastAPI REST API
* Lightweight frontend with HTML, CSS, and JavaScript
* Existing sessions preserved during database migration
* Logout functionality
* Automatic authentication checks on the dashboard

## 🛠️ Tech Stack

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python
* FastAPI
* Uvicorn
* JWT
* bcrypt
* python-dotenv

### Database

* SQLite

## 📁 Project Structure

```text
Skrew/
│
├── Skrew-Backend/
│   ├── main.py
│   ├── auth.py
│   └── requirements.txt
│
├── Skrew-Frontend/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   │
│   └── assets/
│       ├── auth.css
│       ├── auth.js
│       ├── dashboard.css
│       └── dashboard.js
│
├── .env
├── .gitignore
└── README.md
```

## 🔐 Authentication

Skrew uses JWT-based authentication.

The authentication flow is:

```text
Register
   ↓
Username + Password
   ↓
Password hashed with bcrypt
   ↓
User stored in SQLite
```

Login:

```text
Username + Password
   ↓
Backend verifies password
   ↓
JWT generated
   ↓
Token stored in browser
   ↓
User accesses dashboard
```

Protected requests send the token using:

```text
Authorization: Bearer <token>
```

The backend verifies the token before allowing authenticated operations.

## 🗄️ Database

Skrew uses SQLite because the application currently has relatively simple data requirements.

The database contains a `users` table:

```text
users
├── id
├── username
├── password_hash
└── created_at
```

The existing `sessions` table was extended with:

```text
user_id
```

The migration was designed to be additive, so existing session records are preserved.

Older sessions may have a `NULL` `user_id`, while newly created sessions are associated with the currently authenticated user.

## 🔌 API Endpoints

### Authentication

| Method | Endpoint        | Description                | Authentication |
| ------ | --------------- | -------------------------- | -------------- |
| POST   | `/api/register` | Register a new user        | No             |
| POST   | `/register`     | Register a new user        | No             |
| POST   | `/api/login`    | Login and receive JWT      | No             |
| POST   | `/login`        | Login and receive JWT      | No             |
| GET    | `/api/me`       | Get current logged-in user | Yes            |

### Sessions

| Method | Endpoint         | Description          | Authentication |
| ------ | ---------------- | -------------------- | -------------- |
| GET    | `/api/dashboard` | Retrieve sessions    | No             |
| POST   | `/api/sessions`  | Create a new session | Yes            |

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Important

Do not commit `.env` to Git.

Make sure it is included in `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
```

For production, use a strong randomly generated JWT secret.

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Skrew
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

On Linux/macOS:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r Skrew-Backend/requirements.txt
```

If dependencies are not already listed, install:

```bash
pip install fastapi uvicorn python-dotenv bcrypt "python-jose[cryptography]"
```

## ▶️ Running the Application

Navigate to the backend:

```bash
cd Skrew-Backend
```

Start the FastAPI server:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

## 🧪 Testing the Application

### 1. Register

Open:

```text
http://127.0.0.1:8000/register.html
```

Create an account using a username and password.

### 2. Login

Open:

```text
http://127.0.0.1:8000/login.html
```

After successful login, the JWT is stored in the browser and you are redirected to the dashboard.

### 3. Create a Session

From the dashboard, fill out the session form.

The frontend automatically sends the JWT with the request.

The backend:

1. Verifies the JWT.
2. Identifies the logged-in user.
3. Creates the session.
4. Associates the session with the user's `user_id`.
5. Returns the created session.

### 4. Logout

Click **Logout** from the dashboard.

The authentication token is removed from local storage and the user is redirected to the login page.

## 🔒 Protected Routes

Creating a session requires authentication.

For example:

```http
POST /api/sessions
Authorization: Bearer <JWT_TOKEN>
```

An unauthenticated request returns:

```http
401 Unauthorized
```

This prevents users from creating sessions without logging in.

## 📡 Example Authentication Flow

```text
             ┌──────────────┐
             │    Client    │
             └──────┬───────┘
                    │
             Register / Login
                    │
                    ▼
             ┌──────────────┐
             │   FastAPI    │
             └──────┬───────┘
                    │
             Verify / Hash
                    │
                    ▼
             ┌──────────────┐
             │    SQLite    │
             │    Users     │
             └──────────────┘

                    Login
                      │
                      ▼
                JWT Token
                      │
                      ▼
             ┌──────────────┐
             │   Dashboard  │
             └──────┬───────┘
                    │
          POST /api/sessions
          Authorization: Bearer JWT
                    │
                    ▼
             ┌──────────────┐
             │   FastAPI    │
             │ Auth Check   │
             └──────┬───────┘
                    │
                    ▼
             ┌──────────────┐
             │    SQLite    │
             │   Sessions   │
             └──────────────┘
```

## 🧠 Why FastAPI + SQLite?

Skrew currently has relatively simple data requirements, making SQLite a good fit for development and an early-stage application.

### FastAPI

* Lightweight
* Fast
* Easy to build REST APIs
* Automatic API documentation
* Python-based
* Works well with asynchronous applications

### SQLite

* No separate database server required
* Easy to set up
* Lightweight
* Simple to back up
* Suitable for small applications and prototypes

As the application grows, the database can be migrated to PostgreSQL or another production database.

## 🔮 Future Improvements

Possible improvements include:

* User profile pages
* Edit and delete sessions
* Session joining
* Session search and filtering
* Location-based session discovery
* Session date and time
* User avatars
* Password reset
* Refresh tokens
* Email verification
* PostgreSQL support
* Docker deployment
* Production deployment
* Rate limiting
* Better authorization for modifying sessions

## 🧑‍💻 Development

Activate the virtual environment before working on the project:

```bash
source venv/bin/activate
```

Start the development server:

```bash
cd Skrew-Backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

FastAPI's interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## ⚠️ Security Notes

This project is currently intended for development/learning purposes.

Before deploying to production:

* Use a strong JWT secret.
* Never commit `.env`.
* Use HTTPS.
* Configure secure token storage.
* Add rate limiting to authentication endpoints.
* Add appropriate CORS configuration.
* Consider short-lived access tokens with refresh tokens.
* Use a production database such as PostgreSQL.
* Validate and sanitize user input.
* Configure production logging and error handling.

## 📜 License

Add your preferred license here.

For example:

```text
MIT License
```

## 👤 Author

**Ravi**

Built as a full-stack project to learn and demonstrate:

* Backend development with FastAPI
* REST API development
* SQLite database integration
* JWT authentication
* Password hashing
* Frontend/backend communication
* Authentication-protected APIs
