# Architecture Diagrams

PNG diagrams for the SANOVIO Procurement System.

## System & Stack

| Diagram | Description |
|---------|-------------|
| [1-system-overview.png](./1-system-overview.png) | High-level architecture: Frontend, Backend, MongoDB, OpenAI |
| [2-tech-stack.png](./2-tech-stack.png) | Technology stack breakdown |

## Backend

| Diagram | Description |
|---------|-------------|
| [3-backend-architecture.png](./3-backend-architecture.png) | Layered architecture: Routes → Services → Models → Database |
| [5-database-schema.png](./5-database-schema.png) | MongoDB ER diagram (3 collections + embedded documents) |
| [6-api-endpoints.png](./6-api-endpoints.png) | All 24 REST API endpoints |

## Frontend

| Diagram | Description |
|---------|-------------|
| [4-frontend-components.png](./4-frontend-components.png) | React component tree (tabs, forms, modals, hooks) |
| [10-state-management.png](./10-state-management.png) | State flow: central state, props, hooks, refresh triggers |

## User Flow Sequences

| Diagram | Description |
|---------|-------------|
| [7-request-creation-flow.png](./7-request-creation-flow.png) | Form → validate → submit → MongoDB |
| [8-document-extraction-flow.png](./8-document-extraction-flow.png) | Upload → PDF extract → GPT-4o → auto-fill form |
| [9-chat-flow.png](./9-chat-flow.png) | Message → load context → GPT-4o stream → render markdown |
| [11-status-update-flow.png](./11-status-update-flow.png) | Status change → history entry → UI refresh |
