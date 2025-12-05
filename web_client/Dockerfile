# Dockerfile pour le Client Web
FROM nginx:alpine

# Copier les fichiers du client web
COPY index.html /usr/share/nginx/html/
COPY orchestration.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/
COPY auth.js /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/
COPY test.html /usr/share/nginx/html/

# Exposer le port 80
EXPOSE 80

# Nginx démarre automatiquement
