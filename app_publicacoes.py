"""
V360 Jurídico · IA Publicações — tela de triagem
Lê vw_djen_triagem do Supabase "V360 Publicações" (qqvrckiubovboxaqizbl).
Somente leitura. O texto já vem com PII mascarada pela view.

Secrets:
    SUPABASE_URL = "https://qqvrckiubovboxaqizbl.supabase.co"
    SUPABASE_KEY = "<anon key>"
    APP_SENHA    = "<senha de acesso>"
"""

import hmac
import json
from collections import Counter
from datetime import date, datetime
from zoneinfo import ZoneInfo

import streamlit as st
from supabase import create_client

TZ = ZoneInfo("America/Manaus")

st.set_page_config(page_title="V360 Jurídico · IA Publicações",
                   layout="wide", initial_sidebar_state="collapsed")

CSS = """
<style>
:root{
  --bg:#07111f; --panel:#0b1728; --panel2:#0f2036; --line:#1b3350;
  --text:#eef5ff; --muted:#90a4bd; --dim:#6f8297;
  --blue:#2d7df6; --blue2:#58a0ff; --green:#26c281;
  --yellow:#f2b84b; --red:#ef6464; --purple:#8b78ff;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --serif:Georgia,"Iowan Old Style","Times New Roman",serif;
}
.stApp{background:linear-gradient(180deg,#06101d 0%,#081421 100%);color:var(--text)}
#MainMenu,footer,header,section[data-testid="stSidebar"]{display:none}
/* cabeçalho, barra Share/GitHub/Deploy, faixa colorida e badge de status */
[data-testid="stHeader"],header[data-testid="stHeader"],
[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],[data-testid="stToolbarActions"]{
  display:none!important;visibility:hidden!important;height:0!important;
  min-height:0!important}
.block-container{padding:2.2rem 2rem 2rem;max-width:none}

/* ---- topbar ---- */
.topbar{display:flex;align-items:center;gap:14px;border-bottom:1px solid #10243a;
  padding-bottom:14px;margin-bottom:16px;flex-wrap:wrap}
.logo{width:42px;height:42px;border-radius:13px;
  background:linear-gradient(135deg,#2d7df6,#5b9cff 60%,#6bd5ff);
  display:grid;place-items:center;font-weight:900;color:#fff;font-size:18px;
  box-shadow:0 10px 30px rgba(45,125,246,.25)}
.topbar h1{font-size:20px;margin:0;font-weight:750}
.topbar p{margin:3px 0 0;color:var(--muted);font-size:12px}
.tb-right{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap}
.chip{font-size:11.5px;color:var(--muted);background:var(--panel);
  border:1px solid var(--line);padding:6px 12px;border-radius:999px;white-space:nowrap}
.chip .live{display:inline-block;width:6px;height:6px;border-radius:50%;
  background:var(--green);margin-right:6px;vertical-align:1px}

/* ---- métricas ---- */
.cards{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin-bottom:14px}
.metric{background:linear-gradient(180deg,#0c192b,#091626);border:1px solid #15304c;
  border-radius:15px;padding:13px 15px;box-shadow:0 18px 50px rgba(0,0,0,.28)}
.metric .label{color:var(--muted);font-size:12px}
.metric .value{font-weight:800;font-size:26px;margin-top:3px;font-family:var(--mono)}
.metric .hint{font-size:11px;color:var(--dim);margin-top:3px}
.metric.blue .value{color:var(--blue2)} .metric.yellow .value{color:var(--yellow)}
.metric.green .value{color:var(--green)} .metric.red .value{color:var(--red)}
.metric.purple .value{color:var(--purple)}

/* ---- barra de filtros horizontal ---- */
.filtbar{background:#091725;border:1px solid #15304c;border-radius:14px;
  padding:6px 14px 2px;margin:4px 0 14px}
.filtbar-lab{font-size:10px;text-transform:uppercase;letter-spacing:.12em;
  color:#60758f;padding:6px 0 0}

/* ---- painéis ---- */
.panel{background:linear-gradient(180deg,#0b182a,#081523);border:1px solid #15314d;
  border-radius:18px;box-shadow:0 18px 50px rgba(0,0,0,.28);padding:16px 18px;margin-bottom:12px}
.phead{display:flex;align-items:center;justify-content:space-between;gap:14px;
  border-bottom:1px solid #15304c;padding-bottom:11px;margin-bottom:12px}
.phead h2{font-size:15px;margin:0;font-weight:700}
.phead span{font-size:12px;color:var(--muted)}

/* ---- cabeçalho do detalhe ---- */
.chead{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;
  margin-bottom:14px}
.chead h3{margin:0 0 5px;font-size:22px;font-weight:750;letter-spacing:-.3px}
.case-no{color:#93a9c1;font-size:12.5px;font-family:var(--mono)}
.conf{padding:9px 13px;border-radius:11px;background:#0e2a20;border:1px solid #235b45;
  color:#82e7bb;font-weight:800;font-size:15px;white-space:nowrap;text-align:center}
.conf.none{background:#1c1a10;border-color:#5b4a23;color:var(--yellow);font-size:13px}
.conf small{display:block;font-weight:500;font-size:10px;opacity:.8;margin-top:2px}

.badges{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.badge{font-size:10.5px;padding:4px 9px;border-radius:999px;border:1px solid #24415f;
  color:#a9bdd4;background:#0a1929;white-space:nowrap}
.badge.red{border-color:#6a2f36;color:#ff9d9d;background:#2a1218}
.badge.yellow{border-color:#6f5629;color:#fbd580;background:#2b210f}
.badge.green{border-color:#235d47;color:#74e0b1;background:#0d251c}
.badge.blue{border-color:#245ca0;color:#8fc2ff;background:#0b2340}
.badge.purple{border-color:#514399;color:#b7acff;background:#1c1837}

/* ---- O TEOR: protagonista ---- */
.teorwrap{border:1px solid #1d3a5c;border-radius:15px;background:#060f1c;overflow:hidden;
  margin-bottom:13px}
.teorhead{display:flex;align-items:center;justify-content:space-between;gap:10px;
  padding:11px 15px;background:#0b1c30;border-bottom:1px solid #17324f}
.teorhead h4{font-size:12px;margin:0;color:#c7d6e7;font-weight:650;
  text-transform:uppercase;letter-spacing:.09em}
.teorhead span{font-size:11px;color:var(--dim)}
.teor{font-family:var(--serif);font-size:16px;line-height:1.85;color:#dce7f5;
  white-space:pre-wrap;padding:20px 24px;max-height:460px;overflow:auto;
  text-align:justify;hyphens:auto}
.teor::first-line{color:#fff}

/* ---- seções secundárias ---- */
.section{border:1px solid #17324f;border-radius:14px;background:#081523;
  margin:11px 0;overflow:hidden}
.section h4{font-size:11.5px;margin:0;padding:10px 13px;background:#0b1c30;
  border-bottom:1px solid #17324f;color:#c7d6e7;font-weight:650;
  text-transform:uppercase;letter-spacing:.09em}
.section .body{padding:12px}
.kvgrid{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.kv{background:#0a1a2b;border:1px solid #16314c;border-radius:11px;padding:10px 12px}
.kv b{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.08em;
  color:#6f86a0;margin-bottom:5px;font-weight:700}
.kv span{font-size:13.5px;color:#eaf3ff}
.kv .src{font-size:9px;font-weight:700;letter-spacing:.5px;padding:1px 5px;
  border-radius:4px;margin-left:6px;vertical-align:1px}
.src.ia{background:#1c1837;color:#b7acff} .src.regex{background:#0d251c;color:#74e0b1}
.src.calc{background:#0b2340;color:#8fc2ff}
.risk{background:#2a1419;border:1px solid #6b2d38;color:#ffb2b8;border-radius:11px;
  padding:11px 13px;font-size:12.5px;line-height:1.5;margin-top:6px}
.warnbox{background:#2b210f;border:1px solid #6f5629;color:#fbd580;border-radius:12px;
  padding:12px 14px;font-size:12.5px;line-height:1.55;margin:6px 0 12px}
.warnbox b{display:block;margin-bottom:3px;color:var(--yellow)}

/* ---- drawer ---- */
.mini{background:#091725;border:1px solid #15304c;border-radius:14px;padding:13px;height:100%}
.mini h5{margin:0 0 8px;font-size:12px;font-weight:700}
.mini p{margin:0;color:#8ba0b8;font-size:11px;line-height:1.5}
.progress{height:7px;background:#0b2239;border-radius:99px;overflow:hidden;margin:9px 0 6px}
.progress i{display:block;height:100%;background:linear-gradient(90deg,#2d7df6,#58a0ff)}

/* ---- botões da fila ---- */
.stButton>button{
  width:100%;text-align:left;justify-content:flex-start;
  background:#0a1929;border:1px solid #10243a;border-left:3px solid transparent;
  border-radius:12px;color:var(--text);padding:11px 13px;font-size:13px;
  font-weight:650;margin-bottom:6px;line-height:1.45}
.stButton>button:hover{background:#0b1e34;border-color:var(--blue)}
.stButton>button p{text-align:left;width:100%}

/* ---- sino de avisos (fica numa coluna à direita do cabeçalho) ---- */
div[data-testid="stPopover"]{display:flex;justify-content:flex-end;
  margin-top:6px;position:relative;z-index:20}
div[data-testid="stPopover"] button,button[data-testid="stPopoverButton"]{
  background:#2b210f!important;border:1px solid #6f5629!important;
  color:var(--yellow)!important;border-radius:11px!important;
  font-size:14px!important;font-weight:800!important;padding:9px 10px!important;
  text-align:center!important;margin:0!important;line-height:1.1!important}
div[data-testid="stPopover"] button p{text-align:center!important;width:100%}

/* ---- indicadores por tribunal ---- */
.tribs{display:grid;grid-template-columns:repeat(auto-fit,minmax(112px,1fr));
  gap:10px;margin:4px 0 14px}
.trib{background:linear-gradient(180deg,#0c192b,#091626);border:1px solid #15304c;
  border-radius:13px;padding:11px 13px;text-align:center}
.trib .s{font-size:11px;letter-spacing:.1em;color:#a9bdd4;text-transform:uppercase}
.trib .n{font-family:var(--mono);font-size:21px;font-weight:800;color:#fff;
  line-height:1.15;margin-top:3px}
.trib .pc{font-size:10px;color:var(--dim);margin-top:2px}

/* ---- widgets no escuro (o dropdown abre num portal) ---- */
div[data-baseweb="select"]>div{background:#071321!important;
  border-color:#17324f!important;color:#dce9f8!important}
div[data-baseweb="select"] div,div[data-baseweb="select"] span{color:#dce9f8!important}
div[data-baseweb="select"] svg{fill:var(--muted)!important}
div[data-baseweb="popover"],div[data-baseweb="popover"]>div,
div[data-baseweb="menu"],ul[data-baseweb="menu"],ul[role="listbox"]{
  background:var(--panel2)!important;border:1px solid var(--line)!important}
li[role="option"],ul[role="listbox"] li{background:transparent!important;color:var(--text)!important}
li[role="option"]:hover,ul[role="listbox"] li:hover{background:#0b1e34!important}
li[aria-selected="true"]{background:#0e294a!important;color:var(--blue2)!important}
.stTextInput input{background:#071321!important;color:#dce9f8!important;
  border-color:#17324f!important}
label,[data-testid="stCaptionContainer"],[data-testid="stWidgetLabel"] p{
  color:var(--muted)!important;font-size:11px!important}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------ acesso
def porta():
    """Bloqueia antes de qualquer leitura do banco."""
    if st.session_state.get("liberado"):
        return
    esperada = st.secrets.get("APP_SENHA")
    if not esperada:
        st.error("Falta definir APP_SENHA nos secrets do app.")
        st.stop()
    st.markdown("""<div class="topbar"><div class="logo">V</div>
      <div><h1>V360 Jurídico · IA Publicações</h1>
      <p>Acesso restrito · Molina Advogados</p></div></div>""",
        unsafe_allow_html=True)
    _, meio, _ = st.columns([1, 1.2, 1])
    with meio:
        senha = st.text_input("Senha de acesso", type="password",
                              placeholder="digite para entrar")
        if st.button("Entrar", use_container_width=True):
            if hmac.compare_digest(senha, str(esperada)):
                st.session_state.liberado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()


porta()


# ------------------------------------------------------------------ dados
@st.cache_resource
def _cli():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


@st.cache_data(ttl=60, show_spinner="Carregando publicações…")
def carregar(limite: int = 1200):
    linhas, ini = [], 0
    while ini < limite:
        fim = min(ini + 999, limite - 1)
        r = (_cli().table("vw_djen_triagem").select("*")
             .order("data_disponibilizacao", desc=True).range(ini, fim).execute())
        linhas += r.data
        if len(r.data) < (fim - ini + 1):
            break
        ini = fim + 1
    return linhas


@st.cache_data(ttl=300)
def regras_validadas() -> int:
    r = (_cli().table("v360_prazos_legais").select("id", count="exact")
         .eq("status", "validado").execute())
    return r.count or 0


def g(d, *chaves, default=None):
    """Primeira chave que existir. O contrato pode mudar; a tela não quebra."""
    if not isinstance(d, dict):
        return default
    for k in chaves:
        v = d.get(k)
        if v not in (None, "", [], {}):
            return v
    return default


def analise_de(p):
    an = p.get("analise") or {}
    if isinstance(an, str):
        try:
            an = json.loads(an)
        except Exception:
            an = {}
    return an if isinstance(an, dict) else {}


def dias_ate(limite):
    if not limite:
        return None
    try:
        return (date.fromisoformat(str(limite)[:10]) - datetime.now(TZ).date()).days
    except Exception:
        return None


def br(d):
    s = str(d or "")[:10]
    return f"{s[8:10]}/{s[5:7]}/{s[0:4]}" if len(s) == 10 else "—"


MIUDAS = {"de", "da", "do", "das", "dos", "e", "em", "a", "o", "no", "na", "contra"}
SIGLAS = {"sjam", "jef", "inss", "trf1", "tjam", "trt11", "rpv", "adm", "sirea", "stj"}


def bonito(t):
    """O CNJ manda 'SENTENçA' (upper em locale C); title() reconstrói certo."""
    if not t:
        return "—"
    saida = []
    for i, w in enumerate(str(t).split()):
        p = w.title()
        if p.lower() in SIGLAS:
            p = p.upper()
        elif p.lower() in MIUDAS and i:
            p = p.lower()
        saida.append(p)
    return " ".join(saida)


try:
    pubs = carregar()
    n_regras = regras_validadas()
except Exception as e:
    msg = str(e)
    if "does not exist" in msg or "schema cache" in msg:
        st.error("A view `vw_djen_triagem` não existe no banco. Rode o último patch SQL.")
    elif "permission denied" in msg:
        st.error(f"Falta permissão de leitura para a role anon.\n\n{msg}")
    elif "statement timeout" in msg:
        st.error("O banco excedeu o tempo de consulta. A view está calculando "
                 "campo de texto na leitura — rode o patch de materialização.")
    else:
        st.error(f"Não consegui ler o Supabase.\n\n{msg}")
    st.stop()

if not pubs:
    st.info("Nenhuma publicação na base. Rode o coletor no n8n.")
    st.stop()

# ------------------------------------------------------------------ métricas
hoje = datetime.now(TZ).date()
tot = len(pubs)
analisadas = [p for p in pubs if p.get("analisada")]
novas_hoje = sum(1 for p in pubs
                 if str(p.get("data_disponibilizacao"))[:10] == hoje.isoformat())
aguardando = tot - len(analisadas)
com_prazo = [p for p in pubs if p.get("data_limite")]
urgentes = sum(1 for p in com_prazo if (d := dias_ate(p["data_limite"])) is not None and d <= 3)
precisa_autos = sum(1 for p in analisadas
                    if g(analise_de(p), "precisa_autos") in (True, "true", "sim"))
por_regex = sum(1 for p in analisadas
                if str(g(analise_de(p), "origem", default="")).lower() == "regex")
pct_regex = round(100 * por_regex / max(len(analisadas), 1))
com_nome = sum(1 for p in pubs if p.get("cliente"))
pct_nome = round(100 * com_nome / max(tot, 1))

@st.cache_data(ttl=300)
def oabs_faltando() -> int:
    try:
        r = (_cli().table("vw_djen_oabs_descobertas").select("numero_oab", count="exact")
             .eq("cadastrada", False).execute())
        return r.count or 0
    except Exception:
        return -1


# ------------------------------------------------------------------ avisos
# Renderizado ANTES do topbar de propósito: o CSS o fixa no canto superior
# direito, e sair primeiro no DOM evita salto de layout no carregamento.
avisos = []
if n_regras == 0:
    avisos.append((
        "Nenhuma regra de prazo validada",
        "A IA identifica o evento de cada publicação, mas a data limite só sai de "
        "regras aprovadas pelo jurídico em v360_prazos_legais. Hoje os prazos "
        "apurados vêm apenas do número de dias escrito no próprio texto."))
if aguardando:
    custo = aguardando * 0.05
    avisos.append((
        f"{aguardando} publicações aguardando análise",
        f"Custo estimado para processar a fila: US$ {custo:,.0f}".replace(",", ".")
        + ". O analisador deve ficar desligado até a estratégia de custo estar definida."))
_faltam = oabs_faltando()
if _faltam > 0:
    avisos.append((
        f"{_faltam} inscrição(ões) de OAB não cadastrada(s)",
        "O DJEN devolveu grafias de advogados do escritório que não estão em "
        "djen_identidades. Enquanto não forem cadastradas, as publicações sob "
        "essas inscrições não são capturadas — e a falha é silenciosa."))
if tot - com_nome:
    avisos.append((
        f"{tot - com_nome} publicações sem nome de cliente",
        "O texto não traz cabeçalho de partes, ou a inscrição do advogado que "
        "consta nele não permite ancorar o polo. Não é erro de leitura."))

hcol, bcol = st.columns([12, 1], gap="small")
with hcol:
    st.markdown(f"""<div class="topbar">
  <div class="logo">V</div>
  <div><h1>IA Publicações</h1>
    <p>Captura no DJEN, leitura por IA e apuração de prazo</p></div>
  <div class="tb-right">
    <span class="chip"><span class="live"></span>DJEN · CNJ</span>
    <span class="chip">{hoje.strftime('%d/%m/%Y')}</span>
    <span class="chip">{n_regras} regra(s) de prazo validada(s)</span>
  </div>
</div>""", unsafe_allow_html=True)
with bcol:
    if avisos:
        with st.popover(f"🔔 {len(avisos)}", use_container_width=True):
            st.markdown("##### Avisos do sistema")
            for titulo, corpo in avisos:
                st.markdown(f"**{titulo}**  \n{corpo}")
                st.divider()

st.markdown(f"""<div class="cards">
  <div class="metric purple"><div class="label">Na base</div>
    <div class="value">{tot}</div>
    <div class="hint">{novas_hoje} disponibilizadas hoje</div></div>
  <div class="metric yellow"><div class="label">Aguardando análise</div>
    <div class="value">{aguardando}</div>
    <div class="hint">fila do analisador</div></div>
  <div class="metric blue"><div class="label">Prazo apurado</div>
    <div class="value">{len(com_prazo)}</div>
    <div class="hint">{urgentes} vencem em até 3 dias</div></div>
  <div class="metric red"><div class="label">Precisa dos autos</div>
    <div class="value">{precisa_autos}</div>
    <div class="hint">IA não decide só pelo texto</div></div>
  <div class="metric green"><div class="label">Resolvidas sem IA</div>
    <div class="value">{pct_regex}%</div>
    <div class="hint">{por_regex} de {len(analisadas)} por regex · custo zero</div></div>
</div>""", unsafe_allow_html=True)

# ------------------------------------------------------------------ tribunais
cont_trib = Counter((p.get("sigla_tribunal") or "—") for p in pubs)
tribs = [t for t, _ in cont_trib.most_common()]

st.markdown('<div class="filtbar-lab">Por tribunal</div>', unsafe_allow_html=True)
st.markdown('<div class="tribs">' + "".join(
    f'<div class="trib"><div class="s">{t}</div>'
    f'<div class="n">{cont_trib[t]}</div>'
    f'<div class="pc">{round(100 * cont_trib[t] / tot)}%</div></div>'
    for t in tribs) + '</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------ filtros
st.markdown('<div class="filtbar-lab">Filtros</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([1.6, 1, 1, 1, 1])
busca = c1.text_input("Buscar", placeholder="cliente ou número do processo",
                      label_visibility="collapsed")
eventos = sorted({p.get("gatilho_evento") or "—" for p in analisadas})
f_trib = c2.selectbox("Tribunal", ["todos os tribunais"] + tribs,
                      label_visibility="collapsed")
f_ev = c3.selectbox("Evento", ["todos os eventos"] + eventos,
                    label_visibility="collapsed")
f_pri = c4.selectbox("Prioridade",
                     ["qualquer prazo", "com prazo", "vence em 3 dias", "sem prazo"],
                     label_visibility="collapsed")
f_est = c5.selectbox("Estado", ["qualquer estado", "analisadas", "aguardando análise"],
                     label_visibility="collapsed")


def passa(p):
    if not f_trib.startswith("todos") and (p.get("sigla_tribunal") or "—") != f_trib:
        return False
    if not f_ev.startswith("todos") and (p.get("gatilho_evento") or "—") != f_ev:
        return False
    if f_est == "analisadas" and not p.get("analisada"):
        return False
    if f_est == "aguardando análise" and p.get("analisada"):
        return False
    d = dias_ate(p.get("data_limite"))
    if f_pri == "com prazo" and not p.get("data_limite"):
        return False
    if f_pri == "sem prazo" and p.get("data_limite"):
        return False
    if f_pri == "vence em 3 dias" and (d is None or d > 3):
        return False
    if busca:
        alvo = f"{p.get('cliente') or ''} {p.get('numero_processo') or ''}".lower()
        if busca.strip().lower() not in alvo:
            return False
    return True


vis = [p for p in pubs if passa(p)]
if not vis:
    st.warning("Nenhuma publicação com esses filtros. Solte um deles.")
    st.stop()


def peso(p):
    d = dias_ate(p.get("data_limite"))
    if d is not None:
        return (0, d)
    return (1, 0) if p.get("analisada") else (2, 0)


vis = sorted(vis, key=peso)

esq, dir_ = st.columns([0.72, 1.7], gap="medium")

# ------------------------------------------------------------------ fila
with esq:
    st.markdown(f"""<div class="phead"><div><h2>Fila</h2>
      <span>Urgência primeiro</span></div>
      <span>{len(vis)} de {tot}</span></div>""", unsafe_allow_html=True)

    if "sel" not in st.session_state or st.session_state.sel not in {p["id"] for p in vis}:
        st.session_state.sel = vis[0]["id"]

    for p in vis[:60]:
        d = dias_ate(p.get("data_limite"))
        titulo = bonito(p["cliente"]) if p.get("cliente") else p["numero_processo"]
        if not p.get("analisada"):
            estado = "○ aguardando análise"
        elif d is not None:
            estado = f"◆ {d} dia(s) até o limite"
        else:
            estado = "● " + (p.get("gatilho_evento") or "sem gatilho").replace("_", " ")
        if st.button(f"{titulo}\n{estado}", key=f"b{p['id']}", use_container_width=True):
            st.session_state.sel = p["id"]

    if len(vis) > 60:
        st.caption(f"mostrando 60 de {len(vis)} · use os filtros para afunilar")

# ------------------------------------------------------------------ detalhe
sel = next((p for p in vis if p["id"] == st.session_state.sel), vis[0])
an = analise_de(sel)
origem = str(g(an, "origem", default="")).lower()
src = "regex" if origem == "regex" else "ia"
dsel = dias_ate(sel.get("data_limite"))
conf = g(an, "confianca", "confianca_geral")

with dir_:
    titulo = bonito(sel["cliente"]) if sel.get("cliente") else "Cliente não identificado"
    if dsel is not None:
        cbox = (f'<div class="conf">{dsel}d'
                f'<small>até {br(sel.get("data_limite"))}</small></div>')
    elif conf is not None:
        try:
            cbox = f'<div class="conf">{float(conf):.0%}<small>confiança da IA</small></div>'
        except (TypeError, ValueError):
            cbox = f'<div class="conf">{conf}<small>confiança</small></div>'
    else:
        cbox = '<div class="conf none">sem prazo<small>apurado</small></div>'

    bs = [f'<span class="badge blue">{sel.get("area") or "—"}</span>',
          f'<span class="badge">{bonito(sel.get("nome_classe"))}</span>']
    if sel.get("cliente_origem") == "advogado":
        bs.append('<span class="badge green">nome por âncora de advogado</span>')
    elif sel.get("cliente_origem") == "polo_ativo":
        bs.append('<span class="badge yellow">nome por polo ativo</span>')
    else:
        bs.append('<span class="badge red">sem nome no texto</span>')
    if g(an, "precisa_autos") in (True, "true", "sim"):
        bs.append('<span class="badge red">precisa dos autos</span>')
    if origem:
        bs.append(f'<span class="badge purple">lido por {origem}</span>')

    texto = sel.get("texto") or "—"
    nchars = f"{len(texto):,}".replace(",", ".")

    # HTML sem indentação e SEM linha em branco: o Markdown do Streamlit
    # trata linha vazia como fim do bloco e o que vem indentado depois
    # vira code block — foi o que sumiu com o teor.
    html = (
        '<div class="panel">'
        '<div class="chead">'
        '<div style="min-width:0">'
        f'<h3>{titulo}</h3>'
        f'<div class="case-no">{sel["numero_processo"]} · '
        f'{sel.get("sigla_tribunal") or "—"} · {bonito(sel.get("orgao"))}</div>'
        f'<div class="badges">{"".join(bs)}</div>'
        '</div>'
        f'{cbox}'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

    # --- prazo
    if sel.get("data_limite"):
        st.markdown(
            '<div class="section"><h4>Prazo apurado</h4><div class="body">'
            '<div class="kvgrid">'
            f'<div class="kv"><b>Publicação</b><span>{br(sel.get("data_publicacao"))}'
            '<span class="src calc">calc</span></span></div>'
            f'<div class="kv"><b>Termo inicial</b><span>{br(sel.get("termo_inicial"))}'
            '<span class="src calc">calc</span></span></div>'
            f'<div class="kv"><b>Data limite</b><span>{br(sel.get("data_limite"))}'
            '<span class="src calc">calc</span></span></div>'
            f'<div class="kv"><b>Contagem</b><span>{sel.get("dias_aplicados") or "—"} '
            f'{sel.get("contagem") or ""}<span class="src calc">calc</span></span></div>'
            '</div>'
            + (f'<div style="margin-top:9px;font-size:11px;color:#6f8297">'
               f'Fundamento: {sel["fundamento"]}</div>' if sel.get("fundamento") else "")
            + '</div></div>', unsafe_allow_html=True)
    elif sel.get("analisada"):
        ev = str(sel.get("gatilho_evento") or "sem gatilho").replace("_", " ")
        st.markdown(
            f'<div class="warnbox"><b>Sem regra validada para “{ev}”</b>'
            'O evento foi identificado, mas não há regra aprovada para esta classe '
            'e o texto não traz número de dias. Entra na fila sem contagem.</div>',
            unsafe_allow_html=True)

    # --- leitura da IA
    kvs = []
    if sel.get("gatilho_evento"):
        kvs.append(("Evento identificado",
                    str(sel["gatilho_evento"]).replace("_", " "), src))
    for rot, chaves in [("Tipo de ato", ("tipo_ato", "padrao_detectado")),
                        ("Prazo no texto", ("prazo_dias", "prazo_expresso")),
                        ("Destinatário", ("destinatario",)),
                        ("Resumo", ("resumo", "sintese")),
                        ("Providência", ("providencia", "acao_sugerida"))]:
        v = g(an, *chaves)
        if v is not None:
            kvs.append((rot, str(v), src))
    kvs.append(("Segmento", sel.get("segmento") or "—", "calc"))

    if sel.get("analisada"):
        st.markdown('<div class="section"><h4>Leitura da IA</h4><div class="body">'
                    '<div class="kvgrid">' + "".join(
                        f'<div class="kv"><b>{k}</b><span>{v}'
                        f'<span class="src {s}">{s}</span></span></div>'
                        for k, v, s in kvs) + '</div></div></div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="section"><h4>Leitura da IA</h4><div class="body">'
            '<div class="risk">Ainda não analisada. Está na fila do analisador — '
            'nada foi extraído desta publicação.</div></div></div>',
            unsafe_allow_html=True)

    # --- alertas
    alertas = g(an, "alertas", "avisos_validacao", default=[])
    if alertas:
        if isinstance(alertas, str):
            alertas = [alertas]
        st.markdown('<div class="section"><h4>Alertas da análise</h4><div class="body">'
                    + "".join(f'<div class="risk">{a}</div>' for a in alertas)
                    + '</div></div>', unsafe_allow_html=True)

    # --- o teor, para conferir contra o que a IA leu
    st.markdown(
        '<div class="teorwrap">'
        '<div class="teorhead"><h4>Publicação · texto do tribunal</h4>'
        f'<span>{nchars} caracteres · disponibilizada '
        f'{br(sel.get("data_disponibilizacao"))} · PII mascarada</span></div>'
        f'<div class="teor">{texto}</div>'
        '</div>', unsafe_allow_html=True)

    with st.expander("JSON bruto da análise"):
        st.json(an if an else {"sem_analise": True})

# ------------------------------------------------------------------ drawer
d1, d2, d3 = st.columns(3)
with d1:
    st.markdown(f"""<div class="mini"><h5>Cobertura de nomes</h5>
      <div class="progress"><i style="width:{pct_nome}%"></i></div>
      <p>{com_nome} de {tot} publicações ({pct_nome}%) com cliente identificado
      no texto. O resto não traz cabeçalho de partes.</p></div>""",
      unsafe_allow_html=True)
with d2:
    st.markdown(f"""<div class="mini"><h5>Regras de prazo</h5>
      <div class="progress"><i style="width:{min(100, n_regras * 8)}%"></i></div>
      <p>{n_regras} validada(s) pelo jurídico. Enquanto estiver em zero, só há
      prazo onde o próprio texto escreve o número de dias.</p></div>""",
      unsafe_allow_html=True)
with d3:
    st.markdown(f"""<div class="mini"><h5>Economia por regex</h5>
      <div class="progress"><i style="width:{pct_regex}%"></i></div>
      <p>{pct_regex}% das análises saíram sem chamar a IA. Cada padrão novo que
      o regex absorve é custo zero permanente.</p></div>""",
      unsafe_allow_html=True)
