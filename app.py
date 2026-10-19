
import os
import requests
import streamlit as st

# =========================
# CONFIGURAÇÃO DA RFLIX
# =========================
st.set_page_config(
    page_title="RFlix | Seu cinema",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"

st.markdown("""
<style>
.stApp {
    background: #090b10;
    color: white;
}
header[data-testid="stHeader"] {
    background: #090b10;
}
section[data-testid="stSidebar"] {
    background: #151923;
}
h1, h2, h3 {
    color: white;
}
.movie-title {
    font-size: 15px;
    font-weight: bold;
    min-height: 40px;
}
div.stButton > button {
    border-radius: 7px;
    font-weight: bold;
}
[data-testid="stImage"] img {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# A chave fica nos Secrets do Streamlit.
# Nunca coloque o token diretamente neste arquivo.
try:
    TMDB_TOKEN = st.secrets.get("TMDB_BEARER_TOKEN", "")
except Exception:
    TMDB_TOKEN = os.environ.get("TMDB_BEARER_TOKEN", "")

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

if "my_videos" not in st.session_state:
    st.session_state.my_videos = []

# =========================
# CONSULTA À TMDB
# =========================
def tmdb_get(endpoint, params=None):
    if not TMDB_TOKEN:
        return None

    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "accept": "application/json"
    }

    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            headers=headers,
            params=params or {},
            timeout=20
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def carregar_filmes(endpoint, params=None):
    data = tmdb_get(endpoint, params)
    if not data:
        return []
    return data.get("results", [])


def imagem_filme(filme):
    poster = filme.get("poster_path")
    if poster:
        return IMAGE_URL + poster
    return None


# =========================
# CABEÇALHO
# =========================
st.markdown(
    "<h1 style='color:#e50914;font-size:42px;'>RFLIX</h1>",
    unsafe_allow_html=True
)
st.caption("SEU CINEMA • DESCUBRA • EXPLORE • ASSISTA")

st.markdown("---")

# =========================
# MENU LATERAL
# =========================
with st.sidebar:
    st.title("⚙️ Configurações")
    st.write("Catálogo de filmes pela TMDB.")

    if TMDB_TOKEN:
        st.success("Token TMDB configurado.")
    else:
        st.warning(
            "Configure TMDB_BEARER_TOKEN nos Secrets "
            "para carregar o catálogo."
        )

    st.markdown("---")
    st.subheader("🎞️ Adicionar vídeo autorizado")

    titulo_video = st.text_input("Título do vídeo")
    url_video = st.text_input(
        "URL direta do vídeo",
        placeholder="https://exemplo.com/filme.mp4"
    )

    direitos_confirmados = st.checkbox(
        "Tenho autorização para disponibilizar este vídeo."
    )

    if st.button("Adicionar à RFlix", use_container_width=True):
        url_limpa = url_video.strip()

        if not titulo_video.strip():
            st.error("Informe o título.")
        elif not url_limpa.startswith("https://"):
            st.error("Informe uma URL HTTPS válida.")
        elif not direitos_confirmados:
            st.error("Confirme que possui autorização.")
        else:
            st.session_state.my_videos.append({
                "title": titulo_video.strip(),
                "url": url_limpa
            })
            st.success("Vídeo adicionado nesta sessão.")

    st.caption(
        "Use somente vídeos próprios, de domínio público "
        "ou licenciados. A URL precisa apontar para um "
        "arquivo de vídeo compatível com o player."
    )

# =========================
# DESTAQUE PRINCIPAL
# =========================
st.markdown("""
<div style="
background:linear-gradient(110deg,#252b3b,#11141c);
padding:30px;border-radius:12px;">
<p style="color:#ff5964;font-weight:bold;">BEM-VINDO À RFLIX</p>
<h1>Grandes histórias esperam por você.</h1>
<p>Explore o catálogo e descubra seu próximo filme.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# =========================
# PESQUISA
# =========================
pesquisa = st.text_input(
    "🔎 Buscar filmes",
    placeholder="Digite o nome de um filme..."
)

if pesquisa.strip():
    resultados = carregar_filmes(
        "/search/movie",
        {
            "query": pesquisa.strip(),
            "language": "pt-BR",
            "include_adult": False,
            "page": 1
        }
    )
    titulo_secao = "Resultados da pesquisa"
else:
    resultados = []
    titulo_secao = ""

# =========================
# FILEIRAS DE FILMES
# =========================
def mostrar_fileira(titulo, filmes, chave):
    st.subheader(titulo)

    if not filmes:
        st.info("Nenhum filme disponível nesta seção.")
        return

    colunas = st.columns(5)

    for indice, filme in enumerate(filmes[:20]):
        with colunas[indice % 5]:
            poster = imagem_filme(filme)

            if poster:
                st.image(poster, use_container_width=True)
            else:
                st.markdown("🎬 *Cartaz indisponível*")

            nome = (
                filme.get("title")
                or filme.get("name")
                or "Filme sem título"
            )
            st.markdown(
                f"<div class='movie-title'>{nome}</div>",
                unsafe_allow_html=True
            )

            nota = filme.get("vote_average", 0)
            ano = (filme.get("release_date") or "")[:4]
            st.caption(f"★ {nota:.1f}/10 · {ano or 'Ano indisponível'}")

            if st.button(
                "Ver detalhes",
                key=f"{chave}_{filme.get('id', indice)}",
                use_container_width=True
            ):
                st.session_state.selected_movie = filme


if pesquisa.strip():
    mostrar_fileira(titulo_secao, resultados, "busca")
else:
    if TMDB_TOKEN:
        em_alta = carregar_filmes(
            "/trending/movie/week",
            {"language": "pt-BR"}
        )
        populares = carregar_filmes(
            "/movie/popular",
            {"language": "pt-BR", "page": 1}
        )
        avaliados = carregar_filmes(
            "/movie/top_rated",
            {"language": "pt-BR", "page": 1}
        )

        mostrar_fileira("🔥 Em alta", em_alta, "alta")
        st.markdown("---")
        mostrar_fileira("🎬 Filmes populares", populares, "pop")
        st.markdown("---")
        mostrar_fileira("⭐ Mais bem avaliados", avaliados, "nota")
    else:
        st.info(
            "Configure a chave da TMDB para visualizar "
            "cartazes, sinopses e catálogo."
        )

# =========================
# DETALHES DO FILME
# =========================
filme = st.session_state.selected_movie

if filme:
    st.markdown("---")
    st.header(filme.get("title", "Detalhes do filme"))

    poster, detalhes = st.columns([1, 2])

    with poster:
        if imagem_filme(filme):
            st.image(imagem_filme(filme), use_container_width=True)

    with detalhes:
        st.write(filme.get("overview") or "Sinopse indisponível.")
        st.write(
            f"Data de lançamento: "
            f"{filme.get('release_date') or 'Não informada'}"
        )
        st.write(
            f"Avaliação: {filme.get('vote_average', 0):.1f}/10"
        )

        if TMDB_TOKEN and filme.get("id"):
            videos = tmdb_get(
                f"/movie/{filme['id']}/videos",
                {"language": "pt-BR"}
            )

            if videos:
                trailers = [
                    v for v in videos.get("results", [])
                    if v.get("site") == "YouTube"
                    and v.get("type") in ("Trailer", "Teaser")
                ]

                if trailers:
                    trailer = trailers[0]
                    st.link_button(
                        "▶️ Assistir ao trailer",
                        "https://www.youtube.com/watch?v="
                        + trailer["key"]
                    )

    st.caption(
        "O catálogo não fornece o filme completo. "
        "A reprodução depende de uma fonte autorizada."
    )

# =========================
# FILMES AUTORIZADOS
# =========================
st.markdown("---")
st.header("🍿 Filmes disponíveis para assistir")

if st.session_state.my_videos:
    for indice, video in enumerate(st.session_state.my_videos):
        with st.expander("🎬 " + video["title"]):
            st.video(video["url"])
else:
    st.info(
        "Ainda não há vídeos adicionados. "
        "Use o menu lateral para cadastrar um vídeo autorizado."
    )

# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.caption(
    "RFlix — Projeto independente. "
    "Este produto utiliza a API da TMDB, mas não é "
    "endossado nem certificado pela TMDB."
)
st.caption(
    "TMDB: https://www.themoviedb.org/ | "
    "Documentação: https://developer.themoviedb.org/"
    )
    
