FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production image
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies only
RUN npm ci --only=production

# Copy built application
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/next.config.js ./
# Create empty public directory (Next.js doesn't require it, but some configs expect it)
RUN mkdir -p ./public

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]

