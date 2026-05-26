import streamlit as st
import google.generativeai as genai
import os
import datetime
import json
import re

# --- 設定・ディレクトリ ---
LOG_DIR = "racing_logs_standard"
CONFIG_FILE = "baru_pro_config.json"
os.makedirs(LOG_DIR, exist_ok=True)

# 設定保存・読込
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
st.set_page_config(page_title="Baru AI Pro", layout="wide", initial_sidebar_state="expanded")

# --- サイドバー：完全統合構成 ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 バイアス補正", value=cfg.get("b"), height=100)
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
            prompt = f"予想:\n{st.session_state['res']}\n\n結果:\n{result_copypaste}\n\n上記に基づき、展開のズレを猛省せよ。"
            response = model.generate_content(prompt)
            st.session_state["res"] += f"\n\n--- 🏁 猛省レポート ---\n{response.text}"
            st.rerun()

# --- メインエリア：3連複フォーメーション特化 ---
st.title("🏇 Baru 競馬AI Pro - 3連複15点指示書")
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
                # 買い目を強制指定
                prompt = f"""
                データ: {manual_data}
                バイアス: {bias}
                指示: 以下のフォーマットで【3連複15点フォーメーション】を必ず出力せよ。
                
                【3連複15点指示書】
                1列目(軸): ◎ (1頭)
                2列目(相手): ○, ▲ (2頭)
                3列目(紐): ◎, ○, ▲, △, 注 (5頭)
                計算式: 1×2×(5+1+1)は15点を超えないように。
                """
                response = model.generate_content(prompt)
                st.session_state["res"] = response.text
                st.rerun()

with col2:
    st.subheader("📊 投資指示書")
    if "res" in st.session_state:
        st.markdown(st.session_state["res"])
