import streamlit as st
import google.generativeai as genai
import os

# --- 設定・ディレクトリ ---
LOG_DIR = "racing_logs"
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

st.set_page_config(page_title="Baru AI Pro", layout="wide")
st.title("🏇 Baru 競馬AI Pro - 復旧版")

# --- サイドバーエリア ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("API KEY", type="password")
    
    st.markdown("---")
    st.header("📂 過去ログ・結果復習ルーム")
    
    # ここで確実にディレクトリを読み込む
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    
    if log_files:
        selected_log = st.selectbox("確認する過去ログ", log_files)
        if st.button("📖 読み込む"):
            with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
                st.session_state["res"] = f.read()
    else:
        st.write("ログはありません")

# --- メインエリア ---
col1, col2 = st.columns([1, 1])

with col1:
    manual_data = st.text_area("データ入力", height=300)
    if st.button("🚀 3連複15点フォーメーション解析開始"):
        if not api_key:
            st.error("APIキーを入力してください")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(f"3連複15点で競馬予想せよ: {manual_data}")
                st.session_state["res"] = response.text
                
                # ログ保存
                with open(os.path.join(LOG_DIR, "latest_race.txt"), "w", encoding="utf-8") as f:
                    f.write(response.text)
                st.rerun()
            except Exception as e:
                st.error(f"エラー: {e}")

with col2:
    st.subheader("📊 投資指示書")
    if "res" in st.session_state:
        st.markdown(st.session_state["res"])
