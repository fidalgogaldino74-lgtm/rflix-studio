import streamlit as st
import json
from datetime import datetime

# ⚙️ Configurações da página
st.set_page_config(
    page_title="Clique e Ganhe",
    page_icon="💰",
    layout="centered"
)

# 📦 Inicializar dados do usuário
if 'saldo' not in st.session_state:
    st.session_state.saldo = 0.0
if 'cliques_hoje' not in st.session_state:
    st.session_state.cliques_hoje = 0
if 'ultimo_dia' not in st.session_state:
    st.session_state.ultimo_dia = datetime.now().strftime("%Y-%m-%d")

# 🔄 Reset diário
hoje = datetime.now().strftime("%Y-%m-%d")
if st.session_state.ultimo_dia != hoje:
    st.session_state.cliques_hoje = 0
    st.session_state.ultimo_dia = hoje

# 📊 Constantes
VALOR_POR_CLIQUE = 0.02
LIMITE_DIARIO = 50
SAQUE_MINIMO = 15.00

# 🎨 Interface
st.title("💰 Clique e Ganhe")
st.divider()

# 👤 Seção de Saldo
st.subheader("Seu Saldo")
st.markdown(f"<h1 style='color: #2e7d32; font-size: 42px;'>R$ {st.session_state.saldo:.2f}</h1>", 
            unsafe_allow_html=True)
st.info(f"📊 Anúncios hoje: {st.session_state.cliques_hoje}/{LIMITE_DIARIO}")

st.divider()

# 🖱️ Botão Ver Anúncio
st.subheader("Ver Anúncio")
if st.button("👆 Ver Anúncio e Ganhar", type="primary", use_container_width=True, disabled=st.session_state.cliques_hoje >= LIMITE_DIARIO):
    st.session_state.saldo += VALOR_POR_CLIQUE
    st.session_state.cliques_hoje += 1
    st.success(f"🎉 +R$ {VALOR_POR_CLIQUE:.2f} adicionado!")
    st.rerun()

if st.session_state.cliques_hoje >= LIMITE_DIARIO:
    st.warning("⚠️ Limite diário atingido! Volte amanhã.")

st.divider()

# 💵 Seção de Saque
st.subheader("💳 Solicitar Saque")
chave_pix = st.text_input("Sua Chave PIX", placeholder="Digite sua chave PIX")

if st.button("📤 Solicitar Saque", use_container_width=True):
    if len(chave_pix.strip()) < 5:
        st.error("❌ Digite uma chave PIX válida!")
    elif st.session_state.saldo >= SAQUE_MINIMO:
        # Salva o pedido (aqui você pode integrar com banco de dados depois)
        st.success("✅ Solicitação enviada com sucesso!")
        st.info(f"Valor: R$ {st.session_state.saldo:.2f}\nPIX: {chave_pix}\nIremos analisar em até 48h úteis.")
        # Zera saldo após solicitar
        st.session_state.saldo = 0.0
    else:
        st.warning(f"⚠️ Saldo insuficiente! Mínimo para saque: R$ {SAQUE_MINIMO:.2f}")

st.divider()

# 📌 Rodapé
st.caption("© 2026 Clique e Ganhe | Seja bem-vindo! 💚")

