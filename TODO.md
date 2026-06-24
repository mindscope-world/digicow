# To-Do List for DigiCow Farmer Intelligence Backend

## ✅ Completed Features

### Training Management
- **POST /trainings/** – Record a new training session
- **GET /trainings/{session_id}** – Get training session details by ID
- **GET /trainings/** – List training sessions with filtering (title, location, date range) and pagination

### Adoption Management
- **POST /adoptions/** – Record a new input adoption
- **GET /farmers/{farmer_id}/adoption-history** – Get adoption timeline for a specific farmer

### Farmer Management (existing)
- **GET /farmers/** – List farmers with filtering, pagination, and scoring
- **GET /farmers/{farmer_id}** – Get detailed farmer profile with relationships
- **POST /farmers/** – Register new farmer
- **PUT /farmers/{farmer_id}** – Update farmer information
- **DELETE /farmers/{farmer_id}** – Deactivate farmer record (soft delete)

### Core Infrastructure
- FastAPI application with CORS configuration
- Neo4j/database connection setup
- Pydantic schemas for requests/responses
- Service layer separating business logic from API routers
- Unit/test stubs (`test_*.py` files)

## 🚧 In Progress
_(None yet – will be updated as we work on new features)_

## 📋 Next Steps / Backlog
- Implement additional advisory/recommendation endpoints
- Add authentication & authorization (JWT/OAuth2)
- Implement cooperative management endpoints
- Add input product management endpoints
- Write comprehensive integration tests
- Set up Docker Compose for local development
- Add API documentation enhancements (examples, response models)
- Implement background jobs / scheduled tasks (e.g., engagement score updates)
- Add data validation & error handling improvements
- Performance optimization & indexing for Neo4j queries

---
*Last updated: 2026-06-24*