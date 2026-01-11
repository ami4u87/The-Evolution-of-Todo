# Evolution of Todo - Project Overview

## Project Vision
Build a Todo application that evolves from a simple console app to a full-stack, multi-user, cloud-native AI-powered system using strictly spec-driven development.

## Current Phase: Phase II - Full-Stack Multi-User Web Application

### Completed Phases
- **Phase I**: In-memory Python console application with basic CRUD operations

### Phase II Goals
- Transform console app into full-stack web application
- Multi-user support with proper authentication and data isolation
- Modern tech stack (Next.js 16+, FastAPI, Neon PostgreSQL)
- Better Auth for authentication with JWT tokens
- RESTful API with proper authorization

## Tech Stack

### Frontend
- Next.js 16+ with App Router
- TypeScript
- Better Auth for authentication
- Modern UI components

### Backend
- FastAPI (Python 3.13+)
- SQLModel ORM
- Pydantic for validation
- JWT token verification

### Database
- Neon Serverless PostgreSQL

### Development Tools
- UV for Python dependency management
- Docker Compose for local development
- Claude Code + Spec-Kit Plus for spec-driven development

## Repository Structure
```
/
├── .spec-kit/          # Spec-Kit Plus configuration
├── specs/              # All specifications
│   ├── features/       # Feature specs
│   ├── api/           # API specifications
│   ├── database/      # Database schemas
│   └── ui/            # UI/UX specifications
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── history/           # PHRs and ADRs
└── docker-compose.yml # Local development setup
```

## Development Principles
- Spec-Driven Development only: All changes driven by refined specs
- Clean architecture and type safety
- Progressive evolution: Each phase builds on previous work
- Proper testing and documentation
