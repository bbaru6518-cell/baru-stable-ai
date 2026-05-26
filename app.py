import streamlit as st
import google.generativeai as genai
import json
import os
import datetime
import re

# --- 設定・ディレクトリ ---
CONFIG_FILE = "baru_pro_config.json"
LOG_DIR = "racing_logs_standard"
os.makedirs(LOG_DIR, exist_ok=True)

def save_cfg(k, b):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"k": k, "b": b}, f, ensure_ascii=False, indent=4)

def load_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"k": "", "b": "JRA・地方競馬の高速馬場・トラックバイアス、芝・ダートのキレ、走破タイム理論、上がり3F、展開・ハナ争いを統合解析せよ。"}

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>| \t]', '_', name.strip())[:50]

cfg = load_cfg()
st.set_page_config(page_title="Baru AI Pro v24.8", layout="wide", initial_sidebar_state="expanded")
st.title("🏇 Baru 競馬AI Pro - 【Ver 24.8 最終統合版】")

# --- サイドバー：全機能搭載 ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 総監督バイアス", value=cfg.get("b"), height=100)
    if st.button("💾 設定保存"):
        save_cfg(api_key, bias)
        st.success("設定を保存しました。")

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
    if st.button("🚨 実際の着順と照合して猛省"):
        if "res" in st.session_state and result_copypaste:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"予想指示書:\n{st.session_state['res']}\n\n結果:\n{result_copypaste}\n\n上記を比較し猛省レポートを生成せよ。"
            response = model.generate_content(prompt)
            st.session_state["res"] += f"\n\n--- 🏁 猛省レポート ---\n{response.text}"
            st.rerun()

# --- メインエリア ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 9走馬柱・データ入力")
    manual_data = st.text_area("netkeibaデータをコピペ", height=400)
    
    if st.button("🚀 構造解剖・3連複15点解析開始"):
        if not api_key:
            st.error("APIキーを入力してください")
        else:
            with st.spinner("解析中..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"データ: {manual_data}\nバイアス: {bias}\n指示: 3連複15点フォーメーションで予想せよ。"
                response = model.generate_content(prompt)
                
                st.session_state["res"] = response.text
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(os.path.join(LOG_DIR, f"Race_{now}.txt"), "w", encoding="utf-8") as f:
                    f.write(response.text)
                st.rerun()

with col2:
    st.subheader("📊 投資指示書・復習表示")
    if "res" in st.session_state:
        st.markdown(st.session_state["res"])
