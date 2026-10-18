FROM nginxinc/nginx-unprivileged:1.27-alpine

LABEL org.opencontainers.image.title="recmin" \
      org.opencontainers.image.description="Record Minutes Timer - voice-triggered recording countdown" \
      org.opencontainers.image.source="https://github.com/jaswanthkumarj1234-beep/recmin" \
      org.opencontainers.image.licenses="MIT"

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html sw.js /usr/share/nginx/html/
COPY clips /usr/share/nginx/html/clips
COPY vosk /usr/share/nginx/html/vosk

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
