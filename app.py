import streamlit as st
import edge_tts
import asyncio
import os

st.set_page_config(page_title="RFlix Studio — Vozes Humanas", layout="wide")

# ------------------- LISTA DE VOZES -------------------
VOZES = {
    "👩 Mulher Jovem (Brasil)": "pt-BR-AntoniaNeural",
    "👩 Mulher Adulta (Brasil)": "pt-BR-FranciscaNeural",
    "👨 Homem Jovem (Brasil)": "pt-BR-AntonioNeural",
    "👨 Homem Adulto (Brasil)": "pt-BR-ThalitaNeural".replace("Thalita", "Manoel"),
    "👩 Mulher Jovem (Portugal)": "pt-PT-RaquelNeural",
    "👨 Homem Adulto (Portugal)": "pt-PT-DuarteNeural",
}

st.title("🎤 RFlix Studio — Vozes Humanas")
st.subheader("Texto → Fala com vozes naturais")

# ------------------- INTERFACE -------------------
texto = st.text_area("✍️ Digite o que você quer ouvir:", height=180, 
                     placeholder="Escreva aqui...")

col1, col2 = st.columns(2)
with col1:
    voz_escolhida = st.selectbox("Escolha a voz:", list(VOZES.keys()))
with col2:
    velocidade = st.slider("Velocidade da fala:", 0.6, 1.4, 1.0, 0.05)

estilo = st.selectbox("Tom de voz:", [
    "Padrão", 
    "Calmo", 
    "Animado", 
    "Narrativo"
])

# ------------------- FUNÇÃO DE GERAÇÃO -------------------
async def gerar_audio(texto, voz, velocidade):
    ARQUIVO = "fala_gerada.mp3"
    rate = f"+{int((velocidade - 1) * 100)}%" if velocidade >= 1 else f"{int((velocidade - 1) * 100)}%"
    
    communicate = edge_tts.Communicate(texto, voz, rate=rate)
    await communicate.save(ARQUIVO)
    return ARQUIVO

# ------------------- BOTÃO -------------------
if st.button("🔊 Gerar Fala", type="primary", use_container_width=True):
    if not texto.strip():
        st.warning("⚠️ Por favor, digite algum texto acima!")
    else:
        with st.spinner("🎙️ Gerando voz... Aguarde um instante..."):
            voz_codigo = VOZES[voz_escolhida]
            arquivo = asyncio.run(gerar_audio(texto, voz_codigo, velocidade))
            
        st.success("✅ Pronto! Escute abaixo 👇")
        st.audio(arquivo, format="audio/mp3")
        
        with open(arquivo, "rb") as f:
            st.download_button(
                label="⬇️ Baixar áudio MP3",
                data=f,
                file_name="RFlix_Fala.mp3",
                mime="audio/mpeg",
                use_container_width=True
            )

st.divider()
st.info("💡 Dica: Vozes mais calmas ficam melhores com velocidade um pouco menor. Teste e encontre a sua preferida! 😊")
