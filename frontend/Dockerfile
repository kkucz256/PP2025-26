FROM node:18-alpine

WORKDIR /app

# Install minimal static server
COPY package.json ./
RUN npm install --production

COPY . .

EXPOSE 3000
CMD ["npm", "start"]