import streamlit as st
import google.generativeai as genai
import os
import datetime

# --- 設定 ---
LOG_DIR = "racing_logs_standard"
os.makedirs(LOG_DIR, exist_ok=True)
st.set_page_config(page_title="Baru AI Pro", layout="wide", initial_sidebar_state="expanded")

# --- サイドバー定義（固定） ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", type="password")
    
    st.markdown("---")
    st.header("📂 過去ログ・復習")
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    if log_files:
        selected_log = st.selectbox("ログ選択", log_files)
        if st.button("📖 呼び出す"):
            with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
                st.session_state["res"] = f.read()
            st.rerun()

    st.markdown("---")
    st.header("🏁 照合・猛省")
    result_copypaste = st.text_area("レース結果", height=100)
    if st.button("🚨 照合開始"):
        if "res" in st.session_state and result_copypaste:
            with st.spinner("猛省レポート生成中..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash-latest")
                    prompt = f"予想:\n{st.session_state['res']}\n\n結果:\n{result_copypaste}\n\n猛省せよ。"
                    res = model.generate_content(prompt)
                    st.session_state["res"] += f"\n\n--- 🏁 猛省レポート ---\n{res.text}"
                    st.rerun()
                except Exception as e:
                    st.error(f"照合エラー: {e}")

# --- メイン処理 ---
st.title("🏇 Baru 競馬AI Pro")
manual_data = st.text_area("✍️ 馬柱データ", height=300)

if st.button("🚀 解析開始"):
    if not api_key:
        st.error("APIキーを入力してください")
    else:
        try:
            with st.spinner("解析中..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash-latest")
                prompt = f"データ: {manual_data}\n指示: 全頭診断と3連複15点指示書を作成せよ。"
                res = model.generate_content(prompt)
                st.session_state["res"] = res.text
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(os.path.join(LOG_DIR, f"Race_{now}.txt"), "w", encoding="utf-8") as f:
                    f.write(res.text)
                st.rerun()
        except Exception as e:
            st.error(f"解析エラー: {e}")

if "res" in st.session_state:
    st.markdown(st.session_state["res"])
