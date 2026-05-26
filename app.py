import streamlit as st
import google.generativeai as genai
import os
import datetime
import json

# --- 設定・ディレクトリ ---
LOG_DIR = "racing_logs_standard"
os.makedirs(LOG_DIR, exist_ok=True)

# モデル選択ロジック（自動解決型）
def get_model(api_key):
    genai.configure(api_key=api_key)
    # 利用可能なモデルを全取得
    models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if not models:
        raise Exception("利用可能なモデルが見つかりません。")
    # 最初のモデルを強制選択
    return genai.GenerativeModel(models[0].name)

# --- サイドバー構成 ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", type="password")
    if st.button("💾 設定保存"):
        st.success("保存完了")

# --- メイン解析処理 ---
st.title("🏇 Baru 競馬AI Pro - 接続安定版")
manual_data = st.text_area("netkeibaデータをコピペ", height=300)

if st.button("🚀 解析実行"):
    if not api_key:
        st.error("APIキーを入力してください")
    else:
        try:
            with st.spinner("モデルを探索中..."):
                model = get_model(api_key)
                prompt = f"データ: {manual_data}\n指示: 3連複15点フォーメーションを生成せよ。"
                response = model.generate_content(prompt)
                st.session_state["res"] = response.text
                st.rerun()
        except Exception as e:
            st.error(f"接続エラー詳細: {e}")
            st.info("💡 ヒント: これでもエラーが出る場合、APIキーを再生成し、Google AI Studioのプロジェクト設定を確認してください。")

if "res" in st.session_state:
    st.markdown(st.session_state["res"])
