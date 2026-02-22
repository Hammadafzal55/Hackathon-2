# Todo Application Frontend

A modern, responsive frontend for the Todo web application built with Next.js 16+, TypeScript, and Tailwind CSS. This application provides a beautiful and intuitive user interface for managing tasks with seamless integration to the backend API.

## Features

- **Task Management**: Create, read, update, and delete tasks with real-time synchronization
- **Visual Feedback**: Loading spinners, success/error notifications, and smooth transitions
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices with adaptive layouts
- **Form Validation**: Client-side validation with detailed error messages for better user experience
- **Task Status Management**: Toggle tasks between completed and pending states
- **Modern UI**: Clean, contemporary design with gradient backgrounds and card-based layout
- **Accessibility**: Semantic HTML and keyboard navigation support
- **Error Handling**: Comprehensive error handling with user-friendly messages

## Tech Stack

- **Framework**: Next.js 16+ with App Router
- **Language**: TypeScript with strict type checking
- **Styling**: Tailwind CSS with custom utility classes
- **State Management**: React Hooks and Context API
- **API Client**: Class-based API client with proper error handling
- **Build Tool**: Next.js built-in bundler

## Environment Variables

Create a `.env.local` file in the root directory with the following variables:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIXED_USER_ID=123e4567-e89b-12d3-a456-426614174000
```

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- npm or yarn package manager

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Create a `.env.local` file with your environment variables (see above)

4. Run the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx          # Root layout with responsive container
│   └── page.tsx           # Main todo page
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   └── TaskForm.tsx
│   ├── hooks/             # Custom React hooks
│   │   └── useTasks.ts
│   ├── lib/               # Utility functions and API client
│   │   ├── api.ts
│   │   └── errors.ts
│   ├── styles/            # CSS styles
│   │   └── globals.css
│   └── types/             # TypeScript type definitions
│       └── index.ts
├── public/                # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── README.md
```

## API Integration

The frontend communicates with the backend API using the following endpoints:

- `GET /api/{user_id}/tasks` - Fetch all tasks for user
- `POST /api/{user_id}/tasks` - Create a new task
- `PUT /api/{user_id}/tasks/{id}` - Update a task
- `DELETE /api/{user_id}/tasks/{id}` - Delete a task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion

## Components

### TaskList
Displays a list of tasks with loading and error states.

### TaskItem
Represents a single task with the ability to toggle completion, edit, and delete.

### TaskForm
Handles task creation and editing with form validation.

### useTasks Hook
Custom hook that manages all task-related API operations and state.

## Error Handling

The application implements comprehensive error handling:

- Network errors
- Validation errors
- API response errors
- Loading states during operations

## Styling

The application uses Tailwind CSS for styling with custom classes defined in `src/styles/globals.css`. The design is responsive and follows modern UI/UX principles.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License.