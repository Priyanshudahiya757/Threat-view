# =============================================================================
# Stage 1: Build — Node + Vite production bundle
# =============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

ARG VITE_API_URL=http://localhost:5000/api
ENV VITE_API_URL=$VITE_API_URL

COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

COPY . .
RUN npm run build

# =============================================================================
# Stage 2: Runtime — Nginx serving the static bundle
# =============================================================================
FROM nginx:1.27-alpine AS runtime

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built SPA
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx config (SPA fallback, gzip, security headers)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
