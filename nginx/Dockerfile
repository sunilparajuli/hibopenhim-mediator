FROM nginx:alpine
RUN apk add --no-cache openssl
COPY default.conf /etc/nginx/conf.d/default.conf
COPY generate-certs.sh /docker-entrypoint.d/generate-certs.sh
RUN chmod +x /docker-entrypoint.d/generate-certs.sh
