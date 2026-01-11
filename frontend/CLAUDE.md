# Frontend Development Guidelines - Todo App

## Overview
This is the Next.js 16+ frontend for the Evolution of Todo application. It uses the App Router, TypeScript, and Better Auth for authentication.

## Tech Stack
- **Framework**: Next.js 16+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth
- **HTTP Client**: Native Fetch API
- **State Management**: React hooks and Server Components

## Project Structure
```
frontend/
├── app/                    # App Router pages and layouts
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   ├── login/             # Authentication pages
│   ├── dashboard/         # Protected dashboard
│   └── api/               # API routes (Better Auth)
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   └── features/         # Feature-specific components
├── lib/                  # Utility functions and configs
│   ├── api-client.ts     # API communication with backend
│   ├── auth.ts           # Better Auth configuration
│   └── types.ts          # TypeScript types
├── public/               # Static assets
└── .env.local           # Environment variables
```

## Development Principles

### 1. Spec-Driven Development
- All features must have a spec in `/specs/features/` or `/specs/ui/`
- Follow the spec precisely
- No manual coding without specs

### 2. TypeScript Strict Mode
- Enable strict mode in tsconfig.json
- Define explicit types for all props and state
- Use interfaces for complex types
- Avoid `any` type

### 3. Component Architecture
- Use Server Components by default
- Add 'use client' only when necessary (interactivity, hooks)
- Keep components small and focused
- Extract reusable UI components to `/components/ui/`
- Feature-specific components go in `/components/features/`

### 4. Authentication Flow
- Use Better Auth for user management
- JWT tokens stored securely (httpOnly cookies preferred)
- All API calls to backend include Authorization header
- Protected routes wrapped with authentication checks
- Redirect to login if unauthorized

### 5. API Communication
```typescript
// Example API client structure
const apiClient = {
  baseURL: process.env.NEXT_PUBLIC_API_URL,

  async request(endpoint: string, options: RequestInit) {
    const token = await getAuthToken();
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return response.json();
  },

  tasks: {
    list: () => apiClient.request('/api/tasks', { method: 'GET' }),
    create: (data) => apiClient.request('/api/tasks', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiClient.request(`/api/tasks/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiClient.request(`/api/tasks/${id}`, { method: 'DELETE' }),
    complete: (id) => apiClient.request(`/api/tasks/${id}/complete`, { method: 'PATCH' }),
  },
};
```

### 6. Error Handling
- Use try-catch for async operations
- Display user-friendly error messages
- Log errors for debugging
- Handle network failures gracefully
- Show loading states during async operations

### 7. Environment Variables
Required environment variables in `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-shared-secret-key
BETTER_AUTH_URL=http://localhost:3000
```

### 8. Code Quality
- Use ESLint for code linting
- Follow Next.js best practices
- Write clean, readable code
- Add comments for complex logic only
- Keep functions small and focused

### 9. Performance
- Use Next.js Image component for images
- Implement proper loading states
- Lazy load heavy components
- Optimize bundle size
- Use React.memo for expensive renders

### 10. Security
- Never expose secrets in client code
- Validate all user inputs
- Sanitize data before rendering
- Use HTTPS in production
- Implement CSRF protection via Better Auth

## Better Auth Setup
1. Install Better Auth: `npm install better-auth`
2. Configure in `/lib/auth.ts`
3. Create API routes in `/app/api/auth/[...all]/route.ts`
4. Use `useSession()` hook for auth state
5. Protect routes with auth middleware

## Testing (Future Phase)
- Unit tests with Jest and React Testing Library
- E2E tests with Playwright
- Test authentication flows
- Test API integration
- Component testing

## Development Workflow
1. Read and understand the spec in `/specs/`
2. Create necessary types in `/lib/types.ts`
3. Build UI components in `/components/`
4. Implement pages in `/app/`
5. Test locally with backend running
6. Commit with descriptive messages

## Common Tasks

### Adding a New Page
1. Create route folder in `/app/`
2. Add `page.tsx` with Server Component
3. Add `loading.tsx` for loading state
4. Add `error.tsx` for error handling
5. Update navigation if needed

### Adding a New Component
1. Create component file in appropriate folder
2. Define TypeScript interface for props
3. Implement component logic
4. Export and use in pages

### Calling Backend API
1. Use the centralized API client in `/lib/api-client.ts`
2. Handle loading and error states
3. Update UI based on response
4. Show user feedback (success/error messages)

## Monorepo Context
- This frontend is part of a monorepo structure
- Backend API runs on http://localhost:8000 (in development)
- Coordinate with backend specs in `/specs/api/`
- Database schema in `/specs/database/`

## Resources
- [Next.js Documentation](https://nextjs.org/docs)
- [Better Auth Documentation](https://better-auth.com)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)

## Notes
- This is a spec-driven project: NO manual coding without specs
- All changes must be justified by project requirements
- Follow the monorepo structure defined in root `/specs/architecture.md`
- Coordinate authentication between frontend and backend via shared secret
