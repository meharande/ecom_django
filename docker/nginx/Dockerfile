FROM nginx:stable-alpine

# Copy custom nginx config
COPY default.conf /etc/nginx/conf.d/default.conf

# Create directory for static files mountpoint
RUN mkdir -p /vol/static

EXPOSE 80 443
