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

    # レース結果コピペ投入エリア（機能完全実装）
    st.header("🏁 レース結果のコピペ投入")
    st.caption("💡 1行目にレース名を入力し、2行目から結果を丸ごとコピペしてください！")
    race_result_input = st.text_area("1行目：レース名 / 2行目～：結果コピペ", height=200)
    
    if st.button("🚨 実際の着順・ハナ争いと照合して復習"):
        if not api_key:
            st.error("APIキーを入力してください")
        elif not race_result_input:
            st.error("結果データをコピペしてください")
        elif "res" not in st.session_state:
            st.error("まずメイン画面で過去ログを呼び出すか、予想を実行して『現在の予想指示書』を表示させてください")
        else:
            try:
                with st.spinner("実際のレース結果と照合し、反省会を実施中..."):
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    review_prompt = f"""
                    【総監督からの命令：レース結果の答え合わせと徹底反省】
                    
                    あなたが先ほど出力した【予想指示書】と、実際に発生した【レース結果・着順】を照合し、以下の基準で猛反省（回顧）を行え。
                    
                    1. 軸馬（◎, ○, ▲）の成否
                       - 軸に据えた馬は馬券圏内（3着以内）にきたか？
                       - netkeibaの「データ上位馬3頭」の信頼度はどうだったか？
                    
                    2. 「死んだふり下剋上穴馬」の生存確認
                       - あなたが「上がり最速爆弾馬」や「激走警戒馬（注）」として救済・指名した不人気馬の実際の着順・上がり3Fを確認せよ。
                       - 実際に激走したか？ 凡走した場合、展開（スローペース等）やトラックバイアスがどう影響したか推測せよ。
                    
                    3. 展開・ハナ争いの答え合わせ
                       - 事前に想定したハナ争いやペース（ハイ・ミドル・スロー）は、実際の展開と一致していたか？
                    
                    【提出された現在の予想指示書】
                    {st.session_state["res"]}
                    
                    【実際のレース結果（コピペデータ）】
                    {race_result_input}
                    
                    【出力フォーマット】
                    ### 🏁 {race_result_input.splitlines()[0] if race_result_input.splitlines() else '対象レース'} - 統合反省レポート
                    - **総合評価**: （例：大的中 / 軸は合致も紐抜け / 展開不一致による大敗 など）
                    
                    #### 📊 着順答え合わせ
                    | 印 | 馬名 | 事前評価 | 実際の着順 | 上がり3F（結果） | 反省・要因分析 |
                    | --- | --- | --- | --- | --- | --- |
                    
                    #### 🧠 次回に向けたロジック修正点（総監督への進言）
                    - （例：高速馬場での前残りバイアスを軽視していた、距離延長の死んだふり馬はダートだと不発しやすい等、次回以降プロンプトで微調整すべき教訓を箇条書きで書くこと）
                    """
                    
                    response = model.generate_content(review_prompt)
                    # 反省結果を画面に上書き描画
                    st.session_state["res"] = response.text
                st.rerun()
            except Exception as e:
                st.error(f"反省解析エラー: {e}")

    st.divider()

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
                genai.configure(api_key=api_key)
                
                # エラー回避のため、1.5から2.5-flashへ完全移行
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = f"""
                【今回の馬柱・オッズデータ（netkeiba分析情報含む）】
                {manual_data}
                
                【統合解析基準】
                - JRAおよび地方競馬の高速馬場・トラックバイアス、芝・ダートのキレ、走破タイム理論（基準タイム・馬場補正）、上がり3F、展開・ハナ争いを統合解析せよ。
                
                【⚙️ 総監督絶対厳守ロジック：netkeibaデータ傾向スクリーニング】
                1. 投入されたデータ内に「データ上位馬3頭」というセクションがある場合、そこに名前がある馬はクラス・条件への地力高いと判断し、軸馬・相手筆頭（◎, 〇, ▲）の最有力候補として評価パラメータを大きく加算せよ（＝軸にきやすい）。
                2. データ内の「今回の馬場状態が得意な馬」「今回のレース間隔で実績がある馬」「この競馬場が得意な馬」のいずれかの項目に該当する不人気馬（目安：単勝5番人気以下）を発見した場合は、近走着順がどれだけ悪くても「消し」評価にすることを厳禁とし、必ず【穴候補・紐（△または注）】として救済・格納せよ。

                【⚙️ 総監督絶対厳守ロジック：死んだふり下剋上馬（上がり最速爆弾）の検知】
                近走成績が崩れていても、以下の「激走ファクター」を満たす伏兵馬は、展開（ミドル〜ハイペース）がハマった瞬間に上がり最速で下剋上を起こす爆弾馬として自動検知せよ。
                - 条件A：過去2〜3走以内に、敗れてはいるが「上がり3Fタイムがメンバー中1位または2位」の隠れた強烈な末脚・スタミナ実績がある馬。
                - 条件B：前走が短い距離（マイル以下）で大敗しており、今回スタミナが問われる長距離（1800m〜2000m以上）へと大幅に距離延長してきた馬（追走ペースが楽になり、道中死んだふりから3〜4コーナーでの捲り差しが裂裂するパターン）。
                - 上記に該当する馬は、展開利による激走警戒馬（注）として評価し、3連複フォーメーション等の3列目（紐）に必ず強制配置せよ。

                【指示】
                上記の基準および総監督厳守ロジックを1つの思考に統合し、全頭を精密に診断せよ。
                出力は必ず以下のMarkdownテーブル形式で行うこと：
                | 馬番 | 馬名 | 単勝勝率(%) | 複勝勝率(%) | ダート砂適性 | 脚質 | 人気 | 評価 | 診断コメント（データ連動・下剋上穴馬に該当した場合はその理由を明記） |
                | --- | --- | --- | --- | --- | --- | --- | --- | --- |
                
                最後に、最も期待値の高い買い目（三連複フォーメーション、三連単等）を総監督への【投資指示書】として結論提示せよ。
                """
                
                response = model.generate_content(prompt)
                st.session_state["res"] = response.text
                
                # ログの自動保存
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(os.path.join(LOG_DIR, f"Race_{now}.txt"), "w", encoding="utf-8") as f:
                    f.write(response.text)
            
            st.rerun()
            
        except Exception as e: 
            st.error(f"解析エラー: {e}")

if "res" in st.session_state:
    st.markdown(st.session_state["res"])
