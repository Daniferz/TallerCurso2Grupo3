#!/usr/bin/env bash

set -u

puerto="${1:-8000}"
if ! [[ "$puerto" =~ ^[0-9]+$ ]] || (( puerto < 1 || puerto > 65535 )); then
  echo "Error: el puerto debe ser un número entre 1 y 65535."
  exit 1
fi

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "No se encontró cloudflared. Instálalo con: brew install cloudflared"
  exit 1
fi

url_local="http://127.0.0.1:${puerto}"
echo "Abriendo un túnel de Cloudflare hacia ${url_local}."
echo "Deja esta terminal abierta mientras tus compañeros prueban el agente."

ultima_url=""
cloudflared tunnel --url "$url_local" 2>&1 | while IFS= read -r linea; do
  printf '%s\n' "$linea"
  url_publica="$(printf '%s\n' "$linea" | grep -Eo 'https://[[:alnum:]-]+\.trycloudflare\.com' | head -n 1 || true)"
  if [[ -n "$url_publica" && "$url_publica" != "$ultima_url" ]]; then
    ultima_url="$url_publica"
    printf '\n============================================================\n'
    printf ' URL PUBLICA: %s\n' "$url_publica"
    printf '============================================================\n'
    echo "Pega esta dirección en URL_PUBLICA de tu .env y reinicia tu agente; pásasela a tu compañero para que la ponga en su URLS_AGENTES."
    echo
  fi
done
