import streamlit as st
import edge_tts
import asyncio
import os
from datetime import datetime

st.set_page_config(page_title="RFlix Studio", page_icon="🎙️", layout="wide")

# ==========================================
# 🎙️ BANCO DE VOZES
# ==========================================
VOZES = {
    "👩 LARISSA — Jovem, animada e suave": "pt-BR-AntoniaNeural",
    "👩 JULIA — Jovem, clara e gentil": "pt-BR-FranciscaNeural",
    "👩 BEATRIZ — Adulta, calma e confiante": "pt-BR-FranciscaNeural",
    "👨 PEDRO — Jovem, amigável e energético": "pt-BR-AntonioNeural",
    "👨 GABRIEL — Jovem, firme e sereno": "pt-BR-AntonioNeural",
    "👨 MARCUS — Adulto, grave e seguro": "pt-BR-MarceloNeural",
    "👨 RICARDO — Adulto, aquecido e profissional": "pt-BR-MarceloNeural",
}

ARQUIVO_ATUAL = "ultimo_audio.mp3"
HISTORICO_ARQUIVO = "historico.txt"

# ==========================================
# 💾 FUNÇÕES DE HISTÓRICO
# ==========================================
def carregar_historico():
    if os.path.exists(HISTORICO_ARQUIVO):
        with open(HISTORICO_ARQUIVO, "r", encoding="utf-8") as f:
            return [linha.strip().split("||") for linha in f.readlines() if linha.strip()]
    return []

def salvar_no_historico(voz, texto, data):
    with open(HISTORICO_ARQUIVO, "a", encoding="utf-8") as f:
        f.write(f"{data}||{voz}||{texto[:60]}...\n")

# ==========================================
# 🎯 MENU DE NAVEGAÇÃO
# ==========================================
aba = st.sidebar.radio(
    "📂 Navegação",
    ["🎙️ Gerar Voz", "📋 Meus Áudios", "ℹ️ Sobre"],
    label_visibility="collapsed"
)

st.title("🎬 RFlix Studio")
st.markdown("---")

# ==========================================
# 🎙️ ABA 1 — GERAR VOZ
# ==========================================
if aba == "🎙️ Gerar Voz":
    st.header("🎙️ Criar nova fala")
    
    texto = st.text_area("✍️ Seu texto:", height=180,
                         placeholder="Digite aqui o que você quer transformar em áudio...")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        voz_escolhida = st.selectbox("Escolha a voz:", list(VOZES.keys()))
    with col2:
        velocidade = st.slider("Velocidade:", 0.7, 1.3, 1.0, 0.05)
    
    st.markdown("💡 **Dicas rápidas:**")
    dicas = {
        "Larissa": "Ótima para histórias animadas e mensagens curtas",
        "Júlia / Beatriz": "Perfeitas para narrações e explicações calmas",
        "Pedro / Gabriel": "Boa para diálogos e conversas naturais",
        "Marcus / Ricardo": "Ideais para narração profissional e tom sério"
    }
    for nome, dica in dicas.items():
        if nome.split(" —")[0] in voz_escolhida:
            st.info(f"✨ {nome}: {dica}")
            break
    
    st.markdown("")
    gerar = st.button("🔊 Gerar Áudio", type="primary", use_container_width=True)
    
    if gerar:
        if not texto.strip():
            st.warning("⚠️ Por favor, digite algum texto!")
        else:
            with st.spinner("🎙️ Criando áudio... aguarde um instante..."):
                voz_cod = VOZES[voz_escolhida]
                
                # Ajusta velocidade
                if velocidade == 1.0:
                    rate = "+0%"
                elif velocidade > 1.0:
                    rate = f"+{int((velocidade - 1)*100)}%"
                else:
                    rate = f"-{int((1 - velocidade)*100)}%"
                
                # Função assíncrona
                async def salvar(texto, voz, rate):
                    if os.path.exists(ARQUIVO_ATUAL):
                        os.remove(ARQUIVO_ATUAL)
                    comm = edge_tts.Communicate(texto, voz, rate=rate)
                    await comm.save(ARQUIVO_ATUAL)
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(salvar(texto, voz_cod, rate))
                finally:
                    loop.close()
                
                if os.path.exists(ARQUIVO_ATUAL) and os.path.getsize(ARQUIVO_ATUAL) > 500:
                    data_hora = datetime.now().strftime("%d/%m %H:%M")
                    salvar_no_historico(voz_escolhida, texto, data_hora)
                    
                    st.success("✅ Pronto! Ouça abaixo 👇")
                    st.audio(ARQUIVO_ATUAL, format="audio/mp3")
                    
                    with open(ARQUIVO_ATUAL, "rb") as f:
                        st.download_button(
                            "⬇️ Baixar MP3",
                            f,
                            file_name=f"RFlix_{datetime.now().strftime('%Y%m%d_%H%M')}.mp3",
                            mime="audio/mpeg",
                            use_container_width=True
                        )
                else:
                    st.error("❌ Ops! Não consegui gerar. Tente novamente em alguns instantes.")

# ==========================================
# 📋 ABA 2 — HISTÓRICO
# ==========================================
elif aba == "📋 Meus Áudios":
    st.header("📋 Histórico de áudios gerados")
    historico = carregar_historico()
    
    if not historico:
        st.info("📭 Ainda não há áudios gerados. Comece criando seu primeiro áudio na aba **Gerar Voz**! 😊")
    else:
        st.write(f"📊 Total: **{len(historico)}** áudios gerados")
        st.markdown("---")
        
        for i, item in enumerate(reversed(historico), 1):
            if len(item) == 3:
                data, voz, resumo = item
                with st.expander(f"#{i} — {voz.split(' —')[0]} | {data}"):
                    st.write(f"🎙️ **Voz:** {voz}")
                    st.write(f"⏰ **Criado em:** {data}")
                    st.write(f"📝 **Texto:** {resumo}")
                    if os.path.exists(ARQUIVO_ATUAL) and i == 1:
                        st.audio(ARQUIVO_ATUAL, format="audio/mp3")
        
        st.markdown("---")
        if st.button("🗑️ Limpar Histórico"):
            if os.path.exists(HISTORICO_ARQUIVO):
                os.remove(HISTORICO_ARQUIVO)
            if os.path.exists(ARQUIVO_ATUAL):
                os.remove(ARQUIVO_ATUAL)
            st.success("✅ Histórico limpo! Atualize a página.")
            st.rerun()

# ==========================================
# ℹ️ ABA 3 — SOBRE
# ==========================================
elif aba == "ℹ️ Sobre":
    st.header("ℹ️ Sobre o RFlix Studio")
    st.markdown("""
    **RFlix Studio** é uma plataforma de criação de vozes com Inteligência Artificial.
    
    ✅ **O que você pode fazer:**
    - Transformar texto em áudio com vozes naturais
    - Escolher entre diferentes vozes e tons
    - Ajustar a velocidade da fala
    - Baixar os arquivos em MP3
    - Manter um histórico das suas criações
    
    📌 **Como usar:**
    1. Escreva seu texto
    2. Escolha uma voz
    3. Ajuste a velocidade
    4. Clique em **Gerar Áudio**
    5. Ouça e baixe quando quiser!
    
    💡 **Dica:** Teste diferentes combinações de voz e velocidade — cada uma cria uma sensação diferente!
    
    ---
    *Versão atual: 1.1 — Vozes Humanas + Histórico* 🎙️✨
    """)

# Rodapé
st.sidebar.markdown("---")
st.sidebar.info("💡 **Passo 2 concluído!** Histórico e interface melhorada ✅")
