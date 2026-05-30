import streamlit as st
import google.generativeai as genai
import os
import datetime

# --- 設定 ---
LOG_DIR = "racing_logs_standard"
os.makedirs(LOG_DIR, exist_ok=True)
st.set_page_config(page_title="Baru 競馬AI Pro", layout="wide")

# --- サイドバー：総監督司令部 ---
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
    
    # 過去ログエリア
    st.header("📂 過去ログ・結果復習ルーム")
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    selected_log = st.selectbox("復習・確認する過去の予想", log_files)
    if st.button("📖 予想指示書を呼び出す"):
        with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
            st.session_state["res"] = f.read()
        st.rerun()

    st.divider()

    # レース結果コピペ投入エリア
    st.header("🏁 レース結果のコピペ投入")
    st.caption("💡 1行目にレース名を入力し、2行目から結果を丸ごとコピペしてください！")
    race_result_input = st.text_area("1行目：レース名 / 2行目～：結果コピペ", height=200)
    if st.button("🚨 実際の着順・ハナ争いと照合して復習"):
        st.info("解析結果と実際のレース結果を照合中...")
        # 必要に応じてここに照合ロジックを追加可能

# --- メインエリア ---
st.title("🏇 Baru 競馬AI Pro - 統合解析司令部")
st.caption("💡 馬柱やオッズデータに加え、netkeibaの『データ分析画面のテキスト』も一緒に丸ごと貼り付けてください。")
manual_data = st.text_area("✍️ 次回の馬柱・オッズデータ入力（データ分析傾向も含む）", height=300)

if st.button("🚀 統合解析実行"):
    if not api_key: 
        st.error("APIキーを入力してください")
    else:
        try:
            with st.spinner("統合解析中..."):
                # 【最重要エラー対策】最新ライブラリ仕様に合わせ、APIバージョンを 'v1' に完全固定
                genai.configure(api_key=api_key, client_options={"api_version": "v1"})
                
                # 404エラーを回避するため、プレフィックスなしの最新指定形式を採用
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # 【バルさん専用拡張ロジック搭載プロンプト】
                prompt = f"""
                【今回の馬柱・オッズデータ（netkeiba分析情報含む）】
                {manual_data}
                
                【統合解析基準】
                - JRAおよび地方競馬の高速馬場・トラックバイアス、芝・ダートのキレ、走破タイム理論（基準タイム・馬場補正）、上がり3F、展開・ハナ争いを統合解析せよ。
                
                【⚙️ 総監督絶対厳守ロジック：netkeibaデータ傾向スクリーニング】
                1. 投入されたデータ内に「データ上位馬3頭」というセクションがある場合、そこに名前がある馬はクラス・条件への地力が高いと判断し、軸馬・相手筆頭（◎, 〇, ▲）の最有力候補として評価パラメータを大きく加算せよ（＝軸にきやすい）。
                2. データ内の「今回の馬場状態が得意な馬」「今回のレース間隔で実績がある馬」「この競馬場が得意
