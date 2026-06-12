FROM node:20-alpine AS builder

ARG EXPO_PUBLIC_API_URL=/api
ENV EXPO_PUBLIC_API_URL=$EXPO_PUBLIC_API_URL

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npx expo export --platform web --output-dir dist

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
