
import os
import requests
import streamlit as st

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
.stApp { background: #090b10; color: white; }
header[data-testid="stHeader"] { background: #090b10; }
section[data-testid="stSidebar"] { background: #151923; }
h1, h2, h3 { color: white; }
.movie-title { font-size: 15px; font-weight: bold; min-height: 40px; }
div.stButton > button {
    border-radius: 7px;
    font-weight: bold;
}
[data-testid="stImage"] img { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# TOKEN TMDB: configurar em App settings > Secrets
try:
    TMDB_TOKEN = st.secrets.get("TMDB_BEARER_TOKEN", "")
except Exception:
    TMDB_TOKEN = os.environ.get("TMDB_BEARER_TOKEN", "")

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

if "my_videos" not in st.session_state:
    st.session_state.my_videos = []


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
    return data.get("results", []) if data else []


def imagem_filme(filme):
    poster = filme.get("poster_path")
    return IMAGE_URL + poster if poster else None


def nome_filme(filme):
    return filme.get("title") or filme.get("name") or "Filme sem título"


# CABEÇALHO
st.markdown(
    "<h1 style='color:#e50914;font-size:42px;'>RFLIX</h1>",
    unsafe_allow_html=True
)
st.caption("SEU CINEMA • DESCUBRA • EXPLORE • ASSISTA")
st.markdown("---")

# MENU LATERAL
with st.sidebar:
    st.title("⚙️ Configurações")

    if TMDB_TOKEN:
        st.success("TMDB conectada.")
    else:
        st.warning("Configure TMDB_BEARER_TOKEN nos Secrets.")

    st.markdown("---")
    st.subheader("🎞️ Adicionar vídeo autorizado")

    titulo_video = st.text_input("Título do vídeo")
    url_video = st.text_input(
        "URL direta do vídeo",
        placeholder="https://seusite.com/video.mp4"
    )

    direitos = st.checkbox(
        "Tenho autorização para disponibilizar este vídeo."
    )

    if st.button("Adicionar vídeo", use_container_width=True):
        url_limpa = url_video.strip()

        if not titulo_video.strip():
            st.error("Informe o título do vídeo.")
        elif not url_limpa.startswith("https://"):
            st.error("Use uma URL HTTPS.")
        elif not direitos:
            st.error("Confirme que tem autorização.")
        else:
            st.session_state.my_videos.append({
                "title": titulo_video.strip(),
                "url": url_limpa
            })
            st.success("Vídeo adicionado nesta sessão.")
            st.rerun()

    st.caption(
        "Cadastre somente vídeos próprios, de domínio público "
        "ou licenciados. A URL deve ser compatível com o player."
    )

# DESTAQUE
st.markdown("""
<div style="background:linear-gradient(110deg,#252b3b,#11141c);
padding:30px;border-radius:12px;">
<p style="color:#ff5964;font-weight:bold;">BEM-VINDO À RFLIX</p>
<h1>Grandes histórias esperam por você.</h1>
<p>Encontre seu próximo filme e descubra o que assistir.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# PESQUISA
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
else:
    resultados = []


# DETALHES: MOSTRADOS LOGO APÓS A SELEÇÃO
filme = st.session_state.selected_movie

if filme:
    st.markdown("---")
    st.subheader("🎬 Filme selecionado")

    if st.button("✖ Fechar detalhes"):
        st.session_state.selected_movie = None
        st.rerun()

    col_poster, col_info = st.columns([1, 2])

    with col_poster:
        poster = imagem_filme(filme)
        if poster:
            st.image(poster, use_container_width=True)
        else:
            st.info("Cartaz indisponível.")

    with col_info:
        st.header(nome_filme(filme))
        st.write(filme.get("overview") or "Sinopse indisponível.")
        st.write(
            "Lançamento: "
            + (filme.get("release_date") or "Não informado")
        )
        st.write(
            f"Avaliação: {filme.get('vote_average', 0):.1f}/10"
        )

        filme_id = filme.get("id")
        videos_tmdb = (
            tmdb_get(
                f"/movie/{filme_id}/videos",
                {"language": "pt-BR"}
            )
            if TMDB_TOKEN and filme_id else None
        )

        trailers = []
        if videos_tmdb:
            trailers = [
                v for v in videos_tmdb.get("results", [])
                if v.get("site") == "YouTube"
                and v.get("type") in ("Trailer", "Teaser")
            ]

        if trailers:
            trailer = trailers[0]
            st.link_button(
                "▶ Assistir ao trailer",
                "https://www.youtube.com/watch?v=" + trailer["key"]
            )

        # Procura vídeo autorizado com o mesmo título
        correspondencias = [
            v for v in st.session_state.my_videos
            if v["title"].strip().casefold()
            == nome_filme(filme).strip().casefold()
        ]

        if correspondencias:
            st.success("Vídeo autorizado disponível!")
            for video in correspondencias:
                st.video(video["url"])
        else:
            st.info(
                "Não há vídeo completo cadastrado para este título. "
                "A TMDB fornece informações e cartazes, não o filme completo."
            )

# CATÁLOGO
def mostrar_fileira(titulo, filmes, chave):
    st.subheader(titulo)

    if not filmes:
        st.info("Nenhum filme encontrado nesta seção.")
        return

    colunas = st.columns(5)

    for indice, item in enumerate(filmes[:20]):
        with colunas[indice % 5]:
            poster = imagem_filme(item)

            if poster:
                st.image(poster, use_container_width=True)
            else:
                st.markdown("🎬 Cartaz indisponível")

            st.markdown(
                f"<div class='movie-title'>{nome_filme(item)}</div>",
                unsafe_allow_html=True
            )

            nota = item.get("vote_average", 0)
            ano = (item.get("release_date") or "")[:4]
            st.caption(f"★ {nota:.1f}/10 · {ano or 'Ano não informado'}")

            if st.button(
                "▶ Ver detalhes e assistir",
                key=f"{chave}_{item.get('id', indice)}",
                use_container_width=True
            ):
                st.session_state.selected_movie = item
                st.rerun()


if pesquisa.strip():
    mostrar_fileira("🔎 Resultados da pesquisa", resultados, "busca")
elif TMDB_TOKEN:
    em_alta = carregar_filmes(
        "/trending/movie/week", {"language": "pt-BR"}
    )
    populares = carregar_filmes(
        "/movie/popular", {"language": "pt-BR", "page": 1}
    )
    avaliados = carregar_filmes(
        "/movie/top_rated", {"language": "pt-BR", "page": 1}
    )

    mostrar_fileira("🔥 Em alta", em_alta, "alta")
    st.markdown("---")
    mostrar_fileira("🎬 Filmes populares", populares, "pop")
    st.markdown("---")
    mostrar_fileira("⭐ Mais bem avaliados", avaliados, "nota")
else:
    st.warning(
        "Configure TMDB_BEARER_TOKEN nos Secrets para carregar o catálogo."
    )

# TODOS OS VÍDEOS CADASTRADOS
st.markdown("---")
st.header("🍿 Vídeos disponíveis para assistir")

if st.session_state.my_videos:
    for video in st.session_state.my_videos:
        with st.expander("🎬 " + video["title"]):
            st.video(video["url"])
else:
    st.info(
        "Nenhum vídeo cadastrado. Adicione um vídeo autorizado "
        "pelo menu lateral."
    )

# RODAPÉ
st.markdown("---")
st.caption(
    "RFlix — Projeto independente. Este produto utiliza a API da TMDB, "
    "mas não é endossado nem certificado pela TMDB."
)
st.caption("TMDB: https://www.themoviedb.org/")
    
