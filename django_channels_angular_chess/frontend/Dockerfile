FROM node:lts-alpine AS builder

WORKDIR /app/

COPY angular/package.json ./

RUN npm install

COPY ./angular /app

RUN npm run build

FROM nginx:stable-alpine

EXPOSE 80

COPY --from=builder /app/dist/chess/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
