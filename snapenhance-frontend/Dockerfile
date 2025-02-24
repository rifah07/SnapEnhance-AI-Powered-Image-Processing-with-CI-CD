#use an official Node.js runtime as a parent image
FROM node:18-alpine AS build

# Set the working directory
WORKDIR /app

#copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install --frozen-lockfile

#copy the rest of the application files
COPY . .

#build the React app
RUN npm run build

#use Nginx for serving the static files
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html

#expose port 80
EXPOSE 80

#Start Nginx
CMD ["nginx", "-g", "daemon off;"]
