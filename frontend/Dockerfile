# Etapa de compilación
FROM node:18-alpine AS build

WORKDIR /app

# Copiar archivos de configuración e instalar dependencias
COPY package*.json ./
RUN npm ci

# Copiar el código del frontend y compilar
COPY . .
RUN npm run build

# Etapa de producción
FROM nginx:alpine

# Copiar el build del frontend a la carpeta pública de Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Configurar Nginx para que escuche en el puerto 3000
RUN sed -i 's/listen\(.*\)80;/listen 3000;/g' /etc/nginx/conf.d/default.conf

# Exponer el puerto
EXPOSE 3000

# Iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
