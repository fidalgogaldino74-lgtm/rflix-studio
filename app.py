
import streamlit as st
from gtts import gTTS
import os

st.set_page_config(page_title="RFlix Studio", layout="wide")
st.title("🎬 RFlix Studio")
st.subheader("Plataforma de IA — Vozes + Vídeos")

menu = st.sidebar.selectbox(
    "Escolha uma função",
    ["🎤 Gerar Fala", "🎬 Gerar Vídeo por Prompt", "📂 Arquivos"]
)

# ------------------- GERAR FALA -------------------
if menu == "🎤 Gerar Fala":
    st.header("Texto → Fala")
    texto = st.text_area("Digite seu texto:", height=150)
    idioma = st.selectbox("Idioma:", ["Português", "Inglês", "Espanhol"])
    
    if st.button("🔊 Gerar Fala") and texto:
        lang = {"Português":"pt", "Inglês":"en", "Espanhol":"es"}[idioma]
        tts = gTTS(text=texto, lang=lang, slow=False)
        tts.save("fala.mp3")
        st.audio("fala.mp3")
        st.success("Fala pronta ✅")
        with open("fala.mp3", "rb") as f:
            st.download_button("⬇️ Baixar MP3", f, "fala.mp3")

# ------------------- GERAR VÍDEO -------------------
if menu == "🎬 Gerar Vídeo por Prompt":
    st.header("Descreva seu vídeo")
    prompt = st.text_area("O que você quer ver?", height=180)
    estilo = st.selectbox("Estilo:", ["Realista", "Animação", "Cinematográfico"])
    duracao = st.selectbox("Duração:", ["5s", "10s"])
    
    if st.button("🎬 Preparar Vídeo") and prompt:
        st.info(f"📝 Seu prompt: {prompt}")
        st.info(f"🎨 Estilo: {estilo} | ⏱️ Duração: {duracao}")
        st.warning("🔌 Para gerar vídeos reais, conecte uma API como Replicate ou Hugging Face. A estrutura está pronta!")
        st.success("✅ Prompt salvo! Depois é só conectar a API e funcionará!")

# ------------------- ARQUIVOS -------------------
if menu == "📂 Arquivos":
    st.header("Arquivos Gerados")
    if os.path.exists("fala.mp3"):
        st.audio("fala.mp3")
    else:
        st.info("Nenhum arquivo ainda. Comece gerando uma fala!")

st.sidebar.markdown("---")
st.sidebar.info("💡 Comece pela fala — já funciona! Vídeo: API em breve.")
