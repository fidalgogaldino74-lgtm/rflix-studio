import os
import requests
import streamlit as st
import urllib.parse

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
YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query="
ARCHIVE_SEARCH_URL = "https://archive.org/search?query="

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
# ESTILOS
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
    .movie-title {{font-size:15px;font-weight:bold;min-height:40px;}}
    div.stButton>button {{border-radius:7px;font-weight:bold;}}
    [data-testid="stImage"] img {{border-radius:8px;}}
    .destaque {{color:{destaque}}}
    .detalhes-box {{background:rgba(30,30,40,0.7);padding:25px;border-radius:12px;margin:20px 0;border:1px solid #333;}}
    .btn-youtube {{display:inline-block;padding:10px 20px;background:#ff0000;color:white;border-radius:6px;text-decoration:none;font-weight:bold;text-align:center;}}
    .btn-youtube:hover {{background:#cc0000;}}
    .btn-archive {{display:inline-block;padding:10px 20px;background:#333333;color:white;border-radius:6px;text-decoration:none;font-weight:bold;text-align:center;}}
    .btn-archive:hover {{background:#111111;}}
    .btn-tmdb {{display:inline-block;padding:10px 20px;background:#01b4e4;color:white;border-radius:6px;text-decoration:none;font-weight:bold;}}
    .botoes-acao {{display:flex;gap:12px;flex-wrap:wrap;margin:15px 0;}}
    </style>
    """, unsafe_allow_html=True)

aplicar_tema()

# =========================
# FUNÇÕES DA TMDB
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
        return IMAGE_URL + poster.lstrip('/')
    return "https://via.placeholder.com/300x450/1c1c1c/ffffff?text=Sem+Imagem"


def nome_filme(filme):
    return filme.get("title") or filme.get("name") or "Filme sem título"


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
    return f'<a href="{link}" target="_blank" style="display:inline-block;padding:6px 12px;background:#1e88d9;color:white;border-radius:6px;text-decoration:none;font-size:14px;margin:8px 0;">🔗 Ver no TMDB</a>'


def botao_assistir_youtube(filme):
    titulo = nome_filme(filme)
    ano = (filme.get("release_date") or "")[:4]
    busca = f"{titulo} filme completo dublado {ano}" if ano else f"{titulo} filme completo dublado"
    link_busca = YOUTUBE_SEARCH_URL + urllib.parse.quote(busca)
    return f'<a href="{link_busca}" target="_blank" class="btn-youtube">▶️ Assistir no YouTube</a>'


def botao_archive(filme):
    """Busca o filme no Internet Archive"""
    titulo = nome_filme(filme)
    ano = (filme.get("release_date") or "")[:4]
    busca = f"{titulo} {ano} movie" if ano else f"{titulo} movie"
    link_busca = ARCHIVE_SEARCH_URL + urllib.parse.quote(busca)
    return f'<a href="{link_busca}" target="_blank" class="btn-archive">📦 Internet Archive — Filmes Grátis</a>'


def botao_onde_assistir(filme):
    filme_id = filme.get("id")
    link = f"https://www.themoviedb.org/movie/{filme_id}/watch"
    return f'<a href="{link}" target="_blank" class="btn-tmdb">📺 Plataformas Oficiais</a>'


# =========================
# FUNÇÃO: EXIBIR DETALHES
# =========================
def exibir_detalhes_filme(filme):
    if not filme:
        return

    st.markdown('<div class="detalhes-box">', unsafe_allow_html=True)
    
    col_titulo, col_fechar = st.columns([5, 1])
    with col_titulo:
        st.header(f"🎬 {nome_filme(filme)}")
    with col_fechar:
        if st.button("✖ Fechar", type="primary", use_container_width=True):
            st.session_state.selected_movie = None
            st.rerun()

    filme_id = filme.get("id")
    eh_fav = eh_favorito(filme_id)
    fav_text = "❤️ Salvo" if eh_fav else "🤍 Salvar"
    
    col_poster, col_info = st.columns([1, 2])
    
    with col_poster:
        st.image(imagem_filme(filme), width=280, caption="")
        if st.button(fav_text, key="fav_detalhe"):
            alternar_favorito(filme)
            st.rerun()
        
        st.markdown('<div class="botoes-acao">', unsafe_allow_html=True)
        st.markdown(botao_assistir_youtube(filme), unsafe_allow_html=True)
        st.markdown(botao_archive(filme), unsafe_allow_html=True)
        st.markdown(botao_onde_assistir(filme), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.caption("📦 Internet Archive: filmes de domínio público gratuitos e legais.")
    
    with col_info:
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
    
    st.markdown("---")
    
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
            "ℹ️ O Internet Archive oferece filmes em domínio público de forma gratuita e legal. "
            "Clique no botão acima para buscar este filme lá!"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("")


# =========================
# CABEÇALHO
# =========================
col_logo, col_tema = st.columns([4, 1])
with col_logo:
    st.markdown("<h1 class='destaque' style='font-size:42px;margin:0;'>RFLIX</h1>", unsafe_allow_html=True)
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
    genero_nome = st.selectbox("Escolha um gênero:", genero_opcoes, index=0)
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
    st.caption("Cadastre somente vídeos próprios ou licenciados.")

# =========================
# DESTAQUE PRINCIPAL
# =========================
if not st.session_state.get("aba_atual") == "favoritos":
    st.markdown("""
    <div style="background:linear-gradient(110deg,#252b3b,#11141c);padding:30px;border-radius:12px;margin-bottom:25px;">
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
    
    detalhes_abaixo = False
    
    colunas = st.columns(5)
    for indice, filme in enumerate(filmes[:20]):
        fid = filme.get("id")
        with colunas[indice % 5]:
            poster_url = imagem_filme(filme)
            st.image(poster_url, use_container_width=True)
            st.markdown(f"<div class='movie-title'>{nome_filme(filme)}</div>", unsafe_allow_html=True)
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
            
            if st.session_state.selected_movie and st.session_state.selected_movie.get("id") == fid:
                detalhes_abaixo = True
    
    st.markdown("---")
    
    if detalhes_abaixo and st.session_state.selected_movie:
        exibir_detalhes_filme(st.session_state.selected_movie)


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
# CARREGAR FILMES
# =========================
filtrado_por_genero = st.session_state.genero_escolhido

if pesquisa.strip():
    resultados = carregar_filmes("/search/movie", {"query": pesquisa.strip(), "language": "pt-BR", "include_adult": False, "page": 1})
    if filtrado_por_genero:
        resultados = [f for f in resultados if filtrado_por_genero in f.get("genre_ids", [])]
    mostrar_fileira(f"🔎 Resultados para: '{pesquisa}'", resultados, "busca", mostrar_genero=True)
elif filtrado_por_genero:
    genero_nome = GENEROS[filtrado_por_genero]
    st.subheader(f"🎭 Filmes de {genero_nome}")
    resultados = carregar_filmes("/discover/movie", {"with_genres": filtrado_por_genero, "language": "pt-BR", "sort_by": "popularity.desc", "page": 1})
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
st.write("Assista a animações disponibilizadas gratuitamente pela Blender Foundation. Respeite os termos de licença e os créditos dos criadores.")
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
st.caption("RFlix — Projeto independente. Dados da TMDB. Internet Archive é uma organização sem fins lucrativos. Filmes de domínio público. Sempre prefira conteúdo autorizado e legal!")
st.caption("TMDB: themoviedb.org | Internet Archive: archive.org | YouTube: youtube.com")
