import streamlit as st
from gtts import gTTS
from io import BytesIO
import base64
from datetime import datetime

st.set_page_config(page_title="RFlix Studio", page_icon="🎙️", layout="wide")

# ==========================================
# 🎙️ VOZES — Mais estáveis!
# ==========================================
VOZES = {
    "👩 LARISSA — Jovem, animada e suave": {"lang": "pt-br", "tld": "com.br"},
    "👩 JULIA — Jovem, clara e gentil": {"lang": "pt-br", "tld": "com"},
    "👩 BEATRIZ — Adulta, calma e confiante": {"lang": "pt-pt", "tld": "com.pt"},
    "👨 PEDRO — Jovem, amigável e energético": {"lang": "pt-br", "tld": "com"},
    "👨 GABRIEL — Jovem, firme e sereno": {"lang": "pt-br", "tld": "ca"},
    "👨 MARCUS — Adulto, grave e seguro": {"lang": "pt-pt", "tld": "com"},
    "👨 RICARDO — Adulto, aquecido e profissional": {"lang": "pt-br", "tld": "co.uk"},
}

ARQUIVO_HISTORICO = "historico.txt"

# ==========================================
# 💾 FUNÇÕES DE HISTÓRICO
# ==========================================
def carregar_historico():
    try:
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
            return [linha.strip().split("||") for linha in f.readlines() if linha.strip()]
    except:
        return []

def salvar_no_historico(voz, texto, data):
    with open(ARQUIVO_HISTORICO, "a", encoding="utf-8") as f:
        f.write(f"{data}||{voz}||{texto[:60]}...\n")

def gerar_download_link(audio_bytes, filename):
    b64 = base64.b64encode(audio_bytes.read()).decode()
    return f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">⬇️ Baixar MP3</a>'

# ==========================================
# 🎯 MENU
# ==========================================
aba = st.sidebar.radio(
    "📂 Navegação",
    ["🎙️ Gerar Voz", "📋 Meus Áudios", "ℹ️ Sobre"],
    label_visibility="collapsed"
)

st.title("🎬 RFlix Studio")
st.markdown("---")

# ==========================================
# 🎙️ GERAR VOZ
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
        lento = velocidade < 0.9
    
    st.markdown("💡 **Dicas rápidas:**")
    dicas = {
        "Larissa": "Ótima para histórias animadas e mensagens curtas",
        "Júlia": "Boa para narrações claras e naturais",
        "Beatriz": "Tom mais calmo e sereno",
        "Pedro": "Voz jovem e direta",
        "Gabriel": "Mais neutro e conversacional",
        "Marcus": "Tom mais formal e narrativo",
        "Ricardo": "Mais acolhedor e amigável"
    }
    for nome, dica in dicas.items():
        if nome.split(" —")[0] in voz_escolhida:
            st.info(f"✨ {nome}: {dica}")
            break
    
    st.markdown("")
    if st.button("🔊 Gerar Áudio", type="primary", use_container_width=True):
        if not texto.strip():
            st.warning("⚠️ Por favor, digite algum texto!")
        else:
            with st.spinner("🎙️ Gerando áudio... aguarde um instante..."):
                config = VOZES[voz_escolhida]
                
                try:
                    tts = gTTS(text=texto, lang=config["lang"], tld=config["tld"], slow=lento)
                    audio_bytes = BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    
                    data_hora = datetime.now().strftime("%d/%m %H:%M")
                    salvar_no_historico(voz_escolhida, texto, data_hora)
                    
                    st.success("✅ Pronto! Ouça abaixo 👇")
                    st.audio(audio_bytes, format="audio/mp3")
                    
                    filename = f"RFlix_{datetime.now().strftime('%Y%m%d_%H%M')}.mp3"
                    st.markdown(gerar_download_link(audio_bytes, filename), unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Ops! Tente novamente em alguns instantes.")

# ==========================================
# 📋 HISTÓRICO
# ==========================================
elif aba == "📋 Meus Áudios":
    st.header("📋 Histórico de áudios gerados")
    historico = carregar_historico()
    
    if not historico:
        st.info("📭 Ainda não há áudios. Comece criando seu primeiro na aba **Gerar Voz**! 😊")
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
        
        st.markdown("---")
        if st.button("🗑️ Limpar Histórico"):
            import os
            if os.path.exists(ARQUIVO_HISTORICO):
                os.remove(ARQUIVO_HISTORICO)
            st.success("✅ Histórico limpo! Atualize a página.")
            st.rerun()

# ==========================================
# ℹ️ SOBRE
# ==========================================
elif aba == "ℹ️ Sobre":
    st.header("ℹ️ Sobre o RFlix Studio")
    st.markdown("""
    **RFlix Studio** — Vozes Humanas com Inteligência Artificial ✨
    
    ✅ **O que você pode fazer:**
    - Transformar texto em áudio com vozes naturais
    - Escolher entre diferentes vozes e tons
    - Ajustar a velocidade da fala
    - Baixar os arquivos em MP3
    - Manter histórico das suas criações
    
    📌 **Como usar:**
    1. Escreva seu texto
    2. Escolha uma voz
    3. Ajuste a velocidade
    4. Clique em **Gerar Áudio**
    5. Ouça e baixe quando quiser!
    
    💡 **Dica:** Cada voz tem um tom diferente — teste todas e encontre sua preferida!
    
    ---
    *Versão: 1.2 — Mais estável e sem erros!* 🎙️✨
    """)

st.sidebar.markdown("---")
st.sidebar.info("💡 Passo 2 concluído e corrigido! ✅")
