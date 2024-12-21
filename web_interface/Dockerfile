# Build React app
FROM node:16 as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Setup server
FROM node:16-slim
WORKDIR /app
COPY --from=build /app/build ./build
COPY server ./server
COPY package*.json ./
RUN npm install express pg cors react-scripts @testing-library/react
ENV NODE_ENV=production
EXPOSE 3001
CMD ["node", "server/server.js"]
