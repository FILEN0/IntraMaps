# IntraMaps

> The Google Maps for the inside of buildings at UFMG.

IntraMaps is an indoor navigation system that calculates the fastest path between two points inside a building, taking into account the user's profile — gender, accessibility needs and institutional role.

---

## The Problem

Large buildings like ICEx have dozens of rooms, bathrooms, water fountains and exits spread across multiple floors. Paper maps don't tell you which bathroom is closest, or how to get there without using stairs. IntraMaps solves this: given a starting point, it finds the right destination for that person and traces the fastest path to it.

---

## Features

- Search for places by name, type or floor (room, bathroom, water fountain, cafeteria...)
- Route between two points with estimated time and step-by-step instructions in Portuguese
- Route to the nearest place of a given type
- Accessibility profile: avoids stairs for wheelchair users and people on crutches
- Role restriction: students, faculty and staff have access to different areas
- Opening hours: cafeteria and building exits have operating hours
- Account registration, login with session token, search history and favorites
- Anonymous visitors can use the system without an account by providing a profile in the query
- Path drawn over the floor plan, floor by floor

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.12 | Main language |
| FastAPI | REST API with automatic validation (Pydantic) and interactive docs (Swagger) |
| Uvicorn | ASGI server that runs the API |
| SQLite | Local, serverless relational database |
| NetworkX | Fastest path search (A* and multi-source Dijkstra) |
| secrets + hashlib | Session token generation and password hashing |
| Pylint | Static analysis to enforce code standards |
| pytest | Automated tests |
| pdoc | Documentation generated from docstrings |
| HTML + CSS + JS | Web client that draws the floor plan and route in SVG |

---

## Installation

```bash
# Clone the repository
git clone https://github.com/FILEN0/IntraMaps.git
cd IntraMaps

# Create the virtual environment
python -m venv .venv

# Activate it (Linux/Mac)
source .venv/bin/activate

# Activate it (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -e .[dev]
```

---

## Running

```bash
cd src
uvicorn intramaps.main:app --reload
```

Open the interactive API documentation at:
```
http://127.0.0.1:8000/docs
```

To use the web interface, open the `index.html` file from the `frontend/` folder directly in your browser.

---

## Architecture

The system is organized in layers: the API calls the services, the services use the repositories and the domain, and the domain has no knowledge of the outer layers.

**Domain (`building/`, `routing/`, `users/`, `enums/`):** the core entities. `Node` is the abstract base class for any point in the building; `Room`, `Washroom`, `Cafeteria` and other places are subclasses with their own destination rules. `Connection` is the abstract base for edges, specialized into `Corridor`, `Stairs` and `Elevator`. `User` represents the person requesting a route; `Anonymous` inherits from `User` and keeps the same interface for visitors without an account.

**Services (`services/`):** coordinate the use cases. `AuthService` handles registration, login, sessions, favorites and history. `RouteService` validates requests and calculates routes. `GraphService` builds the graph filtered by profile and runs A* or Dijkstra.

**API (`api/`):** four route groups under `/api/v1` — users, floors, places and routes, with 23 operations in total.

**Database (`database/`):** SQLite with nine tables, repositories and a schema with foreign keys and constraints that prevent invalid states.

---

## Project Structure

```
IntraMaps/
├── src/intramaps/
│   ├── api/            # HTTP controllers (users, floors, places, routes)
│   ├── building/       # Building models: nodes, connections and geometry
│   ├── database/       # SQLite database and repositories
│   ├── enums/          # Enumerations (node type, connection type, user attributes)
│   ├── routing/        # Route and step models
│   ├── services/       # Business logic
│   ├── users/          # User model and profile
│   ├── main.py         # API entry point
│   └── settings.py     # Configuration
├── data/               # Test data and floor plan images
├── docs/               # Diagrams and additional documentation
├── tests/              # Automated tests
└── helpers/            # Demo scripts
```

---

## API Overview

All routes use the `/api/v1` prefix. The main ones:

| Method | Route | Description |
|---|---|---|
| GET | `/places?text=&type=&floor=` | List places by name, type or floor |
| GET | `/places/{id}` | Place details |
| GET | `/routes/{a}/to/{b}` | Route between two places |
| GET | `/routes/{a}/to/{b}/instructions` | Step-by-step instructions |
| GET | `/routes/{from}/nearest/{type}` | Route to the nearest place of a type |
| POST | `/users` | Register |
| POST | `/users/login` | Login (returns session token) |
| GET | `/users/me` | Logged-in user profile |
| GET | `/users/me/history` | Search history |
| GET | `/users/me/favorites` | Favorites |

Authenticated routes require the header:
```
Authorization: Bearer <token>
```

See `/docs` for the full specification with all parameters and responses.

---

## Tests

```bash
pytest
```

---

## Authors

- **Gabriel Fileno** — architecture, routing algorithm, hierarchical graph, database and web client
- **Viviane Figueira** — authentication, user sessions, API routes and anonymous profile

Project developed for the Object-Oriented Programming course — UFMG, 2026/2.
