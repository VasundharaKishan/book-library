# Chapter 29: Building a Real-World Project

## Learning Goals

By the end of this chapter, you will have built a complete, production-quality application that demonstrates:

- Feature-based project architecture with clean separation of concerns
- Authentication with protected routes and role awareness
- CRUD operations with optimistic updates and error handling
- Responsive design with dark mode support
- Form validation and multi-step workflows
- Performance optimization with code splitting and lazy loading
- Accessible, keyboard-navigable interfaces
- A codebase you can showcase in your portfolio

---

## The Project: TaskFlow — A Project Management Application

We are building TaskFlow, a project management tool where users can create projects, manage tasks with drag-and-drop, collaborate with team members, and track progress. Think of a simplified Trello or Asana.

### Core Features

1. **Authentication** — register, login, logout, protected routes
2. **Projects** — create, view, edit, delete projects
3. **Task Board** — Kanban-style columns (To Do, In Progress, Done) with draggable tasks
4. **Task Management** — create, edit, delete, assign, and prioritize tasks
5. **Dashboard** — overview of all projects with progress stats
6. **User Profile** — edit profile, change preferences, dark mode
7. **Search** — search across tasks and projects

Since we do not have a real backend, we will build a comprehensive mock API layer that simulates network delays, authentication, and persistence using localStorage. This approach lets you focus entirely on React while having realistic data interactions.

---

## Step 1: Project Setup and Architecture

### Initialize the Project

```bash
npm create vite@latest taskflow -- --template react
cd taskflow
npm install react-router-dom clsx
npm install -D @testing-library/react @testing-library/jest-dom vitest
```

### Configure Path Aliases

```jsx
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@features': path.resolve(__dirname, './src/features'),
      '@shared': path.resolve(__dirname, './src/shared'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@assets': path.resolve(__dirname, './src/assets'),
    },
  },
});
```

```json
// jsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@features/*": ["src/features/*"],
      "@shared/*": ["src/shared/*"],
      "@pages/*": ["src/pages/*"],
      "@assets/*": ["src/assets/*"]
    }
  }
}
```

### Project Structure

```
src/
├── app/
│   ├── App.jsx
│   ├── AppProviders.jsx
│   └── routes.jsx
├── features/
│   ├── auth/
│   │   ├── components/
│   │   │   ├── LoginForm.jsx
│   │   │   ├── RegisterForm.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── services/
│   │   │   └── authService.js
│   │   └── index.js
│   ├── projects/
│   │   ├── components/
│   │   │   ├── ProjectCard.jsx
│   │   │   ├── ProjectList.jsx
│   │   │   ├── ProjectForm.jsx
│   │   │   └── ProjectDetail.jsx
│   │   ├── hooks/
│   │   │   ├── useProjects.js
│   │   │   └── useProject.js
│   │   ├── services/
│   │   │   └── projectService.js
│   │   └── index.js
│   ├── tasks/
│   │   ├── components/
│   │   │   ├── TaskBoard.jsx
│   │   │   ├── TaskColumn.jsx
│   │   │   ├── TaskCard.jsx
│   │   │   ├── TaskForm.jsx
│   │   │   └── TaskDetail.jsx
│   │   ├── hooks/
│   │   │   └── useTasks.js
│   │   ├── services/
│   │   │   └── taskService.js
│   │   └── index.js
│   ├── dashboard/
│   │   ├── components/
│   │   │   ├── DashboardStats.jsx
│   │   │   ├── RecentActivity.jsx
│   │   │   └── ProjectProgress.jsx
│   │   ├── hooks/
│   │   │   └── useDashboard.js
│   │   └── index.js
│   └── search/
│       ├── components/
│       │   ├── SearchBar.jsx
│       │   └── SearchResults.jsx
│       ├── hooks/
│       │   └── useSearch.js
│       └── index.js
├── shared/
│   ├── components/
│   │   ├── Button/
│   │   ├── Input/
│   │   ├── Modal/
│   │   ├── Spinner/
│   │   ├── ErrorBoundary/
│   │   ├── EmptyState/
│   │   ├── Avatar/
│   │   ├── Badge/
│   │   ├── DropdownMenu/
│   │   └── index.js
│   ├── hooks/
│   │   ├── useDebounce.js
│   │   ├── useLocalStorage.js
│   │   └── index.js
│   ├── utils/
│   │   ├── cn.js
│   │   ├── formatDate.js
│   │   ├── mockApi.js
│   │   └── index.js
│   ├── context/
│   │   ├── ThemeContext.jsx
│   │   ├── NotificationContext.jsx
│   │   └── index.js
│   ├── layouts/
│   │   ├── AppLayout.jsx
│   │   ├── AuthLayout.jsx
│   │   └── index.js
│   └── constants/
│       └── index.js
├── pages/
│   ├── DashboardPage.jsx
│   ├── ProjectsPage.jsx
│   ├── ProjectDetailPage.jsx
│   ├── LoginPage.jsx
│   ├── RegisterPage.jsx
│   ├── ProfilePage.jsx
│   └── NotFoundPage.jsx
├── assets/
│   └── styles/
│       ├── variables.css
│       ├── reset.css
│       └── global.css
└── main.jsx
```

---

## Step 2: Foundation — Shared Components and Utilities

### CSS Variables and Global Styles

```css
/* src/assets/styles/variables.css */
:root {
  /* Colors */
  --color-primary: #6366f1;
  --color-primary-hover: #4f46e5;
  --color-primary-light: #e0e7ff;
  --color-success: #22c55e;
  --color-success-light: #dcfce7;
  --color-warning: #f59e0b;
  --color-warning-light: #fef3c7;
  --color-danger: #ef4444;
  --color-danger-light: #fee2e2;

  /* Neutrals */
  --color-bg: #ffffff;
  --color-bg-secondary: #f8fafc;
  --color-bg-tertiary: #f1f5f9;
  --color-surface: #ffffff;
  --color-border: #e2e8f0;
  --color-text: #0f172a;
  --color-text-secondary: #64748b;
  --color-text-muted: #94a3b8;

  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 2rem;

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;

  /* Layout */
  --sidebar-width: 260px;
  --header-height: 64px;
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 200ms ease;
}

/* Dark mode */
[data-theme='dark'] {
  --color-bg: #0f172a;
  --color-bg-secondary: #1e293b;
  --color-bg-tertiary: #334155;
  --color-surface: #1e293b;
  --color-border: #334155;
  --color-text: #f8fafc;
  --color-text-secondary: #94a3b8;
  --color-text-muted: #64748b;
  --color-primary-light: #312e81;
  --color-success-light: #14532d;
  --color-warning-light: #78350f;
  --color-danger-light: #7f1d1d;
}
```

```css
/* src/assets/styles/reset.css */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  color: var(--color-text);
  background-color: var(--color-bg);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

a {
  color: inherit;
  text-decoration: none;
}

button {
  cursor: pointer;
  border: none;
  background: none;
  font: inherit;
  color: inherit;
}

ul, ol {
  list-style: none;
}

img {
  display: block;
  max-width: 100%;
}

input, textarea, select {
  font: inherit;
  color: inherit;
}
```

```css
/* src/assets/styles/global.css */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
```

### Utility: Class Name Helper

```jsx
// src/shared/utils/cn.js
import clsx from 'clsx';

export function cn(...args) {
  return clsx(...args);
}
```

### Utility: Date Formatting

```jsx
// src/shared/utils/formatDate.js
export function formatDate(dateString) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(dateString));
}

export function formatRelativeTime(dateString) {
  const seconds = Math.floor(
    (Date.now() - new Date(dateString).getTime()) / 1000
  );

  const intervals = [
    { label: 'year', seconds: 31536000 },
    { label: 'month', seconds: 2592000 },
    { label: 'week', seconds: 604800 },
    { label: 'day', seconds: 86400 },
    { label: 'hour', seconds: 3600 },
    { label: 'minute', seconds: 60 },
  ];

  for (const interval of intervals) {
    const count = Math.floor(seconds / interval.seconds);
    if (count >= 1) {
      return `${count} ${interval.label}${count > 1 ? 's' : ''} ago`;
    }
  }
  return 'just now';
}
```

### The Mock API Layer

This is the backbone of our application — a realistic API simulation:

```jsx
// src/shared/utils/mockApi.js

// Simulate network delay
function delay(ms = 300) {
  return new Promise(resolve =>
    setTimeout(resolve, ms + Math.random() * 200)
  );
}

// localStorage-based database
function getStore(key) {
  const data = localStorage.getItem(`taskflow_${key}`);
  return data ? JSON.parse(data) : null;
}

function setStore(key, data) {
  localStorage.setItem(`taskflow_${key}`, JSON.stringify(data));
}

// Generate unique IDs
let idCounter = Date.now();
function generateId() {
  return String(idCounter++);
}

// Initialize default data if empty
function initializeData() {
  if (!getStore('initialized')) {
    setStore('users', [
      {
        id: '1',
        name: 'Alex Johnson',
        email: 'alex@taskflow.com',
        password: 'password123',
        avatar: null,
        role: 'admin',
        createdAt: '2025-01-15T10:00:00Z',
      },
      {
        id: '2',
        name: 'Sam Rivera',
        email: 'sam@taskflow.com',
        password: 'password123',
        avatar: null,
        role: 'member',
        createdAt: '2025-02-01T10:00:00Z',
      },
    ]);

    setStore('projects', [
      {
        id: '1',
        name: 'Website Redesign',
        description: 'Complete overhaul of the company website with modern design and improved UX.',
        color: '#6366f1',
        ownerId: '1',
        memberIds: ['1', '2'],
        createdAt: '2025-06-01T10:00:00Z',
        updatedAt: '2025-06-01T10:00:00Z',
      },
      {
        id: '2',
        name: 'Mobile App',
        description: 'Build a cross-platform mobile application for our customers.',
        color: '#22c55e',
        ownerId: '1',
        memberIds: ['1'],
        createdAt: '2025-07-01T10:00:00Z',
        updatedAt: '2025-07-01T10:00:00Z',
      },
    ]);

    setStore('tasks', [
      {
        id: '1',
        projectId: '1',
        title: 'Design new homepage layout',
        description: 'Create wireframes and mockups for the new homepage.',
        status: 'done',
        priority: 'high',
        assigneeId: '2',
        createdBy: '1',
        dueDate: '2025-07-15T00:00:00Z',
        createdAt: '2025-06-05T10:00:00Z',
        updatedAt: '2025-07-10T14:30:00Z',
      },
      {
        id: '2',
        projectId: '1',
        title: 'Implement responsive navigation',
        description: 'Build the main navigation component with mobile menu.',
        status: 'in-progress',
        priority: 'high',
        assigneeId: '1',
        createdBy: '1',
        dueDate: '2025-08-01T00:00:00Z',
        createdAt: '2025-06-10T10:00:00Z',
        updatedAt: '2025-07-20T09:15:00Z',
      },
      {
        id: '3',
        projectId: '1',
        title: 'Set up CI/CD pipeline',
        description: 'Configure GitHub Actions for automated testing and deployment.',
        status: 'todo',
        priority: 'medium',
        assigneeId: null,
        createdBy: '1',
        dueDate: '2025-08-15T00:00:00Z',
        createdAt: '2025-06-15T10:00:00Z',
        updatedAt: '2025-06-15T10:00:00Z',
      },
      {
        id: '4',
        projectId: '1',
        title: 'Write content for About page',
        description: 'Draft copy for the about page including team bios.',
        status: 'todo',
        priority: 'low',
        assigneeId: '2',
        createdBy: '1',
        dueDate: '2025-08-20T00:00:00Z',
        createdAt: '2025-06-20T10:00:00Z',
        updatedAt: '2025-06-20T10:00:00Z',
      },
      {
        id: '5',
        projectId: '2',
        title: 'Set up React Native project',
        description: 'Initialize the project with navigation and basic structure.',
        status: 'in-progress',
        priority: 'high',
        assigneeId: '1',
        createdBy: '1',
        dueDate: '2025-08-01T00:00:00Z',
        createdAt: '2025-07-05T10:00:00Z',
        updatedAt: '2025-07-18T11:00:00Z',
      },
      {
        id: '6',
        projectId: '2',
        title: 'Design app icon and splash screen',
        description: 'Create app branding assets.',
        status: 'todo',
        priority: 'medium',
        assigneeId: null,
        createdBy: '1',
        dueDate: '2025-08-10T00:00:00Z',
        createdAt: '2025-07-05T10:00:00Z',
        updatedAt: '2025-07-05T10:00:00Z',
      },
    ]);

    setStore('activity', [
      { id: '1', type: 'task_completed', userId: '2', taskId: '1', projectId: '1', timestamp: '2025-07-10T14:30:00Z' },
      { id: '2', type: 'task_created', userId: '1', taskId: '5', projectId: '2', timestamp: '2025-07-05T10:00:00Z' },
      { id: '3', type: 'project_created', userId: '1', projectId: '2', timestamp: '2025-07-01T10:00:00Z' },
    ]);

    setStore('initialized', true);
  }
}

initializeData();

// Simulated auth token management
const tokens = new Map();

function createToken(userId) {
  const token = `token_${userId}_${Date.now()}`;
  tokens.set(token, userId);
  return token;
}

function validateToken(token) {
  return tokens.get(token) || null;
}

// ========== AUTH API ==========

export const authApi = {
  async login(email, password) {
    await delay();
    const users = getStore('users') || [];
    const user = users.find(u => u.email === email && u.password === password);

    if (!user) {
      throw new Error('Invalid email or password');
    }

    const token = createToken(user.id);
    const { password: _, ...userWithoutPassword } = user;
    return { user: userWithoutPassword, token };
  },

  async register(name, email, password) {
    await delay();
    const users = getStore('users') || [];

    if (users.find(u => u.email === email)) {
      throw new Error('An account with this email already exists');
    }

    const newUser = {
      id: generateId(),
      name,
      email,
      password,
      avatar: null,
      role: 'member',
      createdAt: new Date().toISOString(),
    };

    setStore('users', [...users, newUser]);
    const token = createToken(newUser.id);
    const { password: _, ...userWithoutPassword } = newUser;
    return { user: userWithoutPassword, token };
  },

  async getMe(token) {
    await delay(100);
    const userId = validateToken(token);
    if (!userId) throw new Error('Invalid token');

    const users = getStore('users') || [];
    const user = users.find(u => u.id === userId);
    if (!user) throw new Error('User not found');

    const { password: _, ...userWithoutPassword } = user;
    return userWithoutPassword;
  },

  async updateProfile(token, updates) {
    await delay();
    const userId = validateToken(token);
    if (!userId) throw new Error('Invalid token');

    const users = getStore('users') || [];
    const index = users.findIndex(u => u.id === userId);
    if (index === -1) throw new Error('User not found');

    users[index] = { ...users[index], ...updates };
    setStore('users', users);

    const { password: _, ...userWithoutPassword } = users[index];
    return userWithoutPassword;
  },
};

// ========== PROJECTS API ==========

export const projectsApi = {
  async getAll(token) {
    await delay();
    const userId = validateToken(token);
    if (!userId) throw new Error('Unauthorized');

    const projects = getStore('projects') || [];
    const tasks = getStore('tasks') || [];

    return projects
      .filter(p => p.memberIds.includes(userId))
      .map(project => {
        const projectTasks = tasks.filter(t => t.projectId === project.id);
        return {
          ...project,
          taskCount: projectTasks.length,
          completedCount: projectTasks.filter(t => t.status === 'done').length,
        };
      });
  },

  async getById(token, projectId) {
    await delay();
    const userId = validateToken(token);
    if (!userId) throw new Error('Unauthorized');

    const projects = getStore('projects') || [];
    const project = projects.find(p => p.id === projectId);
    if (!project) throw new Error('Project not found');
    if (!project.memberIds.includes(userId)) throw new Error('Access denied');

    const users = getStore('users') || [];
    const members = users
      .filter(u => project.memberIds.includes(u.id))
      .map(({ password: _, ...u }) => u);

    return { ...project, members };
  },

  async create(token, data) {
    await delay();
    const userId = validateToken(token);
    if (!userId) throw new Error('Unauthorized');

    const projects = getStore('projects') || [];
    const newProject = {
      id: generateId(),
      ...data,
      ownerId: userId,
      memberIds: [userId],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    setStore('projects', [...projects, newProject]);

    const activity = getStore('activity') || [];
    activity.unshift({
      id: generateId(),
      type: 'project_created',
      userId,
      projectId: newProject.id,
      timestamp: new Date().toISOString(),
    });
    setStore('activity', activity);

    return { ...newProject, taskCount: 0, completedCount: 0 };
  },

  async update(token, projectId, data) {
    await delay();
    const userId = validateToken(token);
    if (!userId) throw new Error('Unauthorized');

    const projects = getStore('projects') || [];
    const index = projects.findIndex(p => p.id === projectId);
    if (index === -1) throw new Error('Project not found');

    projects[index] = {
      ...projects[index],
      ...data,
      updatedAt: new Date().toISOString(),
    };
    setStore('projects', projects);
    return projects[index];
  },

  async delete(token, projectId) {
    await delay();
    const userId = validateToken(token);
    if (!userId) throw new Error('Unauthorized');

    const projects = getStore('projects') || [];
    const project = projects.find(p => p.id === projectId);
    if (!project) throw new Error('Project not found');
    if (project.ownerId !== userId) throw new Error('Only the owner can delete a project');

    setStore('projects', projects.filter(p => p.id !== projectId));

    const tasks = getStore('tasks') || [];
    setStore('tasks', tasks.filter(t => t.projectId !== projectId));
  },
};

// ========== TASKS API ==========

export const tasksApi = {
  async getByProject(token, projectId) {
    await delay();
    const userId = validateToken(token);
    if (!userId) throw new Error('Unauthorized');

    const tasks = getStore('tasks') || [];
    const users = getStore('users') || [];

    return tasks
      .filter(t => t.projectId === projectId)
      .map(task => {
        const assignee = users.find(u => u.id === task.assigneeId);
        return {
          ...task,
          assignee: assignee
            ? { id: assignee.id, name: assignee.name, avatar: assignee.avatar }
            : null,
        };
      });
  },

  async create(token, data) {
    await delay();
    const userId = validateToken(token);
    if (!userId) throw new Error('Unauthorized');

    const tasks = getStore('tasks') || [];
    const newTask = {
      id: generateId(),
      ...data,
      status: data.status || 'todo',
      priority: data.priority || 'medium',
      assigneeId: data.assigneeId || null,
      createdBy: userId,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    setStore('tasks', [...tasks, newTask]);

    const activity = getStore('activity') || [];
    activity.unshift({
      id: generateId(),
      type: 'task_created',
      userId,
      taskId: newTask.id,
      projectId: data.projectId,
      timestamp: new Date().toISOString(),
    });
    setStore('activity', activity);

    return newTask;
  },

  async update(token, taskId, data) {
    await delay();
    const userId = validateToken(token);
    if (!userId) throw new Error('Unauthorized');

    const tasks = getStore('tasks') || [];
    const index = tasks.findIndex(t => t.id === taskId);
    if (index === -1) throw new Error('Task not found');

    const oldTask = tasks[index];
    tasks[index] = {
      ...oldTask,
      ...data,
      updatedAt: new Date().toISOString(),
    };
    setStore('tasks', tasks);

    // Log status changes
    if (data.status && data.status !== oldTask.status) {
      const activity = getStore('activity') || [];
      activity.unshift({
        id: generateId(),
        type: data.status === 'done' ? 'task_completed' : 'task_status_changed',
        userId,
        taskId,
        projectId: oldTask.projectId,
        oldStatus: oldTask.status,
        newStatus: data.status,
        timestamp: new Date().toISOString(),
      });
      setStore('activity', activity);
    }

    return tasks[index];
  },

  async delete(token, taskId) {
    await delay();
    const userId = validateToken(token);
    if (!userId) throw new Error('Unauthorized');

    const tasks = getStore('tasks') || [];
    setStore('tasks', tasks.filter(t => t.id !== taskId));
  },

  async updateStatus(token, taskId, status) {
    return this.update(token, taskId, { status });
  },
};

// ========== DASHBOARD API ==========

export const dashboardApi = {
  async getStats(token) {
    await delay();
    const userId = validateToken(token);
    if (!userId) throw new Error('Unauthorized');

    const projects = getStore('projects') || [];
    const tasks = getStore('tasks') || [];
    const activity = getStore('activity') || [];

    const userProjects = projects.filter(p => p.memberIds.includes(userId));
    const userProjectIds = userProjects.map(p => p.id);
    const userTasks = tasks.filter(t => userProjectIds.includes(t.projectId));

    return {
      totalProjects: userProjects.length,
      totalTasks: userTasks.length,
      completedTasks: userTasks.filter(t => t.status === 'done').length,
      inProgressTasks: userTasks.filter(t => t.status === 'in-progress').length,
      overdueTasks: userTasks.filter(t =>
        t.status !== 'done' && t.dueDate && new Date(t.dueDate) < new Date()
      ).length,
      recentActivity: activity
        .filter(a => userProjectIds.includes(a.projectId))
        .slice(0, 10),
    };
  },
};

// ========== SEARCH API ==========

export const searchApi = {
  async search(token, query) {
    await delay(200);
    const userId = validateToken(token);
    if (!userId) throw new Error('Unauthorized');

    const q = query.toLowerCase();
    const projects = getStore('projects') || [];
    const tasks = getStore('tasks') || [];

    const userProjects = projects.filter(p => p.memberIds.includes(userId));
    const userProjectIds = userProjects.map(p => p.id);

    const matchingProjects = userProjects.filter(p =>
      p.name.toLowerCase().includes(q) ||
      p.description.toLowerCase().includes(q)
    );

    const matchingTasks = tasks
      .filter(t => userProjectIds.includes(t.projectId))
      .filter(t =>
        t.title.toLowerCase().includes(q) ||
        (t.description && t.description.toLowerCase().includes(q))
      );

    return {
      projects: matchingProjects,
      tasks: matchingTasks,
    };
  },
};
```

### Shared Components

```jsx
// src/shared/components/Button/Button.jsx
import { cn } from '@shared/utils/cn';
import styles from './Button.module.css';

export function Button({
  children,
  variant = 'primary',
  size = 'medium',
  type = 'button',
  disabled = false,
  loading = false,
  fullWidth = false,
  className,
  ...props
}) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={cn(
        styles.button,
        styles[variant],
        styles[size],
        fullWidth && styles.fullWidth,
        className
      )}
      {...props}
    >
      {loading ? (
        <>
          <span className={styles.spinner} aria-hidden="true" />
          <span>Loading...</span>
        </>
      ) : (
        children
      )}
    </button>
  );
}
```

```css
/* src/shared/components/Button/Button.module.css */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-weight: 500;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  cursor: pointer;
  white-space: nowrap;
}

.button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Variants */
.primary {
  background-color: var(--color-primary);
  color: white;
}
.primary:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.secondary {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text);
}
.secondary:hover:not(:disabled) {
  background-color: var(--color-border);
}

.danger {
  background-color: var(--color-danger);
  color: white;
}
.danger:hover:not(:disabled) {
  background-color: #dc2626;
}

.ghost {
  background-color: transparent;
  color: var(--color-text-secondary);
}
.ghost:hover:not(:disabled) {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text);
}

/* Sizes */
.small {
  padding: var(--space-1) var(--space-3);
  font-size: var(--font-size-sm);
}
.medium {
  padding: var(--space-2) var(--space-4);
  font-size: var(--font-size-sm);
}
.large {
  padding: var(--space-3) var(--space-6);
  font-size: var(--font-size-base);
}

.fullWidth {
  width: 100%;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

```jsx
// src/shared/components/Input/Input.jsx
import { forwardRef } from 'react';
import { cn } from '@shared/utils/cn';
import styles from './Input.module.css';

export const Input = forwardRef(function Input(
  { label, error, helperText, id, className, ...props },
  ref
) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className={cn(styles.field, className)}>
      {label && (
        <label htmlFor={inputId} className={styles.label}>
          {label}
        </label>
      )}
      <input
        ref={ref}
        id={inputId}
        className={cn(styles.input, error && styles.inputError)}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={
          error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined
        }
        {...props}
      />
      {error && (
        <p id={`${inputId}-error`} className={styles.error} role="alert">
          {error}
        </p>
      )}
      {helperText && !error && (
        <p id={`${inputId}-helper`} className={styles.helper}>
          {helperText}
        </p>
      )}
    </div>
  );
});
```

```css
/* src/shared/components/Input/Input.module.css */
.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text);
}

.input {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-bg);
  font-size: var(--font-size-sm);
  transition: border-color var(--transition-fast);
  width: 100%;
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.inputError {
  border-color: var(--color-danger);
}

.inputError:focus {
  box-shadow: 0 0 0 3px var(--color-danger-light);
}

.error {
  font-size: var(--font-size-xs);
  color: var(--color-danger);
}

.helper {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}
```

```jsx
// src/shared/components/Modal/Modal.jsx
import { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import styles from './Modal.module.css';

export function Modal({ isOpen, onClose, title, children, size = 'medium' }) {
  const modalRef = useRef(null);
  const previousFocusRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement;
      document.body.style.overflow = 'hidden';
      // Focus the modal after a brief delay for animation
      setTimeout(() => modalRef.current?.focus(), 50);
    }
    return () => {
      document.body.style.overflow = '';
      previousFocusRef.current?.focus();
    };
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    function handleEscape(e) {
      if (e.key === 'Escape') onClose();
    }
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return createPortal(
    <div className={styles.overlay} onClick={onClose}>
      <div
        ref={modalRef}
        className={`${styles.modal} ${styles[size]}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        tabIndex={-1}
        onClick={(e) => e.stopPropagation()}
      >
        <div className={styles.header}>
          <h2 id="modal-title" className={styles.title}>{title}</h2>
          <button
            onClick={onClose}
            className={styles.closeButton}
            aria-label="Close dialog"
          >
            ×
          </button>
        </div>
        <div className={styles.body}>{children}</div>
      </div>
    </div>,
    document.body
  );
}
```

```css
/* src/shared/components/Modal/Modal.module.css */
.overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  z-index: 1000;
  animation: fadeIn 0.15s ease;
}

.modal {
  background-color: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.2s ease;
  outline: none;
}

.small { width: 400px; }
.medium { width: 560px; }
.large { width: 720px; }

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  margin: 0;
}

.closeButton {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
}

.closeButton:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text);
}

.body {
  padding: var(--space-6);
  overflow-y: auto;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
```

```jsx
// src/shared/components/Spinner/Spinner.jsx
import styles from './Spinner.module.css';

export function Spinner({ size = 'medium', className = '' }) {
  return (
    <div className={`${styles.container} ${className}`} role="status">
      <div className={`${styles.spinner} ${styles[size]}`} />
      <span className="sr-only">Loading...</span>
    </div>
  );
}
```

```css
/* src/shared/components/Spinner/Spinner.module.css */
.container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
}

.spinner {
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.small { width: 20px; height: 20px; }
.medium { width: 32px; height: 32px; }
.large { width: 48px; height: 48px; }

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

```jsx
// src/shared/components/EmptyState/EmptyState.jsx
import styles from './EmptyState.module.css';

export function EmptyState({ title, description, action }) {
  return (
    <div className={styles.container}>
      <h3 className={styles.title}>{title}</h3>
      {description && <p className={styles.description}>{description}</p>}
      {action && <div className={styles.action}>{action}</div>}
    </div>
  );
}
```

```css
/* src/shared/components/EmptyState/EmptyState.module.css */
.container {
  text-align: center;
  padding: var(--space-12) var(--space-4);
}

.title {
  font-size: var(--font-size-lg);
  color: var(--color-text);
  margin: 0 0 var(--space-2);
}

.description {
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-6);
}

.action {
  display: flex;
  justify-content: center;
}
```

```jsx
// src/shared/components/Badge/Badge.jsx
import styles from './Badge.module.css';

export function Badge({ children, variant = 'default', size = 'medium' }) {
  return (
    <span className={`${styles.badge} ${styles[variant]} ${styles[size]}`}>
      {children}
    </span>
  );
}
```

```css
/* src/shared/components/Badge/Badge.module.css */
.badge {
  display: inline-flex;
  align-items: center;
  font-weight: 500;
  border-radius: var(--radius-full);
}

.small { padding: 1px 6px; font-size: var(--font-size-xs); }
.medium { padding: 2px 10px; font-size: var(--font-size-xs); }

.default { background: var(--color-bg-tertiary); color: var(--color-text-secondary); }
.primary { background: var(--color-primary-light); color: var(--color-primary); }
.success { background: var(--color-success-light); color: var(--color-success); }
.warning { background: var(--color-warning-light); color: var(--color-warning); }
.danger { background: var(--color-danger-light); color: var(--color-danger); }
```

```jsx
// src/shared/components/index.js
export { Button } from './Button/Button';
export { Input } from './Input/Input';
export { Modal } from './Modal/Modal';
export { Spinner } from './Spinner/Spinner';
export { EmptyState } from './EmptyState/EmptyState';
export { Badge } from './Badge/Badge';
```

### Shared Hooks

```jsx
// src/shared/hooks/useDebounce.js
import { useState, useEffect } from 'react';

export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
```

```jsx
// src/shared/hooks/useLocalStorage.js
import { useState, useEffect } from 'react';

export function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initialValue;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}
```

---

## Step 3: Authentication

```jsx
// src/features/auth/services/authService.js
import { authApi } from '@shared/utils/mockApi';

const TOKEN_KEY = 'taskflow_token';

export const authService = {
  getToken() {
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
  },

  removeToken() {
    localStorage.removeItem(TOKEN_KEY);
  },

  async login(email, password) {
    const result = await authApi.login(email, password);
    this.setToken(result.token);
    return result;
  },

  async register(name, email, password) {
    const result = await authApi.register(name, email, password);
    this.setToken(result.token);
    return result;
  },

  async getMe() {
    const token = this.getToken();
    if (!token) return null;
    return authApi.getMe(token);
  },

  async updateProfile(updates) {
    const token = this.getToken();
    return authApi.updateProfile(token, updates);
  },

  logout() {
    this.removeToken();
  },
};
```

```jsx
// src/features/auth/context/AuthContext.jsx
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    authService
      .getMe()
      .then(user => setUser(user))
      .catch(() => authService.removeToken())
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email, password) => {
    const { user } = await authService.login(email, password);
    setUser(user);
    return user;
  }, []);

  const register = useCallback(async (name, email, password) => {
    const { user } = await authService.register(name, email, password);
    setUser(user);
    return user;
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
  }, []);

  const updateProfile = useCallback(async (updates) => {
    const updated = await authService.updateProfile(updates);
    setUser(updated);
    return updated;
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

```jsx
// src/features/auth/components/ProtectedRoute.jsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Spinner } from '@shared/components';

export function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <Spinner size="large" />;
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />;
  return children;
}
```

```jsx
// src/features/auth/components/LoginForm.jsx
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button, Input } from '@shared/components';
import styles from './AuthForm.module.css';

export function LoginForm({ onSuccess }) {
  const { login } = useAuth();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState('');

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setErrors(prev => ({ ...prev, [name]: '' }));
    setServerError('');
  }

  function validate() {
    const newErrors = {};
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    if (!formData.password) newErrors.password = 'Password is required';
    return newErrors;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setSubmitting(true);
    setServerError('');

    try {
      await login(formData.email, formData.password);
      onSuccess?.();
    } catch (err) {
      setServerError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <h1 className={styles.title}>Welcome back</h1>
      <p className={styles.subtitle}>Sign in to your TaskFlow account</p>

      {serverError && (
        <div className={styles.serverError} role="alert">
          {serverError}
        </div>
      )}

      <Input
        label="Email"
        name="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
        error={errors.email}
        autoComplete="email"
      />

      <Input
        label="Password"
        name="password"
        type="password"
        value={formData.password}
        onChange={handleChange}
        error={errors.password}
        autoComplete="current-password"
      />

      <Button type="submit" loading={submitting} fullWidth size="large">
        Sign In
      </Button>

      <p className={styles.footer}>
        Don't have an account? <Link to="/register">Sign up</Link>
      </p>

      <p className={styles.hint}>
        Demo: alex@taskflow.com / password123
      </p>
    </form>
  );
}
```

```css
/* src/features/auth/components/AuthForm.module.css */
.form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  width: 100%;
  max-width: 400px;
}

.title {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  margin: 0;
}

.subtitle {
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-2);
}

.serverError {
  padding: var(--space-3) var(--space-4);
  background-color: var(--color-danger-light);
  color: var(--color-danger);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
}

.footer {
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.footer a {
  color: var(--color-primary);
  font-weight: 500;
}

.hint {
  text-align: center;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  padding: var(--space-2);
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-sm);
}
```

```jsx
// src/features/auth/components/RegisterForm.jsx
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button, Input } from '@shared/components';
import styles from './AuthForm.module.css';

export function RegisterForm({ onSuccess }) {
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState('');

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setErrors(prev => ({ ...prev, [name]: '' }));
    setServerError('');
  }

  function validate() {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Invalid email';
    if (!formData.password) newErrors.password = 'Password is required';
    else if (formData.password.length < 8) newErrors.password = 'At least 8 characters';
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    return newErrors;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setSubmitting(true);
    setServerError('');

    try {
      await register(formData.name, formData.email, formData.password);
      onSuccess?.();
    } catch (err) {
      setServerError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <h1 className={styles.title}>Create account</h1>
      <p className={styles.subtitle}>Start managing your projects with TaskFlow</p>

      {serverError && (
        <div className={styles.serverError} role="alert">{serverError}</div>
      )}

      <Input label="Full Name" name="name" value={formData.name} onChange={handleChange} error={errors.name} autoComplete="name" />
      <Input label="Email" name="email" type="email" value={formData.email} onChange={handleChange} error={errors.email} autoComplete="email" />
      <Input label="Password" name="password" type="password" value={formData.password} onChange={handleChange} error={errors.password} helperText="At least 8 characters" autoComplete="new-password" />
      <Input label="Confirm Password" name="confirmPassword" type="password" value={formData.confirmPassword} onChange={handleChange} error={errors.confirmPassword} autoComplete="new-password" />

      <Button type="submit" loading={submitting} fullWidth size="large">
        Create Account
      </Button>

      <p className={styles.footer}>
        Already have an account? <Link to="/login">Sign in</Link>
      </p>
    </form>
  );
}
```

```jsx
// src/features/auth/index.js
export { LoginForm } from './components/LoginForm';
export { RegisterForm } from './components/RegisterForm';
export { ProtectedRoute } from './components/ProtectedRoute';
export { AuthProvider, useAuth } from './context/AuthContext';
```

---

## Step 4: Theme and Notifications

```jsx
// src/shared/context/ThemeContext.jsx
import { createContext, useContext } from 'react';
import { useLocalStorage } from '@shared/hooks/useLocalStorage';
import { useEffect } from 'react';

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useLocalStorage('taskflow_theme', 'light');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  function toggleTheme() {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}
```

```jsx
// src/shared/context/NotificationContext.jsx
import { createContext, useContext, useState, useCallback } from 'react';
import styles from './Notification.module.css';

const NotificationContext = createContext(null);

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);

  const addNotification = useCallback((message, type = 'info') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 4000);
  }, []);

  const notify = {
    success: (msg) => addNotification(msg, 'success'),
    error: (msg) => addNotification(msg, 'error'),
    info: (msg) => addNotification(msg, 'info'),
  };

  return (
    <NotificationContext.Provider value={notify}>
      {children}
      <div className={styles.container} aria-live="polite">
        {notifications.map(n => (
          <div key={n.id} className={`${styles.notification} ${styles[n.type]}`}>
            {n.message}
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  );
}

export function useNotification() {
  const context = useContext(NotificationContext);
  if (!context) throw new Error('useNotification must be used within NotificationProvider');
  return context;
}
```

```css
/* src/shared/context/Notification.module.css */
.container {
  position: fixed;
  top: var(--space-4);
  right: var(--space-4);
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.notification {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: 500;
  box-shadow: var(--shadow-md);
  animation: slideIn 0.2s ease;
  min-width: 280px;
}

.success {
  background-color: var(--color-success);
  color: white;
}

.error {
  background-color: var(--color-danger);
  color: white;
}

.info {
  background-color: var(--color-primary);
  color: white;
}

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
```

---

## Step 5: Layouts

```jsx
// src/shared/layouts/AppLayout.jsx
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '@features/auth';
import { useTheme } from '@shared/context/ThemeContext';
import { SearchBar } from '@features/search';
import styles from './AppLayout.module.css';

export function AppLayout() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        <div className={styles.logo}>
          <h1>TaskFlow</h1>
        </div>

        <nav className={styles.nav} aria-label="Main navigation">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `${styles.navLink} ${isActive ? styles.active : ''}`
            }
          >
            <span aria-hidden="true">📊</span> Dashboard
          </NavLink>
          <NavLink
            to="/projects"
            className={({ isActive }) =>
              `${styles.navLink} ${isActive ? styles.active : ''}`
            }
          >
            <span aria-hidden="true">📁</span> Projects
          </NavLink>
          <NavLink
            to="/profile"
            className={({ isActive }) =>
              `${styles.navLink} ${isActive ? styles.active : ''}`
            }
          >
            <span aria-hidden="true">👤</span> Profile
          </NavLink>
        </nav>

        <div className={styles.sidebarFooter}>
          <button onClick={toggleTheme} className={styles.themeToggle}>
            {theme === 'light' ? '🌙' : '☀️'} {theme === 'light' ? 'Dark' : 'Light'} Mode
          </button>
          <button onClick={handleLogout} className={styles.logoutButton}>
            Sign Out
          </button>
        </div>
      </aside>

      <div className={styles.main}>
        <header className={styles.header}>
          <SearchBar />
          <div className={styles.headerRight}>
            <span className={styles.userName}>{user?.name}</span>
          </div>
        </header>

        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
```

```css
/* src/shared/layouts/AppLayout.module.css */
.layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: var(--sidebar-width);
  background-color: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
}

.logo {
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.logo h1 {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-primary);
  margin: 0;
}

.nav {
  flex: 1;
  padding: var(--space-4) var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.navLink {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.navLink:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text);
}

.active {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.sidebarFooter {
  padding: var(--space-4) var(--space-3);
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.themeToggle,
.logoutButton {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.themeToggle:hover,
.logoutButton:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text);
}

.main {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
}

.header {
  height: var(--header-height);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  background-color: var(--color-surface);
  position: sticky;
  top: 0;
  z-index: 50;
}

.headerRight {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.userName {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.content {
  flex: 1;
  padding: var(--space-6);
  background-color: var(--color-bg-secondary);
}

@media (max-width: 768px) {
  .sidebar { display: none; }
  .main { margin-left: 0; }
}
```

```jsx
// src/shared/layouts/AuthLayout.jsx
import { Outlet } from 'react-router-dom';
import styles from './AuthLayout.module.css';

export function AuthLayout() {
  return (
    <div className={styles.layout}>
      <div className={styles.container}>
        <Outlet />
      </div>
    </div>
  );
}
```

```css
/* src/shared/layouts/AuthLayout.module.css */
.layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-secondary);
  padding: var(--space-4);
}

.container {
  background-color: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  box-shadow: var(--shadow-md);
  width: 100%;
  max-width: 480px;
}
```

---

## Step 6: Projects Feature

```jsx
// src/features/projects/services/projectService.js
import { projectsApi } from '@shared/utils/mockApi';
import { authService } from '@features/auth/services/authService';

export const projectService = {
  async getAll() {
    return projectsApi.getAll(authService.getToken());
  },
  async getById(id) {
    return projectsApi.getById(authService.getToken(), id);
  },
  async create(data) {
    return projectsApi.create(authService.getToken(), data);
  },
  async update(id, data) {
    return projectsApi.update(authService.getToken(), id, data);
  },
  async delete(id) {
    return projectsApi.delete(authService.getToken(), id);
  },
};
```

```jsx
// src/features/projects/hooks/useProjects.js
import { useState, useEffect, useCallback } from 'react';
import { projectService } from '../services/projectService';

export function useProjects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProjects = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await projectService.getAll();
      setProjects(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const createProject = async (data) => {
    const newProject = await projectService.create(data);
    setProjects(prev => [...prev, newProject]);
    return newProject;
  };

  const deleteProject = async (id) => {
    await projectService.delete(id);
    setProjects(prev => prev.filter(p => p.id !== id));
  };

  return { projects, loading, error, createProject, deleteProject, refetch: fetchProjects };
}
```

```jsx
// src/features/projects/components/ProjectCard.jsx
import { Link } from 'react-router-dom';
import { Badge } from '@shared/components';
import styles from './ProjectCard.module.css';

export function ProjectCard({ project }) {
  const progress = project.taskCount > 0
    ? Math.round((project.completedCount / project.taskCount) * 100)
    : 0;

  return (
    <Link to={`/projects/${project.id}`} className={styles.card}>
      <div className={styles.header}>
        <div
          className={styles.colorDot}
          style={{ backgroundColor: project.color }}
          aria-hidden="true"
        />
        <h3 className={styles.name}>{project.name}</h3>
      </div>

      <p className={styles.description}>{project.description}</p>

      <div className={styles.stats}>
        <Badge variant={progress === 100 ? 'success' : 'default'}>
          {project.completedCount}/{project.taskCount} tasks
        </Badge>
      </div>

      <div className={styles.progressBar}>
        <div
          className={styles.progressFill}
          style={{ width: `${progress}%` }}
          role="progressbar"
          aria-valuenow={progress}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`${progress}% complete`}
        />
      </div>
    </Link>
  );
}
```

```css
/* src/features/projects/components/ProjectCard.module.css */
.card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  transition: all var(--transition-fast);
}

.card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.colorDot {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.name {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin: 0;
}

.description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.stats {
  display: flex;
  gap: var(--space-2);
}

.progressBar {
  height: 4px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progressFill {
  height: 100%;
  background-color: var(--color-primary);
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
}
```

```jsx
// src/features/projects/components/ProjectForm.jsx
import { useState } from 'react';
import { Button, Input } from '@shared/components';

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899'];

export function ProjectForm({ onSubmit, onCancel, initialData }) {
  const [formData, setFormData] = useState({
    name: initialData?.name || '',
    description: initialData?.description || '',
    color: initialData?.color || COLORS[0],
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setErrors(prev => ({ ...prev, [name]: '' }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = 'Project name is required';
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit(formData);
    } catch (err) {
      setErrors({ name: err.message });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      <Input label="Project Name" name="name" value={formData.name} onChange={handleChange} error={errors.name} placeholder="e.g. Website Redesign" />

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
        <label style={{ fontSize: 'var(--font-size-sm)', fontWeight: 500 }}>Description</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="What is this project about?"
          rows={3}
          style={{
            padding: 'var(--space-2) var(--space-3)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--color-bg)',
            fontSize: 'var(--font-size-sm)',
            resize: 'vertical',
          }}
        />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        <label style={{ fontSize: 'var(--font-size-sm)', fontWeight: 500 }}>Color</label>
        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          {COLORS.map(color => (
            <button
              key={color}
              type="button"
              onClick={() => setFormData(prev => ({ ...prev, color }))}
              aria-label={`Select color ${color}`}
              aria-pressed={formData.color === color}
              style={{
                width: 32,
                height: 32,
                borderRadius: 'var(--radius-full)',
                backgroundColor: color,
                border: formData.color === color ? '3px solid var(--color-text)' : '3px solid transparent',
                cursor: 'pointer',
              }}
            />
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', gap: 'var(--space-3)', justifyContent: 'flex-end' }}>
        <Button type="button" variant="secondary" onClick={onCancel}>Cancel</Button>
        <Button type="submit" loading={submitting}>
          {initialData ? 'Update Project' : 'Create Project'}
        </Button>
      </div>
    </form>
  );
}
```

```jsx
// src/features/projects/components/ProjectList.jsx
import { ProjectCard } from './ProjectCard';
import styles from './ProjectList.module.css';

export function ProjectList({ projects }) {
  return (
    <div className={styles.grid}>
      {projects.map(project => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </div>
  );
}
```

```css
/* src/features/projects/components/ProjectList.module.css */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-4);
}
```

```jsx
// src/features/projects/index.js
export { ProjectCard } from './components/ProjectCard';
export { ProjectList } from './components/ProjectList';
export { ProjectForm } from './components/ProjectForm';
export { useProjects } from './hooks/useProjects';
```

---

## Step 7: Task Board Feature

```jsx
// src/features/tasks/services/taskService.js
import { tasksApi } from '@shared/utils/mockApi';
import { authService } from '@features/auth/services/authService';

export const taskService = {
  async getByProject(projectId) {
    return tasksApi.getByProject(authService.getToken(), projectId);
  },
  async create(data) {
    return tasksApi.create(authService.getToken(), data);
  },
  async update(id, data) {
    return tasksApi.update(authService.getToken(), id, data);
  },
  async delete(id) {
    return tasksApi.delete(authService.getToken(), id);
  },
  async updateStatus(id, status) {
    return tasksApi.updateStatus(authService.getToken(), id, status);
  },
};
```

```jsx
// src/features/tasks/hooks/useTasks.js
import { useState, useEffect, useCallback } from 'react';
import { taskService } from '../services/taskService';

export function useTasks(projectId) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTasks = useCallback(async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await taskService.getByProject(projectId);
      setTasks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const createTask = async (data) => {
    const newTask = await taskService.create({ ...data, projectId });
    setTasks(prev => [...prev, newTask]);
    return newTask;
  };

  const updateTask = async (taskId, data) => {
    const updated = await taskService.update(taskId, data);
    setTasks(prev => prev.map(t => (t.id === taskId ? { ...t, ...updated } : t)));
    return updated;
  };

  const deleteTask = async (taskId) => {
    await taskService.delete(taskId);
    setTasks(prev => prev.filter(t => t.id !== taskId));
  };

  const moveTask = async (taskId, newStatus) => {
    // Optimistic update
    setTasks(prev =>
      prev.map(t => (t.id === taskId ? { ...t, status: newStatus } : t))
    );
    try {
      await taskService.updateStatus(taskId, newStatus);
    } catch (err) {
      // Revert on failure
      fetchTasks();
      throw err;
    }
  };

  const tasksByStatus = {
    todo: tasks.filter(t => t.status === 'todo'),
    'in-progress': tasks.filter(t => t.status === 'in-progress'),
    done: tasks.filter(t => t.status === 'done'),
  };

  return {
    tasks,
    tasksByStatus,
    loading,
    error,
    createTask,
    updateTask,
    deleteTask,
    moveTask,
    refetch: fetchTasks,
  };
}
```

```jsx
// src/features/tasks/components/TaskCard.jsx
import { Badge } from '@shared/components';
import { formatDate } from '@shared/utils/formatDate';
import styles from './TaskCard.module.css';

const PRIORITY_VARIANTS = {
  high: 'danger',
  medium: 'warning',
  low: 'default',
};

export function TaskCard({ task, onClick, onMove }) {
  function handleDragStart(e) {
    e.dataTransfer.setData('text/plain', task.id);
    e.dataTransfer.effectAllowed = 'move';
  }

  const isOverdue = task.dueDate && task.status !== 'done' &&
    new Date(task.dueDate) < new Date();

  return (
    <article
      className={styles.card}
      draggable
      onDragStart={handleDragStart}
      onClick={() => onClick?.(task)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.(task);
        }
      }}
      aria-label={`Task: ${task.title}. Priority: ${task.priority}. ${isOverdue ? 'Overdue.' : ''}`}
    >
      <div className={styles.header}>
        <Badge variant={PRIORITY_VARIANTS[task.priority]} size="small">
          {task.priority}
        </Badge>
        {isOverdue && (
          <Badge variant="danger" size="small">overdue</Badge>
        )}
      </div>

      <h4 className={styles.title}>{task.title}</h4>

      {task.description && (
        <p className={styles.description}>{task.description}</p>
      )}

      <div className={styles.footer}>
        {task.dueDate && (
          <span className={`${styles.dueDate} ${isOverdue ? styles.overdue : ''}`}>
            {formatDate(task.dueDate)}
          </span>
        )}
        {task.assignee && (
          <span className={styles.assignee}>{task.assignee.name}</span>
        )}
      </div>
    </article>
  );
}
```

```css
/* src/features/tasks/components/TaskCard.module.css */
.card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  cursor: grab;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  transition: all var(--transition-fast);
}

.card:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--color-primary);
}

.card:active {
  cursor: grabbing;
}

.card:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.header {
  display: flex;
  gap: var(--space-2);
}

.title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  margin: 0;
  color: var(--color-text);
}

.description {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.overdue {
  color: var(--color-danger);
  font-weight: 500;
}

.assignee {
  font-weight: 500;
}
```

```jsx
// src/features/tasks/components/TaskColumn.jsx
import { useState } from 'react';
import { TaskCard } from './TaskCard';
import styles from './TaskColumn.module.css';

const COLUMN_LABELS = {
  'todo': 'To Do',
  'in-progress': 'In Progress',
  'done': 'Done',
};

export function TaskColumn({ status, tasks, onMoveTask, onTaskClick }) {
  const [dragOver, setDragOver] = useState(false);

  function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOver(true);
  }

  function handleDragLeave() {
    setDragOver(false);
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragOver(false);
    const taskId = e.dataTransfer.getData('text/plain');
    if (taskId) {
      onMoveTask(taskId, status);
    }
  }

  return (
    <section
      className={`${styles.column} ${dragOver ? styles.dragOver : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      aria-label={`${COLUMN_LABELS[status]} column, ${tasks.length} tasks`}
    >
      <div className={styles.header}>
        <h3 className={styles.title}>{COLUMN_LABELS[status]}</h3>
        <span className={styles.count}>{tasks.length}</span>
      </div>

      <div className={styles.tasks}>
        {tasks.map(task => (
          <TaskCard key={task.id} task={task} onClick={onTaskClick} />
        ))}
      </div>
    </section>
  );
}
```

```css
/* src/features/tasks/components/TaskColumn.module.css */
.column {
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  min-height: 200px;
  transition: background-color var(--transition-fast);
}

.dragOver {
  background-color: var(--color-primary-light);
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-2) var(--space-3);
}

.title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  margin: 0;
  color: var(--color-text);
}

.count {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  background-color: var(--color-bg);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.tasks {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
```

```jsx
// src/features/tasks/components/TaskBoard.jsx
import { TaskColumn } from './TaskColumn';
import styles from './TaskBoard.module.css';

const COLUMNS = ['todo', 'in-progress', 'done'];

export function TaskBoard({ tasksByStatus, onMoveTask, onTaskClick }) {
  return (
    <div className={styles.board}>
      {COLUMNS.map(status => (
        <TaskColumn
          key={status}
          status={status}
          tasks={tasksByStatus[status] || []}
          onMoveTask={onMoveTask}
          onTaskClick={onTaskClick}
        />
      ))}
    </div>
  );
}
```

```css
/* src/features/tasks/components/TaskBoard.module.css */
.board {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  min-height: 400px;
}

@media (max-width: 768px) {
  .board {
    grid-template-columns: 1fr;
  }
}
```

```jsx
// src/features/tasks/components/TaskForm.jsx
import { useState } from 'react';
import { Button, Input } from '@shared/components';

export function TaskForm({ onSubmit, onCancel, initialData, members = [] }) {
  const [formData, setFormData] = useState({
    title: initialData?.title || '',
    description: initialData?.description || '',
    priority: initialData?.priority || 'medium',
    assigneeId: initialData?.assigneeId || '',
    dueDate: initialData?.dueDate?.split('T')[0] || '',
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setErrors(prev => ({ ...prev, [name]: '' }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!formData.title.trim()) {
      setErrors({ title: 'Title is required' });
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit({
        ...formData,
        dueDate: formData.dueDate ? new Date(formData.dueDate).toISOString() : null,
        assigneeId: formData.assigneeId || null,
      });
    } catch (err) {
      setErrors({ title: err.message });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      <Input label="Task Title" name="title" value={formData.title} onChange={handleChange} error={errors.title} placeholder="What needs to be done?" />

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
        <label htmlFor="task-description" style={{ fontSize: 'var(--font-size-sm)', fontWeight: 500 }}>Description</label>
        <textarea
          id="task-description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Add more details..."
          rows={3}
          style={{
            padding: 'var(--space-2) var(--space-3)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--color-bg)',
            fontSize: 'var(--font-size-sm)',
            resize: 'vertical',
          }}
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
          <label htmlFor="task-priority" style={{ fontSize: 'var(--font-size-sm)', fontWeight: 500 }}>Priority</label>
          <select
            id="task-priority"
            name="priority"
            value={formData.priority}
            onChange={handleChange}
            style={{
              padding: 'var(--space-2) var(--space-3)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--color-bg)',
              fontSize: 'var(--font-size-sm)',
            }}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <Input label="Due Date" name="dueDate" type="date" value={formData.dueDate} onChange={handleChange} />
      </div>

      {members.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
          <label htmlFor="task-assignee" style={{ fontSize: 'var(--font-size-sm)', fontWeight: 500 }}>Assign To</label>
          <select
            id="task-assignee"
            name="assigneeId"
            value={formData.assigneeId}
            onChange={handleChange}
            style={{
              padding: 'var(--space-2) var(--space-3)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--color-bg)',
              fontSize: 'var(--font-size-sm)',
            }}
          >
            <option value="">Unassigned</option>
            {members.map(member => (
              <option key={member.id} value={member.id}>{member.name}</option>
            ))}
          </select>
        </div>
      )}

      <div style={{ display: 'flex', gap: 'var(--space-3)', justifyContent: 'flex-end' }}>
        <Button type="button" variant="secondary" onClick={onCancel}>Cancel</Button>
        <Button type="submit" loading={submitting}>
          {initialData ? 'Update Task' : 'Create Task'}
        </Button>
      </div>
    </form>
  );
}
```

```jsx
// src/features/tasks/index.js
export { TaskBoard } from './components/TaskBoard';
export { TaskCard } from './components/TaskCard';
export { TaskForm } from './components/TaskForm';
export { useTasks } from './hooks/useTasks';
```

---

## Step 8: Dashboard and Search

```jsx
// src/features/dashboard/hooks/useDashboard.js
import { useState, useEffect } from 'react';
import { dashboardApi } from '@shared/utils/mockApi';
import { authService } from '@features/auth/services/authService';

export function useDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    dashboardApi
      .getStats(authService.getToken())
      .then(setStats)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return { stats, loading, error };
}
```

```jsx
// src/features/dashboard/components/DashboardStats.jsx
import styles from './DashboardStats.module.css';

export function DashboardStats({ stats }) {
  const cards = [
    { label: 'Total Projects', value: stats.totalProjects, color: 'var(--color-primary)' },
    { label: 'Total Tasks', value: stats.totalTasks, color: 'var(--color-text)' },
    { label: 'Completed', value: stats.completedTasks, color: 'var(--color-success)' },
    { label: 'In Progress', value: stats.inProgressTasks, color: 'var(--color-warning)' },
    { label: 'Overdue', value: stats.overdueTasks, color: 'var(--color-danger)' },
  ];

  return (
    <div className={styles.grid}>
      {cards.map(card => (
        <div key={card.label} className={styles.card}>
          <p className={styles.label}>{card.label}</p>
          <p className={styles.value} style={{ color: card.color }}>
            {card.value}
          </p>
        </div>
      ))}
    </div>
  );
}
```

```css
/* src/features/dashboard/components/DashboardStats.module.css */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-4);
}

.card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
}

.label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-1);
}

.value {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  margin: 0;
}
```

```jsx
// src/features/dashboard/index.js
export { DashboardStats } from './components/DashboardStats';
export { useDashboard } from './hooks/useDashboard';
```

```jsx
// src/features/search/hooks/useSearch.js
import { useState, useEffect } from 'react';
import { useDebounce } from '@shared/hooks/useDebounce';
import { searchApi } from '@shared/utils/mockApi';
import { authService } from '@features/auth/services/authService';

export function useSearch(query) {
  const [results, setResults] = useState({ projects: [], tasks: [] });
  const [loading, setLoading] = useState(false);
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (!debouncedQuery || debouncedQuery.length < 2) {
      setResults({ projects: [], tasks: [] });
      return;
    }

    setLoading(true);
    searchApi
      .search(authService.getToken(), debouncedQuery)
      .then(setResults)
      .catch(() => setResults({ projects: [], tasks: [] }))
      .finally(() => setLoading(false));
  }, [debouncedQuery]);

  const hasResults = results.projects.length > 0 || results.tasks.length > 0;

  return { results, loading, hasResults };
}
```

```jsx
// src/features/search/components/SearchBar.jsx
import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSearch } from '../hooks/useSearch';
import styles from './SearchBar.module.css';

export function SearchBar() {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const { results, loading, hasResults } = useSearch(query);
  const navigate = useNavigate();
  const containerRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  function handleSelect(type, id) {
    if (type === 'project') navigate(`/projects/${id}`);
    setQuery('');
    setIsOpen(false);
  }

  return (
    <div ref={containerRef} className={styles.container}>
      <input
        type="search"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setIsOpen(true);
        }}
        onFocus={() => setIsOpen(true)}
        placeholder="Search projects and tasks..."
        className={styles.input}
        aria-label="Search"
        aria-expanded={isOpen && query.length >= 2}
      />

      {isOpen && query.length >= 2 && (
        <div className={styles.dropdown} role="listbox">
          {loading && <p className={styles.status}>Searching...</p>}

          {!loading && !hasResults && (
            <p className={styles.status}>No results found</p>
          )}

          {results.projects.length > 0 && (
            <div>
              <p className={styles.groupLabel}>Projects</p>
              {results.projects.map(p => (
                <button
                  key={p.id}
                  className={styles.result}
                  onClick={() => handleSelect('project', p.id)}
                  role="option"
                >
                  <span
                    className={styles.dot}
                    style={{ backgroundColor: p.color }}
                  />
                  {p.name}
                </button>
              ))}
            </div>
          )}

          {results.tasks.length > 0 && (
            <div>
              <p className={styles.groupLabel}>Tasks</p>
              {results.tasks.map(t => (
                <button
                  key={t.id}
                  className={styles.result}
                  onClick={() => handleSelect('project', t.projectId)}
                  role="option"
                >
                  {t.title}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

```css
/* src/features/search/components/SearchBar.module.css */
.container {
  position: relative;
  width: 320px;
}

.input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-bg-secondary);
  font-size: var(--font-size-sm);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  background-color: var(--color-bg);
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: var(--space-1);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  max-height: 360px;
  overflow-y: auto;
  z-index: 200;
}

.status {
  padding: var(--space-3) var(--space-4);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  margin: 0;
}

.groupLabel {
  padding: var(--space-2) var(--space-4);
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.result {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-2) var(--space-4);
  text-align: left;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  transition: background-color var(--transition-fast);
}

.result:hover {
  background-color: var(--color-bg-tertiary);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}
```

```jsx
// src/features/search/index.js
export { SearchBar } from './components/SearchBar';
export { useSearch } from './hooks/useSearch';
```

---

## Step 9: Pages

```jsx
// src/pages/LoginPage.jsx
import { useNavigate, useLocation } from 'react-router-dom';
import { LoginForm } from '@features/auth';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/';

  return <LoginForm onSuccess={() => navigate(from, { replace: true })} />;
}
```

```jsx
// src/pages/RegisterPage.jsx
import { useNavigate } from 'react-router-dom';
import { RegisterForm } from '@features/auth';

export default function RegisterPage() {
  const navigate = useNavigate();
  return <RegisterForm onSuccess={() => navigate('/')} />;
}
```

```jsx
// src/pages/DashboardPage.jsx
import { DashboardStats, useDashboard } from '@features/dashboard';
import { Spinner } from '@shared/components';

export default function DashboardPage() {
  const { stats, loading, error } = useDashboard();

  if (loading) return <Spinner size="large" />;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h2 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: 'var(--space-6)' }}>
        Dashboard
      </h2>
      <DashboardStats stats={stats} />
    </div>
  );
}
```

```jsx
// src/pages/ProjectsPage.jsx
import { useState } from 'react';
import { useProjects, ProjectList, ProjectForm } from '@features/projects';
import { Button, Spinner, EmptyState, Modal } from '@shared/components';
import { useNotification } from '@shared/context/NotificationContext';

export default function ProjectsPage() {
  const { projects, loading, error, createProject } = useProjects();
  const [showForm, setShowForm] = useState(false);
  const notify = useNotification();

  async function handleCreate(data) {
    await createProject(data);
    setShowForm(false);
    notify.success('Project created successfully!');
  }

  if (loading) return <Spinner size="large" />;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 'var(--space-6)',
      }}>
        <h2 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, margin: 0 }}>
          Projects
        </h2>
        <Button onClick={() => setShowForm(true)}>+ New Project</Button>
      </div>

      {projects.length === 0 ? (
        <EmptyState
          title="No projects yet"
          description="Create your first project to get started."
          action={<Button onClick={() => setShowForm(true)}>Create Project</Button>}
        />
      ) : (
        <ProjectList projects={projects} />
      )}

      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="New Project">
        <ProjectForm onSubmit={handleCreate} onCancel={() => setShowForm(false)} />
      </Modal>
    </div>
  );
}
```

```jsx
// src/pages/ProjectDetailPage.jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { TaskBoard, TaskForm, useTasks } from '@features/tasks';
import { projectService } from '@features/projects/services/projectService';
import { Button, Spinner, Modal } from '@shared/components';
import { useNotification } from '@shared/context/NotificationContext';

export default function ProjectDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const notify = useNotification();
  const [project, setProject] = useState(null);
  const [projectLoading, setProjectLoading] = useState(true);
  const { tasksByStatus, loading: tasksLoading, createTask, moveTask, deleteTask } = useTasks(id);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);

  useEffect(() => {
    projectService
      .getById(id)
      .then(setProject)
      .catch(() => navigate('/projects'))
      .finally(() => setProjectLoading(false));
  }, [id, navigate]);

  async function handleCreateTask(data) {
    await createTask(data);
    setShowTaskForm(false);
    notify.success('Task created!');
  }

  async function handleMoveTask(taskId, newStatus) {
    try {
      await moveTask(taskId, newStatus);
      notify.success('Task moved!');
    } catch {
      notify.error('Failed to move task');
    }
  }

  function handleTaskClick(task) {
    setSelectedTask(task);
  }

  async function handleDeleteTask() {
    if (selectedTask) {
      await deleteTask(selectedTask.id);
      setSelectedTask(null);
      notify.success('Task deleted');
    }
  }

  if (projectLoading || tasksLoading) return <Spinner size="large" />;
  if (!project) return null;

  return (
    <div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 'var(--space-6)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <div style={{
            width: 16, height: 16,
            borderRadius: 'var(--radius-full)',
            backgroundColor: project.color,
          }} />
          <h2 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, margin: 0 }}>
            {project.name}
          </h2>
        </div>
        <Button onClick={() => setShowTaskForm(true)}>+ Add Task</Button>
      </div>

      {project.description && (
        <p style={{
          color: 'var(--color-text-secondary)',
          marginBottom: 'var(--space-6)',
          fontSize: 'var(--font-size-sm)',
        }}>
          {project.description}
        </p>
      )}

      <TaskBoard
        tasksByStatus={tasksByStatus}
        onMoveTask={handleMoveTask}
        onTaskClick={handleTaskClick}
      />

      <Modal isOpen={showTaskForm} onClose={() => setShowTaskForm(false)} title="New Task">
        <TaskForm
          onSubmit={handleCreateTask}
          onCancel={() => setShowTaskForm(false)}
          members={project.members}
        />
      </Modal>

      <Modal isOpen={!!selectedTask} onClose={() => setSelectedTask(null)} title="Task Details">
        {selectedTask && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <h3 style={{ margin: 0 }}>{selectedTask.title}</h3>
            {selectedTask.description && <p style={{ color: 'var(--color-text-secondary)', margin: 0 }}>{selectedTask.description}</p>}
            <div style={{ display: 'flex', gap: 'var(--space-2)', fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
              <span>Priority: <strong>{selectedTask.priority}</strong></span>
              <span>Status: <strong>{selectedTask.status}</strong></span>
            </div>
            {selectedTask.assignee && (
              <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', margin: 0 }}>
                Assigned to: <strong>{selectedTask.assignee.name}</strong>
              </p>
            )}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)' }}>
              <Button variant="danger" size="small" onClick={handleDeleteTask}>Delete Task</Button>
              <Button variant="secondary" size="small" onClick={() => setSelectedTask(null)}>Close</Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
```

```jsx
// src/pages/ProfilePage.jsx
import { useState } from 'react';
import { useAuth } from '@features/auth';
import { Button, Input } from '@shared/components';
import { useNotification } from '@shared/context/NotificationContext';
import { useTheme } from '@shared/context/ThemeContext';

export default function ProfilePage() {
  const { user, updateProfile } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const notify = useNotification();
  const [name, setName] = useState(user?.name || '');
  const [saving, setSaving] = useState(false);

  async function handleSave(e) {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    try {
      await updateProfile({ name });
      notify.success('Profile updated!');
    } catch (err) {
      notify.error(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={{ maxWidth: 560 }}>
      <h2 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: 'var(--space-6)' }}>
        Profile
      </h2>

      <div style={{
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        padding: 'var(--space-6)',
        marginBottom: 'var(--space-6)',
      }}>
        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} />
          <Input label="Email" value={user?.email || ''} disabled helperText="Email cannot be changed" />
          <Button type="submit" loading={saving}>Save Changes</Button>
        </form>
      </div>

      <div style={{
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        padding: 'var(--space-6)',
      }}>
        <h3 style={{ margin: '0 0 var(--space-4)', fontSize: 'var(--font-size-lg)' }}>Preferences</h3>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <p style={{ margin: 0, fontWeight: 500, fontSize: 'var(--font-size-sm)' }}>Dark Mode</p>
            <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-xs)' }}>
              Toggle between light and dark themes
            </p>
          </div>
          <Button variant="secondary" size="small" onClick={toggleTheme}>
            {theme === 'light' ? 'Enable' : 'Disable'}
          </Button>
        </div>
      </div>
    </div>
  );
}
```

```jsx
// src/pages/NotFoundPage.jsx
import { Link } from 'react-router-dom';
import { Button } from '@shared/components';

export default function NotFoundPage() {
  return (
    <div style={{ textAlign: 'center', padding: 'var(--space-12)' }}>
      <h1 style={{ fontSize: 'var(--font-size-3xl)', marginBottom: 'var(--space-4)' }}>404</h1>
      <p style={{ color: 'var(--color-text-secondary)', marginBottom: 'var(--space-6)' }}>
        The page you are looking for does not exist.
      </p>
      <Link to="/"><Button>Go to Dashboard</Button></Link>
    </div>
  );
}
```

---

## Step 10: App Shell and Routing

```jsx
// src/app/routes.jsx
import { Routes, Route } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { ProtectedRoute } from '@features/auth';
import { AppLayout } from '@shared/layouts/AppLayout';
import { AuthLayout } from '@shared/layouts/AuthLayout';
import { Spinner } from '@shared/components';

const LoginPage = lazy(() => import('@pages/LoginPage'));
const RegisterPage = lazy(() => import('@pages/RegisterPage'));
const DashboardPage = lazy(() => import('@pages/DashboardPage'));
const ProjectsPage = lazy(() => import('@pages/ProjectsPage'));
const ProjectDetailPage = lazy(() => import('@pages/ProjectDetailPage'));
const ProfilePage = lazy(() => import('@pages/ProfilePage'));
const NotFoundPage = lazy(() => import('@pages/NotFoundPage'));

export function AppRoutes() {
  return (
    <Suspense fallback={<Spinner size="large" />}>
      <Routes>
        {/* Public routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>

        {/* Protected routes */}
        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/projects/:id" element={<ProjectDetailPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  );
}
```

```jsx
// src/app/AppProviders.jsx
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '@features/auth';
import { ThemeProvider } from '@shared/context/ThemeContext';
import { NotificationProvider } from '@shared/context/NotificationContext';

export function AppProviders({ children }) {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <NotificationProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </NotificationProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}
```

```jsx
// src/app/App.jsx
import { AppProviders } from './AppProviders';
import { AppRoutes } from './routes';

export default function App() {
  return (
    <AppProviders>
      <AppRoutes />
    </AppProviders>
  );
}
```

```jsx
// src/main.jsx
import './assets/styles/reset.css';
import './assets/styles/variables.css';
import './assets/styles/global.css';

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './app/App';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

---

## What This Project Demonstrates

Let us step back and see what skills this project covers:

| Skill | Where It Appears |
|-------|-----------------|
| Component architecture | Feature-based structure with barrel exports |
| Authentication | AuthContext, ProtectedRoute, login/register forms |
| State management | Custom hooks (useProjects, useTasks, useDashboard) |
| CRUD operations | Projects and tasks create, read, update, delete |
| Optimistic updates | Task drag-and-drop with rollback on failure |
| Form handling | Validated forms with error states |
| Routing | Nested routes, layouts, lazy loading, 404 |
| Context API | Auth, Theme, Notifications — each at appropriate scope |
| Code splitting | React.lazy for all page components |
| Responsive design | CSS variables, media queries, flexible grid |
| Dark mode | CSS variables with data-theme attribute |
| Drag and drop | HTML5 drag-and-drop API for task board |
| Search | Debounced search with dropdown results |
| Accessibility | ARIA attributes, semantic HTML, keyboard support, focus management |
| Error handling | Error states in all data-fetching hooks |
| Notifications | Toast notifications for user feedback |
| Service layer | Clean separation of API calls |
| Path aliases | @features, @shared, @pages imports |

---

## Extending the Project

Once you have the base application working, here are features you can add to deepen your skills:

### Feature Ideas

1. **Task comments** — add a comment thread to each task
2. **File attachments** — upload and display files on tasks
3. **Due date reminders** — highlight tasks due within 24 hours
4. **Activity feed** — show recent changes with user avatars and timestamps
5. **Keyboard shortcuts** — press `N` to create a new task, `Escape` to close modals
6. **Bulk actions** — select multiple tasks and move or delete them
7. **Task filters** — filter by priority, assignee, or due date
8. **Export** — export project tasks as CSV
9. **Undo** — add undo functionality for delete actions
10. **Real-time collaboration** — simulate real-time updates with setInterval

### Technical Improvements

1. **Add tests** — write tests for hooks, components, and user flows
2. **Error boundaries** — add boundaries around each page and board section
3. **Skeleton loading** — replace spinners with skeleton UI placeholders
4. **Offline support** — detect offline status and queue changes
5. **Animations** — add transitions for task movement and modal opening
6. **PWA support** — add service worker and manifest for installability
7. **Replace mock API** — connect to a real backend (Firebase, Supabase, or your own)

---

## Summary

Building a real-world project is the best way to cement your React knowledge. TaskFlow combines nearly every concept from this book into a single, cohesive application: components, hooks, state management, routing, authentication, forms, accessibility, performance optimization, and clean architecture.

The key takeaways from this project:

**Architecture matters.** The feature-based structure kept our code organized even as the project grew. Every feature is self-contained with its own components, hooks, and services.

**Separation of concerns works.** Services handle API communication. Hooks manage state and logic. Components handle rendering. Pages compose features together. Each layer has a clear responsibility.

**Start simple, then iterate.** We began with basic components and added features progressively. The mock API layer let us build the entire frontend without waiting for a backend.

**User experience is in the details.** Toast notifications, loading states, error messages, optimistic updates, and keyboard support — these details separate a good application from a great one.

This project is yours now. Extend it, break it, rebuild it. Every bug you fix and feature you add teaches you something new. Put it on GitHub, deploy it to Vercel, and show it in interviews. It demonstrates not just that you know React, but that you can build real things with it.

---

## What Is Next?

Congratulations! You have completed the core chapters of this book. The final section is a **Glossary of React Terms** — a quick reference of every important concept, function, and pattern covered throughout the book. Use it whenever you need a fast refresher on a specific topic.
