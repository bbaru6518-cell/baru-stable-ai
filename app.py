import streamlit as st
import google.generativeai as genai
import json
import os
import datetime

# --- 初期設定 ---
LOG_DIR = "racing_logs_chuo"
CONFIG_FILE = "baru_chuo_config.json"
os.makedirs(LOG_DIR, exist_ok=True)

# --- 設定関数 ---
def save_cfg(k, b):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"k": k, "b": b}, f, ensure_ascii=False, indent=4)

def load_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"k": "", "b": "JRA芝・ダートのトラックバイアス、高速馬場適性、上がり3Fを統合解析せよ。"}

cfg = load_cfg()

# --- UI表示 ---
st.set_page_config(page_title="Baru 中央競馬AI Pro", layout="wide")
st.title("🏇 Baru 中央競馬AI Pro - 【Ver 24.8.5 修正版】")

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム（中央司令部）")
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 中央競馬バイアス補正", value=cfg.get("b"), height=150)
    if st.button("💾 設定保存"):
        save_cfg(api_key, bias)
        st.success("設定を保存しました。")

# --- メイン処理 ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 データ入力")
    manual_data = st.text_area("JRAデータを丸ごとコピペ", height=400)
    
    # 【ここが重要】UIパーツは必ずインデントの合ったメインフローに置く
    if st.button("🚀 全頭精密診断・中央芝ダート適性解析"):
        if not api_key:
            st.error("APIキーを入力してください。")
        elif not manual_data:
            st.warning("データを入力してください。")
        else:
            with st.spinner("解析中..."):
                try:
                    genai.configure(api_key=api_key)
                    models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model = genai.GenerativeModel(models[0].name)
                    
                    prompt = f"データ: {manual_data}\nバイアス: {bias}\n指示: JRA適性を◎○▲△で評価せよ。"
                    response = model.generate_content(prompt)
                    st.session_state["res"] = response.text
                    st.rerun()
                except Exception as e:
                    st.error(f"エラー: {e}")

with col2:
    st.subheader("📊 的中指示書")
    if "res" in st.session_state:
        st.markdown(st.session_state["res"])
