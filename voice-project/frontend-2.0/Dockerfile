# syntax=docker/dockerfile:1.7

# ─── Stage 1: Build ──────────────────────────────────────────────────────────
FROM oven/bun:1.1-alpine AS builder

WORKDIR /app

COPY package.json bun.lockb* package-lock.json* ./
RUN bun install --frozen-lockfile || bun install

# Build → Cloudflare plugin emits a self-contained Worker bundle in dist/
COPY . .
RUN bun run build

# ─── Stage 2: Runtime ────────────────────────────────────────────────────────
# Wrangler's local runtime binary is not reliable on Alpine/musl. Use Debian
# so the bundled runtime can start correctly inside the container.
FROM node:20-bookworm-slim AS runner

WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000

# Wrangler v4 to serve the built Worker bundle
RUN npm install -g wrangler@4

# Copy the entire build output (contains the emitted worker + its wrangler.json)
COPY --from=builder /app/dist ./dist

EXPOSE 3000

# The Cloudflare Vite plugin emits a deployable bundle under dist/<worker-name>/
# with its own wrangler.json. Locate it and run wrangler dev against THAT config
# (NOT the source wrangler.jsonc, whose `main` is a Vite virtual module).
CMD ["sh", "-c", "CFG=$(find dist -maxdepth 3 -name wrangler.json | head -n1); \
  echo \"Serving worker from: $CFG\"; \
  wrangler dev --config \"$CFG\" --ip 0.0.0.0 --port ${PORT}"]
