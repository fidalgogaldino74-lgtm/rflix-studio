import streamlit as st
import edge_tts
import asyncio
import os
from datetime import datetime
import urllib.parse

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
# 🎙️ ABA 1 — GERAR VOZ (continua igual!)
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
# 🎬 ABA 2 — GERAR VÍDEO — SEM TOKEN!
# ==========================================
elif aba == "🎬 Gerar Vídeo":
    st.header("🎬 Criar vídeo com IA — Sem crédito que acaba! 🎉")
    
    prompt = st.text_area("✍️ Descreva o vídeo que você quer:", height=150, placeholder="Ex: Uma mulher entra em uma sala com expressão de surpresa, estilo de novela, iluminação natural...")
    
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
        proporcao = st.selectbox("📐 Formato/Proporção:", ["16:9 (Horizontal/YouTube)", "9:16 (Vertical/TikTok/Reels)", "1:1 (Quadrado)"])
    
    st.markdown("💡 **Dica de prompt:** Seja detalhado! Descreva os personagens, a ação, a iluminação e o clima. Quanto mais detalhes, melhor o resultado!")
    
    st.markdown("---")
    
    opcao = st.radio(
        "🌐 Escolha onde gerar seu vídeo:",
        ["🌐 Wan2.video — Sem cadastro, direto!", "☁️ Hugging Face Space — Crie seu próprio gerador grátis"],
        label_visibility="collapsed"
    )
    
    prompt_completo = f"{prompt}, estilo: {estilo}" if prompt else ""
    proporcao_map = {
        "16:9 (Horizontal/YouTube)": "16:9",
        "9:16 (Vertical/TikTok/Reels)": "9:16",
        "1:1 (Quadrado)": "1:1"
    }
    prop = proporcao_map[proporcao]
    
    if opcao == "🌐 Wan2.video — Sem cadastro, direto!":
        st.info("💡 O Wan2.video é gratuito, não precisa de conta nem token! Basta copiar sua descrição, gerar e voltar aqui para salvar no histórico.")
        
        wan_link = f"https://wan2.video/?q={urllib.parse.quote(prompt_completo)}&ar={prop}" if prompt_completo else "https://wan2.video"
        
        if st.button("🚀 Abrir Wan2.video e Gerar", type="primary", use_container_width=True, disabled=not prompt.strip()):
            data_hora = datetime.now().strftime("%d/%m %H:%M")
            salvar_no_historico(estilo, prompt, data_hora, tipo="video")
            st.success("✅ Salvo no histórico! Clique no link abaixo 👇")
            st.markdown(f"### 👉 [Clique aqui para gerar seu vídeo]({wan_link})")
            st.caption("Copie sua descrição acima, cole no site e gere! Depois é só baixar e usar 😊")
    
    else:
        st.info("💡 Com o Hugging Face você cria seu próprio espaço de geração de vídeos — grátis, sem crédito que acaba!")
        
        hf_prompt = urllib.parse.quote(prompt_completo)
        st.markdown(f"""
        ### 📌 Passo a passo:
        1. Crie uma conta grátis em **huggingface.co**
        2. Vá em **Spaces → New Space → procure "Wan2.2"**
        3. Use o modelo público — não precisa instalar nada!
        4. Cole sua descrição e gere seus vídeos lá mesmo
        
        ✅ **Nunca acaba crédito!** Pode gerar quantas vezes quiser — só pode ter fila em horários de pico.
        """)
        
        if st.button("📝 Salvar no Histórico", type="primary", use_container_width=True, disabled=not prompt.strip()):
            data_hora = datetime.now().strftime("%d/%m %H:%M")
            salvar_no_historico(estilo, prompt, data_hora, tipo="video")
            st.success("✅ Salvo no histórico! Vá ao Hugging Face para gerar 😊")

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
    
    ✅ **🎙️ Gerar Voz:** Converta texto em áudio com vozes naturais — totalmente grátis e ilimitado!
    ✅ **🎬 Gerar Vídeo:** Descreva cenas e gere vídeos — sem token, sem crédito que acaba!
    ✅ **📂 Histórico:** Acesse e gerencie todas suas criações.
    
    🎯 **Como gerar vídeos — Sem token!**
    1. Escreva sua descrição aqui no RFlix Studio
    2. Escolha: **Wan2.video** (rápido, sem cadastro) OU **Hugging Face** (seu próprio espaço)
    3. Clique para abrir o site externo — sua descrição já vai pronta lá!
    4. Gere, baixe e volte aqui para salvar no histórico
    
    💡 **Por que assim?** Gerar vídeo com IA precisa de servidores potentes. Em vez de depender de tokens que acabam, usamos plataformas gratuitas que não têm limite de crédito — você só clica, gera e volta! 😊
    
    ---
    *Versão 2.0 — Sem Token! Sem Crédito que acaba!* 🚀🎬
    """)

st.sidebar.markdown("---")
st.sidebar.success("✅ RFlix Studio atualizado! Sem token! 🎉")
            
