import streamlit as st
import google.generativeai as genai
import os
import datetime

# --- 初期設定 ---
LOG_DIR = "racing_logs_standard"
os.makedirs(LOG_DIR, exist_ok=True)
st.set_page_config(page_title="Baru AI Pro", layout="wide", initial_sidebar_state="expanded")

# --- サイドバー：全機能搭載 ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", type="password")
    
    st.markdown("---")
    st.header("📂 過去ログ・結果復習ルーム")
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    if log_files:
        selected_log = st.selectbox("確認する過去ログ", log_files)
        if st.button("📖 予想を呼び出す"):
            with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
                st.session_state["res"] = f.read()
            st.rerun()

    st.markdown("---")
    st.header("🏁 結果コピペ・猛省")
    result_copypaste = st.text_area("レース結果をコピペ", height=150)
    
    # 照合処理：session_stateを確実に見る
    if st.button("🚨 照合して猛省レポート"):
        if "res" not in st.session_state or not st.session_state["res"]:
            st.error("先に過去の予想を「呼び出し」てください。")
        elif not result_copypaste:
            st.error("レース結果を入力してください。")
        elif not api_key:
            st.error("APIキーを入力してください。")
        else:
            with st.spinner("照合・猛省中..."):
                try:
                    genai.configure(api_key=api_key)
                    models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model = genai.GenerativeModel(models[0].name)
                    
                    prompt = f"予想:\n{st.session_state['res']}\n\n結果:\n{result_copypaste}\n\n展開やハナ争いのズレを猛省せよ。"
                    response = model.generate_content(prompt)
                    
                    st.session_state["res"] += f"\n\n--- 🏁 猛省レポート ---\n{response.text}"
                    st.rerun()
                except Exception as e:
                    st.error(f"エラー: {e}")

# --- メインエリア ---
st.title("🏇 Baru 競馬AI Pro")
manual_data = st.text_area("✍️ 馬柱・データ入力", height=300)

if st.button("🚀 構造解剖・全頭診断開始"):
    if not api_key:
        st.error("APIキーを入力してください")
    else:
        try:
            with st.spinner("解析中..."):
                genai.configure(api_key=api_key)
                models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(models[0].name)
                
                prompt = f"データ: {manual_data}\n全頭診断と3連複15点指示書を作れ。"
                response = model.generate_content(prompt)
                st.session_state["res"] = response.text
                
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(os.path.join(LOG_DIR, f"Race_{now}.txt"), "w", encoding="utf-8") as f:
                    f.write(response.text)
                st.rerun()
        except Exception as e:
            st.error(f"解析エラー: {e}")

if "res" in st.session_state:
    st.markdown(st.session_state["res"])
