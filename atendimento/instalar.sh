#!/usr/bin/env bash
# Instala o auto atendimento (Evolution API + robô) num Ubuntu 22.04/24.04.
# Uso, dentro da pasta atendimento:  sudo bash instalar.sh
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
  echo ">> Instalando Docker..."
  curl -fsSL https://get.docker.com | sh
fi

if [ ! -f .env ]; then
  echo ">> Criando .env com senhas aleatórias..."
  cp .env.example .env
  sed -i "s/^AUTHENTICATION_API_KEY=.*/AUTHENTICATION_API_KEY=$(openssl rand -hex 24)/" .env
  sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$(openssl rand -hex 16)/" .env
  sed -i "s/^PAINEL_TOKEN=.*/PAINEL_TOKEN=$(openssl rand -hex 12)/" .env
  read -rp "Sua chave Pix (enter para preencher depois): " PIX || true
  [ -n "${PIX:-}" ] && sed -i "s|^PIX_CHAVE=.*|PIX_CHAVE=${PIX}|" .env
  read -rp "Número para receber avisos de lead, ex. 5521999999999 (enter para pular): " NOT || true
  [ -n "${NOT:-}" ] && sed -i "s|^NOTIFICAR_NUMERO=.*|NOTIFICAR_NUMERO=${NOT}|" .env
fi

echo ">> Subindo os serviços..."
docker compose up -d --build

TOKEN=$(grep ^PAINEL_TOKEN= .env | cut -d= -f2)
IP=$(curl -s https://api.ipify.org || echo SEU_IP_PUBLICO)
cat <<MSG

✅ Pronto! Agora conecte o WhatsApp:

1) No SEU computador, abra um túnel SSH para o servidor:
     ssh -L 3001:localhost:3001 $(whoami)@${IP}

2) Com o túnel aberto, acesse no navegador:
     http://localhost:3001/qr?token=${TOKEN}

3) No celular: WhatsApp > Aparelhos conectados > Conectar aparelho > leia o QR Code.

Logs do robô:   docker compose logs -f bot
Editar textos:  nano bot/mensagens.js  &&  docker compose up -d --build bot
MSG
