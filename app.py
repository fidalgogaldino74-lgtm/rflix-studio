import streamlit as st
import edge_tts
import asyncio
import os
from datetime import datetime

st.set_page_config(page_title="RFlix Studio", page_icon="🎙️", layout="wide")

# ==========================================
# 🎙️ Vozes que funcionam confirmadas
# ==========================================
VOZES = {
    "👩 LARISSA — Jovem, animada e suave": "pt-BR-AntoniaNeural",
    "👩 JULIA — Jovem, clara e gentil": "pt-BR-FranciscaNeural",
    "👨 PEDRO — Jovem, amigável e energético": "pt-BR-AntonioNeural",
}

ARQUIVO_ATUAL = "ultimo_audio.mp3"
HISTORICO_ARQUIVO = "historico.txt"

# ==========================================
# 💾 HISTÓRICO
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
                         placeholder="Digite aqui...")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        voz_escolhida = st.selectbox("Escolha a voz:", list(VOZES.keys()))
    with col2:
        velocidade = st.slider("Velocidade:", 0.7, 1.3, 1.0, 0.05)
    
    st.markdown("💡 **Dicas:**")
    st.info("✨ Larissa: ótima para histórias animadas | ✨ Júlia: narrações calmas | ✨ Pedro: conversas naturais")
    
    st.markdown("")
    if st.button("🔊 Gerar Áudio", type="primary", use_container_width=True):
        if not texto.strip():
            st.warning("⚠️ Digite algum texto!")
        else:
            with st.spinner("🎙️ Gerando... aguarde..."):
                voz_cod = VOZES[voz_escolhida]
                
                if velocidade == 1.0:
                    rate = "+0%"
                elif velocidade > 1.0:
                    rate = f"+{int((velocidade - 1)*100)}%"
                else:
                    rate = f"-{int((1 - velocidade)*100)}%"
                
                async def gerar():
                    if os.path.exists(ARQUIVO_ATUAL):
                        os.remove(ARQUIVO_ATUAL)
                    comm = edge_tts.Communicate(texto, voz_cod, rate=rate)
                    await comm.save(ARQUIVO_ATUAL)
                
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
                        st.download_button("⬇️ Baixar MP3", f, 
                            f"RFlix_{datetime.now().strftime('%Y%m%d_%H%M')}.mp3",
                            use_container_width=True)
                else:
                    st.error("❌ Erro. Tente novamente em alguns instantes.")

# ==========================================
# 📋 HISTÓRICO
# ==========================================
elif aba == "📋 Meus Áudios":
    st.header("📋 Histórico")
    historico = carregar_historico()
    
    if not historico:
        st.info("📭 Nenhum áudio ainda. Comece acima! 😊")
    else:
        st.write(f"📊 Total: **{len(historico)}** áudios")
        st.markdown("---")
        
        for i, item in enumerate(reversed(historico), 1):
            if len(item) == 3:
                data, voz, resumo = item
                with st.expander(f"#{i} — {voz.split(' —')[0]} | {data}"):
                    st.write(f"🎙️ **Voz:** {voz}")
                    st.write(f"📝 **Texto:** {resumo}")
        
        st.markdown("---")
        if st.button("🗑️ Limpar"):
            if os.path.exists(HISTORICO_ARQUIVO):
                os.remove(HISTORICO_ARQUIVO)
            st.success("✅ Limpo! Atualize a página.")
            st.rerun()

# ==========================================
# ℹ️ SOBRE
# ==========================================
elif aba == "ℹ️ Sobre":
    st.header("ℹ️ RFlix Studio")
    st.markdown("""
    🎙️ **Vozes humanas com IA**
    
    ✅ Escolha uma voz → digite seu texto → clique em gerar
    ✅ Baixe em MP3 quando quiser
    ✅ Histórico salvo automaticamente
    
    *Vozes confirmadas funcionando: Larissa, Júlia e Pedro* ✅
    """)

st.sidebar.markdown("---")
st.sidebar.info("💡 Mantive o Edge-TTS! Só removi as vozes que estavam falhando por enquanto. Depois vamos testar adicionar mais! 😊")
    
