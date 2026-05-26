import streamlit as st
import google.generativeai as genai
import os

# --- 設定 ---
LOG_DIR = "racing_logs_standard"
os.makedirs(LOG_DIR, exist_ok=True)
st.set_page_config(page_title="Baru AI Pro", layout="wide")

# --- サイドバー定義 ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", type="password")
    
    st.markdown("---")
    st.header("📂 過去ログ・猛省アーカイブ")
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    if log_files:
        selected_log = st.selectbox("過去ログ", log_files)
        if st.button("📖 呼び出す"):
            with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
                st.session_state["res"] = f.read()
            st.rerun()

# --- メイン処理 ---
st.title("🏇 Baru 競馬AI Pro - 接続安定版")
manual_data = st.text_area("✍️ 馬柱データ", height=300)

if st.button("🚀 解析実行"):
    if not api_key:
        st.error("APIキーを入力してください")
    else:
        try:
            with st.spinner("解析中..."):
                genai.configure(api_key=api_key)
                
                # エラーの原因であるモデル名を最新の正式名称に変更
                model = genai.GenerativeModel("gemini-1.5-flash-latest")
                
                prompt = f"データ: {manual_data}\n指示: 全頭診断表と3連複15点フォーメーションを作れ。"
                response = model.generate_content(prompt)
                st.session_state["res"] = response.text
                st.rerun()
        except Exception as e:
            st.error(f"接続エラー発生: {e}")
            st.info("💡 モデル名が合わない場合は、'gemini-1.5-flash' または 'gemini-1.5-pro-latest' に書き換えて試してください。")

if "res" in st.session_state:
    st.markdown(st.session_state["res"])
