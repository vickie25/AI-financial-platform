FROM node:20.11.0-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    openssl && \
    rm -rf /var/lib/apt/lists/*

RUN npm ci

RUN npx prisma generate

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
