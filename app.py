import streamlit as st
import google.generativeai as genai
import json
import os
import datetime

# --- 初期設定 ---
LOG_DIR = "racing_logs_chuo"
CONFIG_FILE = "baru_chuo_config.json"
os.makedirs(LOG_DIR, exist_ok=True)

def load_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"k": "", "b": "JRA・地方競馬の高速馬場・トラックバイアス、走破タイム、展開・ハナ争いを統合解析せよ。"}

cfg = load_cfg()
st.set_page_config(page_title="Baru 中央競馬AI Pro", layout="wide")
st.title("🏇 Baru 中央競馬AI Pro - 【Ver 24.9.0 15点特化版】")

# --- サイドバー：総監督ルーム ＆ 復習ルーム ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 バイアス補正", value=cfg.get("b"), height=100)
    
    st.markdown("---")
    st.header("📂 過去ログ・結果復習ルーム")
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    selected_log = st.selectbox("確認する過去ログ", log_files)
    if st.button("📖 予想を呼び出す"):
        with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
            st.session_state["res"] = f.read()

    st.markdown("---")
    st.subheader("🏁 結果コピペ・猛省")
    res_input = st.text_area("レース結果をコピペ", height=150)
    if st.button("🚨 猛省レポート生成"):
        if "res" in st.session_state and res_input:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"【予想】\n{st.session_state['res']}\n\n【結果】\n{res_input}\n\nこの結果を分析し、何が的中し何が外れたか、次回への改善点を猛省せよ。"
            response = model.generate_content(prompt)
            st.session_state["res"] += f"\n\n--- 🏁 猛省レポート ---\n{response.text}"
            st.rerun()

# --- メイン：解析処理 ---
st.subheader("📋 データ解析")
manual_data = st.text_area("出馬表・オッズ等を丸ごとコピペ", height=300)

if st.button("🚀 3連複15点フォーメーション解析開始"):
    if not api_key:
        st.error("APIキーが必要です")
    else:
        with st.spinner("解析中..."):
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            あなたは競馬のプロAIです。入力データから展開と能力を分析し、以下のフォーマットで【3連複15点】を出力せよ。
            
            データ: {manual_data}
            バイアス: {bias}
            
            【出力フォーマット】
            1. 全頭診断（テーブル形式）
            2. 展開・ハナ争い・トラックバイアスの分析
            3. 【3連複15点フォーメーション】
               - 1頭目(軸): ◎ (1頭)
               - 2頭目(対抗): ○, ▲ (2頭)
               - 3頭目(紐): ◎, ○, ▲, △, 注 (合計7頭から紐5頭)
               - 計算式: 1頭×2頭×5頭 = 15点
            """
            response = model.generate_content(prompt)
            st.session_state["res"] = response.text
            
            # ログ自動保存
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(os.path.join(LOG_DIR, f"Race_{now}.txt"), "w", encoding="utf-8") as f:
                f.write(response.text)
            st.rerun()

# --- 結果表示 ---
if "res" in st.session_state:
    st.markdown(st.session_state["res"])
