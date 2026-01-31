FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

# Create .env.local with API URL for production
RUN echo "NEXT_PUBLIC_API_URL=http://api:8000/api/v1" > .env.local

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
