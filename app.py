import streamlit as st
import edge_tts
import asyncio
import os
from datetime import datetime

st.set_page_config(page_title="RFlix Studio", page_icon="🎬", layout="wide")

# ==========================================
# 🎙️ VOZES
# ==========================================
VOZES = {
    "👩 LARISSA — Jovem, animada e suave": "pt-BR-AntoniaNeural",
    "👩 JULIA — Jovem, clara e gentil": "pt-BR-FranciscaNeural",
    "👨 PEDRO — Jovem, amigável e energético": "pt-BR-AntonioNeural",
}

ARQUIVO_ATUAL = "ultimo_audio.mp3"
HISTORICO_ARQUIVO = "historico.txt"
HISTORICO_VIDEOS = "historico_videos.txt"

# ==========================================
# 💾 FUNÇÕES DE HISTÓRICO
# ==========================================
def carregar_historico(tipo="audio"):
    arquivo = HISTORICO_ARQUIVO if tipo == "audio" else HISTORICO_VIDEOS
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return [linha.strip().split("||") for linha in f.readlines() if linha.strip()]
    return []

def salvar_no_historico(voz, texto, data, tipo="audio"):
    arquivo = HISTORICO_ARQUIVO if tipo == "audio" else HISTORICO_VIDEOS
    with open(arquivo, "a", encoding="utf-8") as f:
        f.write(f"{data}||{voz}||{texto[:80]}...\n")

# ==========================================
# 🎯 MENU PRINCIPAL
# ==========================================
aba = st.sidebar.radio(
    "📂 Navegação",
    ["🎙️ Gerar Voz", "🎬 Gerar Vídeo", "📂 Meus Arquivos", "ℹ️ Sobre"],
    label_visibility="collapsed"
)

st.title("🎬 RFlix Studio")
st.markdown("---")

# ==========================================
# 🎙️ ABA 1 — GERAR VOZ
# ==========================================
if aba == "🎙️ Gerar Voz":
    st.header("🎙️ Criar nova fala")
    texto = st.text_area("✍️ Seu texto:", height=180, placeholder="Digite aqui...")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        voz_escolhida = st.selectbox("Escolha a voz:", list(VOZES.keys()))
    with col2:
        velocidade = st.slider("Velocidade:", 0.7, 1.3, 1.0, 0.05)
        
    st.info("✨ Larissa: histórias animadas | ✨ Júlia: narrações calmas | ✨ Pedro: conversas naturais")
    
    if st.button("🔊 Gerar Áudio", type="primary", use_container_width=True):
        if not texto.strip():
            st.warning("⚠️ Digite algum texto!")
        else:
            with st.spinner("🎙️ Gerando áudio..."):
                voz_cod = VOZES[voz_escolhida]
                rate = "+0%" if velocidade == 1.0 else (f"+{int((velocidade-1)*100)}%" if velocidade > 1.0 else f"-{int((1-velocidade)*100)}%")
                
                async def gerar():
                    if os.path.exists(ARQUIVO_ATUAL):
                        os.remove(ARQUIVO_ATUAL)
                    await edge_tts.Communicate(texto, voz_cod, rate=rate).save(ARQUIVO_ATUAL)
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(gerar())
                finally:
                    loop.close()
                
                if os.path.exists(ARQUIVO_ATUAL) and os.path.getsize(ARQUIVO_ATUAL) > 500:
                    data_hora = datetime.now().strftime("%d/%m %H:%M")
                    salvar_no_historico(voz_escolhida, texto, data_hora)
                    st.success("✅ Pronto!")
                    st.audio(ARQUIVO_ATUAL, format="audio/mp3")
                    with open(ARQUIVO_ATUAL, "rb") as f:
                        st.download_button("⬇️ Baixar MP3", f, f"RFlix_{datetime.now().strftime('%Y%m%d_%H%M')}.mp3", use_container_width=True)
                else:
                    st.error("❌ Erro. Tente novamente.")

# ==========================================
# 🎬 ABA 2 — GERAR VÍDEO — MODELO WAN 3.0
# ==========================================
elif aba == "🎬 Gerar Vídeo":
    st.header("🎬 Criar vídeo com IA")
    replicate_token = st.text_input("🔑 Token do Replicate", type="password", placeholder="Cole seu token aqui: r8_...", help="Crie gratuitamente em: replicate.com/account/tokens")
    
    prompt = st.text_area("✍️ Descreva o vídeo que você quer:", height=150, placeholder="Ex: Um cachorro golden retriever correndo na praia ao pôr do sol, filmagem em 4k, cinematográfico...")
    
    col1, col2 = st.columns(2)
    with col1:
        estilo = st.selectbox("🎨 Estilo visual:", [
            "Realista / Cinematográfico",
            "Animação / Desenho",
            "Sonhador / Arte Digital",
            "Vintage / Retrô",
            "Futurista / Sci-Fi"
        ])
    with col2:
        proporcao = st.selectbox("📐 Formato/Proporção:", ["16:9 (Horizontal/YouTube)", "9:16 (Vertical/TikTok)", "1:1 (Quadrado)"])
        
    st.markdown("💡 **Dica de prompt:** Seja detalhado! Descreva os movimentos, a iluminação e o clima. Quanto mais detalhes, melhor o resultado!")
    
    if st.button("🎬 Gerar Vídeo", type="primary", use_container_width=True):
        if not replicate_token.startswith("r8_"):
            st.warning("⚠️ Cole seu token do Replicate primeiro! Crie gratuitamente em replicate.com")
        elif not prompt.strip():
            st.warning("⚠️ Descreva seu vídeo acima!")
        else:
            with st.spinner("🎬 Sua IA está no estúdio criando o vídeo... Pode levar de 1 a 3 minutos..."):
                try:
                    import replicate
                    os.environ["REPLICATE_API_TOKEN"] = replicate_token
                    
                    prompt_completo = f"{prompt}, style: {estilo}"
                    
                    aspect_map = {
                        "16:9 (Horizontal/YouTube)": "16:9",
                        "9:16 (Vertical/TikTok)": "9:16",
                        "1:1 (Quadrado)": "1:1"
                    }
                    
                    output = replicate.run(
                        "alibaba/wan-3",
                        input={
                            "prompt": prompt_completo,
                            "aspect_ratio": aspect_map[proporcao]
                        }
                    )
                    
                    video_url = output[0] if isinstance(output, list) else output
                    
                    data_hora = datetime.now().strftime("%d/%m %H:%M")
                    salvar_no_historico(estilo, prompt, data_hora, tipo="video")
                    
                    st.success("✅ Vídeo pronto! 🎉")
                    st.video(video_url)
                    st.markdown(f"🔗 **Link do vídeo:** [{video_url}]({video_url})")
                    st.caption("💡 Clique nos três pontinhos no canto do vídeo ou use o link para salvar no seu dispositivo.")
                except Exception as e:
                    st.error(f"❌ Erro: Verifique seu token ou tente novamente mais tarde.")
                    st.info(f"Detalhe do erro: {str(e)[:150]}")

# ==========================================
# 📂 ABA 3 — MEUS ARQUIVOS
# ==========================================
elif aba == "📂 Meus Arquivos":
    st.header("📂 Histórico de Criações")
    tab1, tab2 = st.tabs(["🎙️ Áudios", "🎬 Vídeos"])
    
    with tab1:
        audios = carregar_historico("audio")
        if not audios:
            st.info("📭 Nenhum áudio ainda.")
        else:
            st.write(f"📊 Total: **{len(audios)}** áudios")
            for i, item in enumerate(reversed(audios), 1):
                if len(item) == 3:
                    data, voz, resumo = item
                    with st.expander(f"#{i} — {voz.split(' —')[0]} | {data}"):
                        st.write(f"🎙️ **Voz:** {voz}")
                        st.write(f"📝 **Texto:** {resumo}")
                        
    with tab2:
        videos = carregar_historico("video")
        if not videos:
            st.info("📭 Nenhum vídeo ainda. Comece na aba **🎬 Gerar Vídeo**! 😊")
        else:
            st.write(f"📊 Total: **{len(videos)}** vídeos")
            for i, item in enumerate(reversed(videos), 1):
                if len(item) == 3:
                    data, estilo, resumo = item
                    with st.expander(f"#{i} — {estilo} | {data}"):
                        st.write(f"🎨 **Estilo:** {estilo}")
                        st.write(f"📝 **Prompt:** {resumo}")
    
    st.markdown("---")
    if st.button("🗑️ Limpar Todo o Histórico"):
        for arq in [HISTORICO_ARQUIVO, HISTORICO_VIDEOS, ARQUIVO_ATUAL]:
            if os.path.exists(arq):
                os.remove(arq)
        st.success("✅ Histórico limpo!")
        st.rerun()

# ==========================================
# ℹ️ ABA 4 — SOBRE
# ==========================================
elif aba == "ℹ️ Sobre":
    st.header("ℹ️ Sobre o RFlix Studio")
    st.markdown("""
    O **RFlix Studio** é uma plataforma completa de criação de conteúdo com Inteligência Artificial.
    
    ✅ **🎙️ Gerar Voz:** Converta texto em áudio com vozes naturais.
    ✅ **🎬 Gerar Vídeo:** Descreva cenas e a IA cria vídeos com o modelo **Wan 3.0**.
    ✅ **📂 Histórico:** Acesse e gerencie todas suas criações.
    
    📌 **Como usar os vídeos:**
    1. Crie sua conta gratuita em **replicate.com**
    2. Copie seu token em: replicate.com/account/tokens
    3. Cole o token na aba "Gerar Vídeo"
    4. Escreva sua descrição e clique em "Gerar Vídeo"
    5. Aguarde de 1 a 3 minutos — vale a pena! ✨
    
    💡 **Dica:** Sempre baixe seus arquivos logo após gerar. O histórico é uma referência, mas os arquivos ficam salvos com você!
    
    ---
    *Versão 1.3 — Wan 3.0 Integrado* 🚀🎬
    """)

st.sidebar.markdown("---")
st.sidebar.success("✅ Passo 3 concluído! RFlix Studio completo! 🎉")
    
