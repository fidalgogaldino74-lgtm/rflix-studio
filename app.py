import requests
import streamlit as st
import urllib.parse

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(
    page_title="RFlix | Seu cinema",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500/"
YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query="
VIX_URL = "https://vix.com/pt-br/search?q="

TMDB_BEARER_TOKEN = st.secrets.get("TMDB_BEARER_TOKEN", "")

# =========================
# ESTADO
# =========================
if "aba_atual" not in st.session_state:
    st.session_state.aba_atual = "filmes"
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None
if "favoritos" not in st.session_state:
    st.session_state.favoritos = []

# =========================
# FUNÇÕES
# =========================
def tmdb_get(endpoint, params=None):
    if not TMDB_BEARER_TOKEN:
        return None
    headers = {"Authorization": f"Bearer {TMDB_BEARER_TOKEN}", "accept": "application/json"}
    try:
        r = requests.get(f"{API_URL}{endpoint}", headers=headers, params=params or {}, timeout=20)
        r.raise_for_status()
        return r.json()
    except:
        return None

def carregar(endpoint, params=None):
    data = tmdb_get(endpoint, params)
    return data.get("results", []) if data else []

def imagem(item):
    p = item.get("poster_path")
    return IMAGE_URL + p.lstrip('/') if p else "https://via.placeholder.com/300x450/1c1c1c/ffffff?text=Sem+Imagem"

def nome(item):
    return item.get("title") or item.get("name") or "Sem título"

def botao_youtube(item):
    link = YOUTUBE_SEARCH_URL + urllib.parse.quote(f"{nome(item)} completo dublado")
    return f'<a href="{link}" target="_blank" style="padding:8px 16px;background:#ff0000;color:white;border-radius:6px;text-decoration:none;font-weight:bold;margin:4px;">▶️ YouTube</a>'

def botao_vix(item):
    link = VIX_URL + urllib.parse.quote(nome(item))
    return f'<a href="{link}" target="_blank" style="padding:8px 16px;background:#E50914;color:white;border-radius:6px;text-decoration:none;font-weight:bold;margin:4px;">📺 ViX</a>'

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
.stApp {background:#090b10;color:white;}
section[data-testid="stSidebar"] {background:#151923;}
.movie-title {font-size:15px;font-weight:bold;min-height:42px;}
</style>
""", unsafe_allow_html=True)

# =========================
# CABEÇALHO
# =========================
st.markdown("# 🎬 RFLIX")
st.caption("🎬 Filmes • 📺 Séries • 📖 Novelas • 🎌 Animes • 🎨 Desenhos")
st.write("---")

# ABAS
abas = ["filmes", "series", "novelas", "animes", "desenhos"]
nomes = ["🎬 Filmes", "📺 Séries", "📖 Novelas", "🎌 Animes", "🎨 Desenhos"]
colunas_abas = st.columns(5)
for i, aba in enumerate(abas):
    with colunas_abas[i]:
        if st.button(nomes[i], use_container_width=True, type="primary" if st.session_state.aba_atual == aba else "secondary"):
            st.session_state.aba_atual = aba
            st.session_state.selected_movie = None
            st.rerun()

st.write("---")

pesquisa = st.text_input("🔎 Pesquisar...")

# =========================
# EXIBIR FILEIRA
# =========================
def mostrar_fileira(titulo, lista, chave):
    st.subheader(titulo)
    if not lista:
        st.info("Nenhum resultado encontrado.")
        return
    cols = st.columns(5)
    for i, item in enumerate(lista[:20]):
        item_id = item.get("id")
        with cols[i % 5]:
            st.image(imagem(item), use_container_width=True)
            st.markdown(f"<div class='movie-title'>{nome(item)}</div>", unsafe_allow_html=True)
            nota = item.get("vote_average", 0)
            data = item.get("release_date") or item.get("first_air_date", "")
            st.caption(f"★ {nota:.1f} · {data[:4] if data else ''}")
            c1, c2 = st.columns(2)
            with c1:
                txt = "❤️" if item_id in st.session_state.favoritos else "🤍"
                if st.button(txt, key=f"fav_{chave}_{item_id}"):
                    if item_id in st.session_state.favoritos:
                        st.session_state.favoritos.remove(item_id)
                    else:
                        st.session_state.favoritos.append(item_id)
                    st.rerun()
            with c2:
                if st.button("▶", key=f"det_{chave}_{item_id}"):
                    st.session_state.selected_movie = item
                    st.rerun()
    st.write("---")
    if st.session_state.selected_movie and st.session_state.selected_movie.get("id") in [x.get("id") for x in lista]:
        item = st.session_state.selected_movie
        col_p, col_i = st.columns([1, 2])
        with col_p:
            st.image(imagem(item), width=250)
            st.markdown("<div style='margin:12px 0;display:flex;gap:8px;'>" + botao_youtube(item) + botao_vix(item) + "</div>", unsafe_allow_html=True)
        with col_i:
            st.subheader(nome(item))
            st.write(item.get("overview") or "Sem sinopse disponível.")
            st.write(f"📅 Data: {item.get('release_date') or item.get('first_air_date', '---')}")
            st.write(f"⭐ Nota: {item.get('vote_average', 0):.1f}/10")
        st.write("---")

# =========================
# CONTEÚDO DAS ABAS
# =========================
aba = st.session_state.aba_atual

if aba == "filmes":
    if pesquisa.strip():
        res = carregar("/search/movie", {"query": pesquisa.strip(), "language": "pt-BR"})
        mostrar_fileira(f"Resultados para: {pesquisa}", res, "busca_f")
    else:
        mostrar_fileira("🔥 Em Alta", carregar("/trending/movie/week", {"language": "pt-BR"}), "alta_f")
        mostrar_fileira("🎞️ Populares", carregar("/movie/popular", {"language": "pt-BR"}), "pop_f")
        mostrar_fileira("⭐ Melhores Avaliados", carregar("/movie/top_rated", {"language": "pt-BR"}), "top_f")

elif aba == "series":
    if pesquisa.strip():
        res = carregar("/search/tv", {"query": pesquisa.strip(), "language": "pt-BR"})
        mostrar_fileira(f"Resultados para: {pesquisa}", res, "busca_s")
    else:
        mostrar_fileira("🔥 Em Alta", carregar("/trending/tv/week", {"language": "pt-BR"}), "alta_s")
        mostrar_fileira("📺 Populares", carregar("/tv/popular", {"language": "pt-BR"}), "pop_s")

elif aba == "novelas":
    if pesquisa.strip():
        res = carregar("/search/tv", {"query": pesquisa.strip(), "language": "pt-BR"})
        mostrar_fileira(f"Resultados para: {pesquisa}", res, "busca_n")
    else:
        res = carregar("/discover/tv", {"with_genres": "10766", "with_original_language": "pt", "language": "pt-BR"})
        mostrar_fileira("📖 Novelas Brasileiras", res, "nov_br")

elif aba == "animes":
    if pesquisa.strip():
        res1 = carregar("/search/tv", {"query": pesquisa.strip(), "language": "pt-BR"})
        res2 = carregar("/search/tv", {"query": pesquisa.strip(), "language": "en-US"})
        vistos = set()
        unicos = []
        for r in res1 + res2:
            rid = r.get("id")
            if rid not in vistos:
                vistos.add(rid)
                unicos.append(r)
        mostrar_fileira(f"Resultados para: {pesquisa}", unicos, "busca_a")
    else:
        res = carregar("/discover/tv", {"with_genres": "16", "with_original_language": "ja", "language": "pt-BR"})
        mostrar_fileira("🎌 Animes Populares", res, "anime_pop")

elif aba == "desenhos":
    if pesquisa.strip():
        res1 = carregar("/search/movie", {"query": pesquisa.strip(), "language": "pt-BR"})
        res2 = carregar("/search/tv", {"query": pesquisa.strip(), "language": "pt-BR"})
        vistos = set()
        unicos = []
        for r in res1 + res2:
            rid = r.get("id")
            if rid not in vistos:
                vistos.add(rid)
                unicos.append(r)
        mostrar_fileira(f"Resultados para: {pesquisa}", unicos, "busca_d")
    else:
        res = carregar("/discover/movie", {"with_genres": "16", "language": "pt-BR"})
        mostrar_fileira("🎬 Filmes de Animação", res, "desenho_f")
        res_tv = carregar("/discover/tv", {"with_genres": "16", "language": "pt-BR"})
        mostrar_fileira("📺 Séries de Desenhos", res_tv, "desenho_s")

st.write("---")
st.caption("RFlix • Dados da TMDB • ViX e YouTube são marcas independentes • Prefira conteúdo legal e autorizado!")
    
