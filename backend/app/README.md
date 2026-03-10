# Backend Application Structure

This document describes the organized structure of the procurement request management backend.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application setup
│   ├── config.py                # Configuration and environment variables
│   ├── database.py              # Database connection and utilities
│   ├── constants.py             # Application constants (commodity groups, departments)
│   │
│   ├── models/                  # Pydantic models
│   │   ├── __init__.py          # Model exports
│   │   ├── request.py           # Request-related models
│   │   └── metadata.py          # Metadata and AI response models
│   │
│   ├── routes/                  # API route handlers
│   │   ├── __init__.py          # Route router aggregation
│   │   ├── requests.py          # Procurement request endpoints
│   │   ├── metadata.py          # Metadata endpoints (commodity groups, departments)
│   │   └── ai.py                # AI-powered endpoints
│   │
│   └── services/                 # Business logic layer
│       ├── __init__.py          # Service exports
│       ├── ai_service.py        # AI service (OpenAI integration)
│       └── request_service.py   # Request management service
│
├── main.py                      # Entry point (imports from app.main)
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## Module Descriptions

### `app/main.py`

FastAPI application initialization, middleware setup, and event handlers.

### `app/config.py`

Centralized configuration management:

- MongoDB connection settings
- OpenAI API configuration
- CORS origins
- Environment variable loading

### `app/database.py`

Database connection management:

- MongoDB client initialization
- Database connection utilities
- Database seeding functions

### `app/constants.py`

Application constants:

- Commodity groups (50 groups across 7 categories)
- Department list
- Static data that doesn't change frequently

### `app/models/`

Pydantic models for data validation and serialization:

- **`request.py`**: Request-related models

  - `OrderLine`: Order line item
  - `ProcurementRequest`: Full request model
  - `ProcurementRequestCreate`: Request creation model
  - `ProcurementRequestUpdate`: Request update model
  - `ProcurementRequestResponse`: Request response model
  - `StatusHistoryEntry`: Status change history
  - `StatusUpdate`: Status update model
  - `RequestStatus`: Status enumeration

- **`metadata.py`**: Metadata and AI models
  - `CommodityGroup`: Commodity group model
  - `DocumentExtractionResponse`: AI extraction response
  - `CommodityGroupSuggestion`: AI suggestion response

### `app/routes/`

API route handlers organized by functionality:

- **`requests.py`**: Procurement request CRUD operations

  - `POST /api/requests` - Create request
  - `GET /api/requests` - List requests (with filters)
  - `GET /api/requests/{id}` - Get request
  - `PATCH /api/requests/{id}` - Update request
  - `PATCH /api/requests/{id}/status` - Update status
  - `DELETE /api/requests/{id}` - Delete request
  - `GET /api/requests/{id}/history` - Get status history
  - `GET /api/stats` - Get statistics

- **`metadata.py`**: Metadata endpoints

  - `GET /api/commodity-groups` - List commodity groups
  - `GET /api/departments` - List departments

- **`ai.py`**: AI-powered endpoints
  - `POST /api/extract-document` - Extract from document
  - `POST /api/suggest-commodity-group` - Suggest commodity group

### `app/services/`

Business logic layer (separated from routes):

- **`ai_service.py`**: AI service for OpenAI integration

  - Document extraction using GPT-4o
  - Commodity group suggestion
  - Error handling and response parsing

- **`request_service.py`**: Request management service
  - Request CRUD operations
  - Validation logic
  - Database operations
  - Statistics calculation

## Benefits of This Structure

1. **Separation of Concerns**: Routes handle HTTP, services handle business logic
2. **Maintainability**: Easy to locate and modify specific functionality
3. **Testability**: Services can be tested independently
4. **Scalability**: Easy to add new features without cluttering
5. **Reusability**: Services can be reused across different routes
6. **Organization**: Clear structure following Python best practices

## Running the Application

The entry point remains the same:

```bash
uvicorn main:app --reload
```

The `main.py` file imports the FastAPI app from `app.main`, maintaining backward compatibility.

## Adding New Features

1. **New Model**: Add to `app/models/` and export in `__init__.py`
2. **New Route**: Create file in `app/routes/` and include in `routes/__init__.py`
3. **New Service**: Create file in `app/services/` and export in `__init__.py`
4. **New Constant**: Add to `app/constants.py`

This structure follows FastAPI best practices and makes the codebase production-ready.
