# SYRA Frontend

Modern Next.js 14.2.0 frontend for SYRA Medical ID application.

## Tech Stack

- **Framework**: Next.js 14.2.0 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **Linting**: ESLint
- **Package Manager**: npm (or Bun)

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── app/           # Next.js App Router pages
│   ├── components/    # Reusable React components
│   ├── lib/           # Utility functions
│   ├── styles/        # Global styles
│   └── public/        # Static assets
├── public/            # Public static assets
├── package.json       # Dependencies
├── tsconfig.json      # TypeScript config
├── next.config.ts     # Next.js config
└── .eslintrc.json     # ESLint config
```

## Development

The frontend is designed to work with the existing Django backend API. Configure the API URL in your environment variables.
