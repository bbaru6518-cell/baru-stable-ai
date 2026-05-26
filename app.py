import streamlit as st
import google.generativeai as genai
import os
import datetime

# --- 設定 ---
LOG_DIR = "racing_logs_standard"
os.makedirs(LOG_DIR, exist_ok=True)
st.set_page_config(page_title="Baru AI Pro", layout="wide")

# --- サイドバー：猛省ログの蓄積機能 ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", type="password")
    
    st.markdown("---")
    st.header("📂 過去ログ・猛省アーカイブ")
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    
    if log_files:
        selected_log = st.selectbox("確認する過去ログ", log_files)
        if st.button("📖 予想と猛省を呼び出す"):
            with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
                st.session_state["res"] = f.read()
            st.rerun()

    st.markdown("---")
    st.header("🏁 結果コピペ・猛省生成")
    result_copypaste = st.text_area("結果を入力して猛省", height=150)
    if st.button("🚨 猛省レポート作成"):
        if "res" in st.session_state and result_copypaste:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"予想:\n{st.session_state['res']}\n\n結果:\n{result_copypaste}\n\n指示: 上記を分析し、猛省レポートを作成せよ。これを次回の予想精度向上のための教訓とせよ。"
                response = model.generate_content(prompt)
                
                # ログを上書き更新
                new_log = f"{st.session_state['res']}\n\n--- 🏁 【猛省レポート】 ---\n{response.text}"
                st.session_state["res"] = new_log
                
                # 最新ログとして保存
                with open(os.path.join(LOG_DIR, selected_log), "w", encoding="utf-8") as f:
                    f.write(new_log)
                st.rerun()
            except Exception as e:
                st.error(f"エラー: {e}")

# --- メインエリア：学習を反映させた解析 ---
st.title("🏇 Baru 競馬AI Pro - 猛省反映型")
manual_data = st.text_area("✍️ 次回の馬柱データ", height=300)

if st.button("🚀 猛省を活かした次回の構造解剖"):
    if not api_key:
        st.error("APIキーを入力してください")
    else:
        try:
            with st.spinner("過去の猛省を振り返り、精度向上中..."):
                genai.configure(api_key=api_key)
                # 過去の猛省履歴をプロンプトに含める
                history = st.session_state.get("res", "過去のデータなし")
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                prompt = f"""
                【過去の猛省履歴】
                {history}
                
                【今回のデータ】
                {manual_data}
                
                指示: 過去の敗因（展開読みのズレ、穴馬の取りこぼし）を深く反省し、今回のレースで同じ失敗をしないよう、より精密に診断せよ。
                """
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
