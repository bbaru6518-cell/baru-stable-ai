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
manual_data = st.text_area("✍️ 次回の馬柱・オッズデータ入力（netkeibaのデータ分析テキストも含む）", height=300)

if st.button("🚀 統合解析実行"):
    if not api_key: 
        st.error("APIキーを入力してください")
    else:
        try:
            with st.spinner("統合解析中..."):
                genai.configure(api_key=api_key)
                
                # 【エラー修正箇所】モデル名の前に 'models/' を明示的に指定
                model = genai.GenerativeModel('models/gemini-1.5-flash')
                
                # 【ロジック強化】バルさん専用の「下剋上穴馬検知」と「netkeiba連動」をプロンプトに統合
                prompt = f"""
                【今回の馬柱・オッズデータ（netkeiba分析含む）】
                {manual_data}
                
                【統合解析基準】
                - JRA/地方競馬の高速馬場・トラックバイアス、芝・ダートのキレ、走破タイム理論（基準タイム・馬場補正）、上がり3F、展開・ハナ争い。
                
                【💡 総監督絶対厳守ロジック：netkeibaデータ傾向スクリーニング】
                1. データ内の「データ上位馬3頭」に記載がある馬は、地力上位として軸・相手筆頭（◎, 〇, ▲）の最有力候補にせよ。
                2. 「今回の馬場状態が得意な馬」「今回のレース間隔で実績がある馬」「この競馬場が得意な馬」の項目に該当する不人気馬（単勝5番人気以下）は、近走着順が悪くても「消し」を厳禁とし、必ず【穴候補・紐（△または注）】に組み込め。

                【💡 総監督絶対厳守ロジック：死んだふり下剋上馬（上がり最速爆弾）の検知】
                以下の条件を満たす「近走大敗の伏兵馬」は、展開を引っ掻き回す下剋上馬として検知せよ。
                - 条件A：2-3走前に「上がり3F上位（1〜2位）」の脚を繰り出した隠れたスタミナ・末脚特性がある馬。
                - 条件B：前走が短い距離（マイル以下）で大敗し、今回スタミナの問われる長距離（1800m〜2000m以上）へ延長してきた馬（追走が楽になり死んだふりから捲り可能）。
                - 上記に該当する馬は、展開が「前崩れ・ミドルペース以上」になった場合の想定3着以内（紐馬）としてフォーメーションの3頭目に強制配置すること。

                【指示】
                上記すべての基準とロジックを完全に統合し、全頭を精密に診断せよ。
                必ず以下の形式のテーブルで出力すること：
                | 馬番 | 馬名 | 単勝勝率(%) | 複勝勝率(%) | 診断コメント（穴判定・紐判定の理由も明記） |
                | --- | --- | --- | --- | --- |
                
                最後に、最も期待値の高い買い目（三連複フォーメーション等）を結論として提示せよ。
                """
                response = model.generate_content(prompt)
                st.session_state["res"] = response.text
                
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(os.path.join(LOG_DIR, f"Race_{now}.txt"), "w", encoding="utf-8") as f:
                    f.write(response.text)
                    
            st.rerun() # 画面をリフレッシュして即時反映
        except Exception as e: 
            st.error(f"解析エラー: {e}")

if "res" in st.session_state:
    st.markdown(st.session_state["res"])
