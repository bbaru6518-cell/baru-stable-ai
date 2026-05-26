import streamlit as st
import google.generativeai as genai
import os

# --- 設定 ---
LOG_DIR = "racing_logs"
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

st.title("🏇 Baru AI 安定版")

# --- 解析ロジック ---
# ボタンをメインの1箇所に集中させます
input_data = st.text_area("netkeibaデータをコピペ")
api_key = st.text_input("APIキー", type="password")

if st.button("🚀 解析実行"):
    if not api_key or not input_data:
        st.error("キーとデータを入れてください")
    else:
        try:
            with st.spinner("解析中..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"3連複15点指示書を作れ: {input_data}")
                st.session_state["res"] = response.text
                st.success("完了")
        except Exception as e:
            st.error(f"エラー内容: {e}")

# 結果表示
if "res" in st.session_state:
    st.markdown(st.session_state["res"])
