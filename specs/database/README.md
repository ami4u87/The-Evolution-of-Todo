# Database Specifications

This directory contains database-related specifications for the Evolution of Todo application.

## Files

### `schema.md`
Complete database schema specification including:
- Table definitions (users, tasks)
- Columns, types, and constraints
- Indexes for performance
- Foreign key relationships
- Migration strategy from Phase I
- Query patterns with user isolation
- Security and performance considerations

## Using This Specification

### For Implementation
1. Read `schema.md` to understand the complete data model
2. Implement SQLModel models in `/backend/app/models/`
3. Ensure all queries filter by `user_id` for data isolation
4. Create database migration scripts (Alembic)

### For Database Setup
The schema will be created automatically by SQLModel when the backend starts:
```python
# app/database.py
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

### Manual Database Creation (Optional)
If you need to create the database manually:
```bash
psql -U postgres -d todo_db -f init.sql
```

## Key Principles

1. **User Isolation**: Every task has a `user_id` foreign key
2. **UUID Primary Keys**: For security and distributed systems
3. **Audit Timestamps**: Track creation and modification
4. **Data Integrity**: Foreign keys and constraints at database level
5. **Performance**: Strategic indexes on foreign keys and query columns

## Database Providers

- **Development**: PostgreSQL in Docker (docker-compose)
- **Production**: Neon Serverless PostgreSQL

## Connection Strings

Development:
```
postgresql://todo_user:todo_password@localhost:5432/todo_db
```

Production (Neon):
```
postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
```

## Future Enhancements
See `schema.md` for planned future enhancements like:
- Task categories
- Due dates and priorities
- Task sharing
- Full-text search
