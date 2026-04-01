# frontend/Dockerfile
# Multi-stage build for Next.js

FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# For Next.js, NEXT_PUBLIC_* values are baked at build time.
# We rely on the API being reachable at /api via reverse proxy in production.
ENV NEXT_PUBLIC_API_BASE_URL=/api
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# If you use standalone output, you can copy .next/standalone. Here we keep default.
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "run", "start", "--", "-p", "3000"]
