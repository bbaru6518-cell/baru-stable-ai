import streamlit as st
import google.generativeai as genai
import os
import json
import datetime

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

    st.markdown("---")
    st.header("🏁 結果入力")
    result_copypaste = st.text_area("レース結果", height=100)
    if st.button("🚨 照合して猛省"):
        if "res" in st.session_state and result_copypaste:
            st.warning("猛省レポート生成中...")
            st.rerun()

# --- メイン処理 ---
st.title("🏇 Baru 競馬AI Pro - 接続突破版")
manual_data = st.text_area("✍️ 馬柱データ", height=300)

if st.button("🚀 解析実行"):
    if not api_key:
        st.error("APIキーを入力してください")
    else:
        try:
            with st.spinner("モデルを探索・接続中..."):
                genai.configure(api_key=api_key)
                
                # 【重要】モデルを自動取得し、サポートされているものだけを抽出
                all_models = genai.list_models()
                valid_models = [m for m in all_models if 'generateContent' in m.supported_generation_methods]
                
                if not valid_models:
                    st.error("利用可能なモデルが見つかりません。")
                else:
                    # 最初のモデルを強制適用
                    model = genai.GenerativeModel(valid_models[0].name)
                    st.sidebar.info(f"使用中: {valid_models[0].name}")
                    
                    prompt = f"データ: {manual_data}\n指示: 全頭診断と3連複15点指示書を作れ。"
                    response = model.generate_content(prompt)
                    st.session_state["res"] = response.text
                    st.rerun()
        except Exception as e:
            st.error(f"接続エラー詳細: {e}")

if "res" in st.session_state:
    st.markdown(st.session_state["res"])
