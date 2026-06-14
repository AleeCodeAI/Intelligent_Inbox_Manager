# Stage 1: Build the React application
FROM node:20-alpine AS builder

WORKDIR /app

# Layer Caching: Copy package files first so npm ci is cached unless packages change
COPY package.json package-lock.json ./
RUN npm ci

# Copy the rest of the application code
COPY . .

# Build the Vite project (outputs to /app/dist)
RUN npm run build

# Stage 2: Serve the static files with Nginx
FROM nginx:alpine

# Copy the compiled static assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy the custom nginx configuration for Single Page Application (SPA) routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Nginx default HTTP port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]