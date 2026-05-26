import datetime
import re

# 📁 復習用のディレクトリ設定
LOG_DIR = "racing_logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 🧹 ファイル名クリーニング
def clean_filename(name):
    return re.sub(r'[\\/*?:"<>| \t]', '_', name.strip())[:50]

# --- サイドバー復習セクション ---
with st.sidebar:
    st.markdown("---")
    st.header("📂 過去ログ・結果復習ルーム")
    
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    if log_files:
        selected_log = st.selectbox("復習・確認する過去の予想", log_files)
        
        if st.button("📖 過去の指示書を呼び出す"):
            with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
                st.session_state["res"] = f.read()

    st.markdown("---")
    st.subheader("🏁 レース結果のコピペ投入")
    result_copypaste = st.text_area("1行目：レース名 / 2行目〜：結果コピペ", height=200)
    
    if st.button("🚨 AI猛省・戦果照合開始"):
        if not api_key or not result_copypaste.strip() or not st.session_state["res"]:
            st.error("APIキー、結果データ、そして呼び出した予想ログが必要です")
        else:
            with st.spinner("戦果を分析し、次回の改善点を抽出中..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("models/gemini-1.5-pro") # プロ版推奨
                    
                    # 猛省プロンプト
                    review_prompt = f"""
                    あなたは総監督Baruの右腕AIだ。以下の【当時の予想】と【実際のレース結果】を徹底比較し、短く簡潔に戦果分析レポートを作成せよ。
                    
                    【当時の予想指示書】:
                    {st.session_state["res"]}
                    
                    【実際のレース結果】:
                    {result_copypaste}
                    
                    【出力項目】
                    1. 結果の整理（払戻金と的中・不的中）
                    2. なぜその結果になったのか（展開・バイアス・見落としの猛省）
                    3. 次回制覇のためのロジック修正案（次回の予想指示書にどうバイアスを反映させるか）
                    """
                    
                    response = model.generate_content(review_prompt)
                    
                    # ログの追記保存
                    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_log = f"{st.session_state['res']}\n\n=== 🏁 結果・猛省レポート ({now_str}) ===\n{response.text}"
                    with open(os.path.join(LOG_DIR, f"Result_{now_str}.txt"), "w", encoding="utf-8") as f:
                        f.write(new_log)
                        
                    st.session_state["res"] = new_log
                    st.success("猛省レポートを作成しました！")
                except Exception as e:
                    st.error(f"分析エラー: {e}")
