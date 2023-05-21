FROM node:18.15.0 AS builder

RUN mkdir /angular
WORKDIR /angular
COPY ./angular/package*.json ./

RUN npm install -g @angular/cli@15.2.4 && npm ci

COPY ./angular .
RUN npm run build

FROM nginx:stable

COPY --from=builder /angular/dist/chess/ /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
