import streamlit as st
import google.generativeai as genai
import os
import datetime

# --- 設定 ---
LOG_DIR = "racing_logs_standard"
os.makedirs(LOG_DIR, exist_ok=True)
st.set_page_config(page_title="Baru 3連複解析", layout="wide")

# APIキー読み込み (Secrets優先)
api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else st.sidebar.text_input("Gemini API KEY", type="password")

def get_model(api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

# --- サイドエリア：指示書表示 ---
with st.sidebar:
    st.header("💰 三連複指示書")
    st.subheader("◎ 軸馬: 12番 (フロスティクォーツ)")
    st.markdown("""
    * **1頭目：** 12
    * **2頭目：** 1, 8, 4
    * **3頭目：** 1, 8, 4, 3, 9, 12
    """)
    st.info("**【サイド詳細】**\n* 本線: 12-(1,8,4)-(1,8,4,3,9)\n* 押さえ: 軸馬12を絡めた期待値高めの組み合わせ")

    st.markdown("---")
    st.header("📂 過去ログ・猛省")
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    if log_files:
        selected_log = st.selectbox("ログ選択", log_files)
        if st.button("📖 読み込む"):
            with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
                st.session_state["res"] = f.read()
            st.rerun()

# --- メインエリア ---
st.title("🏇 Baru 競馬AI Pro - 最終完全版")
manual_data = st.text_area("✍️ 次回の馬柱データ", height=300)

if st.button("🚀 猛省を刻んだ解析開始"):
    if not api_key: st.error("APIキーを入力してください")
    else:
        try:
            with st.spinner("解析中..."):
                model = get_model(api_key)
                history = st.session_state.get("res", "過去の猛省履歴なし")
                prompt = f"""
                【過去の敗因】{history}
                【今回のデータ】{manual_data}
                【指示】
                1. 12番(フロスティクォーツ)を軸に、指定フォーメーションを統合して診断せよ。
                2. 馬名・馬番の誤記は絶対に許されない。厳格に照合すること。
                3. 全頭診断表と、指定フォーメーションに基づく推奨買い目を提示せよ。
                """
                response = model.generate_content(prompt)
                st.session_state["res"] = response.text
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(os.path.join(LOG_DIR, f"Race_{now}.txt"), "w", encoding="utf-8") as f:
                    f.write(response.text)
                st.rerun()
        except Exception as e: st.error(f"解析エラー: {e}")

if "res" in st.session_state:
    st.markdown(st.session_state["res"])
