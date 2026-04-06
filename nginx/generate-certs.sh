#!/bin/sh
# Generate self-signed certs for nginx if they don't exist
CERT_DIR=/etc/nginx/certs
if [ ! -f "$CERT_DIR/server.crt" ]; then
    mkdir -p "$CERT_DIR"
    openssl req -x509 -nodes -days 3650 \
        -newkey rsa:2048 \
        -keyout "$CERT_DIR/server.key" \
        -out "$CERT_DIR/server.crt" \
        -subj "/CN=localhost/O=NID Mapping Service"
    echo "Self-signed certificates generated."
else
    echo "Certificates already exist, skipping."
fi

# Start nginx
exec nginx -g 'daemon off;'
