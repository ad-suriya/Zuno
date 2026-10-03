# Cloud Run image for the frontend (Next.js standalone output).
# NEXT_PUBLIC_* values are baked into the browser bundle at build time, so pass the API URL as a build arg:
#   docker build --build-arg NEXT_PUBLIC_API_BASE_URL=https://zuno-backend-xyz.a.run.app -t zuno-frontend frontend
FROM node:22-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:22-slim
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
USER node
# Cloud Run sets $PORT; server.js reads it.
CMD ["node", "server.js"]
