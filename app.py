import streamlit as st
import google.generativeai as genai
import os
import json

# --- 初期設定 ---
LOG_DIR = "racing_logs_standard"
os.makedirs(LOG_DIR, exist_ok=True)
st.set_page_config(page_title="Baru AI Pro", layout="wide")

# --- サイドバー定義 ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", type="password")
    if st.button("💾 設定保存"):
        st.success("設定保存完了")
    
    st.markdown("---")
    st.header("📂 過去ログ・結果復習ルーム")
    # ログ表示処理...

# --- メイン処理：モデル自動探索エンジン ---
st.title("🏇 Baru 競馬AI Pro - 接続安定版")
manual_data = st.text_area("✍️ 馬柱データを入力", height=300)

if st.button("🚀 構造解剖・全頭精密診断開始"):
    if not api_key:
        st.error("APIキーを入力してください")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # 【重要】利用可能なモデルをリストアップして、最初のものを強制適用
            models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if not models:
                st.error("利用可能なモデルが見つかりませんでした。APIキーを確認してください。")
            else:
                st.write(f"使用中モデル: {models[0].name}") # どのモデルを使っているか表示
                model = genai.GenerativeModel(models[0].name)
                
                prompt = f"""
                以下のデータから「全頭診断(Markdown表)」と「3連複15点フォーメーション」を作成せよ。
                データ: {manual_data}
                """
                response = model.generate_content(prompt)
                st.session_state["res"] = response.text
                st.rerun()
        except Exception as e:
            st.error(f"接続エラー: {e}")

if "res" in st.session_state:
    st.markdown(st.session_state["res"])
