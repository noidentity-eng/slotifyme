# Slotifyme Admin UI

A Next.js 14 admin interface for managing Slotifyme plans, add-ons, and tenants.

## Features

- **Authentication**: Secure JWT-based authentication with HttpOnly cookies
- **Plans Management**: View and edit subscription plans with inline editing
- **Add-ons Management**: Manage add-on features and pricing
- **Tenant Management**: Create and manage tenant accounts with locations
- **Bootstrap Data**: One-click sample tenant creation for testing
- **Modern UI**: Built with Tailwind CSS and shadcn/ui components
- **Type Safety**: Full TypeScript support with Zod validation

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui + Radix UI
- **State Management**: TanStack Query
- **Forms**: React Hook Form + Zod validation
- **Icons**: Lucide React

## Quick Start

### Prerequisites

Make sure you have the following services running locally:

- Rules service (port 8000)
- Tenant service (port 8001)
- Router service (port 8002)
- Admin BFF (port 8100)

### Environment Setup

1. Copy the environment example file:

```bash
cp .env.local.example .env.local
```

2. Update the environment variables in `.env.local`:

```env
NEXT_PUBLIC_APP_NAME=Slotifyme Admin
BFF_BASE_URL=http://localhost:8100
JWT_COOKIE_NAME=slotifyme_admin_jwt
JWT_COOKIE_SECURE=false
PUBLIC_HOST_DOMAIN=slotifyme.com
```

### Installation & Development

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

3. Open [http://localhost:3000/login](http://localhost:3000/login)

4. Login with default credentials:
   - Email: `arun@slotifyme.com`
   - Password: `admin123`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Usage

### Plans & Add-ons

Navigate to `/admin/plans` to:

- View all subscription plans (Silver, Gold, Platinum)
- Edit plan limits, features, and overage policies inline
- Manage add-on features and pricing references
- See preview prices from the BFF

### Tenants

Navigate to `/admin/tenants` to:

- View all tenant accounts
- Create new tenants with locations and plans
- Bootstrap sample tenants for testing
- See tenant slugs and location counts

### Creating a New Tenant

1. Click "New Tenant" button
2. Fill in tenant information (name, slug)
3. Add first location details (name, slug, timezone, phone)
4. Select plan and add-ons
5. Preview the public URL that will be generated
6. Submit to create the tenant

### Bootstrap Sample Data

Click "Bootstrap Sample Tenants" to automatically create:

- "Chop It Up" (Seattle location)
- "Clean Cuts" (Miami location)

## API Integration

The admin UI communicates with the Admin BFF through a secure proxy:

- All requests go through `/api/*` routes
- JWT tokens are handled server-side in HttpOnly cookies
- Authentication is automatic for protected routes
- 401 responses clear the auth cookie and redirect to login

## Security

- JWT tokens stored in HttpOnly, SameSite=Lax cookies
- Server-side authentication guards on all admin routes
- Secure proxy prevents token exposure to client-side code
- Automatic logout on authentication failures

## Docker Deployment

Build the Docker image:

```bash
docker build -t slotifyme-admin-ui .
```

Run the container:

```bash
docker run -p 3000:3000 \
  -e BFF_BASE_URL=http://your-bff-url:8100 \
  -e JWT_COOKIE_SECURE=true \
  slotifyme-admin-ui
```

## Project Structure

```
admin-ui/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── admin/             # Protected admin routes
│   │   ├── api/               # API proxy routes
│   │   ├── login/             # Login page
│   │   └── logout/            # Logout route
│   ├── components/            # Reusable UI components
│   └── lib/                   # Utilities and configurations
├── public/                    # Static assets
└── package.json
```

## Troubleshooting

### Common Issues

1. **Login fails**: Ensure the Admin BFF is running on the correct port
2. **API errors**: Check that all backend services are running
3. **Build errors**: Make sure all environment variables are set
4. **Styling issues**: Verify Tailwind CSS is properly configured

### Development Tips

- Use the React Query DevTools for debugging API calls
- Check browser network tab for API request/response details
- Monitor server logs for authentication and proxy issues

## Contributing

1. Follow the existing code style and patterns
2. Add TypeScript types for all new components
3. Use Zod schemas for form validation
4. Test API integrations thoroughly
5. Update documentation for new features
