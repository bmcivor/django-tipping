FROM node:24.18-alpine AS base

WORKDIR /app

COPY package.json .

RUN npm install

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM base AS test

COPY . .

CMD ["npm", "run", "test"]

FROM base AS production

COPY . .

RUN npm run build

EXPOSE 3000

CMD [ "serve", "-s", "dist" ]
