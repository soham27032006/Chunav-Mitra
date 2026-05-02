# API Configuration Guide

## Overview

This document explains how the API configuration works in Chunav Mitra and how to switch between development and production environments.

## Architecture

### Centralized API Layer

All API calls are centralized in `src/lib/api.ts`. This ensures consistency and makes it easy to change the backend URL in one place.

```typescript
// src/lib/api.ts
const PRODUCTION_URL = "https://chunav-mitra-av4k.onrender.com";
const DEVELOPMENT_URL = "http://localhost:8000";

const BASE_URL: string =
  import.meta.env?.VITE_API_BASE_URL || PRODUCTION_URL;
```

### File Structure

```
src/
├── lib/
│   └── api.ts          # Centralized API configuration and methods
├── routes/
│   ├── chat.tsx        # Uses api.ask(), api.streamAskUrl(), api.translateBatch()
│   ├── voter-check.tsx # Uses api.checkVoter()
│   ├── booth.tsx       # Uses api.findBooth()
│   ├── timeline.tsx    # Uses api.timeline()
│   └── dictionary.tsx  # Uses api.explain()
├── hooks/
│   └── useSpeechToText.ts  # Uses api.transcribe()
└── ...
```

## Environment Variables

### Vite Environment Variables

Vite uses environment variables prefixed with `VITE_` to make them available in the client-side code.

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | Production URL |

### Configuration Files

#### `.env` (Active Configuration)
```bash
# Production (current)
VITE_API_BASE_URL=https://chunav-mitra-av4k.onrender.com

# For local development, uncomment:
# VITE_API_BASE_URL=http://localhost:8000
```

#### `.env.example` (Template)
Contains documentation and both development/production examples.

## How to Switch Environments

### Option 1: Edit .env File (Recommended)

```bash
# For local development:
VITE_API_BASE_URL=http://localhost:8000

# For production build:
VITE_API_BASE_URL=https://chunav-mitra-av4k.onrender.com
```

Then restart the dev server:
```bash
npm run dev
```

### Option 2: Use Environment-Specific .env Files

Create separate files for different environments:

**`.env.development`** (for `npm run dev`):
```bash
VITE_API_BASE_URL=http://localhost:8000
```

**`.env.production`** (for `npm run build`):
```bash
VITE_API_BASE_URL=https://chunav-mitra-av4k.onrender.com
```

Vite automatically loads the appropriate file based on the command.

### Option 3: Command-Line Override

```bash
# Development with local backend
VITE_API_BASE_URL=http://localhost:8000 npm run dev

# Production build with specific backend
VITE_API_BASE_URL=https://chunav-mitra-av4k.onrender.com npm run build
```

## API Methods Available

All methods are available via the `api` object imported from `@/lib/api`:

```typescript
import { api } from "@/lib/api";

// Chat
api.ask(query, sessionId?, lang?)           // POST /api/ask
api.streamAskUrl(query, sessionId?, lang?)  // GET /api/ask/stream

// Voter Services
api.checkVoter({ name, state, dob })        // POST /api/check-voter
api.findBooth({ pincode?, lat?, lng? })     // POST /api/find-booth

// Information
api.timeline()                               // GET /api/timeline
api.explain(topic, lang?)                   // POST /api/explain
api.stats()                                  // GET /api/stats

// Speech & Translation
api.transcribe(audioBlob, lang)             // POST /api/transcribe
api.translateBatch(texts[], targetLang)     // POST /api/translate
```

## Build & Deploy Workflow

### Before Building for Production

1. **Verify .env has production URL:**
   ```bash
   cat .env | grep VITE_API_BASE_URL
   # Should output: VITE_API_BASE_URL=https://chunav-mitra-av4k.onrender.com
   ```

2. **Build the project:**
   ```bash
   npm run build
   ```

3. **Test the build locally:**
   ```bash
   npm run preview
   ```

4. **Verify API calls in browser DevTools:**
   - Open Network tab
   - Trigger an API call
   - Confirm requests go to `https://chunav-mitra-av4k.onrender.com`

### Deploy Checklist

- [ ] `.env` file has production URL
- [ ] Build completes without errors
- [ ] Preview shows app working correctly
- [ ] API calls use production URL
- [ ] No localhost references in built files

## Troubleshooting

### API Calls Still Going to Localhost

**Cause:** Environment variable not picked up

**Solution:**
1. Stop the dev server
2. Clear Vite cache: `rm -rf node_modules/.vite`
3. Restart: `npm run dev`

### "undefined" in API URLs

**Cause:** `import.meta.env` not properly typed

**Solution:** The `api.ts` file already includes proper typing. If you see this issue, check that you're accessing `import.meta.env.VITE_API_BASE_URL` correctly.

### CORS Errors

**Cause:** Backend not allowing frontend origin

**Solution:** Ensure your backend (`https://chunav-mitra-av4k.onrender.com`) includes the frontend origin in its CORS configuration.

## Best Practices

1. **Always use the `api` object** - Never make direct `fetch()` calls to backend URLs
2. **Use environment variables** - Don't hardcode URLs in components
3. **Test in preview mode** - Always run `npm run preview` before deploying
4. **Document changes** - Update this file when adding new API endpoints
5. **Keep .env.example updated** - It's the source of truth for new developers

## Quick Reference

| Task | Command |
|------|---------|
| Dev with local backend | Set `VITE_API_BASE_URL=http://localhost:8000` in `.env`, then `npm run dev` |
| Dev with production backend | Set `VITE_API_BASE_URL=https://chunav-mitra-av4k.onrender.com` in `.env`, then `npm run dev` |
| Build for production | Ensure production URL in `.env`, then `npm run build` |
| Test production build | `npm run preview` |
