import streamlit as st
import google.generativeai as genai
import json
import os
import requests
from bs4 import BeautifulSoup
import datetime

# --- 設定保存・ログ管理 ---
CONFIG_FILE = "baru_pro_config.json"
LOG_DIR = "win5_logs"
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
    return {"k": "", "b": "WIN5対象5レースのトラックバイアス、芝・ダートのキレ、走破タイム理論（基準タイム・馬場補正）、展開・ハナ争い、そして『ガチガチ本命レース』と『大荒れ混戦レース』のメリハリを統合解析せよ。"}

cfg = load_cfg()
st.set_page_config(page_title="Baru AI WIN5 Master v25", layout="wide")

# --- サイドバー：総監督WIN5司令部 ---
with st.sidebar:
    st.header("⚙️ 総監督WIN5司令部")
    
    # 【追加】アプリURLリンク
    st.success("🌐 現在の司令部アプリURL")
    st.write("https://baru-stable-ai-atmit7psqdxrey5mz823xs.streamlit.app/")
    
    st.divider()
    
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 総監督バイアス（5レース共通・個別指示）", value=cfg.get("b"), height=150)
    budget = st.number_input("WIN5総予算(円)", value=10000, step=1000)
    
    if st.button("💾 設定保存"):
        save_cfg(api_key, bias)
        st.success("戦略設定を保存しました。")

    st.divider()
    
    # 過去ログエリア
    st.header("📂 過去のWIN5戦略ログ")
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    selected_log = st.selectbox("確認する過去のWIN5戦略", log_files)
    if st.button("📖 指示書を呼び出す"):
        with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
            st.session_state["res"] = f.read()
        st.rerun()

    st.divider()

    # レース結果照合
    st.header("🏁 レース結果の照合")
    st.text_area("WIN5結果のコピペ", height=150)
    if st.button("🚨 実際の的中・結果と照合"):
        st.info("解析結果との照合準備中...")

# --- メインエリア ---
st.title("🏇 WIN5戦略特化型マスター】")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 WIN5対象 5レース分のデータ一括投入")
    manual_data = st.text_area("✍️ WIN5対象5レースの出馬表・オッズ（連続コピペ投入OK）", height=500)
    
    if st.button("🚀 WIN5・5連勝鉄壁フォーメーション生成"):
        if not api_key or not manual_data:
            st.error("APIキーとデータが必要です")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("models/gemini-1.5-pro")
                
                prompt = f"""あなたはWIN5を完全攻略する最強の競馬AIだ。以下のデータを解剖し、最適化されたフォーメーション指示書を作成せよ。
                
                対象データ: {manual_data}
                総監督バイアス: {bias}
                予算: {budget}円
                
                【出力指示】
                1. 各レースの難易度ジャッジメント（テーブル形式）
                2. 展開・ハナ争いの核心
                3. 予算内に収めた最終投資指示書
                """
                
                with st.spinner("🚀 WIN5多角マトリクス解析中..."):
                    response = model.generate_content(prompt)
                    st.session_state["res"] = response.text
                    
                    # ログ保存
                    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    with open(os.path.join(LOG_DIR, f"WIN5_{now}.txt"), "w", encoding="utf-8") as f:
                        f.write(response.text)
            except Exception as e:
                st.error(f"解析エラー: {e}")

with col2:
    st.subheader("📊 WIN5最終投資指示書")
    if "res" in st.session_state:
        st.markdown(st.session_state["res"])
