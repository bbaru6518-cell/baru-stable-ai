import streamlit as st
import google.generativeai as genai
import os
import datetime

# --- 設定 ---
LOG_DIR = "racing_logs_standard"
os.makedirs(LOG_DIR, exist_ok=True)
st.set_page_config(page_title="Baru AI Pro", layout="wide", initial_sidebar_state="expanded")

def get_model(api_key):
    genai.configure(api_key=api_key)
    models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if not models: raise Exception("利用可能なモデルが見つかりません")
    return genai.GenerativeModel(models[0].name)

# --- サイドバー：全機能固定 ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", type="password")
    
    st.markdown("---")
    st.header("📂 過去ログ・猛省アーカイブ")
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    if log_files:
        selected_log = st.selectbox("ログ選択", log_files)
        if st.button("📖 予想・猛省を読み込む"):
            with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
                st.session_state["res"] = f.read()
            st.rerun()

    st.markdown("---")
    st.header("🏁 猛省レポート作成")
    result_copypaste = st.text_area("レース結果", height=100)
    if st.button("🚨 照合・猛省レポート出力"):
        if "res" in st.session_state and result_copypaste and api_key:
            try:
                model = get_model(api_key)
                prompt = f"予想履歴:\n{st.session_state['res']}\n\n結果:\n{result_copypaste}\n\n指示: 敗因を深く分析し、次回への教訓を猛省せよ。"
                response = model.generate_content(prompt)
                st.session_state["res"] += f"\n\n--- 🏁 【猛省レポート】 ---\n{response.text}"
                # ログ更新
                with open(os.path.join(LOG_DIR, selected_log), "w", encoding="utf-8") as f:
                    f.write(st.session_state["res"])
                st.rerun()
            except Exception as e: st.error(f"照合エラー: {e}")

# --- メインエリア ---
st.title("🏇 Baru 競馬AI Pro - 最終完全版")
manual_data = st.text_area("✍️ 次回の馬柱データ", height=300)

if st.button("🚀 猛省を刻んだ解析開始"):
    if not api_key: st.error("APIキーを入力してください")
    else:
        try:
            with st.spinner("過去の教訓を解析に統合中..."):
                model = get_model(api_key)
                # 過去ログがロードされていればプロンプトに含める
                history = st.session_state.get("res", "過去の猛省履歴なし")
                prompt = f"""
                【過去の敗因と教訓】
                {history}
                
                【今回のデータ】
                {manual_data}
                
                指示:
                1. 過去の失敗(穴馬漏れ・データミス)を絶対に行うな。
                2. 馬番・馬名を必ず公式データと照合せよ。
                3. 全頭診断表と3連複15点フォーメーションを提示せよ。
                """
                response = model.generate_content(prompt)
                st.session_state["res"] = response.text
                # ログ保存
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(os.path.join(LOG_DIR, f"Race_{now}.txt"), "w", encoding="utf-8") as f:
                    f.write(response.text)
                st.rerun()
        except Exception as e: st.error(f"解析エラー: {e}")

if "res" in st.session_state:
    st.markdown(st.session_state["res"])
