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
VIX_URL = "https://vix.com/pt-br/search?q="

# =========================
# TOKENS
# =========================
TMDB_BEARER_TOKEN = st.secrets.get("TMDB_BEARER_TOKEN", "")

# =========================
# 📂 CATEGORIAS E GÊNEROS
# =========================
GENEROS_FILMES = {
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

GENEROS_SERIES = {
    10759: "🎬 Ação e Aventura",
    16: "🎨 Animação",
    35: "😂 Comédia",
    80: "🕵️ Crime",
    99: "📜 Documentário",
    18: "💃 Drama",
    10751: "👨‍👩‍👧 Família",
    10762: "🧒 Infantil",
    9648: "🔍 Mistério",
    10763: "📺 Notícias",
    10764: "🎤 Realidade",
    10765: "🚀 Ficção Científica e Fantasia",
    10766: "📖 Novela",
    10767: "🎵 Talk Show",
    10768: "⚔️ Guerra e Política"
}

# =========================
# 📑 ABAS PRINCIPAIS
# =========================
if "aba_atual" not in st.session_state:
    st.session_state.aba_atual = "filmes"

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
    .btn-vix {{display:inline-block;padding:10px 20px;background:#E50914;color:white;border-radius:6px;text-decoration:none;font-weight:bold;text-align:center;}}
    .btn-vix:hover {{background:#b20610;}}
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


def imagem_filme(item):
    poster = item.get("poster_path")
    if poster:
        return IMAGE_URL + poster.lstrip('/')
    return "https://via.placeholder.com/300x450/1c1c1c/ffffff?text=Sem+Imagem"


def nome_item(item):
    return item.get("title") or item.get("name") or "Sem título"


def eh_favorito(item_id):
    return item_id in st.session_state.favoritos


def alternar_favorito(item):
    fid = item.get("id")
    if fid in st.session_state.favoritos:
        st.session_state.favoritos.remove(fid)
        return False
    else:
        st.session_state.favoritos.append(fid)
        return True


def botao_youtube(item):
    titulo = nome_item(item)
    busca = f"{titulo} completo dublado"
    link_busca = YOUTUBE_SEARCH_URL + urllib.parse.quote(busca)
    return f'<a href="{link_busca}" target="_blank" class="btn-youtube">▶️ Assistir no YouTube</a>'


def botao_vix(item):
    titulo = nome_item(item)
    link_busca = VIX_URL + urllib.parse.quote(titulo)
    return f'<a href="{link_busca}" target="_blank" class="btn-vix">📺 Assistir no ViX — Grátis</a>'


def botao_onde_assistir(item, tipo="movie"):
    item_id = item.get("id")
    if tipo == "movie":
        link = f"https://www.themoviedb.org/movie/{item_id}/watch"
    else:
        link = f"https://www.themoviedb.org/tv/{item_id}/watch"
    return f'<a href="{link}" target="_blank" class="btn-tmdb">📺 Plataformas Oficiais</a>'


# =========================
# 🎬 EXIBIR DETALHES
# =========================
def exibir_detalhes_item(item, tipo="movie"):
    if not item:
        return

    st.markdown('<div class="detalhes-box">', unsafe_allow_html=True)
    
    col_titulo, col_fechar = st.columns([5, 1])
    with col_titulo:
        st.header(f"🎬 {nome_item(item)}")
    with col_fechar:
        if st.button("✖ Fechar", type="primary", use_container_width=True):
            st.session_state.selected_movie = None
            st.rerun()

    item_id = item.get("id")
    eh_fav = eh_favorito(item_id)
    fav_text = "❤️ Salvo" if eh_fav else "🤍 Salvar"
    
    col_poster, col_info = st.columns([1, 2])
    
    with col_poster:
        st.image(imagem_filme(item), width=280, caption="")
        if st.button(fav_text, key="fav_detalhe"):
            alternar_favorito(item)
            st.rerun()
        
        st.markdown('<div class="botoes-acao">', unsafe_allow_html=True)
        st.markdown(botao_youtube(item), unsafe_allow_html=True)
        st.markdown(botao_vix(item), unsafe_allow_html=True)
        st.markdown(botao_onde_assistir(item, tipo), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.caption("📺 ViX: grátis e legal. Abre direto no navegador!")
    
    with col_info:
        st.subheader("📋 Sobre")
        st.write(item.get("overview") or "Sinopse indisponível.")
        st.markdown("---")
        
        data_info = item.get("release_date") or item.get("first_air_date") or "Não informada"
        st.write(f"📅 **Data de lançamento:** {data_info[:4] if data_info else 'Não informada'}")
        
        nota = item.get("vote_average", 0)
        st.write(f"⭐ **Avaliação:** {nota:.1f}/10")
        
        if tipo == "tv":
            st.write(f"📺 **Temporadas:** {item.get('number_of_seasons', 'N/A')}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("")


# =========================
# 📂 MOSTRAR FILEIRA
# =========================
def mostrar_fileira(titulo, items, chave, tipo="movie", limite=20):
    st.subheader(titulo)
    
    if not items:
        st.info("Nenhum resultado encontrado.")
        return
    
    detalhes_abaixo = False
    colunas = st.columns(5)
    
    for indice, item in enumerate(items[:limite]):
        item_id = item.get("id")
        with colunas[indice % 5]:
            st.image(imagem_filme(item), use_container_width=True)
            st.markdown(f"<div class='movie-title'>{nome_item(item)}</div>", unsafe_allow_html=True)
            
            nota = item.get("vote_average", 0)
            data = item.get("release_date") or item.get("first_air_date", "")
            ano = data[:4] if data else ""
            st.caption(f"★ {nota:.1f} · {ano}")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                texto_fav = "❤️" if eh_favorito(item_id) else "🤍"
                if st.button(texto_fav, key=f"fav_{chave}_{item_id}", use_container_width=True):
                    alternar_favorito(item)
                    st.rerun()
            with col_btn2:
                if st.button("▶ Detalhes", key=f"det_{chave}_{item_id}", use_container_width=True):
                    st.session_state.selected_movie = item
                    st.rerun()
            
            if st.session_state.selected_movie and st.session_state.selected_movie.get("id") == item_id:
                detalhes_abaixo = True
    
    st.markdown("---")
    
    if detalhes_abaixo and st.session_state.selected_movie:
        exibir_detalhes_item(st.session_state.selected_movie, tipo)


# =========================
# 🏠 CABEÇALHO E MENU DE ABAS
# =========================
col_logo, col_tema = st.columns([4, 1])
with col_logo:
    st.markdown("<h1 class='destaque' style='font-size:42px;margin:0;'>RFLIX</h1>", unsafe_allow_html=True)
    st.caption("🎬 FILMES • 📺 SÉRIES • 📖 NOVELAS • 🎌 ANIMES • 🎨 DESENHOS")
with col_tema:
    if st.button("🌙" if st.session_state.tema_escuro else "☀️", help="Alternar tema"):
        st.session_state.tema_escuro = not st.session_state.tema_escuro
        st.rerun()

st.markdown("---")

# 📑 ABAS PRINCIPAIS
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🎬 Filmes", use_container_width=True, 
                 type="primary" if st.session_state.aba_atual == "filmes" else "secondary"):
        st.session_state.aba_atual = "filmes"
        st.session_state.selected_movie = None
        st.rerun()
with col2:
    if st.button("📺 Séries", use_container_width=True,
                 type="primary" if st.session_state.aba_atual == "series" else "secondary"):
        st.session_state.aba_atual = "series"
        st.session_state.selected_movie = None
        st.rerun()
with col3:
    if st.button("📖 Novelas", use_container_width=True,
                 type="primary" if st.session_state.aba_atual == "novelas" else "secondary"):
        st.session_state.aba_atual = "novelas"
        st.session_state.selected_movie = None
        st.rerun()
with col4:
    if st.button("🎌 Animes", use_container_width=True,
                 type="primary" if st.session_state.aba_atual == "animes" else "secondary"):
        st.session_state.aba_atual = "animes"
        st.session_state.selected_movie = None
        st.rerun()
with col5:
    if st.button("🎨 Desenhos", use_container_width=True,
                 type="primary" if st.session_state.aba_atual == "desenhos" else "secondary"):
        st.session_state.aba_atual = "desenhos"
        st.session_state.selected_movie = None
        st.rerun()

st.markdown("---")

# 🔍 PESQUISA
pesquisa = st.text_input("🔎 Pesquisar...", placeholder="Digite o nome e aperte Enter")

# =========================
# 🎯 CONTEÚDO DE CADA ABA
# =========================
aba = st.session_state.aba_atual

# -------------------------
# 🎬 FILMES
# -------------------------
if aba == "filmes":
    st.subheader("🎬 Filmes")
    
    genero_opcoes = ["Todos"] + list(GENEROS_FILMES.values())
    genero_nome = st.selectbox("Filtrar por gênero:", genero_opcoes, index=0, key="filtro_filmes")
    genero_id = None
    if genero_nome != "Todos":
        for gid, nome in GENEROS_FILMES.items():
            if nome == genero_nome:
                genero_id = gid
    
    if pesquisa.strip():
        resultados = carregar_filmes("/search/movie", {"query": pesquisa.strip(), "language": "pt-BR", "page": 1})
        if genero_id:
            resultados = [f for f in resultados if genero_id in f.get("genre_ids", [])]
        mostrar_fileira(f"🔎 Resultados para: '{pesquisa}'", resultados, "busca_filmes", "movie")
    elif genero_id:
        resultados = carregar_filmes("/discover/movie", {"with_genres": genero_id, "language": "pt-BR", "sort_by": "popularity.desc", "page": 1})
        mostrar_fileira(f"{genero_nome} — Populares", resultados, "genero_filmes", "movie")
    else:
        em_alta = carregar_filmes("/trending/movie/week", {"language": "pt-BR"})
        mostrar_fileira("🔥 Em Alta", em_alta, "filmes_emalta", "movie")
        
        populares = carregar_filmes("/movie/popular", {"language": "pt-BR", "page": 1})
        mostrar_fileira("🎞️ Mais Populares", populares, "filmes_populares", "movie")
        
        lancamentos = carregar_filmes("/movie/now_playing", {"language": "pt-BR", "page": 1})
        mostrar_fileira("🎬 Em Cartaz", lancamentos, "filmes_lancamentos", "movie")
        
        bem_avaliados = carregar_filmes("/movie/top_rated", {"language": "pt-BR", "page": 1})
        mostrar_fileira("⭐ Melhores Avaliados", bem_avaliados, "filmes_top", "movie")

# -------------------------
# 📺 SÉRIES
# -------------------------
elif aba == "series":
    st.subheader("📺 Séries")
    
    genero_opcoes = ["Todos"] + list(GENEROS_SERIES.values())
    genero_nome = st.selectbox("Filtrar por gênero:", genero_opcoes, index=0, key="filtro_series")
    genero_id = None
    if genero_nome != "Todos":
        for gid, nome in GENEROS_SERIES.items():
            if nome == genero_nome:
                genero_id = gid
    
    if pesquisa.strip():
        resultados = carregar_filmes("/search/tv", {"query": pesquisa.strip(), "language": "pt-BR", "page": 1})
        if genero_id:
            resultados = [s for s in resultados if genero_id in s.get("genre_ids", [])]
        mostrar_fileira(f"🔎 Resultados para: '{pesquisa}'", resultados, "busca_series", "tv")
    elif genero_id:
        resultados = carregar_filmes("/discover/tv", {"with_genres": genero_id, "language": "pt-BR", "sort_by": "popularity.desc", "page": 1})
        mostrar_fileira(f"{genero_nome} — Populares", resultados, "genero_series", "tv")
    else:
        em_alta = carregar_filmes("/trending/tv/week", {"language": "pt-BR"})
        mostrar_fileira("🔥 Em Alta", em_alta, "series_emalta", "tv")
        
        populares = carregar_filmes("/tv/popular", {"language": "pt-BR", "page": 1})
        mostrar_fileira("📺 Mais Populares", populares, "series_populares", "tv")
        
        no_ar = carregar_filmes("/tv/on_the_air", {"language": "pt-BR", "page": 1})
        mostrar_fileira("📡 No Ar Agora", no_ar, "series_noar", "tv")
        
        bem_avaliados = carregar_filmes("/tv/top_rated", {"language": "pt-BR", "page": 1})
        mostrar_fileira("⭐ Melhores Avaliados", bem_avaliados, "series_top", "tv")

# -------------------------
# 📖 NOVELAS
# -------------------------
elif aba == "novelas":
    st.subheader("📖 Novelas")
    
    if pesquisa.strip():
        resultados = carregar_filmes("/search/tv", {"query": pesquisa.strip(), "language": "pt-BR", "page": 1})
        mostrar_fileira(f"🔎 Resultados para: '{pesquisa}'", resultados, "busca_novelas", "tv")
    else:
        novelas = carregar_filmes("/discover/tv", {"with_genres": "10766", "with_original_language": "pt", "language": "pt-BR", "sort_by": "popularity.desc", "page": 1})
        mostrar_fileira("📖 Novelas Brasileiras", novelas, "novelas_br", "tv")
        
        drama = carregar_filmes("/discover/tv", {"with_genres": "18", "with_original_language": "pt", "language": "pt-BR", "sort_by": "popularity.desc", "page": 1})
        mostrar_fileira("💃 Séries de Drama", drama, "novelas_drama", "tv")

# -------------------------
# 🎌 ANIMES
# -------------------------
elif aba == "animes":
    st.subheader("🎌 Animes")
    
    if pesquisa.strip():
        resultados_pt = carregar_filmes("/search/tv", {"query": pesquisa.strip(), "language": "pt-BR", "page": 1})
        resultados_en = carregar_filmes("/search/tv", {"query": pesquisa.strip(), "language": "en-US", "page": 1})
        todos = resultados_pt + resultados_en
        vistos = set()
        unicos = []
        for item in todos:
            item_id = item.get("id")
            if item_id not in vistos:
                vistos.add(item_id)
                unicos.append(item)
        mostrar_fileira(f"🔎 Resultados para: '{pesquisa}'", unicos, "busca_animes", "tv")
    else:
        animes_pop = carregar_filmes("/discover/tv", {"with_genres": "16", "with_original_language": "ja", "language": "pt-BR", "sort_by": "popularity.desc", "page": 1})
        mostrar_fileira("🎌 Animes Populares", animes_pop, "animes_pop", "tv")
        
        animes_top = carregar_filmes("/discover/tv", {"with_genres": "16", "with_original_language": "ja", "language": "pt-BR", "sort_by": "vote_average.desc", "page": 1})
        mostrar_fileira("⭐ Melhores Avaliados", animes_top, "animes_top", "tv")

# -------------------------
# 🎨 DESENHOS
# -------------------------
elif aba == "desenhos":
    st.subheader("🎨 Desenhos")
    
    if pesquisa.strip():
        res_filmes = carregar_filmes("/search/movie", {"query": pesquisa.strip(), "language": "pt-BR", "page": 1})
        res_series = carregar_filmes("/search/tv", {"query": pesquisa.strip(), "language": "pt-BR", "page": 1})
        todos = res_filmes + res_series
        vistos = set()
        unicos = []
        for item in todos:
            item_id = item.get("id")
            if item_id not in vistos:
                vistos.add(item_id)
                unicos.append(item)
        mostrar_fileira(f"🔎 Resultados para: '{pesquisa}'", unicos, "busca_desenhos", "movie")
    else:
        desenhos_filmes = carregar_filmes("/discover/movie", {"with_genres": "16,10751", "language": "pt-BR", "sort_by": "popularity.desc", "page": 1})
        mostrar_fileira("🎬 Filmes de Animação", desenhos_filmes, "desenhos_filmes", "movie")
        
        desenhos_series = carregar_filmes("/discover/tv", {"with_genres": "16,10762", "language": "pt-BR", "sort_by": "popularity.desc", "page": 1})
        mostrar_fileira("📺 Séries de Desenhos", desenhos_series, "desenhos_series", "tv")

# =========================
# ⭐ MEUS FAVORITOS — LATERAL
# =========================
with st.sidebar:
    st.title("⚙️ Menu")
    if not TMDB_BEARER_TOKEN:
        st.warning("⚠️ Configure sua chave TMDB no Secrets")
    else:
        st.success("✅ TMDB conectada")
    
    st.markdown("---")
    st.subheader("⭐ Meus Favoritos")
    st.caption(f"{len(st.session_state.favoritos)} itens salvos")
    
    if st.session_state.favoritos:
        if st.button("Limpar todos os favoritos", use_container_width=True):
            st.session_state.favoritos = []
            st.rerun()
    
    st.markdown("---")
    st.subheader("🎞️ Meus Vídeos")
    titulo_video = st.text_input("Título", key="vid_titulo")
    url_video = st.text_input("URL do vídeo", placeholder="https://...", key="vid_url")
    direitos = st.checkbox("Tenho autorização", key="vid_check")
    if st.button("Adicionar à RFlix", use_container_width=True):
        if titulo_video.strip() and url_video.strip().startswith("https://") and direitos:
            st.session_state.my_videos.append({"title": titulo_video.strip(), "url": url_video.strip()})
            st.success("✅ Adicionado!")
            st.rerun()
        else:
            st.error("Preencha corretamente e confirme os direitos")
# =========================
 # 🎬 CINEMA GRATUITO
 # =========================
 st.write("---")
 st.header("🎬 Cinema Gratuito")
 FILMES_GRATUITOS = [
     {
         "titulo": "Big Buck Bunny",
         "descricao": "Animação de comédia sobre um coelho tranquilo que enfrenta três pequenos provocadores.",
         "url": "https://www.youtube.com/watch?v=YE7VzlLtp-4",
         "credito": "Blender Foundation / bigbuckbunny.org"
     },
     {
         "titulo": "Sintel",
         "descricao": "Uma aventura de fantasia sobre uma jovem que parte em busca de um pequeno dragão.",
         "url": "https://www.youtube.com/watch?v=eRsGyueVLvQ",
         "credito": "Blender Foundation / durian.blender.org"
     }
 ]
 colunas_gratis = st.columns(2)
 for indice, item in enumerate(FILMES_GRATUITOS):
     with colunas_gratis[indice]:
         st.markdown(f"### 🍿 {item['titulo']}")
         st.write(item["descricao"])
         st.video(item["url"])
         st.caption(f"🎬 {item['credito']}")
 # =========================
 # 🍿 MEUS VÍDEOS
 # =========================
 st.markdown("---")
 st.header("🍿 Meus Vídeos Autorizados")
 if st.session_state.my_videos:
     for idx, video in enumerate(st.session_state.my_videos):
         with st.expander(f"🎬 {video['title']}"):
             st.video(video["url"])
             if st.button("🗑️ Remover", key=f"del_vid_{idx}"):
                 st.session_state.my_videos.pop(idx)
                 st.rerun()
 else:
     st.info("Nenhum vídeo cadastrado ainda. Use o menu lateral para adicionar!")
 # =========================
 # RODAPÉ
 # =========================
 st.markdown("---")
 st.caption("RFlix — Seu espaço de entretenimento! Dados da TMDB. ViX e YouTube são marcas independentes. Sempre prefira conteúdo autorizado e legal!")
 st.caption("TMDB: themoviedb.org | ViX: vix.com | YouTube: youtube.com")
