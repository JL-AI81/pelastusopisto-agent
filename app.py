"""Pelastusopisto-avustaja - Yksinkertainen versio"""

import streamlit as st

st.set_page_config(
    page_title="Pelastusopisto-avustaja",
    page_icon="🚒"
)

from agent import PelastusopistoAgent

st.title("🚒 Pelastusopisto-avustaja")
st.markdown("Kysy mitä tahansa Pelastusopistosta")

if 'agent' not in st.session_state:
    st.session_state.agent = PelastusopistoAgent()
    st.session_state.messages = []

for msg in st.session_state.messages:
    if msg['role'] == 'user':
        st.chat_message("user").write(msg['content'])
    else:
        st.chat_message("assistant").write(msg['content'])

if prompt := st.chat_input("Kirjoita kysymyksesi..."):
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    st.chat_message("user").write(prompt)
    
    with st.spinner('Ajattelee...'):
        vastaus = st.session_state.agent.chat(prompt)
    
    st.session_state.messages.append({'role': 'assistant', 'content': vastaus})
    st.chat_message("assistant").write(vastaus)