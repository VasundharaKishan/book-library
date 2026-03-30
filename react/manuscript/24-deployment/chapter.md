# Chapter 24: Deployment and Production Optimization

## Learning Goals

By the end of this chapter, you will be able to:

- Understand what happens when you build a React app for production
- Configure environment variables for different environments
- Optimize bundle size with code splitting and lazy loading
- Analyze your bundle to find what is making it large
- Deploy to popular hosting platforms (Vercel, Netlify, GitHub Pages)
- Handle client-side routing on static hosting
- Implement basic SEO for single-page applications
- Set up a production-ready build pipeline
- Apply performance optimizations that matter in production

---

## From Development to Production

During development, your React application runs with Vite's dev server, which provides:

- Hot Module Replacement (HMR) — instant updates without page reload
- Detailed error messages with component stacks
- Unminified code for easy debugging
- Source maps pointing to original files
- React's Strict Mode double-rendering for catching bugs

None of this belongs in production. When you deploy, you need a **production build** — optimized, minified, and stripped of development-only code.

### The Build Command

```bash
npm run build
```

This runs Vite's build process, which:

1. **Bundles** — Combines all your JavaScript files into a few optimized chunks
2. **Minifies** — Removes whitespace, shortens variable names, and eliminates dead code
3. **Tree-shakes** — Removes unused exports from imported modules
4. **Compiles JSX** — Converts JSX to JavaScript function calls
5. **Processes CSS** — Minifies CSS, adds vendor prefixes, extracts CSS into separate files
6. **Hashes filenames** — Adds content hashes to filenames for cache busting (`index-a1b2c3d4.js`)
7. **Generates assets** — Copies static files and optimizes images

The output goes to the `dist/` folder:

```
dist/
  index.html
  assets/
    index-a1b2c3d4.js      ← Your application code (minified)
    index-x7y8z9.css        ← Your styles (minified)
    vendor-e5f6g7h8.js      ← Third-party libraries
    logo-i9j0k1l2.svg       ← Static assets
```

### Previewing the Production Build

```bash
npm run build
npm run preview
```

The `preview` command serves the `dist/` folder locally so you can test the production build before deploying.

---

## Environment Variables

Applications need different configurations for different environments — a development API URL, a staging API URL, and a production API URL. Environment variables solve this.

### How Environment Variables Work in Vite

Vite reads environment variables from `.env` files:

```
.env                  ← Loaded in all environments
.env.local            ← Loaded in all environments, ignored by git
.env.development      ← Loaded only in development (npm run dev)
.env.production       ← Loaded only in production (npm run build)
```

**Important:** Only variables prefixed with `VITE_` are exposed to your application code. This prevents accidentally exposing server-side secrets.

```bash
# .env
VITE_APP_NAME=My React App

# .env.development
VITE_API_URL=http://localhost:3001/api

# .env.production
VITE_API_URL=https://api.myapp.com

# .env.local (not committed to git)
VITE_GOOGLE_MAPS_KEY=AIzaSyB...
```

### Accessing Environment Variables

```jsx
// In your React code
const apiUrl = import.meta.env.VITE_API_URL;
const appName = import.meta.env.VITE_APP_NAME;
const isDev = import.meta.env.DEV;
const isProd = import.meta.env.PROD;
const mode = import.meta.env.MODE; // "development" or "production"
```

### Using Environment Variables in API Calls

```jsx
// api.js
const BASE_URL = import.meta.env.VITE_API_URL;

export async function fetchUsers() {
  const response = await fetch(`${BASE_URL}/users`);
  if (!response.ok) throw new Error("Failed to fetch users");
  return response.json();
}
```

In development, this calls `http://localhost:3001/api/users`. In production, it calls `https://api.myapp.com/users`. The code is the same — only the environment variable changes.

### Validation

Validate required environment variables at startup:

```jsx
// config.js
const requiredVars = ["VITE_API_URL"];

for (const varName of requiredVars) {
  if (!import.meta.env[varName]) {
    throw new Error(`Missing required environment variable: ${varName}`);
  }
}

export const config = {
  apiUrl: import.meta.env.VITE_API_URL,
  appName: import.meta.env.VITE_APP_NAME || "My App",
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
};
```

### Git and Environment Variables

**Never commit secrets to git.** Add `.env.local` and any files containing secrets to `.gitignore`:

```gitignore
# .gitignore
.env.local
.env.*.local
```

Commit `.env.development` and `.env.production` (without secrets) to document which variables are needed. Store actual secrets in your hosting platform's environment variable settings.

---

## Bundle Optimization

### Analyzing Bundle Size

Before optimizing, you need to see what is in your bundle. Install the bundle analyzer:

```bash
npm install --save-dev rollup-plugin-visualizer
```

```js
// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { visualizer } from "rollup-plugin-visualizer";

export default defineConfig({
  plugins: [
    react(),
    visualizer({
      open: true,
      filename: "bundle-analysis.html",
      gzipSize: true,
    }),
  ],
});
```

Run `npm run build` and a visualization opens showing every module in your bundle, sized proportionally. This immediately reveals:

- Which libraries are the largest
- Whether you are importing entire libraries when you only need a small part
- Duplicate code that is bundled multiple times

### Code Splitting with React.lazy

Code splitting breaks your bundle into smaller chunks that load on demand. The most impactful place to split is at route boundaries:

```jsx
import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";

// These components are loaded only when their route is visited
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Settings = lazy(() => import("./pages/Settings"));
const AdminPanel = lazy(() => import("./pages/AdminPanel"));
const Analytics = lazy(() => import("./pages/Analytics"));

function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/admin" element={<AdminPanel />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Suspense>
  );
}

function PageLoader() {
  return (
    <div style={{ display: "flex", justifyContent: "center", padding: "4rem" }}>
      <p>Loading...</p>
    </div>
  );
}
```

Without code splitting, visiting the home page downloads the JavaScript for every page in the application. With code splitting, the home page only downloads the home page's code. Dashboard code loads when the user navigates to `/dashboard`.

### Import Only What You Need

Many libraries offer both a full import and individual imports:

```jsx
// WRONG — imports the entire library (large)
import _ from "lodash";
const sorted = _.sortBy(items, "name");

// CORRECT — imports only the function you need (small)
import sortBy from "lodash/sortBy";
const sorted = sortBy(items, "name");
```

```jsx
// WRONG — imports all icons (huge)
import { FaHome, FaUser } from "react-icons/fa";

// CORRECT — import from specific path (smaller)
import FaHome from "react-icons/fa/FaHome";
import FaUser from "react-icons/fa/FaUser";
```

### Remove Unused Dependencies

Check your `package.json` for libraries you no longer use:

```bash
npx depcheck
```

This lists unused dependencies that you can remove with `npm uninstall`.

### Image Optimization

Large images are often the biggest contributor to slow page loads — bigger than JavaScript in many cases.

- **Use modern formats** — WebP and AVIF are 25-50% smaller than JPEG/PNG
- **Resize images** — Do not serve a 4000px image in a 400px container
- **Use responsive images** — Serve different sizes for different screen widths

```jsx
<img
  src="/images/hero-800.webp"
  srcSet="
    /images/hero-400.webp 400w,
    /images/hero-800.webp 800w,
    /images/hero-1200.webp 1200w
  "
  sizes="(max-width: 600px) 400px, (max-width: 1000px) 800px, 1200px"
  alt="Hero banner"
  loading="lazy"
/>
```

The `loading="lazy"` attribute defers loading images that are below the fold until the user scrolls near them.

---

## Deploying to Hosting Platforms

A production React build is a collection of static files (HTML, CSS, JavaScript). Any static file hosting service can serve it.

### Deploying to Vercel

Vercel is the simplest option — it detects React projects and configures everything automatically.

**Method 1: Git integration (recommended)**

1. Push your code to GitHub, GitLab, or Bitbucket
2. Go to [vercel.com](https://vercel.com) and sign in
3. Click "Import Project" and select your repository
4. Vercel auto-detects the framework and build settings
5. Click "Deploy"

Every push to your main branch triggers a new deployment. Pull requests get preview deployments with unique URLs.

**Method 2: CLI**

```bash
npm install -g vercel
vercel
```

**Environment variables:**

Set them in Vercel's dashboard: Project → Settings → Environment Variables. They are injected at build time.

### Deploying to Netlify

Similar to Vercel with automatic Git integration.

**Method 1: Git integration**

1. Push your code to GitHub
2. Go to [netlify.com](https://netlify.com) and sign in
3. Click "Add new site" → "Import an existing project"
4. Select your repository
5. Build command: `npm run build`
6. Publish directory: `dist`
7. Click "Deploy"

**Method 2: CLI**

```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

**Client-side routing fix:**

Netlify needs a `_redirects` file to handle client-side routing:

```
# public/_redirects
/*    /index.html   200
```

Or a `netlify.toml`:

```toml
# netlify.toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Deploying to GitHub Pages

GitHub Pages hosts static sites for free from a repository.

**Setup:**

```bash
npm install --save-dev gh-pages
```

```json
// package.json
{
  "homepage": "https://yourusername.github.io/your-repo-name",
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d dist"
  }
}
```

```js
// vite.config.js
export default defineConfig({
  base: "/your-repo-name/",
  // ...
});
```

```bash
npm run deploy
```

**Client-side routing fix:**

GitHub Pages does not support client-side routing natively. For paths like `/about`, the server returns 404. The workaround is using `HashRouter` instead of `BrowserRouter`:

```jsx
import { HashRouter } from "react-router-dom";

// URLs become: https://user.github.io/repo/#/about
<HashRouter>
  <App />
</HashRouter>
```

Or use a `404.html` redirect trick — create a `public/404.html` that redirects to `index.html` with the path encoded in a query parameter.

### Handling Client-Side Routing on Static Hosts

The core problem: when a user navigates to `/dashboard` and refreshes, the server receives a request for `/dashboard`. But there is no `dashboard.html` file — only `index.html`. The server returns 404.

The solution: configure the server to serve `index.html` for all routes. Each platform does this differently:

| Platform | Solution |
|----------|----------|
| Vercel | Automatic (zero config) |
| Netlify | `_redirects` file or `netlify.toml` |
| GitHub Pages | `HashRouter` or `404.html` hack |
| Nginx | `try_files $uri /index.html;` |
| Apache | `.htaccess` with `FallbackResource /index.html` |
| AWS S3 + CloudFront | Error page configuration → `/index.html` |

---

## SEO for Single-Page Applications

Search engines need to read your page's content to index it. SPAs load content dynamically with JavaScript, which creates SEO challenges.

### The Problem

When Google's crawler visits your SPA, it sees:

```html
<div id="root"></div>
<script src="/assets/index-a1b2c3d4.js"></script>
```

The actual content is rendered by JavaScript after the page loads. While Googlebot can execute JavaScript, it is not reliable for all search engines, and there is a delay before content is indexed.

### Meta Tags with react-helmet-async

Even without server-side rendering, you can set meta tags dynamically:

```bash
npm install react-helmet-async
```

```jsx
// main.jsx
import { HelmetProvider } from "react-helmet-async";

createRoot(document.getElementById("root")).render(
  <HelmetProvider>
    <App />
  </HelmetProvider>
);
```

```jsx
// pages/AboutPage.jsx
import { Helmet } from "react-helmet-async";

function AboutPage() {
  return (
    <>
      <Helmet>
        <title>About Us — My App</title>
        <meta name="description" content="Learn about our company, our mission, and our team." />
        <meta property="og:title" content="About Us — My App" />
        <meta property="og:description" content="Learn about our company." />
        <meta property="og:type" content="website" />
        <link rel="canonical" href="https://myapp.com/about" />
      </Helmet>

      <h1>About Us</h1>
      <p>Learn about our company...</p>
    </>
  );
}
```

```jsx
// pages/BlogPost.jsx
function BlogPost({ post }) {
  return (
    <>
      <Helmet>
        <title>{post.title} — My Blog</title>
        <meta name="description" content={post.excerpt} />
        <meta property="og:title" content={post.title} />
        <meta property="og:description" content={post.excerpt} />
        <meta property="og:image" content={post.coverImage} />
        <meta property="og:type" content="article" />
        <meta property="article:published_time" content={post.publishedAt} />
      </Helmet>

      <article>
        <h1>{post.title}</h1>
        <p>{post.content}</p>
      </article>
    </>
  );
}
```

### Static Pre-Rendering

For pages where SEO is critical (landing page, blog posts, product pages), consider **static site generation (SSG)** or **server-side rendering (SSR)** with a framework like Next.js or Remix. These frameworks render HTML on the server, so crawlers see complete content without executing JavaScript.

**When to consider SSR/SSG:**

- Marketing/landing pages that need SEO
- Blog or content sites
- E-commerce product pages
- Any public page that needs to be indexed

**When a client-side SPA is fine:**

- Dashboard/admin panels (behind login, no SEO needed)
- Internal tools
- Applications where all content is behind authentication

### Essential SEO Checklist

1. **Unique `<title>` per page** — Descriptive, under 60 characters
2. **Meta description per page** — Compelling summary, under 160 characters
3. **Canonical URLs** — Prevent duplicate content issues
4. **Open Graph tags** — For social media sharing previews
5. **Semantic HTML** — Use `<h1>`, `<h2>`, `<article>`, `<nav>`, `<main>`
6. **Alt text on images** — Descriptive alternative text
7. **robots.txt** — Tell crawlers what to index
8. **sitemap.xml** — List all public URLs

```
# public/robots.txt
User-agent: *
Allow: /
Sitemap: https://myapp.com/sitemap.xml
```

---

## Performance Optimization Checklist

### Build-Time Optimizations

These happen automatically or with configuration — no code changes needed.

**1. Minification (automatic)**

Vite minifies JavaScript and CSS by default in production builds. Variable names are shortened, whitespace is removed, and dead code is eliminated.

**2. Tree-shaking (automatic)**

Unused exports are removed from the bundle. This works best with ES module imports (`import { specific } from "library"`), not CommonJS (`require("library")`).

**3. Asset hashing (automatic)**

Filenames include content hashes (`index-a1b2c3.js`). When file content changes, the hash changes, busting browser caches. When content does not change, the hash stays the same, and browsers serve the cached version.

**4. Gzip/Brotli compression**

Most hosting platforms compress assets automatically. For self-hosted servers, enable compression:

```nginx
# Nginx
gzip on;
gzip_types text/html text/css application/javascript application/json;
```

### Runtime Optimizations

These require code changes.

**1. Code splitting** — Split at route boundaries with `React.lazy`

**2. Image lazy loading** — Add `loading="lazy"` to images below the fold

**3. Memoization** — Use `React.memo`, `useMemo`, and `useCallback` where profiling shows unnecessary re-renders (see Chapter 11)

**4. Virtualize long lists** — For lists with hundreds of items, use `react-window` or `@tanstack/react-virtual` to render only visible items

**5. Debounce expensive operations** — Debounce search inputs, resize handlers, and other frequent events

### Measuring Performance

**Lighthouse** — Built into Chrome DevTools. Run an audit to get scores for Performance, Accessibility, Best Practices, and SEO.

**Core Web Vitals** — Google's metrics for user experience:

| Metric | What It Measures | Good |
|--------|-----------------|------|
| **LCP** (Largest Contentful Paint) | When the main content appears | Under 2.5s |
| **FID** (First Input Delay) | Time until the page responds to interaction | Under 100ms |
| **CLS** (Cumulative Layout Shift) | Visual stability (elements jumping around) | Under 0.1 |

```jsx
// Measure Web Vitals in your app
import { onCLS, onFID, onLCP } from "web-vitals";

onCLS(console.log);
onFID(console.log);
onLCP(console.log);
```

---

## Production Build Configuration

### Vite Production Config

```js
// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  build: {
    // Output directory (default: "dist")
    outDir: "dist",

    // Generate source maps for error tracking (optional)
    sourcemap: true,

    // Chunk splitting strategy
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor code from app code
          vendor: ["react", "react-dom"],
          router: ["react-router-dom"],
        },
      },
    },

    // Warn when a chunk exceeds this size (in KB)
    chunkSizeWarningLimit: 500,
  },
});
```

### Manual Chunk Splitting

By default, Vite bundles all vendor code together. For large applications, split vendors into separate chunks so they can be cached independently:

```js
manualChunks: {
  "react-vendor": ["react", "react-dom"],
  "router": ["react-router-dom"],
  "ui-library": ["@headlessui/react", "clsx"],
}
```

When you update your application code, the vendor chunks stay cached because their content has not changed. Users only download the updated application chunk.

### Source Maps in Production

Source maps connect minified code back to original source files. They are essential for debugging production errors with tools like Sentry:

```js
build: {
  sourcemap: true, // Generates .map files
}
```

Source maps should be uploaded to your error monitoring service but not served to users. Configure your web server to deny access to `.map` files:

```nginx
# Nginx — block source maps from public access
location ~* \.map$ {
  deny all;
}
```

---

## CI/CD Pipeline

A CI/CD (Continuous Integration / Continuous Deployment) pipeline automates testing and deployment. Here is a basic GitHub Actions workflow:

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}

      - name: Upload build artifact
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

This workflow:

1. Triggers on pushes and pull requests to `main`
2. Installs dependencies with `npm ci` (clean install, faster than `npm install`)
3. Runs the linter to catch code quality issues
4. Runs the test suite
5. Builds for production with environment variables from GitHub Secrets
6. Uploads the build artifact for deployment

If any step fails, the pipeline stops and the deployment does not happen. This prevents broken code from reaching production.

---

## Common Deployment Issues

### Issue 1: Blank Page After Deployment

**Cause:** The `base` path is wrong. If your app is not at the root of the domain (e.g., it is at `github.io/my-repo/`), you need to set the base:

```js
// vite.config.js
export default defineConfig({
  base: "/my-repo/",
});
```

**Check:** Open the browser DevTools Network tab. Are the JavaScript and CSS files returning 404?

### Issue 2: Routes Return 404 on Refresh

**Cause:** The hosting platform does not serve `index.html` for all routes. See the client-side routing section above for platform-specific fixes.

### Issue 3: API Calls Fail in Production

**Cause:** The API URL is hardcoded to `localhost` or the environment variable is not set.

**Fix:** Use environment variables for all API URLs. Verify they are set in your hosting platform's settings.

### Issue 4: Build Fails Due to TypeScript or Lint Errors

**Cause:** Development builds are more lenient than production builds. Some warnings become errors in production mode.

**Fix:** Run `npm run build` locally before pushing. Fix all warnings.

### Issue 5: Large Bundle Size

**Cause:** Importing large libraries entirely, no code splitting, unoptimized images.

**Fix:** Run the bundle analyzer, implement code splitting at route boundaries, check for unnecessary dependencies, and optimize images.

---

## Mini Project: Deployment-Ready Application

Here is a complete Vite configuration and project structure for a production-ready React application:

```js
// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => ({
  plugins: [react()],

  base: "/",

  build: {
    outDir: "dist",
    sourcemap: mode === "production",
    rollupOptions: {
      output: {
        manualChunks: {
          "react-vendor": ["react", "react-dom"],
          router: ["react-router-dom"],
        },
      },
    },
  },

  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:3001",
        changeOrigin: true,
      },
    },
  },
}));
```

```jsx
// src/config.js
const config = {
  apiUrl: import.meta.env.VITE_API_URL || "/api",
  appName: import.meta.env.VITE_APP_NAME || "My App",
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
};

// Validate required variables in production
if (config.isProd && !import.meta.env.VITE_API_URL) {
  console.warn("VITE_API_URL is not set. Using default: /api");
}

export default config;
```

```jsx
// src/App.jsx
import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import config from "./config";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import PageLoader from "./components/PageLoader";
import ErrorBoundary from "./components/ErrorBoundary";

// Lazy-loaded routes
const About = lazy(() => import("./pages/About"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Settings = lazy(() => import("./pages/Settings"));
const NotFound = lazy(() => import("./pages/NotFound"));

function App() {
  return (
    <ErrorBoundary>
      <Helmet>
        <title>{config.appName}</title>
        <meta name="description" content="A production-ready React application" />
      </Helmet>

      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="about" element={<About />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="settings" element={<Settings />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
}

export default App;
```

```jsx
// src/components/PageLoader.jsx
function PageLoader() {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "50vh",
      }}
    >
      <div
        style={{
          width: 40,
          height: 40,
          border: "4px solid #e5e7eb",
          borderTopColor: "#3b82f6",
          borderRadius: "50%",
          animation: "spin 0.8s linear infinite",
        }}
      />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

export default PageLoader;
```

```bash
# .env.development
VITE_API_URL=http://localhost:3001/api
VITE_APP_NAME=My App (Dev)

# .env.production
VITE_API_URL=https://api.myapp.com
VITE_APP_NAME=My App
```

```json
// package.json scripts
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest",
    "lint": "eslint src/",
    "typecheck": "tsc --noEmit"
  }
}
```

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

```
# vercel.json (only needed for custom config)
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

This project setup provides:

- **Environment-based configuration** — different API URLs for dev and production
- **Code splitting** — routes are lazy-loaded for smaller initial bundles
- **Vendor chunking** — React and router are in separate cached chunks
- **Error boundary** — catches and displays errors gracefully
- **SEO meta tags** — per-page titles and descriptions with react-helmet-async
- **Loading states** — spinner while lazy-loaded routes are loading
- **Dev proxy** — API calls proxied to a backend server during development
- **Deployment configs** — ready for Netlify and Vercel with client-side routing support
- **CI-ready scripts** — lint, test, and build commands for automation

---

## Common Mistakes

### Mistake 1: Hardcoding API URLs

```jsx
// WRONG — breaks when deployed
const response = await fetch("http://localhost:3001/api/users");

// CORRECT — uses environment variable
const response = await fetch(`${import.meta.env.VITE_API_URL}/users`);
```

### Mistake 2: Committing .env.local to Git

```gitignore
# .gitignore — always exclude local env files
.env.local
.env.*.local
```

Local env files contain secrets (API keys, database URLs). Never commit them.

### Mistake 3: Not Testing the Production Build Locally

```bash
# Always test before deploying
npm run build
npm run preview
# Click through your app, check the console for errors
```

Issues that do not appear in development often show up in production builds — missing environment variables, broken imports, CSS differences.

### Mistake 4: Ignoring Bundle Size

A 5MB JavaScript bundle takes 10+ seconds to load on a mobile connection. Monitor your bundle size:

```bash
# Check the size after building
npm run build
# Vite reports chunk sizes in the terminal output
```

If your bundle is over 200KB gzipped, analyze it and apply code splitting.

### Mistake 5: No Error Tracking in Production

```jsx
// In development, you see errors in the console
// In production, errors are silent — users see a white screen

// Set up error tracking (Sentry, LogRocket, etc.)
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
});
```

---

## Best Practices

1. **Always test the production build locally** — Run `npm run build && npm run preview` and test your app before deploying. Many bugs only appear in production builds.

2. **Use environment variables for all external URLs** — API URLs, CDN URLs, third-party service keys — anything that differs between environments.

3. **Code split at route boundaries** — Use `React.lazy` for every route that is not the initial landing page. This dramatically reduces initial load time.

4. **Monitor bundle size** — Add the bundle analyzer to your build process. Set a size budget and investigate when it is exceeded.

5. **Set up CI/CD** — Automate linting, testing, and building. Never deploy manually if you can avoid it.

6. **Enable source maps for error tracking** — Upload source maps to your error tracking service but do not serve them publicly.

7. **Use content hashing for cache busting** — Vite does this by default. Long-lived cache headers combined with content-hashed filenames give the best performance.

8. **Add a robots.txt and sitemap** — Even if your app is not SEO-focused, these files help search engines understand your site.

---

## Summary

In this chapter, you learned:

- **Production builds** minify, tree-shake, and bundle your code into optimized static files in the `dist/` folder
- **Environment variables** (`VITE_` prefix) configure different API URLs and settings for development and production
- **Bundle optimization** uses code splitting (`React.lazy`), tree-shaking, targeted imports, and vendor chunking to reduce what users download
- **Deployment** to Vercel, Netlify, and GitHub Pages each require specific configuration for client-side routing
- **Client-side routing** requires the server to serve `index.html` for all routes — configure redirects on your hosting platform
- **SEO** for SPAs uses `react-helmet-async` for meta tags and considers SSR/SSG (Next.js) for content that needs indexing
- **Performance** is measured with Lighthouse and Core Web Vitals (LCP, FID, CLS)
- **CI/CD pipelines** automate testing and deployment with GitHub Actions
- **Error tracking** (Sentry) and source maps are essential for debugging production issues

---

## Interview Questions

1. **What happens when you run `npm run build` in a React project?**

   The build tool (Vite/Webpack) bundles all JavaScript files into optimized chunks, minifies the code (removes whitespace, shortens variables), tree-shakes unused exports, compiles JSX to JavaScript, processes and minifies CSS, adds content hashes to filenames for cache busting, and outputs everything to a `dist/` folder. The result is a collection of static files (HTML, CSS, JS) that can be served by any web server.

2. **Why do React SPAs need special server configuration for routing?**

   In a SPA, routes like `/about` are handled by JavaScript in the browser, not by the server. When a user navigates to `/about` and refreshes, the browser sends a request for `/about` to the server. Since there is no `about.html` file, the server returns 404. The fix is configuring the server to serve `index.html` for all routes, letting React Router handle the routing on the client side.

3. **What is code splitting and why is it important?**

   Code splitting breaks a single large JavaScript bundle into smaller chunks that load on demand. Using `React.lazy` and dynamic `import()`, route components are only downloaded when the user navigates to them. This reduces the initial bundle size, meaning users download less JavaScript upfront and the page loads faster. It is especially impactful for large applications where most users only visit a few pages per session.

4. **How do environment variables work in a Vite React project?**

   Vite reads variables from `.env` files (`.env`, `.env.development`, `.env.production`). Only variables prefixed with `VITE_` are exposed to client-side code via `import.meta.env.VITE_VARIABLE_NAME`. This prefix prevents accidentally exposing server-side secrets. Different `.env` files are loaded based on the mode — `.env.development` for `npm run dev` and `.env.production` for `npm run build`. Secrets should be stored in `.env.local` (gitignored) or in the hosting platform's environment variable settings.

5. **What are Core Web Vitals and why do they matter?**

   Core Web Vitals are Google's metrics for measuring user experience: LCP (Largest Contentful Paint) measures loading speed — when the main content becomes visible. FID (First Input Delay) measures interactivity — how quickly the page responds to user input. CLS (Cumulative Layout Shift) measures visual stability — whether elements move around as the page loads. They matter because Google uses them as ranking signals for search results, and they directly correlate with user satisfaction and conversion rates.

---

## Practice Exercises

### Exercise 1: Production Build Analysis

Build your React application for production and analyze the output. Note the total bundle size, identify the three largest dependencies, and apply at least two optimizations (code splitting, import optimization, removing unused deps). Compare the before and after bundle sizes.

### Exercise 2: Multi-Environment Setup

Configure your application for three environments: development (local API), staging (staging API), and production (production API). Create the appropriate `.env` files, add a config module that validates required variables, and build for each environment to verify the correct URLs are used.

### Exercise 3: Deploy to Two Platforms

Deploy your application to both Vercel and Netlify. Configure client-side routing on both. Set up environment variables on both platforms. Compare the deployment experience, build times, and preview URL features.

### Exercise 4: CI/CD Pipeline

Set up a GitHub Actions workflow that lints, tests, and builds your application on every push. Add a step that fails the pipeline if the bundle size exceeds a threshold. Add deployment to your chosen platform on merges to `main`.

---

## What Is Next?

In Chapter 25, we will explore **React App Architecture and Folder Structure** — how to organize a growing React application with scalable file structures, separation of concerns, and patterns that keep large codebases maintainable.
