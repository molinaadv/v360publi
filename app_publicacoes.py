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
from datetime import date, datetime
from zoneinfo import ZoneInfo

import streamlit as st
from supabase import create_client

TZ = ZoneInfo("America/Manaus")

st.set_page_config(page_title="V360 Jurídico · IA Publicações",
                   layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
:root{
  --bg:#07111f; --panel:#0b1728; --panel2:#0f2036; --line:#1b3350;
  --text:#eef5ff; --muted:#90a4bd; --dim:#6f8297;
  --blue:#2d7df6; --blue2:#58a0ff; --green:#26c281;
  --yellow:#f2b84b; --red:#ef6464; --purple:#8b78ff;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
}
.stApp{background:linear-gradient(180deg,#06101d 0%,#081421 100%);color:var(--text)}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:1rem;padding-bottom:2rem;max-width:1500px}

/* ---- topbar ---- */
.topbar{display:flex;align-items:center;gap:14px;border-bottom:1px solid #10243a;
  padding-bottom:14px;margin-bottom:18px;flex-wrap:wrap}
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
.cards{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin-bottom:18px}
.metric{background:linear-gradient(180deg,#0c192b,#091626);border:1px solid #15304c;
  border-radius:15px;padding:15px;box-shadow:0 18px 50px rgba(0,0,0,.28)}
.metric .label{color:var(--muted);font-size:12px}
.metric .value{font-weight:800;font-size:26px;margin-top:4px;font-family:var(--mono)}
.metric .hint{font-size:11px;color:var(--dim);margin-top:4px}
.metric.blue .value{color:var(--blue2)} .metric.yellow .value{color:var(--yellow)}
.metric.green .value{color:var(--green)} .metric.red .value{color:var(--red)}
.metric.purple .value{color:var(--purple)}

/* ---- painéis ---- */
.panel{background:linear-gradient(180deg,#0b182a,#081523);border:1px solid #15314d;
  border-radius:18px;box-shadow:0 18px 50px rgba(0,0,0,.28);padding:16px 17px;margin-bottom:14px}
.phead{display:flex;align-items:center;justify-content:space-between;gap:14px;
  border-bottom:1px solid #15304c;padding-bottom:12px;margin-bottom:14px}
.phead h2{font-size:15px;margin:0;font-weight:700}
.phead span{font-size:12px;color:var(--muted)}

/* ---- detalhe ---- */
.chead{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px}
.chead h3{margin:0 0 5px;font-size:18px;font-weight:750}
.case-no{color:#93a9c1;font-size:12px;font-family:var(--mono)}
.conf{padding:8px 12px;border-radius:10px;background:#0e2a20;border:1px solid #235b45;
  color:#82e7bb;font-weight:700;font-size:12px;white-space:nowrap;text-align:center}
.conf.none{background:#1c1a10;border-color:#5b4a23;color:var(--yellow)}
.conf small{display:block;font-weight:500;font-size:10px;opacity:.8;margin-top:2px}

.badges{display:flex;gap:6px;flex-wrap:wrap;margin-top:9px}
.badge{font-size:10px;padding:4px 8px;border-radius:999px;border:1px solid #24415f;
  color:#a9bdd4;background:#0a1929;white-space:nowrap}
.badge.red{border-color:#6a2f36;color:#ff9d9d;background:#2a1218}
.badge.yellow{border-color:#6f5629;color:#fbd580;background:#2b210f}
.badge.green{border-color:#235d47;color:#74e0b1;background:#0d251c}
.badge.blue{border-color:#245ca0;color:#8fc2ff;background:#0b2340}
.badge.purple{border-color:#514399;color:#b7acff;background:#1c1837}

.section{border:1px solid #17324f;border-radius:14px;background:#081523;
  margin:11px 0;overflow:hidden}
.section h4{font-size:12px;margin:0;padding:11px 12px;background:#0b1c30;
  border-bottom:1px solid #17324f;color:#c7d6e7;font-weight:650}
.section .body{padding:12px}
.original{font-size:12.5px;line-height:1.6;color:#b8c8db;white-space:pre-wrap;
  max-height:300px;overflow:auto}
.kvgrid{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.kv{background:#0a1a2b;border:1px solid #16314c;border-radius:11px;padding:10px}
.kv b{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.08em;
  color:#6f86a0;margin-bottom:5px;font-weight:700}
.kv span{font-size:12.5px;color:#eaf3ff}
.kv .src{font-size:9px;font-weight:700;letter-spacing:.5px;padding:1px 5px;
  border-radius:4px;margin-left:6px;vertical-align:1px}
.src.ia{background:#1c1837;color:#b7acff} .src.regex{background:#0d251c;color:#74e0b1}
.src.calc{background:#0b2340;color:#8fc2ff}
.risk{background:#2a1419;border:1px solid #6b2d38;color:#ffb2b8;border-radius:11px;
  padding:11px;font-size:12px;line-height:1.45;margin-top:6px}
.warnbox{background:#2b210f;border:1px solid #6f5629;color:#fbd580;border-radius:11px;
  padding:11px 13px;font-size:12.5px;line-height:1.5;margin-top:6px}
.warnbox b{display:block;margin-bottom:3px;color:var(--yellow)}

/* ---- drawer ---- */
.mini{background:#091725;border:1px solid #15304c;border-radius:14px;padding:13px;height:100%}
.mini h5{margin:0 0 8px;font-size:12px;font-weight:700}
.mini p{margin:0;color:#8ba0b8;font-size:11px;line-height:1.5}
.progress{height:7px;background:#0b2239;border-radius:99px;overflow:hidden;margin:9px 0 6px}
.progress i{display:block;height:100%;background:linear-gradient(90deg,#2d7df6,#58a0ff)}

/* ---- botões da fila ---- */
div[data-testid="stVerticalBlock"] .stButton>button{
  width:100%;text-align:left;justify-content:flex-start;
  background:#0a1929;border:1px solid #10243a;border-left:3px solid transparent;
  border-radius:12px;color:var(--text);padding:11px 13px;font-size:13px;
  font-weight:650;margin-bottom:6px;line-height:1.45}
div[data-testid="stVerticalBlock"] .stButton>button:hover{
  background:#0b1e34;border-color:var(--blue)}
div[data-testid="stVerticalBlock"] .stButton>button p{text-align:left;width:100%}

/* ---- widgets no escuro (o dropdown abre num portal) ---- */
section[data-testid="stSidebar"]{background:#06101c;border-right:1px solid #10243a}
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
  color:var(--muted)!important}
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

st.markdown(f"""
<div class="topbar">
  <div class="logo">V</div>
  <div><h1>IA Publicações</h1>
    <p>Captura no DJEN, leitura por IA e apuração de prazo</p></div>
  <div class="tb-right">
    <span class="chip"><span class="live"></span>DJEN · CNJ</span>
    <span class="chip">{hoje.strftime('%d/%m/%Y')}</span>
    <span class="chip">{n_regras} regra(s) de prazo validada(s)</span>
  </div>
</div>

<div class="cards">
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
</div>
""", unsafe_allow_html=True)

if n_regras == 0:
    st.markdown("""<div class="warnbox">
      <b>Nenhuma regra de prazo validada</b>
      A IA já identifica o evento de cada publicação, mas a data limite só é
      calculada a partir de regras aprovadas pelo jurídico em
      <b>v360_prazos_legais</b>. Os prazos apurados hoje vêm do número de dias
      escrito no próprio texto. O resto fica em branco de propósito.
      </div>""", unsafe_allow_html=True)

# ------------------------------------------------------------------ filtros
with st.sidebar:
    st.markdown("""<div style="display:flex;gap:11px;align-items:center;padding:4px 0 18px">
      <div class="logo" style="width:38px;height:38px;font-size:16px">V</div>
      <div><b style="font-size:15px">V360 Jurídico</b>
      <small style="display:block;color:var(--muted);font-size:11px">Operação Jurídica</small></div>
      </div>""", unsafe_allow_html=True)

    busca = st.text_input("Buscar cliente ou processo", placeholder="nome ou número")
    tribs = sorted({p.get("sigla_tribunal") or "—" for p in pubs})
    eventos = sorted({p.get("gatilho_evento") or "—" for p in analisadas})
    f_trib = st.selectbox("Tribunal", ["todos"] + tribs)
    f_ev = st.selectbox("Evento", ["todos"] + eventos)
    f_pri = st.selectbox("Prioridade",
                         ["todas", "com prazo", "vence em 3 dias", "sem prazo"])
    f_est = st.selectbox("Estado", ["todos", "analisadas", "aguardando análise"])
    st.markdown("""<div style="margin-top:18px;padding:12px;border-radius:12px;
      background:#0a1b2f;border:1px solid #16314e;color:#9db1c8;font-size:11px">
      <b>Somente leitura</b><br>Fonte: DJEN · CNJ</div>""", unsafe_allow_html=True)


def passa(p):
    if f_trib != "todos" and (p.get("sigla_tribunal") or "—") != f_trib:
        return False
    if f_ev != "todos" and (p.get("gatilho_evento") or "—") != f_ev:
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

esq, dir_ = st.columns([1, 1.35], gap="medium")

# ------------------------------------------------------------------ fila
with esq:
    st.markdown(f"""<div class="phead"><div><h2>Fila de publicações</h2>
      <span>Urgência primeiro, depois data</span></div>
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
        linha3 = f"{p.get('sigla_tribunal') or '—'} · {p.get('area') or '—'}"
        if st.button(f"{titulo}\n{estado}\n{linha3}",
                     key=f"b{p['id']}", use_container_width=True):
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
    if conf is not None:
        try:
            cbox = (f'<div class="conf">{float(conf):.0%}'
                    f'<small>confiança da IA</small></div>')
        except (TypeError, ValueError):
            cbox = f'<div class="conf">{conf}<small>confiança</small></div>'
    elif dsel is not None:
        cbox = (f'<div class="conf">{dsel}d'
                f'<small>até {br(sel.get("data_limite"))}</small></div>')
    else:
        cbox = '<div class="conf none">—<small>sem prazo apurado</small></div>'

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

    st.markdown(f"""<div class="panel">
      <div class="chead">
        <div style="min-width:0">
          <h3>{titulo}</h3>
          <div class="case-no">{sel['numero_processo']} ·
            {sel.get('sigla_tribunal') or '—'} · {bonito(sel.get('orgao'))}</div>
          <div class="badges">{''.join(bs)}</div>
        </div>
        {cbox}
      </div>""", unsafe_allow_html=True)

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
    kvs.append(("Disponibilizada", br(sel.get("data_disponibilizacao")), "calc"))

    if sel.get("analisada"):
        st.markdown('<div class="section"><h4>Leitura da IA</h4><div class="body">'
                    '<div class="kvgrid">' + "".join(
                        f'<div class="kv"><b>{k}</b><span>{v}'
                        f'<span class="src {s}">{s}</span></span></div>'
                        for k, v, s in kvs) + '</div></div></div>',
                    unsafe_allow_html=True)
    else:
        st.markdown("""<div class="section"><h4>Leitura da IA</h4><div class="body">
          <div class="risk">Ainda não analisada. Está na fila do analisador —
          nada foi extraído desta publicação.</div></div></div>""",
          unsafe_allow_html=True)

    # --- prazo
    if sel.get("data_limite"):
        st.markdown(f"""<div class="section"><h4>Prazo</h4><div class="body">
          <div class="kvgrid">
            <div class="kv"><b>Publicação</b><span>{br(sel.get('data_publicacao'))}
              <span class="src calc">calc</span></span></div>
            <div class="kv"><b>Termo inicial</b><span>{br(sel.get('termo_inicial'))}
              <span class="src calc">calc</span></span></div>
            <div class="kv"><b>Data limite</b><span>{br(sel.get('data_limite'))}
              <span class="src calc">calc</span></span></div>
            <div class="kv"><b>Contagem</b><span>{sel.get('dias_aplicados') or '—'}
              {sel.get('contagem') or ''}<span class="src calc">calc</span></span></div>
          </div>
          {f'<div style="margin-top:9px;font-size:11px;color:#6f8297">Fundamento: {sel["fundamento"]}</div>' if sel.get('fundamento') else ''}
          </div></div>""", unsafe_allow_html=True)
    elif sel.get("analisada"):
        ev = str(sel.get("gatilho_evento") or "sem gatilho").replace("_", " ")
        st.markdown(f"""<div class="section"><h4>Prazo</h4><div class="body">
          <div class="warnbox"><b>Sem regra validada para “{ev}”</b>
          O evento foi identificado, mas não há regra aprovada para esta classe
          e o texto não traz número de dias. A publicação entra na fila sem contagem.
          </div></div></div>""", unsafe_allow_html=True)

    # --- alertas
    alertas = g(an, "alertas", "avisos_validacao", default=[])
    if alertas:
        if isinstance(alertas, str):
            alertas = [alertas]
        st.markdown('<div class="section"><h4>Alertas da análise</h4><div class="body">'
                    + "".join(f'<div class="risk">{a}</div>' for a in alertas)
                    + '</div></div>', unsafe_allow_html=True)

    # --- teor
    st.markdown('<div class="section"><h4>Publicação original · PII mascarada</h4>'
                f'<div class="body"><div class="original">{sel.get("texto") or "—"}'
                '</div></div></div></div>', unsafe_allow_html=True)

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
