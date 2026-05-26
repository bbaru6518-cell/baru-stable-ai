import streamlit as st
import google.generativeai as genai
import os
import datetime

# --- 設定 ---
LOG_DIR = "racing_logs_standard"
os.makedirs(LOG_DIR, exist_ok=True)
st.set_page_config(page_title="Baru 競馬AI Pro", layout="wide")

# --- サイドバー：総監督司令部（統合解析ロジック） ---
with st.sidebar:
    st.header("⚙️ 総監督司令部")
    api_key = st.text_input("Gemini API KEY", type="password")
    
    st.subheader("🎯 統合解析基準（常時適用）")
    st.info("""
    以下の要素を全頭診断に統合せよ：
    - JRA/地方競馬の高速馬場・トラックバイアス
    - 芝・ダートのキレ
    - 走破タイム理論（基準タイム・馬場補正）
    - 上がり3F
    - 展開・ハナ争い
    """)
    
    st.divider()
    
    st.header("📂 過去ログ・結果復習ルーム")
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    selected_log = st.selectbox("復習・確認する過去の予想", log_files)
    if st.button("📖 予想指示書を呼び出す"):
        with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
            st.session_state["res"] = f.read()
        st.rerun()

# --- メインエリア ---
st.title("🏇 Baru 競馬AI Pro - 統合解析司令部")
manual_data = st.text_area("✍️ 次回の馬柱・オッズデータ入力", height=300)

if st.button("🚀 統合解析実行"):
    if not api_key: 
        st.error("APIキーを入力してください")
    else:
        try:
            with st.spinner("統合解析中..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # サイドバーの統合解析基準をAIに強制
                prompt = f"""
                【今回の馬柱・オッズデータ】
                {manual_data}
                
                【統合解析基準】
                - JRA/地方競馬の高速馬場・トラックバイアス、芝・ダートのキレ、走破タイム理論（基準タイム・馬場補正）、上がり3F、展開・ハナ争い。
                
                【指示】
                上記基準を統合し、全頭を診断せよ。
                出力には必ず以下のテーブルを含めること：
                | 馬番 | 馬名 | 単勝勝率(%) | 複勝勝率(%) | 診断コメント |
                | --- | --- | --- | --- | --- |
                
                最後に、最も期待値の高い買い目を結論として提示せよ。
                """
                response = model.generate_content(prompt)
                st.session_state["res"] = response.text
                
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(os.path.join(LOG_DIR, f"Race_{now}.txt"), "w", encoding="utf-8") as f:
                    f.write(response.text)
        except Exception as e: 
            st.error(f"解析エラー: {e}")

if "res" in st.session_state:
    st.markdown(st.session_state["res"])
