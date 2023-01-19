FROM nginx:1.17.6
# Remove default Nginx config
RUN rm /etc/nginx/nginx.conf
# Copy the modified Nginx conf
COPY docker/nginx/nginx.conf /etc/nginx
# Copy proxy config
COPY docker/nginx/hazen.conf /etc/nginx/sites-enabled/
