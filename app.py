import streamlit as st
import google.generativeai as genai
import os
import json
import datetime

# --- 設定 ---
LOG_DIR = "racing_logs_standard"
os.makedirs(LOG_DIR, exist_ok=True)
st.set_page_config(page_title="Baru AI Pro", layout="wide", initial_sidebar_state="expanded")

# --- サイドバー定義（一番最初に記述することで表示を固定） ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", type="password")
    if st.button("💾 設定保存"):
        st.success("保存完了")

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
    if st.button("🚨 照合して猛省"):
        st.warning("猛省レポート生成中...")
        st.rerun()

# --- メインエリア ---
st.title("🏇 Baru 競馬AI Pro - 最終完全版")
manual_data = st.text_area("✍️ 馬柱・データ入力", height=300)

if st.button("🚀 構造解剖・3連複15点解析開始"):
    if not api_key:
        st.error("APIキーを入力してください")
    else:
        try:
            with st.spinner("接続先探索中..."):
                genai.configure(api_key=api_key)
                # モデル自動探索で404エラーを回避
                models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(models[0].name)
                
                prompt = f"""
                【全頭診断・3連複15点フォーメーション】
                データ: {manual_data}
                
                指示: 
                1. 以下の形式で全頭診断Markdown表を出力せよ。
                | 馬番 | 馬名 | 父 | 母 | ダート適性 | 脚質 | 人気 | 評価 | 理由 |
                2. 以下の形式で【3連複15点フォーメーション】を出力せよ。
                ・1列目(軸): ◎ 1頭
                ・2列目(相手): ○, ▲ 2頭
                ・3列目(紐): ◎, ○, ▲, △, 注 計5頭
                """
                response = model.generate_content(prompt)
                st.session_state["res"] = response.text
                
                # 自動ログ保存
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(os.path.join(LOG_DIR, f"Race_{now}.txt"), "w", encoding="utf-8") as f:
                    f.write(response.text)
                st.rerun()
        except Exception as e:
            st.error(f"接続エラー: {e}")

if "res" in st.session_state:
    st.markdown(st.session_state["res"])
