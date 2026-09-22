# Build the dashboard inside the pnpm workspace (context = repository root).
FROM node:24-alpine AS build
WORKDIR /app

RUN npm install -g pnpm@12

# Workspace manifests first for layer caching.
COPY pnpm-workspace.yaml pnpm-lock.yaml package.json ./
COPY ui/package.json ui/
COPY web/package.json web/
RUN pnpm install --frozen-lockfile

# Sources (web consumes the ui package from source).
COPY ui ./ui
COPY web ./web

ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

RUN pnpm --filter seb-xrif-web build

# Serve the static bundle with nginx and proxy /api to the API service.
FROM nginx:alpine
COPY web/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/web/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
