# Stage 1: build the static bundle with Vite+ (Vite 8 + Rolldown + Oxc)
FROM node:24-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
# The project declares npm 12 via devEngines; the base image ships npm 11.
RUN npm install -g npm@12 && npm ci

COPY . .

ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

# `vp` resolves from the local vite-plus install (node_modules/.bin/vp).
RUN npx vp build

# Stage 2: serve with nginx and proxy /api to the API service
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
