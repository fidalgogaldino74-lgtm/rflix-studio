import streamlit as st
import edge_tts
import asyncio
import os

st.set_page_config(page_title="RFlix Studio — Vozes Humanas", layout="wide")

# ✅ LISTA DE VOZES — SÓ as que funcionam confirmadas
VOZES = {
    "👩 Mulher Jovem": "pt-BR-AntoniaNeural",
    "👩 Mulher Adulta": "pt-BR-FranciscaNeural",
    "👨 Homem Jovem": "pt-BR-AntonioNeural",
    "👨 Homem Adulto": "pt-BR-MarceloNeural",
}

st.title("🎤 RFlix Studio — Vozes Humanas")
st.subheader("Texto → Fala com vozes naturais")

texto = st.text_area("✍️ Digite o que você quer ouvir:", height=180,
                     placeholder="Escreva aqui...")

col1, col2 = st.columns(2)
with col1:
    voz_escolhida = st.selectbox("Escolha a voz:", list(VOZES.keys()))
with col2:
    velocidade = st.slider("Velocidade da fala:", 0.6, 1.4, 1.0, 0.05)

ARQUIVO = "fala_gerada.mp3"

async def gerar(texto, voz, rate):
    if os.path.exists(ARQUIVO):
        os.remove(ARQUIVO)
    communicate = edge_tts.Communicate(texto, voz, rate=rate)
    await communicate.save(ARQUIVO)

if st.button("🔊 Gerar Fala", type="primary", use_container_width=True):
    if not texto.strip():
        st.warning("⚠️ Digite algum texto!")
    else:
        with st.spinner("🎙️ Gerando áudio..."):
            voz_cod = VOZES[voz_escolhida]
            
            # Ajusta velocidade
            if velocidade == 1.0:
                rate = "+0%"
            elif velocidade > 1.0:
                rate = f"+{int((velocidade - 1)*100)}%"
            else:
                rate = f"-{int((1 - velocidade)*100)}%"
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(gerar(texto, voz_cod, rate))
            finally:
                loop.close()
            
            if os.path.exists(ARQUIVO) and os.path.getsize(ARQUIVO) > 100:
                st.success("✅ Pronto!")
                st.audio(ARQUIVO, format="audio/mp3")
                with open(ARQUIVO, "rb") as f:
                    st.download_button("⬇️ Baixar MP3", f, "RFlix_Fala.mp3", use_container_width=True)
            else:
                st.error("❌ Erro ao gerar. Tente outra voz ou aguarde um instante.")

st.divider()
st.info("💡 Dica: Se uma voz não funcionar, troque por outra e tente de novo!")
            
