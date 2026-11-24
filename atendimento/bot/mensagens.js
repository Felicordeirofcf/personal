// Textos do auto atendimento. Edite à vontade e reinicie: docker compose up -d --build bot
// Variáveis disponíveis: {nome} {pix} {site}

module.exports = {
  boasVindas:
`Fala, {nome}! 💪 Aqui é o *Felipe Ferreira*, personal trainer (CREF 071550-G/RJ).

Obrigado por chamar! Minha consultoria online é *R$ 80/mês* com série nova todo mês e *acompanhamento diário* aqui no WhatsApp.

Me diz o número do que você quer:`,

  menu:
`*1* - Como funciona
*2* - Valor e pagamento
*3* - Já paguei / preencher anamnese
*4* - Falar direto com o Felipe`,

  comoFunciona:
`Funciona assim 👇

1️⃣ Você preenche uma anamnese rápida (3 min)
2️⃣ Eu monto *pessoalmente* sua série, com vídeo de cada exercício
3️⃣ Todo dia você me manda o check-in do treino e eu ajusto carga e execução
4️⃣ No fim do mês: reavaliação e *série nova*

Serve pra iniciante ou avançado, em casa ou na academia.

Quer começar? Digite *2* pra ver o pagamento.`,

  valor:
`💰 *R$ 80 por mês*, pago no Pix
✅ Sem fidelidade: renova mês a mês e para quando quiser
✅ Dá menos de R$ 2,70 por dia

*Chave Pix:* {pix}

Depois de pagar, *manda o comprovante aqui* e preenche sua anamnese:
{site}/anamnese/`,

  anamnese:
`Show! 🙌 Preenche sua anamnese aqui (leva uns 3 minutos):
{site}/anamnese/

Assim que eu receber, começo a montar sua série. Se ainda não mandou o comprovante do Pix, pode mandar aqui mesmo.`,

  humano:
`Beleza, {nome}! Já avisei o Felipe, ele te responde pessoalmente em breve. 👊`,

  comprovante:
`Recebi! ✅ Vou conferir e já te chamo.

Enquanto isso, se ainda não preencheu, sua anamnese está aqui:
{site}/anamnese/`,

  naoEntendi:
`Não entendi muito bem 😅 Me responde com o número de uma opção:`,

  encaminhado:
`Vou chamar o Felipe pra te responder pessoalmente, tá? Ele já fala com você. 👊`,

  // Aviso que vai para NOTIFICAR_NUMERO (se configurado)
  aviso: `🔔 *{motivo}*\nContato: {nome}\nNúmero: {numero}\nÚltima mensagem: "{texto}"`,
};
