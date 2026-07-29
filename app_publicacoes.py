"""
V360 · Publicações (DJEN) — Tela de Triagem
Lê vw_djen_triagem do Supabase "V360 Publicações" (qqvrckiubovboxaqizbl).
Somente leitura. O texto já vem mascarado pela view.

Secrets necessários (.streamlit/secrets.toml):
    SUPABASE_URL = "https://qqvrckiubovboxaqizbl.supabase.co"
    SUPABASE_KEY = "<anon key>"
"""

import hmac
import json
from datetime import date, datetime
from zoneinfo import ZoneInfo

import streamlit as st
from supabase import create_client

TZ = ZoneInfo("America/Manaus")

st.set_page_config(page_title="V360 · Publicações", layout="wide",
                   initial_sidebar_state="collapsed")

# ---------------------------------------------------------------- estilo
CSS = """
<style>
:root{
  --bg:#0b1220; --panel:#141d2e; --panel2:#1b2740; --line:#26324d;
  --ink:#f2f6ff; --muted:#93a1bd; --dim:#6b7a99;
  --accent:#5b8cff; --warn:#f5a524; --ok:#2fce8f; --crit:#ef7a7a; --roxo:#8b7bff;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
}
.stApp{background:var(--bg);color:var(--ink)}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:1.2rem;max-width:1400px}

.brand{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px}
.badge{width:34px;height:34px;border-radius:10px;
  background:linear-gradient(140deg,var(--roxo),var(--accent));
  display:grid;place-items:center;font-weight:800;font-size:13px;color:#fff}
.brand h1{font-size:19px;font-weight:700;margin:0;letter-spacing:-.2px;color:var(--ink)}
.pills{display:flex;gap:8px;flex-wrap:wrap;margin-left:auto}
.pill{font-size:11.5px;color:var(--muted);background:var(--panel);
  border:1px solid var(--line);padding:5px 11px;border-radius:999px}
.pill .dot{display:inline-block;width:6px;height:6px;border-radius:50%;
  background:var(--ok);margin-right:6px;vertical-align:1px}

.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:6px 0 16px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:12px 14px}
.kpi .n{font-size:clamp(22px,3.2vw,30px);font-weight:800;line-height:1.05;font-family:var(--mono)}
.kpi .l{font-size:11px;color:var(--muted);margin-top:3px}
.kpi.crit .n{color:var(--crit)} .kpi.warn .n{color:var(--warn)}
.kpi.ok .n{color:var(--ok)} .kpi.roxo .n{color:var(--roxo)} .kpi.blue .n{color:var(--accent)}

.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;
  padding:16px 18px;margin-bottom:12px}
.card h3{margin:0 0 2px;font-size:19px;font-weight:700;letter-spacing:-.3px;color:var(--ink)}
.dsub{font-family:var(--mono);font-size:11.5px;color:var(--dim);margin-bottom:12px}

.teorlab{font-size:10px;letter-spacing:1px;text-transform:uppercase;
  color:var(--dim);margin:14px 0 7px}
.teor{background:#0d1424;border:1px solid var(--line);border-left:3px solid var(--dim);
  border-radius:10px;padding:13px 15px;font-size:13.5px;color:#cdd8ef;line-height:1.65;
  max-height:280px;overflow:auto;white-space:pre-wrap}

.f{display:flex;justify-content:space-between;gap:10px;align-items:baseline;
  padding:10px 0;border-bottom:1px solid #1d2740}
.f:last-child{border-bottom:0}
.fk{font-size:10.5px;text-transform:uppercase;letter-spacing:.8px;color:var(--dim)}
.fv{font-size:14px;font-weight:600;text-align:right;color:var(--ink)}
.src{font-size:9.5px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;
  padding:2px 6px;border-radius:5px;margin-left:8px}
.src.ia{background:#1e1a33;color:var(--roxo)}
.src.regex{background:#12251d;color:var(--ok)}
.src.calc{background:#151f38;color:var(--accent)}

.lock{background:#241f12;border:1px solid #4a3a1a;border-radius:12px;
  padding:13px 15px;margin-top:12px}
.lock .t{font-weight:700;color:var(--warn);font-size:13.5px;margin-bottom:4px}
.lock .d{font-size:12.5px;color:#e3d3b4;line-height:1.55}
.gap{background:#1a1220;border:1px solid #4a2830;border-radius:12px;padding:13px 15px;margin-top:12px}
.gap .t{font-weight:700;color:var(--crit);font-size:13.5px;margin-bottom:4px}
.gap .d{font-size:12.5px;color:#d9c4cc;line-height:1.55}

div[data-testid="stVerticalBlock"] .stButton>button{
  width:100%;text-align:left;background:var(--panel);border:1px solid var(--line);
  border-left:3px solid transparent;border-radius:10px;color:var(--ink);
  padding:9px 12px;font-size:13px;font-weight:600;margin-bottom:5px;line-height:1.35;
  justify-content:flex-start}
div[data-testid="stVerticalBlock"] .stButton>button:hover{
  background:var(--panel2);border-color:var(--accent)}
div[data-testid="stVerticalBlock"] .stButton>button p{text-align:left;width:100%}

/* inputs no tema escuro (o baseweb do Streamlit vem claro por padrão) */
div[data-baseweb="select"]>div{background:var(--panel)!important;
  border-color:var(--line)!important;color:var(--ink)!important}
div[data-baseweb="select"] div,div[data-baseweb="select"] span{color:var(--ink)!important}
div[data-baseweb="select"] svg{fill:var(--muted)!important}
ul[data-baseweb="menu"]{background:var(--panel2)!important}
li[role="option"]{color:var(--ink)!important}
.stTextInput input{background:var(--panel)!important;color:var(--ink)!important;
  border-color:var(--line)!important}
label,[data-testid="stCaptionContainer"],[data-testid="stWidgetLabel"] p{
  color:var(--muted)!important}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------- acesso
def porta():
    """Bloqueia antes de qualquer leitura do banco. Sem senha, nada de Supabase."""
    if st.session_state.get("liberado"):
        return

    esperada = st.secrets.get("APP_SENHA")
    if not esperada:
        st.error("Falta definir APP_SENHA nos secrets do app.")
        st.stop()

    st.markdown("""<div class="brand">
      <div class="badge">V360</div><h1>Publicações · Triagem</h1></div>""",
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
        st.caption("Acesso restrito · Molina Advogados")
    st.stop()


porta()


# ---------------------------------------------------------------- dados
@st.cache_resource
def _cli():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


@st.cache_data(ttl=60, show_spinner="Carregando publicações…")
def carregar(limite: int = 600):
    linhas, ini = [], 0
    while ini < limite:
        fim = min(ini + 999, limite - 1)
        r = (_cli().table("vw_djen_triagem").select("*")
             .order("data_disponibilizacao", desc=True)
             .range(ini, fim).execute())
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
    """Lê a primeira chave que existir. O contrato muda; a tela não quebra."""
    if not isinstance(d, dict):
        return default
    for k in chaves:
        v = d.get(k)
        if v not in (None, "", [], {}):
            return v
    return default


def dias_ate(limite):
    if not limite:
        return None
    try:
        return (date.fromisoformat(str(limite)[:10]) - datetime.now(TZ).date()).days
    except Exception:
        return None


def br(d):
    """2026-07-29 → 29/07/2026"""
    s = str(d or "")[:10]
    return f"{s[8:10]}/{s[5:7]}/{s[0:4]}" if len(s) == 10 else "—"


MIUDAS = {"de", "da", "do", "das", "dos", "e", "em", "a", "o", "no", "na", "contra"}
SIGLAS = {"sjam", "jef", "inss", "trf1", "tjam", "trt11", "rpv", "adm", "sirea"}


def bonito(t):
    """O CNJ manda 'SENTENçA' (upper em locale C). title() reconstrói certo."""
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
    st.error(f"Não consegui ler o Supabase. Confira SUPABASE_URL e SUPABASE_KEY nos secrets.\n\n{e}")
    st.stop()

if not pubs:
    st.info("Nenhuma publicação na base ainda. Rode o coletor no n8n.")
    st.stop()

hoje = datetime.now(TZ).strftime("%d/%m/%Y")
tot = len(pubs)
analisadas = sum(1 for p in pubs if p.get("analisada"))
com_prazo = sum(1 for p in pubs if p.get("data_limite"))
urgentes = sum(1 for p in pubs if (d := dias_ate(p.get("data_limite"))) is not None and d <= 3)
sem_evento = sum(1 for p in pubs if p.get("analisada") and not p.get("gatilho_evento"))

st.markdown(f"""
<div class="brand">
  <div class="badge">V360</div>
  <h1>Publicações · Triagem</h1>
  <div class="pills">
    <span class="pill"><span class="dot"></span>DJEN · CNJ</span>
    <span class="pill">{hoje}</span>
    <span class="pill">{n_regras} regra(s) validada(s)</span>
  </div>
</div>
<div class="kpis">
  <div class="kpi roxo"><div class="n">{tot}</div><div class="l">na base</div></div>
  <div class="kpi blue"><div class="n">{analisadas}</div><div class="l">analisadas</div></div>
  <div class="kpi warn"><div class="n">{tot - analisadas}</div><div class="l">aguardando análise</div></div>
  <div class="kpi ok"><div class="n">{com_prazo}</div><div class="l">com data limite</div></div>
  <div class="kpi crit"><div class="n">{urgentes}</div><div class="l">vencem em 3 dias</div></div>
</div>
""", unsafe_allow_html=True)

if n_regras == 0:
    st.markdown("""<div class="lock">
      <div class="t">Nenhuma regra de prazo validada</div>
      <div class="d">A IA já identifica o evento de cada publicação, mas a data limite
      só é calculada a partir de regras aprovadas pelo jurídico em
      <b>v360_prazos_legais</b>. Enquanto isso, a coluna de prazo fica vazia de propósito —
      é melhor que um prazo inventado.</div></div>""", unsafe_allow_html=True)

# ---------------------------------------------------------------- filtros
c1, c2, c3 = st.columns([1, 1, 1])
tribs = sorted({p.get("sigla_tribunal") or "—" for p in pubs})
eventos = sorted({p.get("gatilho_evento") or "—" for p in pubs})
f_trib = c1.selectbox("Tribunal", ["todos"] + tribs)
f_ev = c2.selectbox("Evento", ["todos"] + eventos)
f_est = c3.selectbox("Estado", ["todos", "analisadas", "aguardando análise"])

vis = [p for p in pubs
       if (f_trib == "todos" or (p.get("sigla_tribunal") or "—") == f_trib)
       and (f_ev == "todos" or (p.get("gatilho_evento") or "—") == f_ev)
       and (f_est == "todos"
            or (f_est == "analisadas" and p.get("analisada"))
            or (f_est == "aguardando análise" and not p.get("analisada")))]

if not vis:
    st.warning("Nenhuma publicação com esses filtros. Solte um deles.")
    st.stop()

st.caption(f"{len(vis)} de {tot} publicações")

esq, dir_ = st.columns([1, 1.9], gap="medium")

# ---------------------------------------------------------------- fila
with esq:
    st.markdown('<div class="teorlab">Fila</div>', unsafe_allow_html=True)

    # ordem operacional: quem tem prazo mais curto primeiro, depois as já
    # analisadas sem prazo, e por último as que ainda não foram lidas.
    def peso(p):
        d = dias_ate(p.get("data_limite"))
        if d is not None:
            return (0, d)
        return (1, 0) if p.get("analisada") else (2, 0)

    vis = sorted(vis, key=peso)

    if "sel" not in st.session_state or st.session_state.sel not in {p["id"] for p in vis}:
        st.session_state.sel = vis[0]["id"]
    for p in vis[:60]:
        d = dias_ate(p.get("data_limite"))
        if not p.get("analisada"):
            marca, rot = "○", "aguardando análise"
        else:
            marca = "●"
            rot = (p.get("gatilho_evento") or "sem gatilho").replace("_", " ")
        prazo = f" · {d}d" if d is not None else ""
        if st.button(f"{marca} {p['numero_processo']}\n{rot}{prazo}",
                     key=f"b{p['id']}", use_container_width=True):
            st.session_state.sel = p["id"]
    if len(vis) > 60:
        st.caption(f"mostrando 60 de {len(vis)} · use os filtros para afunilar")

# ---------------------------------------------------------------- detalhe
sel = next((p for p in vis if p["id"] == st.session_state.sel), vis[0])
an = sel.get("analise") or {}
if isinstance(an, str):
    try:
        an = json.loads(an)
    except Exception:
        an = {}

origem = (g(an, "origem") or "").lower()
cls_src = "regex" if origem == "regex" else "ia"

with dir_:
    st.markdown(f"""<div class="card">
      <h3>{bonito(sel.get('nome_classe'))}</h3>
      <div class="dsub">{sel['numero_processo']} · {sel.get('sigla_tribunal') or '—'}
        · {bonito(sel.get('orgao'))}</div>""", unsafe_allow_html=True)

    campos = []
    if sel.get("gatilho_evento"):
        campos.append(("Evento", str(sel["gatilho_evento"]).replace("_", " "), cls_src))
    if sel.get("segmento"):
        campos.append(("Segmento", sel["segmento"], "calc"))
    if sel.get("data_disponibilizacao"):
        campos.append(("Disponibilizada", br(sel["data_disponibilizacao"]), "calc"))
    for rot, chaves in [("Resumo", ("resumo", "sintese")),
                        ("Providência", ("providencia", "acao_sugerida")),
                        ("Prazo no texto", ("prazo_expresso", "prazo_dias")),
                        ("Confiança", ("confianca", "confianca_geral")),
                        ("Destinatário", ("destinatario",))]:
        v = g(an, *chaves)
        if v is not None:
            campos.append((rot, str(v), cls_src))
    if sel.get("data_limite"):
        campos.append(("Termo inicial", br(sel.get("termo_inicial")), "calc"))
        campos.append(("Data limite", br(sel["data_limite"]), "calc"))
        if sel.get("fundamento"):
            campos.append(("Fundamento", sel["fundamento"], "calc"))

    st.markdown("".join(
        f'<div class="f"><div class="fk">{k}</div>'
        f'<div class="fv">{v}<span class="src {s}">{s}</span></div></div>'
        for k, v, s in campos), unsafe_allow_html=True)

    if not sel.get("analisada"):
        st.markdown("""<div class="gap"><div class="t">Ainda não analisada</div>
          <div class="d">Está na fila do analisador. Nada foi extraído desta publicação.</div>
          </div>""", unsafe_allow_html=True)
    elif not sel.get("data_limite") and sel.get("gatilho_evento"):
        st.markdown(f"""<div class="lock"><div class="t">Sem regra para “{
          str(sel['gatilho_evento']).replace('_',' ')}”</div>
          <div class="d">O evento foi identificado, mas não há regra validada para
          esta classe. A publicação aparece na fila sem contagem de prazo.</div>
          </div>""", unsafe_allow_html=True)

    alertas = g(an, "alertas", "avisos_validacao", default=[])
    if alertas:
        st.markdown('<div class="teorlab">Alertas</div>', unsafe_allow_html=True)
        if isinstance(alertas, str):
            alertas = [alertas]
        for a in alertas:
            st.markdown(f'<div class="gap"><div class="d">{a}</div></div>',
                        unsafe_allow_html=True)

    st.markdown('<div class="teorlab">Teor · PII mascarada na origem</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="teor">{(sel.get("texto") or "—")}</div></div>',
                unsafe_allow_html=True)

    with st.expander("JSON bruto da análise"):
        st.json(an if an else {"sem_analise": True})
