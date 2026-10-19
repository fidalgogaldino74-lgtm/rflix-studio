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
    initial_sidebar_state="expanded"
)

API_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500/"
YOUTUBE_URL = "https://www.youtube.com/watch?v="

# =========================
# TOKENS
# =========================
TMDB_BEARER_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmODcwODQ4NjM3OTAzOTlhMjlkNDYwYzM0ODAwOGJhNCIsIm5iZiI6MTc5MjM3OTM4Mi45MzUwMDAyLCJzdWIiOiI2YWQ1ODlmNjNlNWYwYjVkYTc3OTdmYzQiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.YO3TBVfUDz8Eu93ClyAVV3zG8cXJUpSbMTuGMEN-ASw"

# =========================
# GÊNEROS
# =========================
GENEROS = {
    28: "🎬 Ação",
    12: "🌍 Aventura",
    16: "🎨 Animação",
    35: "😂 Comédia",
    80: "🕵️ Crime",
    99: "📜 Documentário",
    18: "💃 Drama",
    10751: "👨‍👩‍👧 Família",
    14: "🧙 Fantasia",
    36: "🏛️ História",
    27: "👻 Terror",
    10402: "🎵 Música",
    9648: "🔍 Mistério",
    10749: "❤️ Romance",
    878: "🚀 Ficção Científica",
    53: "😱 Suspense",
    10752: "⚔️ Guerra",
    37: "🤠 Faroeste"
}

# =========================
# ESTADO DA SESSÃO
# =========================
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

if "my_videos" not in st.session_state:
    st.session_state.my_videos = []

if "free_movie_selected" not in st.session_state:
    st.session_state.free_movie_selected = None

if "favoritos" not in st.session_state:
    st.session_state.favoritos = []

if "tema_escuro" not in st.session_state:
    st.session_state.tema_escuro = True

if "genero_escolhido" not in st.session_state:
    st.session_state.genero_escolhido = None

# =========================
# ESTILOS — TEMA CLARO E ESCURO
# =========================
def aplicar_tema():
    if st.session_state.tema_escuro:
        bg_main = "#090b10"
        bg_sidebar = "#151923"
        texto = "white"
        destaque = "#e50914"
    else:
        bg_main = "#ffffff"
        bg_sidebar = "#f0f2f6"
        texto = "#090b10"
        destaque = "#e50914"

    st.markdown(f"""
    <style>
    .stApp {{background:{bg_main};color:{texto}}}
    header[data-testid="stHeader"] {{background:{bg_main}}}
    section[data-testid="stSidebar"] {{background:{bg_sidebar}}}
    h1,h2,h3 {{color:{texto}}}
    .movie-title {{
        font-size:15px;
        font-weight:bold;
        min-height:40px;
    }}
    div.stButton>button {{
        border-radius:7px;
        font-weight:bold;
    }}
    [data-testid="stImage"] img {{border-radius:8px}}
    .destaque {{color:{destaque}}}
    </style>
    """, unsafe_allow_html=True)

aplicar_tema()

# =========================
# FUNÇÕES DA TMDB — CORRIGIDAS
# =========================
def tmdb_get(endpoint, params=None):
    if not TMDB_BEARER_TOKEN:
        return None

    headers = {
        "Authorization": f"Bearer {TMDB_BEARER_TOKEN}",
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
    if poster:
        # ✅ CORRIGIDO: garante a URL correta
        return IMAGE_URL + poster.lstrip('/')
    return "https://via.placeholder.com/300x450/1c1c1c/ffffff?text=Sem+Imagem"


def nome_filme(filme):
    return (
        filme.get("title")
        or filme.get("name")
        or "Filme sem título"
    )


def eh_favorito(filme_id):
    return filme_id in st.session_state.favoritos


def alternar_favorito(filme):
    fid = filme.get("id")
    if fid in st.session_state.favoritos:
        st.session_state.favoritos.remove(fid)
        return False
    else:
        st.session_state.favoritos.append(fid)
        return True


def botao_compartilhar(filme):
    filme_id = filme.get("id")
    link = f"https://www.themoviedb.org/movie/{filme_id}"
    return f"""
    <a href="{link}" target="_blank" style="
        display:inline-block;
        padding:6px 12px;
        background:#1e88d9;
        color:white;
        border-radius:6px;
        text-decoration:none;
        font-size:14px;
        margin:8px 0;
    ">🔗 Compartilhar no TMDB</a>
    """

# =========================
# CABEÇALHO
# =========================
col_logo, col_tema = st.columns([4, 1])
with col_logo:
    st.markdown(
        "<h1 class='destaque' style='font-size:42px;margin:0;'>RFLIX</h1>",
        unsafe_allow_html=True
    )
    st.caption("SEU CINEMA • DESCUBRA • EXPLORE • ASSISTA")

with col_tema:
    if st.button("🌙" if st.session_state.tema_escuro else "☀️", help="Alternar tema"):
        st.session_state.tema_escuro = not st.session_state.tema_escuro
        st.rerun()

st.markdown("---")

# =========================
# MENU LATERAL
# =========================
with st.sidebar:
    st.title("⚙️ Menu")
    st.success("✅ TMDB conectada.")
    st.markdown("---")
    
    st.subheader("🎭 Filtrar por Gênero")
    genero_opcoes = ["Todos"] + list(GENEROS.values())
    genero_nome = st.selectbox(
        "Escolha um gênero:",
        genero_opcoes,
        index=0
    )
    if genero_nome == "Todos":
        st.session_state.genero_escolhido = None
    else:
        for gid, gnome in GENEROS.items():
            if gnome == genero_nome:
                st.session_state.genero_escolhido = gid
                break

    st.markdown("---")
    st.subheader("⭐ Meus Favoritos")
    if st.button("Ver meus favoritos", use_container_width=True):
        st.session_state.aba_atual = "favoritos"
        st.rerun()
    st.caption(f"{len(st.session_state.favoritos)} filmes salvos")

    st.markdown("---")
    st.subheader("🎞️ Adicionar vídeo autorizado")
    titulo_video = st.text_input("Título do vídeo")
    url_video = st.text_input("URL do vídeo", placeholder="https://seusite.com/video.mp4")
    direitos = st.checkbox("Tenho autorização para disponibilizar este vídeo.")
    if st.button("Adicionar à RFlix", use_container_width=True):
        url_limpa = url_video.strip()
        if not titulo_video.strip():
            st.error("Informe o título.")
        elif not url_limpa.startswith("https://"):
            st.error("Informe uma URL HTTPS.")
        elif not direitos:
            st.error("Confirme que tem autorização.")
        else:
            st.session_state.my_videos.append({"title": titulo_video.strip(), "url": url_limpa})
            st.success("Vídeo adicionado nesta sessão.")
            st.rerun()
    st.caption(
        "Cadastre somente vídeos próprios, de domínio público "
        "ou licenciados. A TMDB fornece informações e trailers, "
        "não os filmes completos por questões de direitos autorais."
    )

# =========================
# DESTAQUE PRINCIPAL
# =========================
if not st.session_state.get("aba_atual") == "favoritos":
    st.markdown("""
    <div style="
    background:linear-gradient(110deg,#252b3b,#11141c);
    padding:30px;border-radius:12px;margin-bottom:25px;">
    <p style="color:#ff5964;font-weight:bold;">BEM-VINDO À RFLIX</p>
    <h1>Grandes histórias esperam por você.</h1>
    <p>Explore o catálogo e descubra seu próximo filme.</p>
    </div>
    """, unsafe_allow_html=True)

# =========================
# PESQUISA
# =========================
pesquisa = st.text_input("🔎 Buscar filmes", placeholder="Digite o nome de um filme...")

# =========================
# FUNÇÃO DE EXIBIÇÃO DE FILEIRA
# =========================
def mostrar_fileira(titulo, filmes, chave, mostrar_genero=False):
    st.subheader(titulo)
    if not filmes:
        st.info("Nenhum filme encontrado nesta seção.")
        return

    colunas = st.columns(5)
    for indice, filme in enumerate(filmes[:20]):
        fid = filme.get("id")
        with colunas[indice % 5]:
            poster_url = imagem_filme(filme)
            st.image(poster_url, use_container_width=True)

            st.markdown(
                f"<div class='movie-title'>{nome_filme(filme)}</div>",
                unsafe_allow_html=True
            )

            nota = filme.get("vote_average", 0)
            ano = (filme.get("release_date") or "")[:4]
            st.caption(f"★ {nota:.1f}/10 · {ano or 'Ano indisponível'}")
            
            if mostrar_genero and filme.get("genre_ids"):
                generos_filme = [GENEROS.get(g, "").split(" ")[-1] for g in filme.get("genre_ids", []) if g in GENEROS][:2]
                st.caption(", ".join(generos_filme))

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                texto_fav = "❤️" if eh_favorito(fid) else "🤍"
                if st.button(texto_fav, key=f"fav_{chave}_{fid}", use_container_width=True):
                    alternar_favorito(filme)
                    st.rerun()
            with col_btn2:
                if st.button("▶ Detalhes", key=f"det_{chave}_{fid}", use_container_width=True):
                    st.session_state.selected_movie = filme
                    st.rerun()
            st.markdown(botao_compartilhar(filme), unsafe_allow_html=True)
    st.markdown("---")

# =========================
# ABA: MEUS FAVORITOS
# =========================
if st.session_state.get("aba_atual") == "favoritos":
    st.session_state.aba_atual = None
    st.header("⭐ Meus Filmes Favoritos")
    if not st.session_state.favoritos:
        st.info("🤍 Você ainda não salvou nenhum filme como favorito. Clique no coração nos cartazes dos filmes para adicionar aqui!")
    else:
        with st.spinner("Carregando seus favoritos..."):
            lista_filmes = []
            for fid in st.session_state.favoritos:
                dados = tmdb_get(f"/movie/{fid}", {"language": "pt-BR"})
                if dados:
                    lista_filmes.append(dados)
            if lista_filmes:
                mostrar_fileira("Seus favoritos", lista_filmes, "favoritos")
            else:
                st.info("Nenhum filme encontrado.")
    if st.button("← Voltar ao catálogo", type="primary"):
        st.rerun()
    st.stop()

# =========================
# CARREGAR FILMES CONFORME SELEÇÃO
# =========================
filtrado_por_genero = st.session_state.genero_escolhido

if pesquisa.strip():
    resultados = carregar_filmes(
        "/search/movie",
        {"query": pesquisa.strip(), "language": "pt-BR", "include_adult": False, "page": 1}
    )
    if filtrado_por_genero:
        resultados = [f for f in resultados if filtrado_por_genero in f.get("genre_ids", [])]
    mostrar_fileira(f"🔎 Resultados para: '{pesquisa}'", resultados, "busca", mostrar_genero=True)

elif filtrado_por_genero:
    genero_nome = GENEROS[filtrado_por_genero]
    st.subheader(f"🎭 Filmes de {genero_nome}")
    resultados = carregar_filmes(
        "/discover/movie",
        {"with_genres": filtrado_por_genero, "language": "pt-BR", "sort_by": "popularity.desc", "page": 1}
    )
    mostrar_fileira(f"🎭 {genero_nome} — Populares", resultados, "genero")

else:
    em_alta = carregar_filmes("/trending/movie/week", {"language": "pt-BR"})
    mostrar_fileira("🔥 Em Alta esta Semana", em_alta, "alta")

    lancamentos = carregar_filmes("/movie/now_playing", {"language": "pt-BR", "page": 1})
    mostrar_fileira("🎬 Em Cartaz — Lançamentos", lancamentos, "lancamentos")

    populares = carregar_filmes("/movie/popular", {"language": "pt-BR", "page": 1})
    mostrar_fileira("🎞️ Mais Populares", populares, "pop")

    avaliados = carregar_filmes("/movie/top_rated", {"language": "pt-BR", "page": 1})
    mostrar_fileira("⭐ Mais Bem Avaliados", avaliados, "nota")

# =========================
# DETALHES DO FILME — LAYOUT REORGANIZADO
# =========================
filme = st.session_state.selected_movie

if filme:
    st.markdown("---")
    col_titulo, col_fav = st.columns([5, 1])
    with col_titulo:
        st.header(nome_filme(filme))
    with col_fav:
        filme_id = filme.get("id")
        eh_fav = eh_favorito(filme_id)
        fav_text = "❤️ Salvo" if eh_fav else "🤍 Salvar"
        if st.button(fav_text, key="fav_detalhe"):
            alternar_favorito(filme)
            st.rerun()

    # 🖼️ CAPA DO FILME
    poster_url = imagem_filme(filme)
    st.image(poster_url, width=300, caption="")
    
    # 🔗 COMPARTILHAR
    st.markdown(botao_compartilhar(filme), unsafe_allow_html=True)
    st.markdown("")

    # 📋 INFORMAÇÕES
    st.subheader("📋 Sobre este filme")
    st.write(filme.get("overview") or "Sinopse indisponível.")
    st.markdown("---")
    st.write(f"📅 **Data de lançamento:** {filme.get('release_date') or 'Não informada'}")
    st.write(f"⭐ **Avaliação:** {filme.get('vote_average', 0):.1f}/10 — baseado em {filme.get('vote_count', 0)} votos")
    
    if filme.get("genre_ids"):
        nomes_generos = [GENEROS.get(g, "") for g in filme.get("genre_ids", []) if g in GENEROS]
        st.write(f"🎭 **Gêneros:** {', '.join(nomes_generos)}")
    
    st.write(f"🌐 **Idioma original:** {filme.get('original_language', 'desconhecido').upper()}")
    st.markdown("---")

    # ▶️ TRAILER
    st.subheader("▶ Trailer Oficial")
    videos_data = tmdb_get(f"/movie/{filme_id}/videos", {"language": "pt-BR"})
    trailers = []
    if videos_data:
        trailers = [v for v in videos_data.get("results", []) 
                    if v.get("site") == "YouTube" and v.get("type") in ("Trailer", "Teaser")]
    if trailers:
        trailer = trailers[0]
        st.video(f"{YOUTUBE_URL}{trailer['key']}")
    else:
        st.info("🎬 Nenhum trailer disponível no momento.")
        st.markdown(f"[🔎 Ver mais informações no TMDB](https://www.themoviedb.org/movie/{filme_id})")

    st.markdown("---")

    # 🎬 VÍDEOS AUTORIZADOS
    correspondencias = [
        v for v in st.session_state.my_videos
        if v["title"].strip().casefold() == nome_filme(filme).strip().casefold()
    ]
    if correspondencias:
        st.subheader("🎬 Vídeo disponível")
        for video in correspondencias:
            st.video(video["url"])
    else:
        st.info(
            "ℹ️ A TMDB fornece informações, sinopse e trailers oficiais, "
            "mas não disponibiliza o filme completo por questões de direitos autorais."
        )

    st.markdown("")
    if st.button("✖ Fechar detalhes", type="primary"):
        st.session_state.selected_movie = None
        st.rerun()
    st.markdown("---")

# =========================
# CINEMA GRATUITO
# =========================
st.markdown("---")
st.header("🎬 Cinema Gratuito")

FILMES_GRATUITOS = [
    {
        "titulo": "Big Buck Bunny",
        "descricao": "Animação de comédia sobre um coelho tranquilo que enfrenta três pequenos provocadores.",
        "url": "https://www.youtube.com/watch?v=YE7VzlLtp-4",
        "licenca": "Creative Commons Attribution 3.0",
        "credito": "Blender Foundation / bigbuckbunny.org",
        "fonte": "https://peach.blender.org/about/"
    },
    {
        "titulo": "Sintel",
        "descricao": "Uma aventura de fantasia sobre uma jovem que parte em busca de um pequeno dragão.",
        "url": "https://www.youtube.com/watch?v=eRsGyueVLvQ",
        "licenca": "Creative Commons Attribution 3.0",
        "credito": "Blender Foundation / durian.blender.org",
        "fonte": "https://durian.blender.org/about/"
    }
]

st.write(
    "Assista a animações disponibilizadas gratuitamente pela Blender Foundation. "
    "Respeite os termos de licença e os créditos dos criadores."
)

colunas_gratis = st.columns(2)
for indice, item in enumerate(FILMES_GRATUITOS):
    with colunas_gratis[indice]:
        st.markdown(f"### 🍿 {item['titulo']}")
        st.write(item["descricao"])
        if st.button("▶ Assistir agora", key=f"cinema_gratis_{indice}", use_container_width=True):
            st.session_state.free_movie_selected = indice
            st.rerun()
        st.caption(f"📜 Licença: {item['licenca']}")
        st.markdown(f"[ℹ️ Fonte e detalhes]({item['fonte']})")

if st.session_state.free_movie_selected is not None:
    selecionado = FILMES_GRATUITOS[st.session_state.free_movie_selected]
    st.markdown("---")
    st.subheader(f"▶ {selecionado['titulo']}")
    st.video(selecionado["url"])
    st.caption(f"🎬 Crédito: {selecionado['credito']}")
    if st.button("✖ Fechar"):
        st.session_state.free_movie_selected = None
        st.rerun()

# =========================
# VÍDEOS AUTORIZADOS
# =========================
st.markdown("---")
st.header("🍿 Seus Vídeos Autorizados")
if st.session_state.my_videos:
    for video in st.session_state.my_videos:
        with st.expander(f"🎬 {video['title']}"):
            st.video(video["url"])
else:
    st.info("Nenhum vídeo cadastrado. Use o menu lateral para adicionar um vídeo que você tenha permissão de compartilhar.")

# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.caption(
    "RFlix — Projeto independente. Dados e imagens fornecidos pela TMDB, "
    "mas não endossado nem certificado pela TMDB. "
    "Os filmes completos não são hospedados aqui — apenas informações, "
    "cartazes e trailers oficiais. Assista sempre por plataformas autorizadas."
)
st.caption("TMDB: https://www.themoviedb.org/")
    t
