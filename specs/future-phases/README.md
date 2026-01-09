# Future Phases Specifications

This directory contains specifications for features planned for future phases of the Evolution of Todo application.

## Purpose

- Document advanced features before they are implemented
- Maintain a roadmap for project evolution
- Capture design decisions and validation rules for future reference
- Allow early feedback on proposed features

## Status

**All specifications in this directory are NOT implemented in Phase II.**

These are planned features for Phase III, Phase IV, and beyond.

## Current Phase

**Phase II**: Multi-user web application with basic CRUD operations
- Frontend: Next.js 16+
- Backend: FastAPI + SQLModel
- Database: PostgreSQL
- Features: Create, Read, Update, Delete, Mark Complete

## Future Phases

### Phase III (Planned)
**Enhanced Task Management**
- Due dates (ISO 8601)
- Priority levels (high, medium, low)
- Sorting and filtering
- Overdue task detection

**Specifications**:
- `validation-enhanced.md` - Due date and priority validation

### Phase IV (Planned)
**Advanced Features**
- Tags for categorization
- Task sharing between users
- Search and filtering
- Bulk operations

**Specifications**:
- `validation-enhanced.md` - Tag validation
- (More specs to be added)

### Phase V (Ideas)
**AI Integration**
- Smart task suggestions
- Natural language task creation
- Priority recommendations
- Deadline predictions

### Phase VI (Ideas)
**Mobile & Real-time**
- Mobile app (React Native)
- Real-time collaboration (WebSockets)
- Push notifications
- Offline support

## How to Use

1. **Planning**: Review future specs when planning next phase
2. **Design**: Use as starting point for detailed design
3. **Implementation**: Adapt specs to current architecture before implementing
4. **Evolution**: Update specs as requirements change

## Files

### `validation-enhanced.md`
Enhanced input validation for Phase III/IV features:
- Due date validation (must be future, ISO 8601)
- Priority validation (high/medium/low)
- Tags validation (array of strings, alphanumeric)
- Complete Pydantic schemas
- Database schema changes
- Test cases

## Notes

- **Do not implement** features from this directory in Phase II
- Phase II must be complete and stable first
- Future specs may change based on user feedback
- Always maintain backward compatibility
- Update this README when adding new future specs

## Migration Path

When moving a feature from future → current phase:
1. Review and update the specification
2. Move spec from `future-phases/` to appropriate directory (`api/`, `database/`, etc.)
3. Update database schema with migrations
4. Implement backend changes
5. Implement frontend changes
6. Update tests and documentation
7. Update this README

## Contributing

When adding new future phase specifications:
1. Create detailed spec file in this directory
2. Include validation rules and examples
3. Document database changes needed
4. Add test cases
5. Update this README with brief description

---

Last updated: 2025-01-08
Current Phase: Phase II
