# Auto atendimento WhatsApp (Evolution API)

Robô simples que responde quem chama no WhatsApp do Felipe:

| Cliente manda | Robô responde |
|---|---|
| Primeira mensagem (ou depois de 24h sem conversa) | Boas-vindas + menu |
| **1** / "como funciona" | Como funciona a consultoria |
| **2** / "valor", "preço", "pix" | R$ 80/mês, sem fidelidade + **chave Pix** + link da anamnese |
| **3** / "paguei", "anamnese" | Link da anamnese |
| **4** / "falar com o Felipe" | Avisa o Felipe e **para de responder** esse contato por 12h |
| Foto/PDF (comprovante) | "Recebi, vou conferir" + avisa o Felipe + pausa |
| Algo que não entendeu | Repete o menu 1 vez; na 2ª, chama o Felipe e pausa |

**Quando você responde alguém pelo celular, o robô fica calado com aquela pessoa por 12h**, então você pode assumir a conversa a qualquer momento.
Grupos, status e listas de transmissão são ignorados.

## Instalar no servidor (Ubuntu 24.04, Locaweb)

```bash
git clone https://github.com/Felicordeirofcf/personal.git
cd personal/atendimento
sudo bash instalar.sh
```

O script instala o Docker (se faltar), gera senhas, pergunta a chave Pix e o número de avisos, sobe tudo e mostra como conectar.

### Conectar o WhatsApp (QR Code)
As portas ficam fechadas para a internet (só `localhost`). Do seu computador:

```bash
ssh -L 3001:localhost:3001 usuario@IP_PUBLICO_DO_SERVIDOR
```

Com o túnel aberto, acesse `http://localhost:3001/qr?token=SEU_TOKEN` (o token está no `.env`, `PAINEL_TOKEN`).
No celular: **WhatsApp → Aparelhos conectados → Conectar aparelho**. O celular continua funcionando normalmente.

## Dia a dia

| Tarefa | Comando (na pasta `atendimento`) |
|---|---|
| Ver o robô respondendo | `docker compose logs -f bot` |
| Mudar textos | edite `bot/mensagens.js` e rode `docker compose up -d --build bot` |
| Mudar chave Pix / número de aviso | edite `.env` e rode `docker compose up -d` |
| Atualizar | `git pull && docker compose up -d --build` |
| Parar tudo | `docker compose down` |

## Cuidados
- A Evolution API usa conexão **não oficial** do WhatsApp (como o WhatsApp Web). Use para **responder** quem te chama, nunca para disparo em massa, senão o número pode ser bloqueado.
- A VM tem 2 GB de RAM; o conjunto usa ~600–800 MB. Se ela já roda outro sistema, acompanhe com `docker stats`.
- Nunca coloque o `.env` no GitHub (ele já está no `.gitignore`).
