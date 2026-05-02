#!/bin/sh

# Port configurable : 7860 par défaut (HF Spaces), override via PORT env var (80 en local via docker-compose)
PORT=${PORT:-7860}

# 1. Génère env.js avec les variables runtime
cat > /usr/share/nginx/html/env.js << ENVEOF
window.__ENV__ = {
  API_URL: '${API_URL:-http://localhost:8000}'
};
ENVEOF

# 2. Injecte env.js dans index.html si pas déjà présent
if ! grep -q "env.js" /usr/share/nginx/html/index.html; then
  sed -i 's|</head>|<script src="/env.js"></script></head>|' /usr/share/nginx/html/index.html
fi

# 3. Génère la config nginx avec le bon port
cat > /etc/nginx/conf.d/default.conf << NGINXEOF
server {
    listen ${PORT};
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /env.js {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    location ~* \.(js|css|png|jpg|ico|svg|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGINXEOF

echo "✓ API_URL injectée : ${API_URL:-http://localhost:8000}"
echo "✓ Nginx sur le port ${PORT}"

exec "$@"