FROM node:14.15-alpine as builder

# Set working directory.
RUN mkdir /app
WORKDIR /app

# Copy app dependecies.
COPY angular/package.json angular/package-lock.json /app/angular/

# Install app dependecies.
RUN npm install --prefix angular

# Copy all files.
COPY . /app

# Build app.
RUN npm run build --prefix angular -- --output-path=./dist/out

FROM nginx:1.15.7-alpine

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy output directory from builder to nginx image.
COPY --from=builder /app/angular/dist/out /usr/share/nginx/html

# Copy nginx configuration file.
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 4200