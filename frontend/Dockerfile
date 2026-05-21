FROM node:22-alpine

WORKDIR /app

# Install dependencies first so this layer is cached across source changes.
COPY package.json ./
RUN npm install

COPY . ./

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
