
import streamlit as st
import edge_tts
import asyncio
import os
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

# ==========================================
# CONFIGURAÇÃO DO RFLIX STUDIO
# ==========================================

st.set_page_config(
    page_title="RFlix Studio",
    page_icon="🎬",
    layout="wide"
)

PASTA = Path(".")
HISTORICO = PASTA / "historico.txt"
HISTORICO_VIDEOS = PASTA / "historico_videos.txt"
ARQUIVO_AUDIO = PASTA / "ultimo_audio.mp3"

VOZES = {
    "👩 LARISSA — Jovem, animada e suave":
        "pt-BR-AntonioNeural",
    "👩 JULIA — Jovem, clara e gentil":
        "pt-BR-FranciscaNeural",
    "👨 PEDRO — Jovem, amigável e energético":
        "pt-BR-AntonioNeural"
}

st.markdown("""
<style>
.stApp {
    background-color: #071a35;
    color: white;
}
h1, h2, h3 {
    color: #f4c95d;
}
.stButton button {
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 RFlix Studio")
st.caption("Seu estúdio para criar histórias, vozes e projetos de vídeo.")

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def salvar_historico(arquivo, texto):
    with open(arquivo, "a", encoding="utf-8") as f:
        f.write(texto + "\n\n")


def ler_arquivo(arquivo):
    if arquivo.exists():
        return arquivo.read_text(encoding="utf-8")
    return ""


async def criar_audio(texto, voz, destino):
    comunicacao = edge_tts.Communicate(texto, voz)
    await comunicacao.save(str(destino))


def gerar_roteiro_gemini(ideia, genero, duracao, personagens):
    api_key = st.secrets.get("GEMINI_API_KEY", "")

    if not api_key:
        raise ValueError(
            "A chave GEMINI_API_KEY não está configurada "
            "nos Secrets do Streamlit."
        )

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-flash-latest:generateContent"
    )

    prompt = f"""
Crie um roteiro ORIGINAL para uma novela da RFlix Studio.

Gênero: {genero}
Duração desejada: {duracao}
Ideia central: {ideia}
Personagens: {personagens or "Crie personagens originais"}

Escreva em português brasileiro, com linguagem natural.

Organize o episódio em:
1. Título.
2. Abertura que prenda a atenção.
3. Cenas numeradas em ordem.
4. Descrição visual de cada cena.
5. Diálogos naturais, com o nome de quem fala.
6. Emoções, expressões e ações dos personagens.
7. Indicações de som ou música quando forem úteis.
8. Um final envolvente que desperte curiosidade pelo próximo episódio.

Adapte o tamanho à duração desejada. Crie uma história original.
"""

    resposta = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "X-goog-api-key": api_key
        },
        json={
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        },
        timeout=90
    )

    if not resposta.ok:
        raise RuntimeError(
            f"Erro da API Gemini ({resposta.status_code}): "
            f"{resposta.text[:700]}"
        )

    dados = resposta.json()
    candidatos = dados.get("candidates", [])

    if not candidatos:
        raise RuntimeError(
            "O Gemini não retornou um roteiro. "
            "Tente mudar a ideia ou verificar os limites da API."
        )

    partes = candidatos[0].get("content", {}).get("parts", [])
    roteiro = "\n".join(
        parte["text"] for parte in partes if "text" in parte
    )

    if not roteiro.strip():
        raise RuntimeError("A resposta do Gemini veio vazia.")

    return roteiro


# ==========================================
# MENU PRINCIPAL
# ==========================================

with st.sidebar:
    st.title("🎥 RFlix Studio")
    st.write("Menu principal")

    aba = st.radio(
        "Escolha uma função:",
        [
            "🎙️ Gerar Voz",
            "🎬 Gerar Vídeo",
            "🤖 Roteirista IA",
            "📂 Meus Arquivos",
            "ℹ️ Sobre"
        ]
    )

# ==========================================
# ABA 1 — GERAR VOZ
# ==========================================

if aba == "🎙️ Gerar Voz":

    st.header("🎙️ Gerador de Voz")
    st.write("Transforme seus textos em narração.")

    texto = st.text_area(
        "Digite o texto para narrar:",
        height=220,
        placeholder="Cole aqui o texto da sua novela..."
    )

    voz_nome = st.selectbox(
        "Escolha uma voz:",
        list(VOZES.keys())
    )

    if st.button("🔊 GERAR ÁUDIO", type="primary"):

        if not texto.strip():
            st.warning("Digite um texto antes de gerar o áudio.")

        else:
            try:
                with st.spinner("Gerando a narração..."):
                    asyncio.run(
                        criar_audio(
                            texto,
                            VOZES[voz_nome],
                            ARQUIVO_AUDIO
                        )
                    )

                st.success("Áudio gerado!")
                salvar_historico(
                    HISTORICO,
                    f"Data: {datetime.now():%d/%m/%Y %H:%M}\n"
                    f"Voz: {voz_nome}\nTexto:\n{texto}"
                )

            except Exception as erro:
                st.error(f"Erro ao gerar áudio: {erro}")

    if ARQUIVO_AUDIO.exists():
        st.subheader("Seu áudio")
        st.audio(str(ARQUIVO_AUDIO), format="audio/mp3")

        st.download_button(
            "⬇️ Baixar áudio MP3",
            data=ARQUIVO_AUDIO.read_bytes(),
            file_name="rflix_narracao.mp3",
            mime="audio/mpeg"
        )

# ==========================================
# ABA 2 — GERAR VÍDEO
# ==========================================

elif aba == "🎬 Gerar Vídeo":

    st.header("🎬 Criador de Prompts para Vídeos")
    st.write(
        "Prepare a descrição da cena para usar em uma ferramenta "
        "de geração de vídeo."
    )

    ideia_video = st.text_area(
        "Descreva o vídeo que deseja criar:",
        height=180,
        placeholder=(
            "Ex.: Uma jovem chega a uma mansão durante "
            "uma noite de tempestade..."
        )
    )

    estilo = st.selectbox(
        "Estilo visual:",
        [
            "Realista cinematográfico",
            "Cartoon colorido",
            "Animação 3D",
            "Novela dramática",
            "Terror e mistério"
        ]
    )

    duracao_video = st.selectbox(
        "Duração desejada:",
        ["5 segundos", "10 segundos", "15 segundos", "30 segundos"]
    )

    if st.button("✨ PREPARAR PROMPT", type="primary"):

        if not ideia_video.strip():
            st.warning("Descreva a cena primeiro.")

        else:
            prompt_video = f"""
Crie um vídeo no estilo: {estilo}.
Duração desejada: {duracao_video}.
Descrição da cena: {ideia_video}

Inclua movimentos de câmera, iluminação, ambiente,
expressões dos personagens e continuidade visual.
Não inclua legendas, textos ou marcas-d'água,
a menos que sejam solicitados.
"""

            st.session_state["prompt_video"] = prompt_video

            salvar_historico(
                HISTORICO_VIDEOS,
                f"Data: {datetime.now():%d/%m/%Y %H:%M}\n"
                f"{prompt_video}"
            )

    if st.session_state.get("prompt_video"):
        st.subheader("Prompt preparado")
        st.text_area(
            "Copie e utilize na ferramenta de vídeo:",
            value=st.session_state["prompt_video"],
            height=220,
            key="prompt_video_exibicao"
        )

        st.download_button(
            "⬇️ Baixar prompt TXT",
            data=st.session_state["prompt_video"],
            file_name="prompt_rflix.txt",
            mime="text/plain"
        )

    st.divider()
    st.subheader("Ferramentas externas")

    st.markdown(
        "- [Hugging Face Spaces](https://huggingface.co/spaces) — "
        "experimente demonstrações de IA.\n"
        "- [Wan](https://wan.video/) — consulte a disponibilidade "
        "e as condições atuais.\n"
        "- [Google AI Studio](https://aistudio.google.com/) — "
        "experimente ferramentas de IA."
    )

    st.caption(
        "Esses serviços são externos. A disponibilidade gratuita, "
        "os limites e a geração de vídeos dependem de cada plataforma."
    )

# ==========================================
# ABA 3 — ROTEIRISTA IA COM GEMINI
# ==========================================

elif aba == "🤖 Roteirista IA":

    st.header("🤖 Roteirista IA — RFlix Studio")
    st.write(
        "Crie roteiros de novelas, episódios, cenas e diálogos."
    )

    genero = st.selectbox(
        "Gênero da história:",
        [
            "Romance",
            "Drama",
            "Terror e mistério",
            "Comédia",
            "Aventura",
            "Ficção científica"
        ]
    )

    duracao = st.selectbox(
        "Duração aproximada do episódio:",
        ["1 minuto", "3 minutos", "5 minutos", "10 minutos"]
    )

    ideia = st.text_area(
        "Qual é a história?",
        height=140,
        placeholder=(
            "Ex.: Uma jovem descobre que sua família "
            "esconde um segredo há muitos anos..."
        )
    )

    personagens = st.text_area(
        "Personagens principais (opcional):",
        placeholder="Ex.: Ana, Miguel, Clara..."
    )

    if st.button("✨ CRIAR ROTEIRO", type="primary"):

        if not ideia.strip():
            st.warning("Digite a ideia da sua história.")

        else:
            try:
                with st.spinner(
                    "O Gemini está escrevendo seu episódio..."
                ):
                    roteiro = gerar_roteiro_gemini(
                        ideia,
                        genero,
                        duracao,
                        personagens
                    )

                st.session_state["ultimo_roteiro"] = roteiro

                salvar_historico(
                    HISTORICO,
                    f"ROTEIRO — {datetime.now():%d/%m/%Y %H:%M}\n"
                    f"Gênero: {genero}\n"
                    f"Ideia: {ideia}\n\n"
                    f"{roteiro}"
                )

                st.success("Roteiro criado com sucesso!")

            except Exception as erro:
                st.error(str(erro))

    roteiro_atual = st.session_state.get("ultimo_roteiro", "")

    if roteiro_atual:
        st.divider()
        st.subheader("📜 Seu roteiro")

        st.markdown(roteiro_atual)

        st.download_button(
            "⬇️ BAIXAR ROTEIRO TXT",
            data=roteiro_atual,
            file_name="roteiro_rflix.txt",
            mime="text/plain"
        )

# ==========================================
# ABA 4 — MEUS ARQUIVOS
# ==========================================

elif aba == "📂 Meus Arquivos":

    st.header("📂 Meus Arquivos")

    st.subheader("Histórico de textos e roteiros")
    texto_historico = ler_arquivo(HISTORICO)

    if texto_historico:
        st.text_area(
            "Histórico:",
            value=texto_historico,
            height=250
        )

        st.download_button(
            "⬇️ Baixar histórico",
            data=texto_historico,
            file_name="historico_rflix.txt",
            mime="text/plain"
        )
    else:
        st.info("Ainda não há textos ou roteiros salvos.")

    st.divider()

    st.subheader("Histórico de prompts de vídeo")
    historico_videos = ler_arquivo(HISTORICO_VIDEOS)

    if historico_videos:
        st.text_area(
            "Prompts de vídeo:",
            value=historico_videos,
            height=200
        )

        st.download_button(
            "⬇️ Baixar histórico de vídeos",
            data=historico_videos,
            file_name="historico_videos.txt",
            mime="text/plain"
        )
    else:
        st.info("Ainda não há prompts de vídeo salvos.")

    st.divider()

    if ARQUIVO_AUDIO.exists():
        st.subheader("Último áudio gerado")

        st.download_button(
            "⬇️ Baixar último áudio MP3",
            data=ARQUIVO_AUDIO.read_bytes(),
            file_name="ultimo_audio.mp3",
            mime="audio/mpeg"
        )

    st.divider()

    st.warning("A limpeza abaixo apaga os históricos de texto e vídeo.")

    if st.button("🗑️ LIMPAR HISTÓRICOS"):
        for arquivo in [HISTORICO, HISTORICO_VIDEOS]:
            if arquivo.exists():
                arquivo.unlink()

        st.success("Históricos apagados.")
        st.rerun()

# ==========================================
# ABA 5 — SOBRE
# ==========================================

elif aba == "ℹ️ Sobre":

    st.header("ℹ️ Sobre o RFlix Studio")

    st.markdown("""
    O **RFlix Studio** reúne ferramentas para ajudar na criação
    de histórias e conteúdos audiovisuais.

    **Recursos disponíveis nesta versão:**

    - 🎙️ Geração de narração com vozes do Edge TTS.
    - 🤖 Criação de roteiros com a API Gemini.
    - 🎬 Preparação de prompts para geração de vídeos.
    - 📂 Histórico de textos, roteiros e prompts.
    - ⬇️ Downloads de arquivos de texto e áudio.

    **Importante:** a geração de roteiros depende do acesso à API
    Gemini e dos limites da sua conta. A disponibilidade das vozes
    e dos serviços externos também pode mudar.

    O RFlix Studio não garante uso ilimitado ou gratuito de
    serviços de terceiros.
    """)

    st.caption("RFlix Studio — ferramentas para sua criatividade.")
