
import asyncio
import io
import os
import re
import zipfile
import requests
import streamlit as st
import edge_tts

st.set_page_config(
    page_title="RFlix Studio",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #080b12;
    color: white;
}
section[data-testid="stSidebar"] {
    background: #141a27;
}
h1, h2, h3 {
    color: #e7b85c;
}
.stButton > button {
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

VOZES = {
    "Larissa — feminina natural": "pt-BR-FranciscaNeural",
    "Julia — feminina suave": "pt-BR-ThalitaMultilingualNeural",
    "Pedro — masculina": "pt-BR-AntonioNeural",
    "Narrador — masculino": "pt-BR-FabioNeural",
    "Outra voz feminina": "pt-BR-BrendaNeural",
    "Outra voz masculina": "pt-BR-DonatoNeural",
}

def gerar_edge(texto, voz, velocidade):
    async def executar():
        comunicacao = edge_tts.Communicate(
            texto,
            voz,
            rate=velocidade
        )
        audio = bytearray()
        async for parte in comunicacao.stream():
            if parte["type"] == "audio":
                audio.extend(parte["data"])
        return bytes(audio)

    return asyncio.run(executar())


def gerar_elevenlabs(texto, voice_id, api_key):
    url = (
        "https://api.elevenlabs.io/v1/text-to-speech/"
        + voice_id
    )

    resposta = requests.post(
        url,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "text": texto,
            "model_id": "eleven_multilingual_v2",
        },
        timeout=120,
    )
    resposta.raise_for_status()
    return resposta.content


def nome_arquivo(texto):
    nome = re.sub(r"[^a-zA-Z0-9_-]", "_", texto)
    return nome[:40] or "audio"


st.title("🎬 RFLIX STUDIO")
st.caption("Crie diálogos, vozes e narrações para suas novelas.")

pagina = st.sidebar.radio(
    "MENU",
    [
        "🎙️ Estúdio de Vozes",
        "📖 Roteiro da Novela",
        "ℹ️ Sobre o projeto",
    ],
)

if pagina == "🎙️ Estúdio de Vozes":
    st.header("🎙️ Gerador de vozes IA")

    mecanismo = st.radio(
        "Escolha o mecanismo de voz",
        [
            "Edge TTS — opção gratuita",
            "ElevenLabs — voz expressiva",
        ],
    )

    if mecanismo.startswith("Edge"):
        st.info(
            "Geração online de voz neural. "
            "Não precisa de chave de API."
        )
        voz_nome = st.selectbox(
            "Escolha a voz",
            list(VOZES.keys()),
        )
        voz = VOZES[voz_nome]

        velocidade = st.select_slider(
            "Velocidade da fala",
            options=[
                "-15%", "-10%", "-5%", "+0%",
                "+5%", "+10%", "+15%"
            ],
            value="+0%",
        )
        api_key = ""
        voice_id = ""

    else:
        st.info(
            "Insira sua chave da ElevenLabs nos Secrets "
            "do Streamlit ou no campo abaixo."
        )

        api_key = st.text_input(
            "Chave da API",
            type="password",
            value=st.secrets.get("ELEVENLABS_API_KEY", ""),
        )

        voice_id = st.text_input(
            "ID da voz da ElevenLabs",
            placeholder="Cole aqui o ID da voz escolhida",
        )

        voz = ""
        velocidade = "+0%"

    st.write("---")
    st.subheader("Texto do personagem")

    personagem = st.text_input(
        "Nome do personagem",
        value="Larissa",
    )

    texto = st.text_area(
        "Escreva o diálogo ou a narração",
        height=220,
        max_chars=5000,
        placeholder=(
            "Pedro, eu preciso contar uma coisa...\n"
            "Eu nunca deixei de te amar."
        ),
    )

    if st.button(
        "🔊 GERAR VOZ",
        type="primary",
        use_container_width=True,
    ):
        if not texto.strip():
            st.warning("Escreva um texto antes de gerar.")
        elif mecanismo.startswith("ElevenLabs") and (
            not api_key or not voice_id
        ):
            st.warning(
                "Informe a chave da API e o ID da voz."
            )
        else:
            try:
                with st.spinner(
                    "Gerando áudio... aguarde."
                ):
                    if mecanismo.startswith("Edge"):
                        audio = gerar_edge(
                            texto.strip(),
                            voz,
                            velocidade,
                        )
                    else:
                        audio = gerar_elevenlabs(
                            texto.strip(),
                            voice_id.strip(),
                            api_key.strip(),
                        )

                if not audio:
                    st.error(
                        "O serviço não retornou áudio. "
                        "Tente novamente."
                    )
                else:
                    st.session_state.audio_gerado = audio
                    st.session_state.audio_nome = (
                        nome_arquivo(personagem)
                    )
                    st.success("Áudio gerado!")

            except Exception as erro:
                st.error(
                    "Não foi possível gerar a voz. "
                    "Confira sua conexão, a voz escolhida "
                    "e os limites do serviço."
                )
                st.code(str(erro))

    if st.session_state.get("audio_gerado"):
        audio = st.session_state.audio_gerado
        nome = st.session_state.get(
            "audio_nome", "personagem"
        )

        st.subheader("🎧 Prévia do áudio")
        st.audio(audio, format="audio/mpeg")

        st.download_button(
            "⬇️ BAIXAR ÁUDIO MP3",
            data=audio,
            file_name=f"{nome}.mp3",
            mime="audio/mpeg",
            use_container_width=True,
        )

elif pagina == "📖 Roteiro da Novela":
    st.header("📖 Organizador de diálogos")

    st.write(
        "Escreva uma fala por linha, usando o formato "
        "**Personagem: diálogo**."
    )

    roteiro = st.text_area(
        "Roteiro",
        height=300,
        placeholder=(
            "Larissa: Por que você voltou?\n"
            "Pedro: Voltei porque ainda te amo.\n"
            "Larissa: Você chegou tarde demais."
        ),
    )

    if st.button("📋 ORGANIZAR ROTEIRO"):
        falas = []

        for linha in roteiro.splitlines():
            if ":" not in linha:
                continue

            personagem, fala = linha.split(":", 1)

            if personagem.strip() and fala.strip():
                falas.append({
                    "personagem": personagem.strip(),
                    "fala": fala.strip(),
                })

        if falas:
            st.session_state.falas = falas
            st.success(
                f"{len(falas)} falas identificadas."
            )
            for i, fala in enumerate(falas, 1):
                st.markdown(
                    f"**{i}. {fala['personagem']}**: "
                    f"{fala['fala']}"
                )
        else:
            st.warning(
                "Nenhuma fala identificada. "
                "Use Personagem: diálogo."
            )

    if st.session_state.get("falas"):
        conteudo = "\n".join(
            f"{f['personagem']}: {f['fala']}"
            for f in st.session_state.falas
        )

        st.download_button(
            "⬇️ BAIXAR ROTEIRO TXT",
            data=conteudo,
            file_name="roteiro_rflix.txt",
            mime="text/plain",
        )

elif pagina == "ℹ️ Sobre o projeto":
    st.header("Sobre a RFlix Studio")

    st.write("""
    A RFlix Studio é um projeto para produzir novelas,
    histórias e vídeos com ferramentas de inteligência
    artificial.

    Recursos desta versão:
    - Geração de voz neural.
    - Opção de integração com ElevenLabs.
    - Organização de roteiros e diálogos.
    - Download de áudios em MP3.

    A criação de cenas em vídeo e a montagem automática
    de episódios serão etapas posteriores.
    """)

st.write("---")
st.caption("RFlix Studio • Criação de histórias com IA")
    
