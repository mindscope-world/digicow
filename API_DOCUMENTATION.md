r
# DigiCow Farmer Intelligence System - API Documentation

This document provides an overview of the available API endpoints and how to test them using the FastAPI interactive documentation.

## Interactive Documentation

The FastAPI application automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to explore and test all available endpoints without needing to write any code.

## Base URL

All API endpoints are under the `/api/v1` prefix.

Example: `http://localhost:8000/api/v1/farmers/`

## Endpoints Overview

### Farmers

- `GET /farmers/` - List farmers with filtering and pagination
- `GET /farmers/{farmer_id}` - Get detailed farmer profile with relationships
- `POST /farmers/` - Register a new farmer
- `PUT /farmers/{farmer_id}` - Update farmer information
- `DELETE /farmers/{farmer_id}` - Deactivate farmer record (soft delete)
- `GET /farmers/{farmer_id}/adoption-history` - Get adoption timeline for a specific farmer

### Trainings

- `GET /trainings/` - List training sessions with filtering and pagination
- `GET /trainings/{session_id}` - Get a specific training session
- `POST /trainings/` - Create a new training session

### Adoptions

- `POST /adoptions/` - Record a new input adoption

### Recommendations

- `GET /recommendations/{farmer_id}` - Get advisory recommendations for a specific farmer
- `GET /recommendations/ward/{ward_id}` - Get advisory recommendations for a specific ward

### Input Products

- `GET /inputs/` - List input products with pagination
- `GET /inputs/{product_id}` - Get input product details by ID

### Input Requests

- `GET /input-requests/` - List input requests with filtering and pagination
- `GET /input-requests/{request_id}` - Get input request details by ID
- `POST /input-requests/` - Create a new input request

### Analytics

- `GET /analytics/adoption-rates` - Get adoption rates by product
- `GET /analytics/trainer-effectiveness` - Get trainer performance metrics
- `GET /analytics/ward-performance` - Get performance metrics by ward
- `GET /analytics/trends` - Get temporal trends in adoption and training

### Agents

- `GET /agents/{agent_id}/dashboard` - Get dashboard data for a specific agent
- `GET /agents/{agent_id}/farmers-needing-attention` - Get prioritized list of farmers needing attention for a specific agent

### Visit Logs

- `GET /visit-logs/` - List visit logs with filtering and pagination
- `GET /visit-logs/farmer/{farmer_id}` - Get visit logs for a specific farmer
- `POST /visit-logs/` - Create a new visit log entry

### Visit History

- `GET /visit-history/{farmer_id}` - Get visit history timeline for a specific farmer

### Demand Forecast

- `GET /demand-forecast/{ward}` - Get input demand forecast for a specific ward

## Testing Examples

### 1. List Farmers

**Endpoint**: `GET /api/v1/farmers/`

**Parameters** (optional):
- `skip`: number of records to skip (default: 0)
- `limit`: maximum number of records to return (default: 100, max: 1000)
- `gender`: filter by gender (Male, Female, Other)
- `age_bracket`: filter by age bracket (18-25, 26-35, 36-45, 46-55, 56-65, 65+)
- `registration_method`: filter by registration method
- `belongs_to_cooperative`: filter by cooperative membership (true/false)
- `status`: filter by status (Active, At risk, Dormant)

**Example Request**:
```
GET http://localhost:8000/api/v1/farmers/?skip=0&limit=10&gender=Male&age_bracket=26-35
```

### 2. Get Farmer Profile

**Endpoint**: `GET /api/v1/farmers/{farmer_id}`

**Example Request**:
```
GET http://localhost:8000/api/v1/farmers/DC00001
```

**Response Includes**:
- Farmer basic information
- Relationships: member_of, located_in, trained_by, participated_in, has_adopted, receives

### 3. Create Farmer

**Endpoint**: `POST /api/v1/farmers/`

**Request Body**:
```json
{
  "farmer_id": "DC00101",
  "gender": "Male",
  "age_bracket": "26-35",
  "registration_method": "mobile_app",
  "belongs_to_cooperative": true,
  "phone": "+254700000000",
  "herd_size": 5,
  "acres_under_cultivation": 2.5,
  "primary_enterprise": "Dairy"
}
```

### 4. Update Farmer

**Endpoint**: `PUT /api/v1/farmers/{farmer_id}`

**Request Body** (only fields to update):
```json
{
  "registration_method": "field_agent",
  "phone": "+254700000001"
}
```

### 5. Get Adoption History

**Endpoint**: `GET /api/v1/farmers/{farmer_id}/adoption-history`

**Example Request**:
```
GET http://localhost:8000/api/v1/farmers/DC00003/adoption-history
```

### 6. Get Analytics - Adoption Rates

**Endpoint**: `GET /api/v1/analytics/adoption-rates`

**Example Request**:
```
GET http://localhost:8000/api/v1/analytics/adoption-rates
```

### 7. Get Analytics - Trainer Effectiveness

**Endpoint**: `GET /api/v1/analytics/trainer-effectiveness`

**Example Request**:
```
GET http://localhost:8000/api/v1/analytics/trainer-effectiveness
```

### 8. Get Analytics - Ward Performance

**Endpoint**: `GET /api/v1/analytics/ward-performance`

**Example Request**:
```
GET http://localhost:8000/api/v1/analytics/ward-performance
```

### 9. Get Analytics - Trends

**Endpoint**: `GET /api/v1/analytics/trends`

**Example Request**:
```
GET http://localhost:8000/api/v1/analytics/trends
```

## Health Check

The application provides a health check endpoint:

- `GET /` - Returns welcome message
- `GET /health` - Returns health status

**Example**:
```
GET http://localhost:8000/health
```
Response: `{"status": "healthy"}`

## Notes

1. All date-time values are in ISO 8601 format (UTC).
2. IDs for farmers, trainers, etc., are strings as defined in the CSV data.
3. When testing POST/PUT endpoints, ensure the Content-Type header is set to `application/json`.
4. The interactive documentation (Swagger UI) provides detailed schemas for request and response bodies.

## Troubleshooting

If you encounter issues:
- Ensure the server is running: `venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- Check the server logs for any error messages.
- Verify that the Neo4j database is running and accessible (configured in `.env`).
- For CSV data loading, run `venv/bin/python scripts/load_csv_data.py` after clearing the database with `venv/bin/python clear_db.py`.