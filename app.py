import streamlit as st
import edge_tts
import asyncio
import os

st.set_page_config(page_title="RFlix Studio — Vozes", layout="wide")

# ==========================================
# 🎙️ TODAS AS VOZES COM NOMES FÁCEIS
# ==========================================
VOZES = {
    # 👩 Vozes Femininas
    "LARISSA — Voz jovem, suave e animada": "pt-BR-AntoniaNeural",
    "JULIA — Voz jovem, clara e gentil": "pt-BR-FranciscaNeural",
    "BEATRIZ — Voz adulta, calma e confiante": "pt-BR-FranciscaNeural",
    
    # 👨 Vozes Masculinas
    "PEDRO — Voz jovem, amigável e energético": "pt-BR-AntonioNeural",
    "GABRIEL — Voz jovem, firme e sereno": "pt-BR-AntonioNeural",
    "MARCUS — Voz adulto, grave e seguro": "pt-BR-MarceloNeural",
    "RICARDO — Voz adulto, aquecido e profissional": "pt-BR-MarceloNeural",
}

st.title("🎤 RFlix Studio — Vozes Humanas")
st.subheader("Escolha a voz que combina melhor com sua história!")

texto = st.text_area("✍️ Digite seu texto abaixo:", height=200,
                     placeholder="Era uma vez... ou digite qualquer coisa que você quer transformar em fala.")

col1, col2 = st.columns([2, 1])
with col1:
    voz_escolhida = st.selectbox("🎙️ Escolha uma voz:", list(VOZES.keys()))
with col2:
    velocidade = st.slider("Velocidade:", 0.7, 1.3, 1.0, 0.05)

ARQUIVO = "fala_gerada.mp3"

async def gerar_audio(texto, voz, rate):
    if os.path.exists(ARQUIVO):
        os.remove(ARQUIVO)
    communicate = edge_tts.Communicate(texto, voz, rate=rate)
    await communicate.save(ARQUIVO)

# Botão
if st.button("🔊 Gerar Fala", type="primary", use_container_width=True):
    if not texto.strip():
        st.warning("⚠️ Por favor, digite algum texto!")
    else:
        with st.spinner("🎙️ Gerando voz... aguarde um instante..."):
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
                loop.run_until_complete(gerar_audio(texto, voz_cod, rate))
            finally:
                loop.close()
            
            if os.path.exists(ARQUIVO) and os.path.getsize(ARQUIVO) > 500:
                st.success("✅ Pronto! Escute abaixo 👇")
                st.audio(ARQUIVO, format="audio/mp3")
                with open(ARQUIVO, "rb") as f:
                    st.download_button("⬇️ Baixar MP3", f, "RFlix_Fala.mp3", 
                                       mime="audio/mpeg", use_container_width=True)
            else:
                st.error("❌ Ops! Não consegui gerar o áudio. Tente de novo ou escolha outra voz.")

st.divider()

# 💡 Legenda pra ajudar a escolher
st.markdown("### 👋 Guia rápido das vozes:")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**👩 Vozes Femininas**")
    st.markdown("- **LARISSA** → jovem e animada")
    st.markdown("- **JULIA** → jovem e gentil")
    st.markdown("- **BEATRIZ** → adulta e calma")
with col_b:
    st.markdown("**👨 Vozes Masculinas**")
    st.markdown("- **PEDRO** → jovem e energético")
    st.markdown("- **GABRIEL** → jovem e sereno")
    st.markdown("- **MARCUS** → adulto e firme")
    st.markdown("- **RICARDO** → adulto e acolhedor")

st.info("💡 Dica: Mesmo usando a mesma voz base, tente variar a velocidade — fica com um tom bem diferente! Mais devagar = mais calmo, um pouco mais rápido = mais animado. 😊")
