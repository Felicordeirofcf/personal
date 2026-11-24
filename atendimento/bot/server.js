// Robô de auto atendimento do Felipe, recebe o webhook da Evolution API.
// Sem dependências externas (Node 20+).
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const M = require('./mensagens');

const CFG = {
  porta: Number(process.env.PORT || 3000),
  evolution: (process.env.EVOLUTION_URL || 'http://localhost:8080').replace(/\/$/, ''),
  apiKey: process.env.AUTHENTICATION_API_KEY || '',
  instancia: process.env.INSTANCIA || 'felipe',
  pix: process.env.PIX_CHAVE || '(peça a chave Pix ao Felipe)',
  site: (process.env.SITE || 'https://felipepersonal.com').replace(/\/$/, ''),
  notificar: (process.env.NOTIFICAR_NUMERO || '').replace(/\D/g, ''),
  pausaHumanoMs: Number(process.env.PAUSA_HUMANO_HORAS || 12) * 3600e3,
  reinicioMs: Number(process.env.REINICIO_HORAS || 24) * 3600e3,
  token: process.env.PAINEL_TOKEN || '',
  arquivo: process.env.ESTADO_ARQUIVO || path.join(__dirname, 'estado.json'),
};

// ---------- estado por contato (persistido em JSON) ----------
let estado = {};
try { estado = JSON.parse(fs.readFileSync(CFG.arquivo, 'utf8')); } catch { estado = {}; }
let salvarTimer = null;
function salvar() {
  clearTimeout(salvarTimer);
  salvarTimer = setTimeout(() => {
    try { fs.mkdirSync(path.dirname(CFG.arquivo), { recursive: true }); fs.writeFileSync(CFG.arquivo, JSON.stringify(estado)); }
    catch (e) { log('erro ao salvar estado', e.message); }
  }, 500);
}
const contato = (jid) => (estado[jid] ||= { visto: 0, pausadoAte: 0, naoEntendi: 0 });

const enviadosPeloBot = new Set(); // ids das mensagens que o próprio robô mandou
const processados = new Set();     // evita responder 2x ao mesmo webhook
function lembrar(set, id) { set.add(id); if (set.size > 2000) set.delete(set.values().next().value); }

function log(...a) { console.log(new Date().toISOString(), ...a); }

function preencher(txt, vars) {
  return txt.replace(/\{(\w+)\}/g, (_, k) => (vars[k] ?? `{${k}}`));
}

// ---------- Evolution API ----------
async function evo(metodo, rota, corpo) {
  const r = await fetch(CFG.evolution + rota, {
    method: metodo,
    headers: { 'Content-Type': 'application/json', apikey: CFG.apiKey },
    body: corpo ? JSON.stringify(corpo) : undefined,
  });
  const texto = await r.text();
  let json; try { json = JSON.parse(texto); } catch { json = { raw: texto }; }
  if (!r.ok) throw new Error(`${metodo} ${rota} -> ${r.status} ${texto.slice(0, 300)}`);
  return json;
}

async function enviar(numero, texto) {
  try {
    const r = await evo('POST', `/message/sendText/${CFG.instancia}`, { number: numero, text: texto, delay: 1200 });
    if (r?.key?.id) lembrar(enviadosPeloBot, r.key.id);
  } catch (e) { log('erro ao enviar', e.message); }
}

async function avisarFelipe(motivo, nome, numero, texto) {
  if (!CFG.notificar) return;
  await enviar(CFG.notificar, preencher(M.aviso, { motivo, nome, numero, texto: (texto || '').slice(0, 200) }));
}

async function garantirInstancia() {
  try {
    const lista = await evo('GET', `/instance/fetchInstances?instanceName=${encodeURIComponent(CFG.instancia)}`);
    if (Array.isArray(lista) && lista.length) return log('instância já existe:', CFG.instancia);
  } catch (e) { /* 404 quando não existe */ }
  try {
    await evo('POST', '/instance/create', { instanceName: CFG.instancia, integration: 'WHATSAPP-BAILEYS', qrcode: true });
    log('instância criada:', CFG.instancia);
  } catch (e) { log('não consegui criar a instância (tento de novo em 15s):', e.message); setTimeout(garantirInstancia, 15000); }
}

// ---------- lógica do atendimento ----------
const sem = (s) => (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();

function textoDa(msg) {
  const m = msg || {};
  return m.conversation || m.extendedTextMessage?.text || m.imageMessage?.caption || m.documentMessage?.caption
    || m.buttonsResponseMessage?.selectedDisplayText || m.listResponseMessage?.title || '';
}

function intencao(t) {
  const s = sem(t);
  if (/^(0|menu|inicio|voltar)$/.test(s)) return 'menu';
  if (/^1\b/.test(s) || /como funciona|funciona como|explica/.test(s)) return 'comoFunciona';
  if (/^2\b/.test(s) || /valor|preco|quanto|pagamento|pagar|pix|mensalidade|custa/.test(s)) return 'valor';
  if (/^3\b/.test(s) || /anamnese|ficha|ja paguei|paguei|comprovante/.test(s)) return 'anamnese';
  if (/^4\b/.test(s) || /falar com (o )?felipe|humano|atendente|falar com (uma )?pessoa|falar com voce|me liga/.test(s)) return 'humano';
  return null;
}

async function tratar(evento) {
  const d = evento?.data;
  if (!d?.key) return;
  const { key } = d;
  const jid = key.remoteJid || '';
  if (!jid || jid.endsWith('@g.us') || jid === 'status@broadcast' || jid.endsWith('@newsletter') || jid.endsWith('@broadcast')) return;
  if (key.id) { if (processados.has(key.id)) return; lembrar(processados, key.id); }

  // Número para responder (Evolution 2.3 pode mandar @lid com o número real em remoteJidAlt/senderPn)
  const alvo = [key.remoteJidAlt, key.senderPn, jid].find((j) => j && j.endsWith('@s.whatsapp.net')) || jid;
  const numero = alvo.endsWith('@s.whatsapp.net') ? alvo.split('@')[0] : alvo;
  const c = contato(numero);
  const agora = Date.now();

  // Mensagem enviada por você (pelo celular) = atendimento humano: robô pausa nesse contato
  if (key.fromMe) {
    if (!enviadosPeloBot.has(key.id)) { c.pausadoAte = agora + CFG.pausaHumanoMs; salvar(); log('humano assumiu', numero); }
    return;
  }

  if (CFG.notificar && numero === CFG.notificar) return; // não atende o número de avisos
  const nome = (d.pushName || '').split(' ')[0] || 'tudo bem';
  const texto = textoDa(d.message);
  const vars = { nome, pix: CFG.pix, site: CFG.site };
  const novo = !c.visto || agora - c.visto > CFG.reinicioMs;
  c.visto = agora; c.nome = d.pushName || c.nome;

  if (c.pausadoAte > agora) { salvar(); return; }

  const tipo = d.messageType || Object.keys(d.message || {})[0] || '';
  const ehArquivo = /imageMessage|documentMessage|documentWithCaptionMessage/.test(tipo);

  let resposta; let pausar = false;
  if (ehArquivo && !novo) {
    resposta = M.comprovante; pausar = true;
    await avisarFelipe('Possível comprovante recebido', c.nome, numero, texto || '[arquivo]');
  } else {
    const i = novo ? null : intencao(texto); // contato novo sempre recebe boas-vindas + menu
    if (i === 'menu') resposta = `${M.menu}`;
    else if (i === 'humano') { resposta = M.humano; pausar = true; await avisarFelipe('Lead quer falar com você', c.nome, numero, texto); }
    else if (i) resposta = M[i];
    else if (novo) resposta = `${M.boasVindas}\n\n${M.menu}`;
    else if (!/[a-z0-9]/i.test(sem(texto))) resposta = null; // só emoji/figurinha/áudio: não responde
    else if (c.naoEntendi < 1) { c.naoEntendi++; resposta = `${M.naoEntendi}\n\n${M.menu}`; }
    else { resposta = M.encaminhado; pausar = true; await avisarFelipe('Lead com dúvida que o robô não entendeu', c.nome, numero, texto); }
    if (i) c.naoEntendi = 0;
    if (novo && !ehArquivo) await avisarFelipe('Novo contato no WhatsApp', c.nome, numero, texto);
  }

  if (pausar) c.pausadoAte = agora + CFG.pausaHumanoMs;
  salvar();
  if (resposta) { log('->', numero, resposta.split('\n')[0].slice(0, 60)); await enviar(numero, preencher(resposta, vars)); }
}

// ---------- servidor HTTP ----------
function corpoJson(req) {
  return new Promise((ok) => {
    let b = ''; req.on('data', (x) => { b += x; if (b.length > 5e6) req.destroy(); });
    req.on('end', () => { try { ok(JSON.parse(b || '{}')); } catch { ok({}); } });
  });
}

const paginaQr = (img, estadoConexao) => `<!doctype html><html lang="pt-br"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Conectar WhatsApp</title>
<meta http-equiv="refresh" content="${img ? 20 : 8}">
<body style="font-family:system-ui;background:#09090b;color:#fafafa;text-align:center;padding:30px">
<h2>Auto atendimento: ${CFG.instancia}</h2>
<p>Status: <b>${estadoConexao}</b></p>
${estadoConexao === 'open'
    ? '<p style="color:#22c55e;font-size:20px">✅ WhatsApp conectado! Pode fechar esta página.</p>'
    : img ? `<p>No celular: WhatsApp → Aparelhos conectados → Conectar aparelho</p><img src="${img}" style="background:#fff;padding:12px;border-radius:12px;width:300px">`
      : '<p>Gerando QR Code…</p>'}
<p style="color:#71717a;font-size:12px">A página atualiza sozinha.</p></body></html>`;

http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');
  try {
    if (req.method === 'POST' && url.pathname.startsWith('/webhook')) {
      const ev = await corpoJson(req);
      res.writeHead(200).end('ok');
      const evento = sem(ev.event || '').replace(/_/g, '.');
      if (evento === 'messages.upsert') {
        const lista = Array.isArray(ev.data) ? ev.data.map((data) => ({ ...ev, data })) : [ev];
        for (const e of lista) await tratar(e).catch((er) => log('erro no atendimento', er.message));
      }
      return;
    }
    if (url.pathname === '/health') return res.writeHead(200).end('ok');
    if (url.pathname === '/qr') {
      if (!CFG.token || url.searchParams.get('token') !== CFG.token) return res.writeHead(401).end('token inválido');
      let st = 'desconhecido', img = '';
      try { st = (await evo('GET', `/instance/connectionState/${CFG.instancia}`))?.instance?.state || st; } catch (e) { st = 'instância ainda não criada'; }
      if (st !== 'open') { try { const r = await evo('GET', `/instance/connect/${CFG.instancia}`); img = r?.base64 || ''; } catch (e) { log('qr', e.message); } }
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      return res.end(paginaQr(img, st));
    }
    res.writeHead(404).end('não encontrado');
  } catch (e) { log('erro http', e.message); if (!res.headersSent) res.writeHead(500).end('erro'); }
}).listen(CFG.porta, () => {
  log(`robô ouvindo na porta ${CFG.porta}`);
  setTimeout(garantirInstancia, 3000);
});

module.exports = { intencao, textoDa };
