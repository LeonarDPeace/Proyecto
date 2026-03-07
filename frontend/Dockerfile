FROM node:20-alpine AS base

WORKDIR /app

# Dependencias
COPY package.json package-lock.json* ./
RUN npm ci --prefer-offline

# Código fuente
COPY . .

# Desarrollo
EXPOSE 3000

CMD ["npm", "run", "dev"]
