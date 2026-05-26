import streamlit as st
import google.generativeai as genai
import json
import os
import datetime
import re
import requests
from bs4 import BeautifulSoup

# --- 設定・ディレクトリ ---
LOG_DIR = "racing_logs_chuo"
CONFIG_FILE = "baru_chuo_config.json"
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
    return {
        "k": "", 
        "b": "JRA芝・ダートのトラックバイアス、高速馬場適性、上がり3F、パドック気配、エージェント情報を統合解析せよ。"
    }

cfg = load_cfg()
st.set_page_config(page_title="Baru 中央競馬AI Pro", layout="wide")

st.title("🏇 Baru 中央競馬AI Pro - 【Ver 24.8.5 高速・軽量化安定版】")

# --- サイドバー：総監督ルーム ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム（中央司令部）")
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 中央競馬バイアス補正", value=cfg.get("b"), height=150)
    if st.button("💾 設定保存"):
        save_cfg(api_key, bias)
        st.success("設定を保存しました。")

    st.markdown("---")
    st.header("📂 過去ログ・結果復習ルーム")
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    if log_files:
        selected_log = st.selectbox("復習・確認する過去の予想", log_files)
        if st.button("📖 予想指示書を呼び出す"):
            with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
                st.session_state["res"] = f.read()

    st.markdown("---")
    st.subheader("🏁 レース結果のコピペ投入")
    res_copypaste = st.text_area("1行目：レース名 / 2行目〜：結果コピペ", height=150)
    if st.button("🚨 的中判定・猛省レポート生成"):
        if api_key and res_copypaste and "res" in st.session_state:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("models/gemini-1.5-pro")
            prompt = f"以下の予想と結果を比較し、猛省レポートを作成せよ。\n\n【予想】{st.session_state['res']}\n\n【結果】{res_copypaste}"
            res = model.generate_content(prompt)
            st.session_state["res"] += f"\n\n--- 🏁 結果判定 ---\n{res.text}"
            st.rerun()

# --- メイン画面 ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 中央競馬 過去馬柱・オッズデータ・パドック情報入力")
    manual_data = st.text_area("JRAデータを丸ごとコピペ", height=400)
    
    if st.button("🚀 全頭精密診断・中央芝ダート適性解析"):
        if api_key and manual_data:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("models/gemini-1.5-pro")
            
            prompt = f"""
            あなたはJRA中央競馬専門のAIだ。入力データから各馬の「芝適性」「ダート適性」「コース適性」を分析し、
            1着馬を当てるための「中央競馬専用指示書」を作成せよ。
            【条件】
            - 芝・ダートの適性度を◎○▲△で評価。
            - 逃げ・先行・差し・追込を絵文字付きで分類。
            - 中央特有の高速馬場適性を判定。
            
            データ: {manual_data}
            バイアス: {bias}
            """
            with st.spinner("解析中..."):
                response = model.generate_content(prompt)
                st.session_state["res"] = response.text
                
                # 自動保存
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(os.path.join(LOG_DIR, f"Chuo_Race_{now}.txt"), "w", encoding="utf-8") as f:
                    f.write(response.text)
                st.rerun()

with col2:
    st.subheader("📊 的中指示書 & AI解析ログ連動表示")
    if "res" in st.session_state:
        st.markdown(st.session_state["res"])
