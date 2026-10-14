# =========================================================================
# BizMind Frontend Dockerfile
# Multi-stage production build: Node.js 20 build -> Nginx Alpine runtime
# =========================================================================

# Stage 1: Build the production static bundle
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency locks and install dependencies reproducibly
COPY package.json package-lock.json ./
RUN npm ci

# Copy frontend source code
COPY . .

# Build production bundle using Vite + TypeScript
RUN npm run build

# Stage 2: Serve production bundle with Nginx reverse proxy
FROM nginx:1.27-alpine

# Remove default nginx welcome page
RUN rm -rf /usr/share/nginx/html/*

# Copy built distribution assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy tailored Nginx reverse proxy configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost/nginx-health || exit 1

CMD ["nginx", "-g", "daemon off;"]
