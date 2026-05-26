import streamlit as st
import google.generativeai as genai
import os

# --- 設定 ---
LOG_DIR = "racing_logs_standard"
os.makedirs(LOG_DIR, exist_ok=True)

# --- 接続テストおよびモデル取得関数 ---
def get_model(api_key):
    genai.configure(api_key=api_key)
    # モデル名を短縮形にし、接続を試みる
    model_name = "gemini-1.5-flash"
    return genai.GenerativeModel(model_name)

# --- UI ---
st.title("🏇 Baru AI 最終安定版")
api_key = st.text_input("Gemini API KEY", type="password")
manual_data = st.text_area("データ入力")

if st.button("🚀 3連複15点解析開始"):
    if not api_key:
        st.error("APIキーを入力してください")
    else:
        try:
            with st.spinner("接続中..."):
                model = get_model(api_key)
                response = model.generate_content(f"3連複15点で競馬予想せよ: {manual_data}")
                st.session_state["res"] = response.text
                st.rerun()
        except Exception as e:
            st.error(f"接続エラー詳細: {e}")
            st.info("💡 ヒント: APIキーが正しいか、Google AI Studio でプロジェクトが有効か再確認してください。")

if "res" in st.session_state:
    st.markdown(st.session_state["res"])
