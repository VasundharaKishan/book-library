# Chapter 26: Handling Images, Assets, and Environment Variables

## Learning Goals

By the end of this chapter, you will be able to:

- Import and use images in React components using Vite
- Choose between `public/` folder assets and imported assets
- Work with SVGs as components and as image sources
- Manage fonts, icons, and other static assets
- Use environment variables safely across different environments
- Optimize images for performance (compression, lazy loading, responsive images)
- Handle favicons and meta images for SEO
- Organize assets in a scalable project structure

---

## How Vite Handles Assets

Before diving into specifics, let us understand how Vite processes different types of files. This knowledge will help you make the right decision for every asset in your project.

When you build a Vite project, it does two things with your files:

1. **Processed assets** — files you `import` in your JavaScript are processed by Vite's build pipeline. They get hashed filenames (like `logo-abc123.png`), are optimized, and benefit from cache busting.

2. **Static assets** — files in the `public/` folder are copied as-is to the build output. They keep their original filenames and are not processed.

This distinction is fundamental to everything in this chapter.

---

## Images in React

### Importing Images

The most common way to use images in a Vite React project is to import them:

```jsx
import reactLogo from './assets/react-logo.png';

function Header() {
  return (
    <header>
      <img src={reactLogo} alt="React logo" />
      <h1>My React App</h1>
    </header>
  );
}
```

When you import an image, Vite gives you the resolved URL as a string. During development, this might be `/src/assets/react-logo.png`. In production, it becomes something like `/assets/react-logo-a1b2c3d4.png` — the hash ensures browsers always load the latest version.

**Benefits of importing images:**

- **Cache busting** — the hash changes when the file changes, so browsers fetch the new version
- **Build errors** — if the image is missing, you get a build error instead of a broken image at runtime
- **Optimization** — Vite can optimize imported assets during the build
- **Tree shaking** — unused imports are excluded from the bundle

### Small Images as Data URLs

By default, Vite inlines images smaller than 4KB as base64 data URLs. This means the image is embedded directly in your JavaScript bundle, eliminating an extra HTTP request:

```jsx
// If icon.png is under 4KB, this becomes a data URL like:
// "data:image/png;base64,iVBORw0KGgo..."
import icon from './assets/icon.png';

function StatusIndicator() {
  return <img src={icon} alt="" />;  // No HTTP request needed
}
```

You can configure this threshold in `vite.config.js`:

```jsx
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    assetsInlineLimit: 4096,  // Default: 4096 bytes (4KB)
  },
});
```

Set it to `0` to disable inlining entirely. Increase it if you have many tiny icons that would benefit from inlining.

### Images in the `public/` Folder

Files in `public/` are served at the root path and copied unchanged to the build output:

```
public/
├── favicon.ico
├── og-image.jpg
├── robots.txt
└── images/
    └── hero-banner.jpg
```

Reference them with absolute paths starting from `/`:

```jsx
function HeroBanner() {
  return (
    <section>
      <img src="/images/hero-banner.jpg" alt="Welcome to our store" />
    </section>
  );
}
```

**When to use `public/`:**

- Files that must keep their exact filename (like `favicon.ico`, `robots.txt`)
- Files referenced in `index.html` directly
- Files that need a predictable URL (for sharing on social media)
- Very large files you do not want in the JavaScript bundle pipeline

**When NOT to use `public/`:**

- Regular images used in components — import them instead for cache busting
- Assets that might be removed or renamed — imports catch missing files at build time

### Importing Images Dynamically

Sometimes you need to select an image based on data. There are several approaches.

**Approach 1: Import all options statically**

```jsx
import catImage from './assets/animals/cat.jpg';
import dogImage from './assets/animals/dog.jpg';
import birdImage from './assets/animals/bird.jpg';

const animalImages = {
  cat: catImage,
  dog: dogImage,
  bird: birdImage,
};

function AnimalCard({ animal }) {
  return (
    <div>
      <img src={animalImages[animal.type]} alt={animal.name} />
      <p>{animal.name}</p>
    </div>
  );
}
```

This works well when you have a known, small set of images.

**Approach 2: Use Vite's `import.meta.glob`**

For many images or dynamic paths, use Vite's glob import:

```jsx
// Import all images from a directory
const imageModules = import.meta.glob(
  './assets/animals/*.{png,jpg,jpeg,svg}',
  { eager: true, import: 'default' }
);

// imageModules looks like:
// {
//   './assets/animals/cat.jpg': '/src/assets/animals/cat-abc123.jpg',
//   './assets/animals/dog.jpg': '/src/assets/animals/dog-def456.jpg',
//   ...
// }

function AnimalCard({ animal }) {
  const imagePath = `./assets/animals/${animal.type}.jpg`;
  const imageSrc = imageModules[imagePath];

  return (
    <div>
      {imageSrc ? (
        <img src={imageSrc} alt={animal.name} />
      ) : (
        <img src="/images/placeholder.jpg" alt="Unknown animal" />
      )}
      <p>{animal.name}</p>
    </div>
  );
}
```

The `eager: true` option loads all images immediately. Without it, each image is loaded lazily when accessed.

**Approach 3: Use the `public/` folder for fully dynamic images**

When images come from user data or an API and you cannot predict the filenames:

```jsx
function UserAvatar({ user }) {
  // Images uploaded by users, stored in public/uploads/
  return (
    <img
      src={`/uploads/avatars/${user.avatarFilename}`}
      alt={`${user.name}'s avatar`}
      onError={(e) => {
        e.target.src = '/images/default-avatar.png';
      }}
    />
  );
}
```

**Approach 4: External URLs**

For images from a CDN or API, just use the URL directly:

```jsx
function ProductImage({ product }) {
  return (
    <img
      src={product.imageUrl}  // "https://cdn.example.com/products/123.jpg"
      alt={product.name}
    />
  );
}
```

---

## Working with SVGs

SVGs (Scalable Vector Graphics) deserve special attention because they can be used in multiple ways, each with different trade-offs.

### SVG as an Image Source

The simplest approach — import the SVG and use it as an `img` source:

```jsx
import logo from './assets/logo.svg';

function Header() {
  return <img src={logo} alt="Company logo" className="logo" />;
}
```

**Pros:** Simple. The SVG is cached by the browser as a separate file.
**Cons:** You cannot style the SVG with CSS (no changing colors dynamically). No access to internal SVG elements.

### SVG as a React Component

To style SVGs dynamically or animate them, use them as React components. You can do this manually or with a plugin.

**Manual approach — create a component:**

```jsx
// src/shared/components/icons/CheckIcon.jsx
export function CheckIcon({ size = 24, color = 'currentColor', ...props }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}
```

```jsx
function StatusBadge({ status }) {
  return (
    <span className={`badge badge-${status}`}>
      <CheckIcon size={16} color={status === 'active' ? 'green' : 'gray'} />
      {status}
    </span>
  );
}
```

**Using `vite-plugin-svgr`:**

This plugin lets you import SVGs directly as React components:

```bash
npm install vite-plugin-svgr --save-dev
```

```jsx
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import svgr from 'vite-plugin-svgr';

export default defineConfig({
  plugins: [react(), svgr()],
});
```

Now you can import SVGs both ways:

```jsx
// As a React component (note the ?react suffix)
import Logo from './assets/logo.svg?react';

// As a URL (default behavior)
import logoUrl from './assets/logo.svg';

function Header() {
  return (
    <header>
      {/* As a component — fully styleable */}
      <Logo className="logo" fill="blue" width={120} />

      {/* As an image — simpler, cached separately */}
      <img src={logoUrl} alt="Logo" />
    </header>
  );
}
```

### Building an Icon System

For projects with many icons, create an organized icon system:

```
src/shared/components/icons/
├── ArrowLeft.jsx
├── ArrowRight.jsx
├── Check.jsx
├── Close.jsx
├── Menu.jsx
├── Search.jsx
├── User.jsx
└── index.js
```

Create a base icon component:

```jsx
// src/shared/components/icons/IconBase.jsx
export function IconBase({
  children,
  size = 24,
  color = 'currentColor',
  className = '',
  ...props
}) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`icon ${className}`}
      {...props}
    >
      {children}
    </svg>
  );
}
```

Each icon uses the base:

```jsx
// src/shared/components/icons/Search.jsx
import { IconBase } from './IconBase';

export function SearchIcon(props) {
  return (
    <IconBase {...props}>
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </IconBase>
  );
}
```

```jsx
// src/shared/components/icons/Close.jsx
import { IconBase } from './IconBase';

export function CloseIcon(props) {
  return (
    <IconBase {...props}>
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </IconBase>
  );
}
```

```jsx
// src/shared/components/icons/Menu.jsx
import { IconBase } from './IconBase';

export function MenuIcon(props) {
  return (
    <IconBase {...props}>
      <line x1="3" y1="12" x2="21" y2="12" />
      <line x1="3" y1="6" x2="21" y2="6" />
      <line x1="3" y1="18" x2="21" y2="18" />
    </IconBase>
  );
}
```

Export everything from the barrel:

```jsx
// src/shared/components/icons/index.js
export { SearchIcon } from './Search';
export { CloseIcon } from './Close';
export { MenuIcon } from './Menu';
export { CheckIcon } from './Check';
export { ArrowLeftIcon } from './ArrowLeft';
export { ArrowRightIcon } from './ArrowRight';
export { UserIcon } from './User';
```

Now use icons anywhere:

```jsx
import { SearchIcon, CloseIcon } from '@shared/components/icons';

function SearchBar() {
  const [query, setQuery] = useState('');

  return (
    <div className="search-bar">
      <SearchIcon size={18} className="search-icon" />
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
      />
      {query && (
        <button onClick={() => setQuery('')}>
          <CloseIcon size={16} />
        </button>
      )}
    </div>
  );
}
```

### SVG Decision Guide

| Need | Approach |
|------|----------|
| Simple display, no styling needed | `<img src={svgUrl}>` |
| Dynamic colors or sizes | SVG React component |
| Animated SVG | SVG React component |
| Many icons throughout the app | Icon system with base component |
| SVG from user/API | `<img src={url}>` |
| Complex illustration | `<img src={svgUrl}>` or `public/` |

---

## Fonts

### Using Web Fonts

The recommended approach is to self-host fonts for performance and privacy. Download the font files and place them in your assets:

```
src/assets/fonts/
├── Inter-Regular.woff2
├── Inter-Medium.woff2
├── Inter-Bold.woff2
└── Inter-Italic.woff2
```

Define `@font-face` in your global CSS:

```css
/* src/assets/styles/fonts.css */
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('../fonts/Inter-Regular.woff2') format('woff2');
}

@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url('../fonts/Inter-Medium.woff2') format('woff2');
}

@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('../fonts/Inter-Bold.woff2') format('woff2');
}

@font-face {
  font-family: 'Inter';
  font-style: italic;
  font-weight: 400;
  font-display: swap;
  src: url('../fonts/Inter-Italic.woff2') format('woff2');
}
```

Import the font CSS in your main entry:

```jsx
// src/main.jsx
import './assets/styles/fonts.css';
import './assets/styles/global.css';
import App from './app/App';
// ...
```

Use the font in your styles:

```css
/* src/assets/styles/global.css */
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
    Roboto, sans-serif;
}
```

**Key details:**

- **`font-display: swap`** tells the browser to show text immediately with a fallback font, then swap to the custom font once loaded. This prevents invisible text during loading.
- **WOFF2** is the most efficient font format and is supported by all modern browsers. You rarely need other formats.
- Self-hosting avoids third-party requests to Google Fonts or other services, improving both privacy and load times.

### Using Google Fonts (Alternative)

If you prefer Google Fonts, add the link to `index.html`:

```html
<!-- index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap"
    rel="stylesheet"
  />
  <!-- ... -->
</head>
```

The `preconnect` links tell the browser to start connecting to Google's font servers early, reducing load time.

---

## Environment Variables

Environment variables let you configure your application differently for development, staging, and production without changing code.

### How Environment Variables Work in Vite

Vite loads environment variables from `.env` files:

```
.env                 # Loaded in all environments
.env.local           # Loaded in all environments, git-ignored
.env.development     # Loaded only in development (npm run dev)
.env.production      # Loaded only in production (npm run build)
.env.staging         # Loaded in custom "staging" mode
```

**Critical rule:** Only variables prefixed with `VITE_` are exposed to your client-side code. This prevents accidentally leaking server secrets.

```bash
# .env
VITE_API_URL=http://localhost:3001/api
VITE_APP_TITLE=My React App
VITE_ENABLE_ANALYTICS=false

# This will NOT be available in client code (no VITE_ prefix)
DATABASE_URL=postgres://localhost:5432/mydb
SECRET_KEY=super-secret-value
```

### Accessing Environment Variables

Access variables through `import.meta.env`:

```jsx
// Access environment variables
const apiUrl = import.meta.env.VITE_API_URL;
const appTitle = import.meta.env.VITE_APP_TITLE;

// Built-in variables (always available)
const isDev = import.meta.env.DEV;       // true in development
const isProd = import.meta.env.PROD;      // true in production
const mode = import.meta.env.MODE;        // "development" or "production"
```

### Environment-Specific Configuration

Create separate `.env` files for each environment:

```bash
# .env.development
VITE_API_URL=http://localhost:3001/api
VITE_ENABLE_ANALYTICS=false
VITE_LOG_LEVEL=debug
```

```bash
# .env.production
VITE_API_URL=https://api.myapp.com
VITE_ENABLE_ANALYTICS=true
VITE_LOG_LEVEL=error
```

```bash
# .env.staging
VITE_API_URL=https://staging-api.myapp.com
VITE_ENABLE_ANALYTICS=false
VITE_LOG_LEVEL=warn
```

To build for staging:

```bash
npx vite build --mode staging
```

### Creating a Configuration Module

Instead of accessing `import.meta.env` throughout your code, centralize configuration:

```jsx
// src/shared/config/index.js
export const config = {
  api: {
    baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:3001/api',
    timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 10000,
  },
  app: {
    title: import.meta.env.VITE_APP_TITLE || 'React App',
    version: import.meta.env.VITE_APP_VERSION || '0.0.0',
  },
  features: {
    analytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
    darkMode: import.meta.env.VITE_ENABLE_DARK_MODE !== 'false',
    maintenance: import.meta.env.VITE_MAINTENANCE_MODE === 'true',
  },
  logging: {
    level: import.meta.env.VITE_LOG_LEVEL || 'warn',
  },
};
```

Note that environment variables are always strings. You must convert them explicitly:

```jsx
// Environment variables are ALWAYS strings
const timeout = import.meta.env.VITE_TIMEOUT;  // "10000" (string)
const timeout = Number(import.meta.env.VITE_TIMEOUT);  // 10000 (number)

const enabled = import.meta.env.VITE_ENABLED;  // "true" (string)
const enabled = import.meta.env.VITE_ENABLED === 'true';  // true (boolean)
```

Use the configuration module throughout your app:

```jsx
import { config } from '@shared/config';

// In your API client
const response = await fetch(`${config.api.baseUrl}/products`);

// In conditional features
if (config.features.analytics) {
  trackEvent('page_view', { page: '/products' });
}

// In your app shell
document.title = config.app.title;
```

### Validating Environment Variables

Catch missing variables early by validating at startup:

```jsx
// src/shared/config/validate.js
const requiredVars = [
  'VITE_API_URL',
];

const optionalVars = [
  'VITE_APP_TITLE',
  'VITE_ENABLE_ANALYTICS',
  'VITE_LOG_LEVEL',
];

export function validateEnv() {
  const missing = requiredVars.filter(
    (varName) => !import.meta.env[varName]
  );

  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(', ')}\n` +
      'Check your .env file and ensure all required variables are set.'
    );
  }

  if (import.meta.env.DEV) {
    const allVars = [...requiredVars, ...optionalVars];
    console.log('Environment configuration:');
    allVars.forEach((varName) => {
      const value = import.meta.env[varName];
      const status = value ? '✓' : '○ (not set)';
      console.log(`  ${status} ${varName}`);
    });
  }
}
```

```jsx
// src/main.jsx
import { validateEnv } from './shared/config/validate';

validateEnv();  // Throws immediately if required vars are missing

// ... rest of app
```

### What NOT to Put in Environment Variables

Environment variables in a Vite app are embedded in the JavaScript bundle at build time. They are visible to anyone who inspects your code. Never put sensitive data in client-side environment variables:

```bash
# NEVER do this — these are visible in the browser
VITE_DATABASE_URL=postgres://user:pass@localhost/db
VITE_SECRET_KEY=my-super-secret
VITE_PRIVATE_API_KEY=sk_live_abc123
VITE_ADMIN_PASSWORD=admin123

# These are fine — they are meant to be public
VITE_API_URL=https://api.myapp.com
VITE_GOOGLE_MAPS_KEY=pk_abc123          # Public key, not secret
VITE_STRIPE_PUBLIC_KEY=pk_live_abc123   # Public key, not secret
VITE_SENTRY_DSN=https://abc@sentry.io/123
```

### The `.env.example` File

Create a `.env.example` file that documents all variables without real values. Commit this to version control:

```bash
# .env.example
# Copy this file to .env and fill in your values

# Required
VITE_API_URL=http://localhost:3001/api

# Optional
VITE_APP_TITLE=My React App
VITE_ENABLE_ANALYTICS=false
VITE_LOG_LEVEL=debug
VITE_API_TIMEOUT=10000
```

Add `.env` files (except `.env.example`) to `.gitignore`:

```
# .gitignore
.env
.env.local
.env.development.local
.env.production.local
```

---

## Image Optimization

Images are typically the largest assets on a web page. Optimizing them dramatically improves load times.

### Choosing the Right Format

| Format | Best For | Transparency | Animation |
|--------|----------|-------------|-----------|
| **JPEG** | Photos, complex images | No | No |
| **PNG** | Screenshots, images with text, transparency needed | Yes | No |
| **WebP** | Modern replacement for JPEG/PNG (25-35% smaller) | Yes | Yes |
| **AVIF** | Next-gen format (50% smaller than JPEG) | Yes | Yes |
| **SVG** | Icons, logos, simple illustrations | Yes | Yes |

### The `<picture>` Element for Format Fallbacks

Serve modern formats with fallbacks for older browsers:

```jsx
function ProductImage({ product }) {
  return (
    <picture>
      {/* Browser picks the first format it supports */}
      <source srcSet={product.imageAvif} type="image/avif" />
      <source srcSet={product.imageWebp} type="image/webp" />
      <img
        src={product.imageJpg}
        alt={product.name}
        width={400}
        height={300}
      />
    </picture>
  );
}
```

### Responsive Images with `srcSet`

Serve different image sizes based on the device:

```jsx
import heroSmall from './assets/hero-640.jpg';
import heroMedium from './assets/hero-1024.jpg';
import heroLarge from './assets/hero-1920.jpg';

function HeroBanner() {
  return (
    <img
      src={heroMedium}
      srcSet={`
        ${heroSmall} 640w,
        ${heroMedium} 1024w,
        ${heroLarge} 1920w
      `}
      sizes="100vw"
      alt="Welcome to our store"
      style={{ width: '100%', height: 'auto' }}
    />
  );
}
```

The `sizes` attribute tells the browser how wide the image will be displayed. The browser then picks the best source from `srcSet`:

```jsx
// More specific sizes example
<img
  src={productMedium}
  srcSet={`
    ${productSmall} 400w,
    ${productMedium} 800w,
    ${productLarge} 1200w
  `}
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
  alt={product.name}
/>
```

This says: "On screens up to 640px, the image fills 100% of the viewport. On screens up to 1024px, it fills 50%. On larger screens, it fills 33%."

### Lazy Loading Images

Images below the fold should load lazily. The browser's built-in `loading="lazy"` attribute handles this:

```jsx
function ProductCard({ product }) {
  return (
    <article>
      <img
        src={product.image}
        alt={product.name}
        loading="lazy"           // Loads when near viewport
        width={300}              // Prevents layout shift
        height={200}
        style={{ aspectRatio: '3/2' }}
      />
      <h3>{product.name}</h3>
    </article>
  );
}
```

**Important:** Always include `width` and `height` attributes (or set `aspect-ratio` in CSS) on lazy-loaded images. Without dimensions, the browser cannot reserve space, causing layout shifts as images load.

**Do not** lazy-load images that are visible when the page first loads (above the fold). These should load immediately:

```jsx
function HeroBanner() {
  return (
    <img
      src={heroBanner}
      alt="Welcome"
      loading="eager"      // Default — loads immediately
      fetchPriority="high" // Tell browser this is important
      width={1920}
      height={600}
    />
  );
}
```

### A Reusable Optimized Image Component

Combine best practices into a single component:

```jsx
// src/shared/components/Image/Image.jsx
import { useState } from 'react';
import styles from './Image.module.css';

export function Image({
  src,
  alt,
  width,
  height,
  loading = 'lazy',
  className = '',
  fallback = '/images/placeholder.jpg',
  onLoad,
  ...props
}) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  function handleLoad(e) {
    setLoaded(true);
    onLoad?.(e);
  }

  function handleError() {
    setError(true);
  }

  return (
    <div
      className={`${styles.wrapper} ${className}`}
      style={{ aspectRatio: width && height ? `${width}/${height}` : undefined }}
    >
      {!loaded && !error && (
        <div className={styles.placeholder} aria-hidden="true" />
      )}
      <img
        src={error ? fallback : src}
        alt={alt}
        width={width}
        height={height}
        loading={loading}
        onLoad={handleLoad}
        onError={handleError}
        className={`${styles.image} ${loaded ? styles.loaded : ''}`}
        {...props}
      />
    </div>
  );
}
```

```css
/* src/shared/components/Image/Image.module.css */
.wrapper {
  position: relative;
  overflow: hidden;
  background-color: #f0f0f0;
}

.placeholder {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.image {
  display: block;
  width: 100%;
  height: auto;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.loaded {
  opacity: 1;
}
```

Usage:

```jsx
import { Image } from '@shared/components';

function ProductGrid({ products }) {
  return (
    <div className="grid">
      {products.map(product => (
        <article key={product.id}>
          <Image
            src={product.image}
            alt={product.name}
            width={400}
            height={300}
          />
          <h3>{product.name}</h3>
          <p>${product.price.toFixed(2)}</p>
        </article>
      ))}
    </div>
  );
}
```

---

## Favicons and Meta Images

### Favicons

Modern browsers support multiple favicon formats. Here is a practical setup:

```
public/
├── favicon.ico          # 32x32, for legacy browsers
├── favicon.svg          # SVG favicon for modern browsers
├── apple-touch-icon.png # 180x180, for iOS home screen
└── site.webmanifest     # Web app manifest
```

```html
<!-- index.html -->
<head>
  <link rel="icon" href="/favicon.ico" sizes="32x32" />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />
</head>
```

```json
// public/site.webmanifest
{
  "name": "My React App",
  "short_name": "ReactApp",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ],
  "theme_color": "#3b82f6",
  "background_color": "#ffffff",
  "display": "standalone"
}
```

### Open Graph and Social Media Images

When someone shares your page on social media, these meta tags control the preview:

```html
<!-- index.html -->
<head>
  <!-- Open Graph (Facebook, LinkedIn) -->
  <meta property="og:title" content="My React App" />
  <meta property="og:description" content="A modern React application" />
  <meta property="og:image" content="https://myapp.com/og-image.jpg" />
  <meta property="og:url" content="https://myapp.com" />
  <meta property="og:type" content="website" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="My React App" />
  <meta name="twitter:description" content="A modern React application" />
  <meta name="twitter:image" content="https://myapp.com/og-image.jpg" />
</head>
```

For dynamic pages, use `react-helmet-async` (covered in Chapter 24):

```jsx
import { Helmet } from 'react-helmet-async';

function ProductDetailPage({ product }) {
  return (
    <>
      <Helmet>
        <title>{product.name} | My Store</title>
        <meta property="og:title" content={product.name} />
        <meta property="og:description" content={product.description} />
        <meta property="og:image" content={product.image} />
      </Helmet>
      {/* Page content */}
    </>
  );
}
```

**OG image guidelines:**

- Recommended size: 1200x630 pixels
- Format: JPEG or PNG
- Must use an absolute URL (including `https://`)
- Place in `public/` folder since social media crawlers access the URL directly

---

## Asset Organization

Here is a recommended asset structure for a medium-to-large project:

```
src/
├── assets/
│   ├── images/
│   │   ├── illustrations/      # Decorative illustrations
│   │   │   ├── empty-state.svg
│   │   │   ├── error-page.svg
│   │   │   └── onboarding.svg
│   │   ├── backgrounds/        # Background images
│   │   │   ├── hero-pattern.svg
│   │   │   └── gradient.jpg
│   │   └── logos/              # Brand logos
│   │       ├── logo-full.svg
│   │       ├── logo-icon.svg
│   │       └── logo-white.svg
│   ├── fonts/
│   │   ├── Inter-Regular.woff2
│   │   ├── Inter-Medium.woff2
│   │   └── Inter-Bold.woff2
│   └── styles/
│       ├── global.css          # Global styles
│       ├── fonts.css           # @font-face declarations
│       ├── reset.css           # CSS reset
│       └── variables.css       # CSS custom properties
│
public/
├── favicon.ico
├── favicon.svg
├── apple-touch-icon.png
├── og-image.jpg
├── robots.txt
├── site.webmanifest
└── images/
    ├── placeholder.jpg          # Fallback images
    └── default-avatar.png
```

### The Rule of Thumb

- **Import it** → use `src/assets/` (benefits from Vite processing)
- **Link to it** → use `public/` (needs a stable, predictable URL)

---

## Handling CSS and Style Assets

### Global Styles

Import order matters for CSS specificity. Establish a clear import chain:

```jsx
// src/main.jsx
import './assets/styles/reset.css';      // Reset first
import './assets/styles/variables.css';   // CSS variables
import './assets/styles/fonts.css';       // Font declarations
import './assets/styles/global.css';      // Global styles last

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './app/App';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

### CSS Variables File

Centralize your design tokens:

```css
/* src/assets/styles/variables.css */
:root {
  /* Colors */
  --color-primary: #3b82f6;
  --color-primary-dark: #2563eb;
  --color-primary-light: #93c5fd;
  --color-secondary: #8b5cf6;
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;

  /* Neutrals */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-500: #6b7280;
  --color-gray-700: #374151;
  --color-gray-900: #111827;

  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;

  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
  --transition-slow: 350ms ease;
}

/* Dark mode overrides */
[data-theme='dark'] {
  --color-gray-50: #111827;
  --color-gray-100: #1f2937;
  --color-gray-200: #374151;
  --color-gray-300: #4b5563;
  --color-gray-500: #9ca3af;
  --color-gray-700: #d1d5db;
  --color-gray-900: #f9fafb;
}
```

---

## Working with JSON and Data Files

You can import JSON files directly in Vite:

```jsx
// src/data/countries.json
// [
//   { "code": "US", "name": "United States" },
//   { "code": "CA", "name": "Canada" },
//   ...
// ]

import countries from './data/countries.json';

function CountrySelect({ value, onChange }) {
  return (
    <select value={value} onChange={onChange}>
      <option value="">Select a country</option>
      {countries.map(country => (
        <option key={country.code} value={country.code}>
          {country.name}
        </option>
      ))}
    </select>
  );
}
```

For large data files that are not always needed, load them dynamically:

```jsx
function CountrySelect({ value, onChange }) {
  const [countries, setCountries] = useState([]);

  useEffect(() => {
    import('./data/countries.json').then(module => {
      setCountries(module.default);
    });
  }, []);

  return (
    <select value={value} onChange={onChange}>
      <option value="">Select a country</option>
      {countries.map(country => (
        <option key={country.code} value={country.code}>
          {country.name}
        </option>
      ))}
    </select>
  );
}
```

---

## Mini Project: Asset-Optimized Landing Page

Let us build a landing page that demonstrates all the asset management techniques from this chapter.

### Project Structure

```
src/
├── assets/
│   ├── images/
│   │   ├── hero.jpg
│   │   ├── feature-speed.svg
│   │   ├── feature-secure.svg
│   │   └── feature-scale.svg
│   ├── fonts/
│   │   ├── Inter-Regular.woff2
│   │   └── Inter-Bold.woff2
│   └── styles/
│       ├── variables.css
│       └── global.css
├── shared/
│   └── components/
│       ├── Image/
│       │   ├── Image.jsx
│       │   ├── Image.module.css
│       │   └── index.js
│       └── icons/
│           ├── IconBase.jsx
│           ├── ArrowRight.jsx
│           ├── Check.jsx
│           ├── Star.jsx
│           └── index.js
├── features/
│   └── landing/
│       ├── components/
│       │   ├── HeroSection.jsx
│       │   ├── HeroSection.module.css
│       │   ├── FeatureCard.jsx
│       │   ├── FeatureCard.module.css
│       │   ├── FeaturesSection.jsx
│       │   ├── TestimonialCard.jsx
│       │   ├── TestimonialCard.module.css
│       │   ├── TestimonialsSection.jsx
│       │   └── CTASection.jsx
│       └── index.js
├── app/
│   └── App.jsx
└── main.jsx
```

### The Landing Page Components

```jsx
// src/features/landing/components/HeroSection.jsx
import heroImage from '../../../assets/images/hero.jpg';
import { ArrowRightIcon } from '@shared/components/icons';
import styles from './HeroSection.module.css';

export function HeroSection() {
  return (
    <section className={styles.hero}>
      <div className={styles.content}>
        <h1 className={styles.title}>
          Build Better Apps,{' '}
          <span className={styles.highlight}>Faster</span>
        </h1>
        <p className={styles.subtitle}>
          The modern platform for teams who ship great products.
          Start building today with zero configuration.
        </p>
        <div className={styles.actions}>
          <a href="/signup" className={styles.primaryButton}>
            Get Started Free
            <ArrowRightIcon size={18} />
          </a>
          <a href="/demo" className={styles.secondaryButton}>
            Watch Demo
          </a>
        </div>
      </div>
      <div className={styles.imageWrapper}>
        <img
          src={heroImage}
          alt="Dashboard showing app analytics and performance metrics"
          className={styles.image}
          loading="eager"
          fetchpriority="high"
          width={600}
          height={400}
        />
      </div>
    </section>
  );
}
```

```css
/* src/features/landing/components/HeroSection.module.css */
.hero {
  display: flex;
  align-items: center;
  gap: var(--space-12);
  padding: var(--space-12) var(--space-8);
  max-width: 1200px;
  margin: 0 auto;
}

.content {
  flex: 1;
}

.title {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  line-height: 1.2;
  color: var(--color-gray-900);
  margin: 0 0 var(--space-4);
}

.highlight {
  color: var(--color-primary);
}

.subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-gray-500);
  margin: 0 0 var(--space-8);
  line-height: 1.6;
}

.actions {
  display: flex;
  gap: var(--space-4);
}

.primaryButton {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  background-color: var(--color-primary);
  color: white;
  border-radius: var(--radius-lg);
  text-decoration: none;
  font-weight: 500;
  transition: background-color var(--transition-fast);
}

.primaryButton:hover {
  background-color: var(--color-primary-dark);
}

.secondaryButton {
  display: inline-flex;
  align-items: center;
  padding: var(--space-3) var(--space-6);
  border: 1px solid var(--color-gray-300);
  color: var(--color-gray-700);
  border-radius: var(--radius-lg);
  text-decoration: none;
  font-weight: 500;
  transition: border-color var(--transition-fast);
}

.secondaryButton:hover {
  border-color: var(--color-gray-500);
}

.imageWrapper {
  flex: 1;
}

.image {
  width: 100%;
  height: auto;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}

@media (max-width: 768px) {
  .hero {
    flex-direction: column;
    padding: var(--space-8) var(--space-4);
  }

  .title {
    font-size: var(--font-size-2xl);
  }

  .actions {
    flex-direction: column;
  }
}
```

```jsx
// src/features/landing/components/FeatureCard.jsx
import styles from './FeatureCard.module.css';

export function FeatureCard({ icon, title, description }) {
  return (
    <article className={styles.card}>
      <div className={styles.iconWrapper}>
        <img
          src={icon}
          alt=""
          width={48}
          height={48}
          loading="lazy"
        />
      </div>
      <h3 className={styles.title}>{title}</h3>
      <p className={styles.description}>{description}</p>
    </article>
  );
}
```

```css
/* src/features/landing/components/FeatureCard.module.css */
.card {
  padding: var(--space-6);
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-normal);
}

.card:hover {
  box-shadow: var(--shadow-md);
}

.iconWrapper {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-primary-light);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
}

.title {
  font-size: var(--font-size-xl);
  color: var(--color-gray-900);
  margin: 0 0 var(--space-2);
}

.description {
  font-size: var(--font-size-base);
  color: var(--color-gray-500);
  line-height: 1.6;
  margin: 0;
}
```

```jsx
// src/features/landing/components/FeaturesSection.jsx
import featureSpeed from '../../../assets/images/feature-speed.svg';
import featureSecure from '../../../assets/images/feature-secure.svg';
import featureScale from '../../../assets/images/feature-scale.svg';
import { FeatureCard } from './FeatureCard';

const features = [
  {
    icon: featureSpeed,
    title: 'Lightning Fast',
    description:
      'Built on modern infrastructure that delivers sub-second response times. Your users will feel the difference.',
  },
  {
    icon: featureSecure,
    title: 'Secure by Default',
    description:
      'Enterprise-grade security out of the box. SOC2 compliant with end-to-end encryption for all data.',
  },
  {
    icon: featureScale,
    title: 'Scales Automatically',
    description:
      'From 100 to 10 million users without changing a line of code. Auto-scaling infrastructure handles the rest.',
  },
];

export function FeaturesSection() {
  return (
    <section style={{ padding: 'var(--space-12) var(--space-8)' }}>
      <h2 style={{
        textAlign: 'center',
        fontSize: 'var(--font-size-2xl)',
        marginBottom: 'var(--space-8)',
        color: 'var(--color-gray-900)',
      }}>
        Why Teams Choose Us
      </h2>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: 'var(--space-6)',
        maxWidth: '1200px',
        margin: '0 auto',
      }}>
        {features.map(feature => (
          <FeatureCard key={feature.title} {...feature} />
        ))}
      </div>
    </section>
  );
}
```

```jsx
// src/features/landing/components/TestimonialCard.jsx
import { Image } from '@shared/components/Image';
import { StarIcon } from '@shared/components/icons';
import styles from './TestimonialCard.module.css';

export function TestimonialCard({ testimonial }) {
  return (
    <article className={styles.card}>
      <div className={styles.stars}>
        {Array.from({ length: 5 }).map((_, i) => (
          <StarIcon
            key={i}
            size={16}
            color={i < testimonial.rating ? '#f59e0b' : '#d1d5db'}
            fill={i < testimonial.rating ? '#f59e0b' : 'none'}
          />
        ))}
      </div>
      <blockquote className={styles.quote}>
        "{testimonial.text}"
      </blockquote>
      <div className={styles.author}>
        <Image
          src={testimonial.avatar}
          alt={`${testimonial.name}'s photo`}
          width={40}
          height={40}
          className={styles.avatar}
          fallback="/images/default-avatar.png"
        />
        <div>
          <p className={styles.name}>{testimonial.name}</p>
          <p className={styles.role}>{testimonial.role}</p>
        </div>
      </div>
    </article>
  );
}
```

```css
/* src/features/landing/components/TestimonialCard.module.css */
.card {
  padding: var(--space-6);
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.stars {
  display: flex;
  gap: 2px;
  margin-bottom: var(--space-3);
}

.quote {
  font-size: var(--font-size-base);
  color: var(--color-gray-700);
  line-height: 1.6;
  margin: 0 0 var(--space-4);
  font-style: italic;
}

.author {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  object-fit: cover;
}

.name {
  font-weight: 500;
  color: var(--color-gray-900);
  margin: 0;
  font-size: var(--font-size-sm);
}

.role {
  color: var(--color-gray-500);
  margin: 0;
  font-size: var(--font-size-xs);
}
```

```jsx
// src/features/landing/components/TestimonialsSection.jsx
import { TestimonialCard } from './TestimonialCard';

const testimonials = [
  {
    name: 'Sarah Chen',
    role: 'CTO at TechStart',
    avatar: 'https://i.pravatar.cc/80?img=1',
    rating: 5,
    text: 'We migrated our entire platform in two weeks. The developer experience is unmatched.',
  },
  {
    name: 'Marcus Johnson',
    role: 'Lead Developer at ScaleUp',
    avatar: 'https://i.pravatar.cc/80?img=3',
    rating: 5,
    text: 'Finally, a platform that scales without the DevOps headaches. Our team ships twice as fast now.',
  },
  {
    name: 'Emily Rodriguez',
    role: 'Product Manager at BuildCo',
    avatar: 'https://i.pravatar.cc/80?img=5',
    rating: 4,
    text: 'The built-in analytics alone saved us $50K per year. Everything just works out of the box.',
  },
];

export function TestimonialsSection() {
  return (
    <section style={{
      padding: 'var(--space-12) var(--space-8)',
      backgroundColor: 'var(--color-gray-50)',
    }}>
      <h2 style={{
        textAlign: 'center',
        fontSize: 'var(--font-size-2xl)',
        marginBottom: 'var(--space-8)',
        color: 'var(--color-gray-900)',
      }}>
        Loved by Developers
      </h2>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: 'var(--space-6)',
        maxWidth: '1200px',
        margin: '0 auto',
      }}>
        {testimonials.map(testimonial => (
          <TestimonialCard
            key={testimonial.name}
            testimonial={testimonial}
          />
        ))}
      </div>
    </section>
  );
}
```

```jsx
// src/features/landing/components/CTASection.jsx
import { ArrowRightIcon } from '@shared/components/icons';

export function CTASection() {
  return (
    <section style={{
      padding: 'var(--space-12) var(--space-8)',
      textAlign: 'center',
      background: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))',
      color: 'white',
    }}>
      <h2 style={{ fontSize: 'var(--font-size-2xl)', marginBottom: 'var(--space-4)' }}>
        Ready to Get Started?
      </h2>
      <p style={{
        fontSize: 'var(--font-size-lg)',
        marginBottom: 'var(--space-8)',
        opacity: 0.9,
        maxWidth: '600px',
        margin: '0 auto var(--space-8)',
      }}>
        Join thousands of teams building better products.
        Free for teams up to 5 members.
      </p>
      <a
        href="/signup"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 'var(--space-2)',
          padding: 'var(--space-3) var(--space-8)',
          backgroundColor: 'white',
          color: 'var(--color-primary)',
          borderRadius: 'var(--radius-lg)',
          textDecoration: 'none',
          fontWeight: 600,
          fontSize: 'var(--font-size-lg)',
        }}
      >
        Start Building
        <ArrowRightIcon size={20} />
      </a>
    </section>
  );
}
```

```jsx
// src/features/landing/index.js
export { HeroSection } from './components/HeroSection';
export { FeaturesSection } from './components/FeaturesSection';
export { TestimonialsSection } from './components/TestimonialsSection';
export { CTASection } from './components/CTASection';
```

### The Landing Page

```jsx
// src/pages/LandingPage.jsx
import { Helmet } from 'react-helmet-async';
import {
  HeroSection,
  FeaturesSection,
  TestimonialsSection,
  CTASection,
} from '@features/landing';

export default function LandingPage() {
  return (
    <>
      <Helmet>
        <title>MyApp — Build Better Apps, Faster</title>
        <meta
          name="description"
          content="The modern platform for teams who ship great products. Start building today."
        />
        <meta property="og:title" content="MyApp — Build Better Apps, Faster" />
        <meta property="og:image" content="https://myapp.com/og-image.jpg" />
      </Helmet>

      <main>
        <HeroSection />
        <FeaturesSection />
        <TestimonialsSection />
        <CTASection />
      </main>
    </>
  );
}
```

This landing page demonstrates:

- **Imported images** for the hero and feature icons (with cache busting)
- **SVG icons** as React components (with dynamic sizing and colors)
- **Lazy-loaded images** for testimonial avatars
- **Eager-loaded hero image** with `fetchPriority="high"`
- **CSS variables** for consistent design tokens
- **CSS Modules** for scoped styles
- **`react-helmet-async`** for SEO meta tags
- **Feature-based architecture** with barrel exports
- **Error handling** with image fallbacks

---

## Common Mistakes

### Mistake 1: Storing Secrets in VITE_ Variables

```bash
# WRONG — this is visible in the browser's JavaScript
VITE_STRIPE_SECRET_KEY=sk_live_abc123
VITE_DB_PASSWORD=mypassword

# RIGHT — only use public keys on the client
VITE_STRIPE_PUBLIC_KEY=pk_live_abc123
```

Client-side environment variables are embedded in the built JavaScript. Anyone can view them in the browser's DevTools. Secret keys must only be used on your backend server.

### Mistake 2: Missing Image Dimensions

```jsx
// Bad — causes layout shift as images load
<img src={product.image} alt={product.name} loading="lazy" />

// Good — browser reserves space before image loads
<img
  src={product.image}
  alt={product.name}
  loading="lazy"
  width={400}
  height={300}
/>
```

Without `width` and `height`, the browser does not know how much space to allocate. When the image loads, content below it jumps down. This is called Cumulative Layout Shift (CLS) and hurts both user experience and SEO.

### Mistake 3: Lazy Loading Above-the-Fold Images

```jsx
// Bad — hero image should load immediately
<img src={hero} alt="Hero" loading="lazy" />

// Good — hero image loads eagerly with high priority
<img src={hero} alt="Hero" loading="eager" fetchpriority="high" />
```

The hero image is the first thing users see. Making it lazy means it loads after other resources, creating a visible delay.

### Mistake 4: Importing from `public/` Folder

```jsx
// Wrong — Vite cannot process files referenced by string path
<img src="/src/assets/logo.png" />    // Will break in production
import logo from '/public/logo.png';   // Wrong path

// Right — import from src/assets
import logo from './assets/logo.png';  // Vite processes this

// Right — reference public files with absolute paths
<img src="/logo.png" />                // Files in public/
```

### Mistake 5: Not Using `.env.example`

Without a `.env.example` file, new team members have no idea what environment variables are needed. They clone the repo, run `npm run dev`, and get cryptic errors about undefined variables.

Always maintain a `.env.example` with all variable names and safe default values.

---

## Best Practices

1. **Import images used in components** rather than referencing them from `public/`. You get cache busting, build-time error detection, and optimization.

2. **Use the `public/` folder sparingly** — only for files that need predictable URLs (favicons, robots.txt, OG images) or files referenced directly in `index.html`.

3. **Always provide `alt` text for images.** Decorative images should have `alt=""` (empty string, not missing). Meaningful images should describe their content.

4. **Include `width` and `height` on all images** to prevent layout shift. If the exact dimensions vary, use CSS `aspect-ratio` instead.

5. **Lazy load images below the fold.** Use `loading="lazy"` for product grids, testimonials, and any content users scroll to see.

6. **Centralize environment variables** in a configuration module. Access them from one place instead of scattering `import.meta.env` throughout the codebase.

7. **Validate required environment variables** at application startup. Fail fast with a clear error message rather than encountering undefined values at runtime.

8. **Never commit `.env` files** to version control. Commit `.env.example` instead with placeholder values.

9. **Use SVG components for icons** that need dynamic styling. Use `<img>` tags for complex illustrations and decorative SVGs that do not need to change.

10. **Prefer WOFF2 for fonts** and use `font-display: swap` to prevent invisible text during font loading.

---

## Summary

Managing assets and environment variables well is an essential but often overlooked part of React development. The key decisions come down to understanding how Vite processes files.

Images you import in JavaScript get hashed filenames and cache busting — use this for any image referenced by your components. Files in the `public/` folder keep their exact names — use this for favicons, social media images, and files that need predictable URLs.

SVGs offer flexibility: use them as `<img>` sources for simple display, or as React components when you need dynamic styling and animation. Building an icon system with a shared base component keeps your icon usage consistent and maintainable.

Environment variables with the `VITE_` prefix are embedded in your JavaScript at build time. They are always strings, always public, and should never contain secrets. Centralize them in a configuration module, validate them at startup, and document them in a `.env.example` file.

Image optimization — choosing the right format, providing dimensions, using `loading="lazy"` for below-fold content, and serving responsive sizes with `srcSet` — directly impacts your application's performance and user experience.

---

## Interview Questions

1. **What is the difference between importing an image and placing it in the `public/` folder in a Vite React project?**

   *Imported images are processed by Vite's build pipeline: they get hashed filenames for cache busting, can be inlined as data URLs if small enough, and produce build errors if missing. Files in `public/` are copied as-is to the build output with their original filenames. Use imports for component images and `public/` for files needing predictable URLs like favicons and OG images.*

2. **How do environment variables work in a Vite React application?**

   *Vite loads variables from `.env` files. Only variables prefixed with `VITE_` are exposed to client-side code — this prevents accidental exposure of server secrets. Variables are accessed via `import.meta.env.VITE_NAME` and are always strings, requiring explicit conversion for numbers and booleans. They are embedded at build time, meaning different builds are needed for different environments. Vite also provides built-in variables like `import.meta.env.DEV` and `import.meta.env.PROD`.*

3. **How would you optimize images in a React application for performance?**

   *Several strategies: use modern formats like WebP and AVIF with `<picture>` element fallbacks; provide `width` and `height` attributes to prevent layout shift; use `loading="lazy"` for below-fold images and `loading="eager"` with `fetchPriority="high"` for hero images; serve responsive sizes with `srcSet` and `sizes`; let Vite inline small images as data URLs; and compress images before adding them to the project.*

4. **What are the different ways to use SVGs in a React application, and when would you choose each?**

   *Three main approaches: (1) Import as an image URL and use in `<img>` tag — simple display, cached separately, but no dynamic styling; (2) Create SVG React components manually — full control over styling with props for color and size; (3) Use a plugin like `vite-plugin-svgr` to import SVGs as components directly. Choose `<img>` for complex illustrations, React components for icons that need dynamic styling, and the plugin approach for convenience when you have many SVGs to componentize.*

5. **Why should you never store secrets in client-side environment variables?**

   *Client-side environment variables in Vite (VITE_ prefixed) are embedded directly into the JavaScript bundle at build time. Anyone can view them by inspecting the page source or using browser DevTools. Secret keys, API secrets, database credentials, and passwords must only live on the server. Client-side variables should only contain public information like API base URLs, public API keys (like Stripe publishable keys), and feature flags.*

---

## Practice Exercises

### Exercise 1: Image Gallery Component

Build an image gallery that:

- Accepts an array of image objects (`{ src, alt, width, height }`)
- Displays images in a responsive grid
- Lazy loads all images except the first row
- Shows a shimmer placeholder while images load
- Falls back to a placeholder on error
- Uses the `<picture>` element with WebP sources

### Exercise 2: Environment Configuration

Set up a complete environment configuration system:

1. Create `.env`, `.env.development`, `.env.production`, and `.env.example` files
2. Build a `config` module that centralizes all variables with type conversion
3. Add a validation function that checks for required variables at startup
4. Create a `ConfigDebug` component that shows current configuration in development mode (hidden in production)

### Exercise 3: Icon Library

Create an icon library with at least 10 icons:

1. Build a shared `IconBase` component that handles size, color, and accessibility
2. Create 10 icon components using the base (arrows, check, close, search, etc.)
3. Add a barrel export for clean imports
4. Build a demo page that shows all icons with different sizes and colors
5. Add `aria-hidden="true"` for decorative icons and `role="img"` with `aria-label` for meaningful ones

### Exercise 4: Responsive Hero Section

Build a responsive hero section that:

- Uses `srcSet` to serve 3 different image sizes (mobile, tablet, desktop)
- Loads the hero image eagerly with high priority
- Shows the image at the correct aspect ratio before it loads
- Includes proper OG meta tags using `react-helmet-async`
- Adapts layout from single column (mobile) to two columns (desktop)

### Exercise 5: Font Loading Strategy

Implement a font loading strategy:

1. Download a Google Font as WOFF2 files
2. Create `@font-face` declarations with `font-display: swap`
3. Set up font fallback stacks with system fonts
4. Create a `useFontLoaded` hook that detects when the custom font has loaded using the Font Loading API (`document.fonts.ready`)
5. Show a subtle transition when fonts swap

---

## What Is Next?

In Chapter 27, we will explore **React Best Practices and Common Mistakes** — a comprehensive collection of patterns, anti-patterns, and guidelines that experienced React developers follow. We will cover component design principles, state management rules of thumb, performance habits, code organization wisdom, and the most common pitfalls that trip up developers at every level.
