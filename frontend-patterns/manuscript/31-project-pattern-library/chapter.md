# Chapter 31: Project Pattern Library -- A Complete React Application

## What You Will Learn

- How to combine 10+ design patterns in a single, cohesive React application
- How each pattern solves a specific problem in a real project
- The architecture of a production-quality React application
- How patterns interact and complement each other
- A full codebase walkthrough with explanations

## Why This Chapter Matters

Throughout this book, you have learned patterns one at a time. Each chapter focused on a single pattern in isolation. But real applications do not use just one pattern. They use many patterns working together, each solving a different problem.

This chapter is the capstone. We build a complete **Task Management Application** (like a simplified Jira or Trello) that uses patterns from across the book. You will see how patterns compose, where they fit in the architecture, and how they solve real problems you will face in production.

Think of the previous chapters as learning individual musical instruments. This chapter is the orchestra concert where all the instruments play together.

---

## Application Overview

We are building **TaskFlow**, a task management application with these features:

- Create, edit, and delete tasks
- Organize tasks into boards (To Do, In Progress, Done)
- Filter and search tasks
- User notifications
- Theme switching (light/dark)
- Error recovery
- Performance optimization for large task lists

### Architecture Diagram

```
+------------------------------------------------------------------+
|                     TaskFlow Application                         |
+------------------------------------------------------------------+
|                                                                  |
|  Patterns Used:                                                  |
|  1.  Module Pattern          - API service organization          |
|  2.  Factory Pattern         - Task and notification creation    |
|  3.  Observer Pattern        - Event system for notifications    |
|  4.  Compound Components     - Board and Column components       |
|  5.  Provider Pattern        - Theme and Auth context            |
|  6.  Custom Hooks            - Reusable stateful logic           |
|  7.  State Machine           - Task status transitions           |
|  8.  Memoization             - Optimized list rendering          |
|  9.  Error Boundary          - Graceful error handling           |
|  10. Code Splitting          - Lazy-loaded routes                |
|  11. Controlled Components   - Form handling                     |
|  12. Container/Presentational- Data/UI separation                |
|                                                                  |
+------------------------------------------------------------------+

Component Tree:
+------------------------------------------------------------------+
|  <ErrorBoundary>                          [Error Boundary Pattern]|
|    <ThemeProvider>                         [Provider Pattern]     |
|      <AuthProvider>                        [Provider Pattern]     |
|        <NotificationProvider>              [Observer Pattern]     |
|          <AppShell>                                               |
|            <Suspense>                      [Code Splitting]      |
|              <Routes>                                             |
|                <BoardPage>                                        |
|                  <Board>                   [Compound Components]  |
|                    <Board.Column>                                 |
|                      <TaskList>            [Memoization]          |
|                        <TaskCard>          [State Machine]        |
|                <TaskFormPage>              [Controlled Components]|
|                <SettingsPage>              [Code Splitting]       |
|              </Routes>                                            |
|            </Suspense>                                            |
|          </AppShell>                                              |
|        </NotificationProvider>                                    |
|      </AuthProvider>                                              |
|    </ThemeProvider>                                                |
|  </ErrorBoundary>                                                 |
+------------------------------------------------------------------+
```

---

## Pattern 1: Module Pattern -- API Service

The Module Pattern organizes our API layer into clean, self-contained modules with clear public interfaces.

```jsx
// src/services/taskService.js
// MODULE PATTERN: Encapsulates API logic behind a clean interface

const API_BASE = '/api';

// Private helper (not exported)
async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

// Public interface
export const taskService = {
  getAll() {
    return request('/tasks');
  },

  getById(id) {
    return request(`/tasks/${id}`);
  },

  create(taskData) {
    return request('/tasks', {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  },

  update(id, updates) {
    return request(`/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  },

  delete(id) {
    return request(`/tasks/${id}`, {
      method: 'DELETE',
    });
  },

  search(query) {
    return request(`/tasks/search?q=${encodeURIComponent(query)}`);
  },
};

// Usage elsewhere:
// import { taskService } from './services/taskService';
// const tasks = await taskService.getAll();
// const newTask = await taskService.create({ title: 'Fix bug' });
```

---

## Pattern 2: Factory Pattern -- Creating Tasks and Notifications

The Factory Pattern creates objects with consistent structure without exposing the creation logic.

```jsx
// src/factories/taskFactory.js
// FACTORY PATTERN: Creates task objects with proper defaults and validation

let nextId = 1;

export function createTask({
  title,
  description = '',
  priority = 'medium',
  assignee = null,
  status = 'todo',
}) {
  // Validation
  if (!title || title.trim().length === 0) {
    throw new Error('Task title is required');
  }

  const validPriorities = ['low', 'medium', 'high', 'urgent'];
  if (!validPriorities.includes(priority)) {
    throw new Error(`Invalid priority: ${priority}`);
  }

  const validStatuses = ['todo', 'in_progress', 'in_review', 'done'];
  if (!validStatuses.includes(status)) {
    throw new Error(`Invalid status: ${status}`);
  }

  return {
    id: `task-${nextId++}`,
    title: title.trim(),
    description: description.trim(),
    priority,
    assignee,
    status,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
}

// src/factories/notificationFactory.js
// FACTORY PATTERN: Creates notification objects

let notifId = 1;

export function createNotification(type, message, options = {}) {
  const defaults = {
    info: { icon: 'info', duration: 3000, color: 'blue' },
    success: { icon: 'check', duration: 2000, color: 'green' },
    warning: { icon: 'alert', duration: 5000, color: 'yellow' },
    error: { icon: 'error', duration: 0, color: 'red' }, // 0 = no auto-dismiss
  };

  const config = defaults[type] || defaults.info;

  return {
    id: `notif-${notifId++}`,
    type,
    message,
    icon: options.icon || config.icon,
    duration: options.duration ?? config.duration,
    color: config.color,
    createdAt: Date.now(),
  };
}

// Usage:
// const task = createTask({ title: 'Implement login', priority: 'high' });
// const notif = createNotification('success', 'Task created!');
```

---

## Pattern 3: Observer Pattern -- Event System

The Observer Pattern provides a publish/subscribe system for cross-component communication.

```jsx
// src/events/eventBus.js
// OBSERVER PATTERN: Decoupled communication between components

class EventBus {
  constructor() {
    this.listeners = new Map();
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);

    // Return unsubscribe function
    return () => {
      this.listeners.get(event)?.delete(callback);
    };
  }

  emit(event, data) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(cb => cb(data));
    }
  }

  off(event, callback) {
    this.listeners.get(event)?.delete(callback);
  }
}

export const eventBus = new EventBus();

// Event constants for type safety
export const EVENTS = {
  TASK_CREATED: 'task:created',
  TASK_UPDATED: 'task:updated',
  TASK_DELETED: 'task:deleted',
  TASK_MOVED: 'task:moved',
  NOTIFICATION: 'notification',
};

// Usage in components:
// eventBus.emit(EVENTS.TASK_CREATED, { task });
// const unsub = eventBus.on(EVENTS.TASK_CREATED, (data) => { ... });
// unsub(); // cleanup
```

---

## Pattern 4: Compound Components -- Board Layout

The Compound Components Pattern creates a flexible board with columns that share implicit state.

```jsx
// src/components/Board/Board.jsx
// COMPOUND COMPONENTS PATTERN: Board and Column share context

import { createContext, useContext, useMemo } from 'react';

const BoardContext = createContext(null);

function Board({ children, onTaskMove }) {
  const contextValue = useMemo(
    () => ({ onTaskMove }),
    [onTaskMove]
  );

  return (
    <BoardContext.Provider value={contextValue}>
      <div className="board">
        {children}
      </div>
    </BoardContext.Provider>
  );
}

function Column({ status, title, children }) {
  const { onTaskMove } = useContext(BoardContext);

  function handleDrop(e) {
    e.preventDefault();
    const taskId = e.dataTransfer.getData('taskId');
    onTaskMove(taskId, status);
  }

  function handleDragOver(e) {
    e.preventDefault();
  }

  return (
    <div
      className="board-column"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      <h2 className="column-header">{title}</h2>
      <div className="column-content">
        {children}
      </div>
    </div>
  );
}

// Attach sub-components
Board.Column = Column;

export default Board;

// Usage:
// <Board onTaskMove={handleTaskMove}>
//   <Board.Column status="todo" title="To Do">
//     {todoTasks.map(t => <TaskCard key={t.id} task={t} />)}
//   </Board.Column>
//   <Board.Column status="in_progress" title="In Progress">
//     {inProgressTasks.map(t => <TaskCard key={t.id} task={t} />)}
//   </Board.Column>
//   <Board.Column status="done" title="Done">
//     {doneTasks.map(t => <TaskCard key={t.id} task={t} />)}
//   </Board.Column>
// </Board>
```

---

## Pattern 5: Provider Pattern -- Theme and Auth

The Provider Pattern makes values available to any component in the tree without prop drilling.

```jsx
// src/providers/ThemeProvider.jsx
// PROVIDER PATTERN: Theme context available app-wide

import { createContext, useContext, useState, useMemo } from 'react';

const ThemeContext = createContext(null);

const themes = {
  light: {
    background: '#ffffff',
    surface: '#f5f5f5',
    text: '#1a1a1a',
    primary: '#3b82f6',
    border: '#e5e7eb',
  },
  dark: {
    background: '#1a1a2e',
    surface: '#16213e',
    text: '#e0e0e0',
    primary: '#60a5fa',
    border: '#374151',
  },
};

export function ThemeProvider({ children }) {
  const [themeName, setThemeName] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });

  const value = useMemo(() => ({
    theme: themes[themeName],
    themeName,
    toggleTheme: () => {
      setThemeName(prev => {
        const next = prev === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', next);
        return next;
      });
    },
  }), [themeName]);

  return (
    <ThemeContext.Provider value={value}>
      <div style={{
        backgroundColor: value.theme.background,
        color: value.theme.text,
        minHeight: '100vh',
      }}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

// src/providers/AuthProvider.jsx
// PROVIDER PATTERN: Auth state available app-wide

import { createContext, useContext, useState, useMemo, useCallback } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  const login = useCallback(async (email, password) => {
    setLoading(true);
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const userData = await response.json();
      setUser(userData);
      return userData;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem('token');
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, logout, isAuthenticated: !!user }),
    [user, loading, login, logout]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

---

## Pattern 6: Custom Hooks -- Reusable Logic

Custom Hooks extract and share stateful logic across components.

```jsx
// src/hooks/useTasks.js
// CUSTOM HOOKS PATTERN: Reusable data fetching and task management logic

import { useState, useEffect, useCallback } from 'react';
import { taskService } from '../services/taskService';
import { eventBus, EVENTS } from '../events/eventBus';
import { createNotification } from '../factories/notificationFactory';

export function useTasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch all tasks
  useEffect(() => {
    let cancelled = false;

    async function fetchTasks() {
      try {
        setLoading(true);
        const data = await taskService.getAll();
        if (!cancelled) {
          setTasks(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchTasks();
    return () => { cancelled = true; };
  }, []);

  const addTask = useCallback(async (taskData) => {
    const newTask = await taskService.create(taskData);
    setTasks(prev => [...prev, newTask]);
    eventBus.emit(EVENTS.TASK_CREATED, { task: newTask });
    eventBus.emit(EVENTS.NOTIFICATION,
      createNotification('success', `Task "${newTask.title}" created`)
    );
    return newTask;
  }, []);

  const updateTask = useCallback(async (id, updates) => {
    const updated = await taskService.update(id, updates);
    setTasks(prev => prev.map(t => (t.id === id ? updated : t)));
    eventBus.emit(EVENTS.TASK_UPDATED, { task: updated });
    return updated;
  }, []);

  const deleteTask = useCallback(async (id) => {
    await taskService.delete(id);
    setTasks(prev => prev.filter(t => t.id !== id));
    eventBus.emit(EVENTS.TASK_DELETED, { taskId: id });
    eventBus.emit(EVENTS.NOTIFICATION,
      createNotification('info', 'Task deleted')
    );
  }, []);

  const moveTask = useCallback(async (taskId, newStatus) => {
    const updated = await taskService.update(taskId, { status: newStatus });
    setTasks(prev => prev.map(t => (t.id === taskId ? updated : t)));
    eventBus.emit(EVENTS.TASK_MOVED, { task: updated, newStatus });
  }, []);

  return { tasks, loading, error, addTask, updateTask, deleteTask, moveTask };
}

// src/hooks/useSearch.js
// CUSTOM HOOKS PATTERN: Debounced search logic

import { useState, useEffect, useRef } from 'react';

export function useSearch(items, searchFields, delay = 300) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(items);
  const timeoutRef = useRef(null);

  useEffect(() => {
    if (!query.trim()) {
      setResults(items);
      return;
    }

    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      const lowerQuery = query.toLowerCase();
      const filtered = items.filter(item =>
        searchFields.some(field =>
          String(item[field]).toLowerCase().includes(lowerQuery)
        )
      );
      setResults(filtered);
    }, delay);

    return () => clearTimeout(timeoutRef.current);
  }, [query, items, searchFields, delay]);

  return { query, setQuery, results };
}

// src/hooks/useNotifications.js
// CUSTOM HOOKS PATTERN: Notification management with Observer

import { useState, useEffect, useCallback } from 'react';
import { eventBus, EVENTS } from '../events/eventBus';

export function useNotifications() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const unsub = eventBus.on(EVENTS.NOTIFICATION, (notification) => {
      setNotifications(prev => [...prev, notification]);

      // Auto-dismiss if duration > 0
      if (notification.duration > 0) {
        setTimeout(() => {
          setNotifications(prev =>
            prev.filter(n => n.id !== notification.id)
          );
        }, notification.duration);
      }
    });

    return unsub;
  }, []);

  const dismiss = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  return { notifications, dismiss };
}
```

---

## Pattern 7: State Machine -- Task Status Transitions

The State Machine Pattern ensures tasks can only transition through valid statuses.

```jsx
// src/stateMachines/taskStatusMachine.js
// STATE MACHINE PATTERN: Valid task status transitions

const taskStatusMachine = {
  todo: {
    START_WORK: 'in_progress',
  },
  in_progress: {
    SUBMIT_REVIEW: 'in_review',
    MOVE_BACK: 'todo',
  },
  in_review: {
    APPROVE: 'done',
    REQUEST_CHANGES: 'in_progress',
  },
  done: {
    REOPEN: 'todo',
  },
};

export function getNextStatus(currentStatus, action) {
  const transitions = taskStatusMachine[currentStatus];
  if (!transitions) {
    throw new Error(`Unknown status: ${currentStatus}`);
  }

  const nextStatus = transitions[action];
  if (!nextStatus) {
    throw new Error(
      `Invalid action "${action}" for status "${currentStatus}". ` +
      `Valid actions: ${Object.keys(transitions).join(', ')}`
    );
  }

  return nextStatus;
}

export function getAvailableActions(currentStatus) {
  const transitions = taskStatusMachine[currentStatus];
  if (!transitions) return [];

  return Object.entries(transitions).map(([action, targetStatus]) => ({
    action,
    targetStatus,
    label: formatActionLabel(action),
  }));
}

function formatActionLabel(action) {
  const labels = {
    START_WORK: 'Start Working',
    SUBMIT_REVIEW: 'Submit for Review',
    MOVE_BACK: 'Move Back to To Do',
    APPROVE: 'Approve',
    REQUEST_CHANGES: 'Request Changes',
    REOPEN: 'Reopen',
  };
  return labels[action] || action;
}

// Visualization of the state machine:
//
//   +--------+    START_WORK    +--------------+
//   |  todo  | --------------> | in_progress  |
//   +--------+                 +--------------+
//       ^                        |          ^
//       |  REOPEN      SUBMIT_   |          | REQUEST_
//       |              REVIEW    v          | CHANGES
//   +--------+               +-----------+
//   |  done  | <------------ | in_review |
//   +--------+    APPROVE    +-----------+
```

```jsx
// src/components/TaskCard/TaskActions.jsx
// Using the state machine in a component

import { getAvailableActions, getNextStatus } from '../../stateMachines/taskStatusMachine';

function TaskActions({ task, onStatusChange }) {
  const availableActions = getAvailableActions(task.status);

  function handleAction(action) {
    const newStatus = getNextStatus(task.status, action);
    onStatusChange(task.id, newStatus);
  }

  return (
    <div className="task-actions">
      {availableActions.map(({ action, label }) => (
        <button
          key={action}
          onClick={() => handleAction(action)}
          className="action-button"
        >
          {label}
        </button>
      ))}
    </div>
  );
}

export default TaskActions;

// Output for a task with status "in_progress":
// [Submit for Review]  [Move Back to To Do]
//
// Output for a task with status "in_review":
// [Approve]  [Request Changes]
//
// There is NO way to go directly from "todo" to "done"!
// The state machine enforces the workflow.
```

---

## Pattern 8: Memoization -- Optimized Rendering

The Memoization Pattern prevents unnecessary re-renders in the task list.

```jsx
// src/components/TaskList/TaskList.jsx
// MEMOIZATION PATTERN: Optimized list rendering

import React, { useMemo, useCallback, memo } from 'react';
import TaskCard from '../TaskCard/TaskCard';

const MemoizedTaskCard = memo(TaskCard);

function TaskList({ tasks, status, onStatusChange, onDelete }) {
  // Memoize filtered tasks - recalculates only when tasks or status change
  const filteredTasks = useMemo(
    () => tasks.filter(t => t.status === status),
    [tasks, status]
  );

  // Stable callback references for memoized children
  const handleStatusChange = useCallback(
    (taskId, newStatus) => onStatusChange(taskId, newStatus),
    [onStatusChange]
  );

  const handleDelete = useCallback(
    (taskId) => onDelete(taskId),
    [onDelete]
  );

  if (filteredTasks.length === 0) {
    return (
      <div className="empty-list">
        <p>No tasks here yet.</p>
      </div>
    );
  }

  return (
    <div className="task-list">
      {filteredTasks.map(task => (
        <MemoizedTaskCard
          key={task.id}
          task={task}
          onStatusChange={handleStatusChange}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
}

export default memo(TaskList);

// Why memoization matters here:
// - When user types in the search box, App re-renders
// - Without memo, ALL TaskCards re-render (even if tasks have not changed)
// - With memo, only the TaskList that actually changed re-renders
// - With 100+ tasks, this prevents 100+ unnecessary re-renders per keystroke
```

---

## Pattern 9: Error Boundary -- Graceful Failures

The Error Boundary Pattern prevents one broken component from crashing the entire app.

```jsx
// src/components/ErrorBoundary/AppErrorBoundary.jsx
// ERROR BOUNDARY PATTERN: Layered error handling

import { ErrorBoundary } from 'react-error-boundary';

function AppErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div className="app-error" role="alert">
      <h1>Application Error</h1>
      <p>Something unexpected happened. We are working on fixing it.</p>
      <div className="error-actions">
        <button onClick={resetErrorBoundary}>Try Again</button>
        <button onClick={() => window.location.reload()}>
          Reload Page
        </button>
      </div>
    </div>
  );
}

function BoardErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div className="board-error" role="alert">
      <p>Could not load this board section.</p>
      <button onClick={resetErrorBoundary}>Retry</button>
    </div>
  );
}

// Usage in the app:
function App() {
  return (
    // App-level boundary (last resort)
    <ErrorBoundary FallbackComponent={AppErrorFallback}>
      <ThemeProvider>
        <AuthProvider>
          <AppShell>
            {/* Board-level boundaries (granular) */}
            <ErrorBoundary FallbackComponent={BoardErrorFallback}>
              <BoardPage />
            </ErrorBoundary>
          </AppShell>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
```

---

## Pattern 10: Code Splitting -- Lazy Routes

The Code Splitting Pattern loads page-level components only when navigated to.

```jsx
// src/App.jsx
// CODE SPLITTING PATTERN: Lazy-loaded routes

import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import { ThemeProvider } from './providers/ThemeProvider';
import { AuthProvider } from './providers/AuthProvider';
import AppShell from './components/AppShell/AppShell';
import LoadingPage from './components/Loading/LoadingPage';

// Lazy load page components
const BoardPage = lazy(() => import('./pages/BoardPage'));
const TaskFormPage = lazy(() => import('./pages/TaskFormPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));

function AppErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div className="app-error" role="alert">
      <h1>Something went wrong</h1>
      <button onClick={resetErrorBoundary}>Try Again</button>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary FallbackComponent={AppErrorFallback}>
      <ThemeProvider>
        <AuthProvider>
          <BrowserRouter>
            <AppShell>
              <Suspense fallback={<LoadingPage />}>
                <Routes>
                  <Route path="/" element={<BoardPage />} />
                  <Route path="/tasks/new" element={<TaskFormPage />} />
                  <Route path="/tasks/:id/edit" element={<TaskFormPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="/analytics" element={<AnalyticsPage />} />
                </Routes>
              </Suspense>
            </AppShell>
          </BrowserRouter>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

// Bundle output:
// main.js         - App shell, providers, router (~80 KB)
// board.chunk.js  - Board page + task components (~120 KB)
// form.chunk.js   - Task form + validation (~60 KB)
// settings.chunk  - Settings page (~40 KB)
// analytics.chunk - Analytics + charts (~200 KB)
//
// Initial load: only 80 KB instead of 500 KB
```

---

## Patterns 11 & 12: Controlled Components and Container/Presentational

```jsx
// src/pages/TaskFormPage.jsx
// CONTAINER/PRESENTATIONAL PATTERN: Separates data logic from UI
// CONTROLLED COMPONENTS PATTERN: Form state managed by React

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTasks } from '../hooks/useTasks';
import { createTask } from '../factories/taskFactory';
import TaskForm from '../components/TaskForm/TaskForm';

// CONTAINER: handles data and logic
export default function TaskFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { tasks, addTask, updateTask } = useTasks();
  const [submitting, setSubmitting] = useState(false);

  const existingTask = id ? tasks.find(t => t.id === id) : null;
  const isEditing = !!existingTask;

  async function handleSubmit(formData) {
    setSubmitting(true);
    try {
      if (isEditing) {
        await updateTask(id, formData);
      } else {
        const task = createTask(formData); // Factory pattern
        await addTask(task);
      }
      navigate('/');
    } catch (error) {
      console.error('Failed to save task:', error);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="task-form-page">
      <h1>{isEditing ? 'Edit Task' : 'New Task'}</h1>
      <TaskForm
        initialValues={existingTask}
        onSubmit={handleSubmit}
        submitting={submitting}
      />
    </div>
  );
}

// src/components/TaskForm/TaskForm.jsx
// PRESENTATIONAL + CONTROLLED COMPONENT: Pure UI with controlled inputs

import { useState } from 'react';

export default function TaskForm({ initialValues, onSubmit, submitting }) {
  const [title, setTitle] = useState(initialValues?.title || '');
  const [description, setDescription] = useState(
    initialValues?.description || ''
  );
  const [priority, setPriority] = useState(
    initialValues?.priority || 'medium'
  );
  const [errors, setErrors] = useState({});

  function validate() {
    const newErrors = {};
    if (!title.trim()) newErrors.title = 'Title is required';
    if (title.length > 100) newErrors.title = 'Title must be under 100 characters';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({ title, description, priority });
  }

  return (
    <form onSubmit={handleSubmit} className="task-form">
      <div className="form-field">
        <label htmlFor="title">Title *</label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={e => setTitle(e.target.value)}
          className={errors.title ? 'input-error' : ''}
          disabled={submitting}
        />
        {errors.title && (
          <span className="error-message">{errors.title}</span>
        )}
      </div>

      <div className="form-field">
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          value={description}
          onChange={e => setDescription(e.target.value)}
          rows={4}
          disabled={submitting}
        />
      </div>

      <div className="form-field">
        <label htmlFor="priority">Priority</label>
        <select
          id="priority"
          value={priority}
          onChange={e => setPriority(e.target.value)}
          disabled={submitting}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
      </div>

      <button type="submit" disabled={submitting}>
        {submitting ? 'Saving...' : 'Save Task'}
      </button>
    </form>
  );
}
```

---

## Putting It All Together: The Board Page

```jsx
// src/pages/BoardPage.jsx
// This page uses nearly ALL the patterns together

import { useMemo, useCallback } from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import Board from '../components/Board/Board';
import TaskList from '../components/TaskList/TaskList';
import { useTasks } from '../hooks/useTasks';
import { useSearch } from '../hooks/useSearch';

export default function BoardPage() {
  const { tasks, loading, error, moveTask, updateTask, deleteTask } = useTasks();
  const { query, setQuery, results } = useSearch(tasks, ['title', 'description']);

  // Memoize grouped tasks
  const columns = useMemo(() => ({
    todo: results.filter(t => t.status === 'todo'),
    in_progress: results.filter(t => t.status === 'in_progress'),
    in_review: results.filter(t => t.status === 'in_review'),
    done: results.filter(t => t.status === 'done'),
  }), [results]);

  // Stable callbacks for memoized children
  const handleMove = useCallback(
    (taskId, newStatus) => moveTask(taskId, newStatus),
    [moveTask]
  );

  const handleStatusChange = useCallback(
    (taskId, newStatus) => updateTask(taskId, { status: newStatus }),
    [updateTask]
  );

  const handleDelete = useCallback(
    (taskId) => deleteTask(taskId),
    [deleteTask]
  );

  if (loading) return <BoardSkeleton />;
  if (error) return <BoardError message={error} />;

  return (
    <div className="board-page">
      {/* Search bar */}
      <div className="board-toolbar">
        <input
          type="text"
          placeholder="Search tasks..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          className="search-input"
        />
        <span className="task-count">
          {results.length} task{results.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Board with compound components */}
      <Board onTaskMove={handleMove}>
        <Board.Column status="todo" title="To Do">
          <ErrorBoundary fallback={<p>Error loading tasks</p>}>
            <TaskList
              tasks={columns.todo}
              status="todo"
              onStatusChange={handleStatusChange}
              onDelete={handleDelete}
            />
          </ErrorBoundary>
        </Board.Column>

        <Board.Column status="in_progress" title="In Progress">
          <ErrorBoundary fallback={<p>Error loading tasks</p>}>
            <TaskList
              tasks={columns.in_progress}
              status="in_progress"
              onStatusChange={handleStatusChange}
              onDelete={handleDelete}
            />
          </ErrorBoundary>
        </Board.Column>

        <Board.Column status="in_review" title="In Review">
          <ErrorBoundary fallback={<p>Error loading tasks</p>}>
            <TaskList
              tasks={columns.in_review}
              status="in_review"
              onStatusChange={handleStatusChange}
              onDelete={handleDelete}
            />
          </ErrorBoundary>
        </Board.Column>

        <Board.Column status="done" title="Done">
          <ErrorBoundary fallback={<p>Error loading tasks</p>}>
            <TaskList
              tasks={columns.done}
              status="done"
              onStatusChange={handleStatusChange}
              onDelete={handleDelete}
            />
          </ErrorBoundary>
        </Board.Column>
      </Board>
    </div>
  );
}

function BoardSkeleton() {
  return (
    <div className="board-skeleton">
      {[1, 2, 3, 4].map(i => (
        <div key={i} className="column-skeleton">
          <div className="skeleton-header" />
          <div className="skeleton-card" />
          <div className="skeleton-card" />
        </div>
      ))}
    </div>
  );
}

function BoardError({ message }) {
  return (
    <div className="board-error">
      <h2>Could not load board</h2>
      <p>{message}</p>
      <button onClick={() => window.location.reload()}>Reload</button>
    </div>
  );
}
```

---

## File Structure

```
src/
+-- App.jsx                          # Root: ErrorBoundary + Providers + Router
+-- index.jsx                        # Entry point
|
+-- pages/                           # Route-level components (lazy loaded)
|   +-- BoardPage.jsx                # Main board view
|   +-- TaskFormPage.jsx             # Create/edit task form
|   +-- SettingsPage.jsx             # User settings
|   +-- AnalyticsPage.jsx            # Task analytics
|
+-- components/                      # Reusable UI components
|   +-- AppShell/
|   |   +-- AppShell.jsx             # Layout shell with nav
|   +-- Board/
|   |   +-- Board.jsx                # Compound component (Board + Column)
|   +-- TaskCard/
|   |   +-- TaskCard.jsx             # Individual task card
|   |   +-- TaskActions.jsx          # Status transition buttons (State Machine)
|   +-- TaskList/
|   |   +-- TaskList.jsx             # Memoized task list
|   +-- TaskForm/
|   |   +-- TaskForm.jsx             # Controlled form component
|   +-- Notifications/
|   |   +-- NotificationToast.jsx    # Toast notification UI
|   +-- Loading/
|   |   +-- LoadingPage.jsx          # Full-page loading state
|   +-- ErrorBoundary/
|       +-- AppErrorBoundary.jsx     # Error fallback components
|
+-- providers/                       # Context providers
|   +-- ThemeProvider.jsx            # Theme context
|   +-- AuthProvider.jsx             # Auth context
|
+-- hooks/                           # Custom hooks
|   +-- useTasks.js                  # Task CRUD operations
|   +-- useSearch.js                 # Debounced search
|   +-- useNotifications.js          # Notification management
|
+-- services/                        # API services
|   +-- taskService.js               # Module pattern for API calls
|
+-- factories/                       # Object factories
|   +-- taskFactory.js               # Create task objects
|   +-- notificationFactory.js       # Create notification objects
|
+-- stateMachines/                   # State machines
|   +-- taskStatusMachine.js         # Task status transitions
|
+-- events/                          # Event system
    +-- eventBus.js                  # Observer pattern implementation
```

---

## Pattern Interaction Map

```
User creates a task:

1. TaskFormPage (Container)
   --> calls createTask() from taskFactory (FACTORY)
   --> calls addTask() from useTasks hook (CUSTOM HOOK)

2. useTasks hook
   --> calls taskService.create() (MODULE)
   --> emits TASK_CREATED event via eventBus (OBSERVER)
   --> emits NOTIFICATION event via eventBus (OBSERVER)

3. NotificationToast component
   --> receives notification via useNotifications hook (CUSTOM HOOK)
   --> shows "Task created!" toast

4. BoardPage re-renders
   --> useMemo recalculates column grouping (MEMOIZATION)
   --> Board.Column receives new tasks (COMPOUND COMPONENT)
   --> MemoizedTaskCard renders only new task (MEMOIZATION)
   --> TaskActions shows valid transitions (STATE MACHINE)

5. If any component crashes
   --> ErrorBoundary catches it (ERROR BOUNDARY)
   --> Only that column shows error, rest works fine

All of this is within:
   ThemeProvider (PROVIDER) for consistent styling
   AuthProvider (PROVIDER) for user context
   Lazy-loaded routes (CODE SPLITTING) for fast initial load
```

---

## Quick Summary

This chapter demonstrated how 12 design patterns work together in a single React application. The Module Pattern organizes API services. The Factory Pattern creates consistent objects. The Observer Pattern enables decoupled communication. Compound Components build flexible layouts. The Provider Pattern shares global state. Custom Hooks extract reusable logic. The State Machine Pattern enforces valid transitions. Memoization optimizes rendering performance. Error Boundaries provide graceful failure handling. Code Splitting reduces initial bundle size. Controlled Components manage form state. The Container/Presentational split separates concerns. Each pattern solves a specific problem, and together they create a maintainable, performant, production-quality application.

---

## Key Points

- **Patterns complement each other** -- No single pattern solves everything. Combine them.
- **Module Pattern** for API organization keeps service logic contained and testable.
- **Factory Pattern** ensures objects are created consistently with proper defaults.
- **Observer Pattern** (EventBus) enables communication without tight coupling.
- **Compound Components** create flexible, declarative APIs for complex layouts.
- **Provider Pattern** eliminates prop drilling for cross-cutting concerns.
- **Custom Hooks** are the primary way to share stateful logic in modern React.
- **State Machine** enforces business rules at the code level, preventing invalid states.
- **Memoization** should target expensive components identified through profiling.
- **Error Boundaries** should be layered: app-level, page-level, and feature-level.
- **Code Splitting** at route boundaries gives the best effort-to-impact ratio.

---

## Practice Questions

1. In the TaskFlow application, trace the flow from when a user clicks "Start Working" on a task to when the board UI updates. Which patterns are involved at each step?

2. Why does the BoardPage use `useMemo` to group tasks by column instead of filtering in the render? What would happen without memoization when the user types in the search box?

3. The EventBus (Observer Pattern) and the Provider Pattern both share data across components. When would you choose one over the other?

4. If the task status machine allowed a direct transition from "todo" to "done", what code change would you make? How does the State Machine Pattern make this change safe?

5. Explain how Error Boundaries and Code Splitting work together in the App component. What happens if the AnalyticsPage chunk fails to load?

---

## Exercises

### Exercise 1: Add a New Pattern

Extend the TaskFlow application with the **Decorator Pattern** (Chapter 9). Create a `withPriorityHighlight` higher-order component that wraps `TaskCard` and adds a colored border based on the task's priority (red for urgent, orange for high, default for others).

### Exercise 2: Build Your Own Project

Choose a different domain (recipe manager, workout tracker, or expense tracker) and build a small application using at least 8 of the patterns covered in this book. Create the file structure, identify which pattern solves each problem, and draw the pattern interaction map.

### Exercise 3: Pattern Audit

Take an existing React project (yours or open-source) and audit it for patterns. For each feature, identify:
- Which pattern is currently being used (if any)
- Whether a different pattern would be more appropriate
- Where a missing pattern would add value

Create a table mapping features to recommended patterns with justifications.

---

## What Is Next?

You have now seen every pattern in this book in action, both individually and working together. Chapter 32 provides a **Glossary** of all key terms, giving you a quick reference to look up any concept from the book.
