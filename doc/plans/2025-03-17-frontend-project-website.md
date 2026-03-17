# Plan: Frontend Project Website

**Date:** 2025-03-17  
**Scope:** Plan to build a frontend project website for YellowPages (discover/execute MCP server).

---

## 1. Goal

Deliver a frontend project website that:

- Presents YellowPages to visitors (what it is, why it exists, how it works).
- Provides clear setup and usage instructions (e.g. Cursor MCP config, env vars).
- Optionally offers a lightweight “try it” experience (discover/execute in the browser) if the MCP server is exposed via streamable-http.

The plan is scoped so work can be broken into discrete tickets (repo setup, landing, docs, optional demo UI).

---

## 2. Context

- **YellowPages:** MCP server with two tools: `discover_operations` (RAG over OpenAPI schema) and `execute_operation` (run operation by ID with params). No LLM in the server; the caller agent chooses operations and parameters.
- **Current surface:** README, `docs/`, Python backend (UV, FastMCP, Chroma, sentence-transformers). No web UI today.
- **Audience:** Developers and agent builders who want to discover and execute API operations via natural language (e.g. from Cursor or other MCP hosts).

---

## 3. Proposed Scope

### 3.1 In scope

- **Landing/marketing page:** Hero, value proposition, “how it works” (index once, then discover + execute), link to docs/setup.
- **Docs section:** Quick start, environment variables, adding to Cursor (or other MCP hosts), schema format. Can mirror and extend README content.
- **Static site:** Deployable to GitHub Pages, Netlify, or similar (no backend required for landing + docs).
- **Optional Phase 2:** Simple “try it” UI that calls an HTTP-backed YellowPages server (e.g. `YELLOW_PAGES_TRANSPORT=streamable-http`) to run discover and optionally execute, for demo purposes only.

### 3.2 Out of scope (for this plan)

- Full API playground with auth or production traffic.
- Backend changes to the MCP server (beyond existing streamable-http support).
- Hosting or CI/CD implementation (can be separate tickets).

---

## 4. Technology and Structure

- **Stack:** Static site generator or minimal SPA. Options: Vite + React, Astro, or 11ty. Recommendation: **Vite + React** for consistency with common frontend tooling and easy optional “try it” UI later; or **Astro** if content-heavy and SEO/performance are priority.
- **Repo layout:** Either:
  - **Monorepo:** e.g. `frontend/` or `website/` at repo root with its own `package.json`, build, and deploy config; or
  - **Separate repo:** Dedicated `yellow-pages-website` repo that references this repo for copy and links. Prefer monorepo unless there is a strong reason to split (e.g. different release cadence or owners).
- **Content:** Markdown or MDX for docs; copy derived from README and `docs/` where possible.
- **Styling:** Tailwind or simple CSS; avoid heavy UI frameworks unless needed for the optional demo UI.

---

## 5. Phased Tasks (ticket outline)

Tasks below can be turned into individual issues (e.g. in Paperclip or GitHub).

| Phase | Task | Description |
|-------|------|-------------|
| **0** | Frontend project setup | Create `website/` (or `frontend/`) with Vite/React or Astro, add `package.json`, base layout, and a single index route. Document how to run and build locally. |
| **1a** | Landing page | Implement landing: hero, value prop, “how it works” (indexer + discover + execute), CTA to docs. Use content from README. |
| **1b** | Docs section | Add docs routes/pages: Quick start, Env vars, Adding to Cursor, Schema format. Reuse or adapt README and existing `docs/` content. |
| **1c** | Navigation and footer | Global nav (Home, Docs), footer with repo link and minimal legal/links if needed. |
| **2** | Deploy pipeline (optional) | Add GitHub Actions (or similar) to build and deploy to GitHub Pages / Netlify. Branch and path conventions documented. |
| **3** | “Try it” UI (optional) | Page that allows entering a natural-language query, calling discover (and optionally execute) against a configurable YellowPages HTTP endpoint. Clearly label as demo; no auth or production guarantees. |

Phases 0, 1a, 1b, 1c are the minimum for a usable frontend project website. Phases 2 and 3 can be separate follow-up tickets.

---

## 6. Success Criteria

- Visitors can learn what YellowPages is and how to use it without reading the repo only.
- Setup and Cursor integration are documented on the site.
- Site builds and runs locally; deploy (Phase 2) is optional but recommended.
- Optional “try it” (Phase 3) works against a streamable-http YellowPages instance when provided.

---

## 7. Open Questions

- **Domain/hosting:** GitHub Pages under org/repo, or custom domain? (Can be decided when implementing Phase 2.)
- **Try-it endpoint:** Should the demo UI point to a fixed public demo instance or require the user to supply a URL? Recommendation: user-supplied URL (or env) to avoid operating a public demo backend in this plan.

---

## 8. Next Steps

1. Approve or adjust this plan (scope, stack, repo layout).
2. Create tickets for Phase 0 and Phase 1 (setup, landing, docs, nav).
3. Implement Phase 0 and 1a–1c; then optionally Phase 2 (deploy) and Phase 3 (try-it UI).
