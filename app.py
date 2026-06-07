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

    # 過去ログ
    st.header("📂 過去ログ・結果復習ルーム")
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    if log_files:
        selected_log = st.selectbox("復習・確認する過去の予想", log_files)
        if st.button("📖 予想指示書を呼び出す"):
            with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
                st.session_state["res"] = f.read()
            st.rerun()
    else:
        st.info("ログはまだありません")

    st.divider()

    # 結果照合
    st.header("🏁 レース結果のコピペ投入")
    st.caption("💡 1行目にレース名を入力し、2行目から結果を丸ごとコピペしてください！")
    race_result_input = st.text_area("1行目：レース名 / 2行目～：結果コピペ", height=200)

    if st.button("🚨 実際の着順・ハナ争いと照合して復習"):
        if not api_key:
            st.error("APIキーを入力してください")
        elif not race_result_input:
            st.error("結果データをコピペしてください")
        elif "res" not in st.session_state:
            st.error("まず予想を実行してください")
        else:
            try:
                with st.spinner("実際のレース結果と照合し、反省会を実施中..."):
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.5-flash-lite")

                    review_prompt = f"""
【総監督からの命令：レース結果の答え合わせと徹底反省】

あなたが先ほど出力した【予想指示書】と、実際に発生した【レース結果・着順】を照合し、以下の基準で猛反省（回顧）を行え。

1. 軸馬（◎, ○, ▲）の成否
   - 軸に据えた馬は馬券圏内（3着以内）にきたか？
   - netkeibaの「データ上位馬3頭」の信頼度はどうだったか？

2. 「死んだふり下剋上穴馬」の生存確認
   - あなたが「上がり最速爆弾馬」や「激走警戒馬（注）」として救済・指名した不人気馬の実際の着順・上がり3Fを確認せよ。
   - 実際に激走したか？凡走した場合、展開やトラックバイアスがどう影響したか推測せよ。

3. 展開・ハナ争いの答え合わせ
   - 事前に想定したハナ争いやペースは、実際の展開と一致していたか？

【提出された現在の予想指示書】
{st.session_state["res"]}

【実際のレース結果（コピペデータ）】
{race_result_input}

【出力フォーマット】
### 🏁 {race_result_input.splitlines()[0] if race_result_input.splitlines() else '対象レース'} - 統合反省レポート
- **総合評価**: （例：大的中 / 軸は合致も紐抜け / 展開不一致による大敗 など）

#### 📊 着順答え合わせ
| 印 | 馬名 | 事前評価 | 実際の着順 | 上がり3F（結果） | 反省・要因分析 |

#### 🧠 次回に向けたロジック修正点（総監督への進言）
- （次回以降プロンプトで微調整すべき教訓を箇条書きで書くこと）
"""
                    response = model.generate_content(review_prompt, generation_config={"max_output_tokens": 2000})
                    st.session_state["res"] = response.text
                st.rerun()
            except Exception as e:
                st.error(f"反省解析エラー: {e}")

    st.divider()

# ============================================================
# --- メインエリア ---
# ============================================================
st.title("🏇 Baru 競馬AI Pro - 統合解析司令部")

# --- 開催地設定 ---
st.subheader("🏟️ 開催地・レース入力")

col_venue, col_add = st.columns([3, 1])
with col_venue:
    st.caption("開催地名を入力してください（例：東京、阪神、中京）")
with col_add:
    pass

# セッション初期化
if "venues" not in st.session_state:
    st.session_state["venues"] = ["東京", "阪神"]
if "race_data" not in st.session_state:
    st.session_state["race_data"] = {}  # {venue_idx: {race_num: text}}

# 開催地追加・削除
col_v1, col_v2, col_v3 = st.columns([1, 1, 4])
with col_v1:
    if st.button("➕ 開催地を追加", use_container_width=True):
        if len(st.session_state["venues"]) < 5:
            st.session_state["venues"].append(f"開催地{len(st.session_state['venues'])+1}")
            st.rerun()
with col_v2:
    if st.button("➖ 開催地を削除", use_container_width=True):
        if len(st.session_state["venues"]) > 1:
            removed = st.session_state["venues"].pop()
            st.rerun()

# 開催地名入力
venue_cols = st.columns(len(st.session_state["venues"]))
for idx, col in enumerate(venue_cols):
    with col:
        new_name = st.text_input(
            f"開催地{idx+1}",
            value=st.session_state["venues"][idx],
            key=f"venue_name_{idx}"
        )
        st.session_state["venues"][idx] = new_name

st.divider()

# --- レースデータ入力（開催地タブ × 12Rタブ）---
venue_tabs = st.tabs([f"🏟️ {v}" for v in st.session_state["venues"]])

for v_idx, v_tab in enumerate(venue_tabs):
    with v_tab:
        venue_name = st.session_state["venues"][v_idx]
        if v_idx not in st.session_state["race_data"]:
            st.session_state["race_data"][v_idx] = {}

        race_tabs = st.tabs([f"{r}R" for r in range(1, 13)])
        for r_idx, r_tab in enumerate(race_tabs):
            race_num = r_idx + 1
            with r_tab:
                key = f"race_{v_idx}_{race_num}"
                current_val = st.session_state["race_data"][v_idx].get(race_num, "")
                new_val = st.text_area(
                    f"✍️ {venue_name} {race_num}R の馬柱・オッズ（空欄でスキップ）",
                    value=current_val,
                    height=300,
                    key=key,
                    placeholder=f"{venue_name} {race_num}Rの出馬表、オッズ、netkeiba分析データをコピペしてください",
                )
                st.session_state["race_data"][v_idx][race_num] = new_val

st.divider()

# --- 入力状況サマリー & 解析ボタン ---
filled_races = []
for v_idx, venue in enumerate(st.session_state["venues"]):
    for r in range(1, 13):
        val = st.session_state["race_data"].get(v_idx, {}).get(r, "")
        if val.strip():
            filled_races.append(f"{venue} {r}R")

col_status, col_btn = st.columns([3, 1])
with col_status:
    if filled_races:
        st.success(f"✅ 入力済み {len(filled_races)}レース: {' / '.join(filled_races)}")
    else:
        st.info("入力済みのレースはありません")

with col_btn:
    run_btn = st.button("🚀 統合解析実行", type="primary", use_container_width=True)

# --- AI解析 ---
if run_btn:
    if not api_key:
        st.error("APIキーを入力してください")
    elif not filled_races:
        st.error("少なくとも1レース分のデータを入力してください")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash-lite")

            base_prompt = """
【統合解析基準】
- JRAおよび地方競馬の高速馬場・トラックバイアス、芝・ダートのキレ、走破タイム理論（基準タイム・馬場補正）、上がり3F、展開・ハナ争いを統合解析せよ。

【⚙️ 総監督絶対厳守ロジック：netkeibaデータ傾向スクリーニング】
1. 投入されたデータ内に「データ上位馬3頭」というセクションがある場合、そこに名前がある馬はクラス・条件への地力高いと判断し、軸馬・相手筆頭（◎, 〇, ▲）の最有力候補として評価パラメータを大きく加算せよ。
2. データ内の「今回の馬場状態が得意な馬」「今回のレース間隔で実績がある馬」「この競馬場が得意な馬」のいずれかに該当する不人気馬（単勝5番人気以下）は、近走成績が悪くても必ず【穴候補・紐（△または注）】として救済・格納せよ。

【⚙️ 総監督絶対厳守ロジック：死んだふり下剋上馬（上がり最速爆弾）の検知】
以下の激走ファクターを満たす伏兵馬は展開がハマった瞬間に下剋上を起こす爆弾馬として自動検知せよ。
- 条件A：過去2〜3走以内に「上がり3Fタイムがメンバー中1位または2位」の隠れた末脚実績がある馬。
- 条件B：前走が短い距離で大敗しており、今回スタミナが問われる長距離（1800m〜2000m以上）へ大幅に距離延長してきた馬。
- 上記に該当する馬は激走警戒馬（注）として評価し、3連複フォーメーション等の3列目（紐）に必ず強制配置せよ。

【指示】
以下の1レース分のデータのみを解析せよ。他のレースのデータは存在しない。
上記基準を統合して全頭を精密に診断し、以下のMarkdownテーブル形式で出力すること：

| 馬番 | 馬名 | 単勝勝率(%) | 複勝勝率(%) | ダート砂適性 | 脚質 | 人気 | 評価 | 診断コメント |

最後に買い目（三連複フォーメーション等）を総監督への【投資指示書】として結論提示せよ。
"""

            results = {}  # {label: result_text}
            total = len(filled_races)

            progress_bar = st.progress(0, text=f"0 / {total} レース解析中...")

            for i, (v_idx, venue, r) in enumerate([
                (v_idx, venue, r)
                for v_idx, venue in enumerate(st.session_state["venues"])
                for r in range(1, 13)
                if st.session_state["race_data"].get(v_idx, {}).get(r, "").strip()
            ]):
                label = f"{venue} {r}R"
                val = st.session_state["race_data"][v_idx][r].strip()
                prompt = f"【{label} の馬柱・オッズデータ】\n{val}\n\n{base_prompt}"
                progress_bar.progress((i) / total, text=f"{i + 1} / {total} : {label} 解析中...")
                response = model.generate_content(prompt, generation_config={"max_output_tokens": 3000})
                results[label] = response.text

            progress_bar.progress(1.0, text=f"✅ {total}レース 解析完了！")
            st.session_state["results_per_race"] = results
            st.session_state["res"] = "\n\n".join(
                [f"### 🏇 {lbl} 解析結果\n{txt}" for lbl, txt in results.items()]
            )

            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(os.path.join(LOG_DIR, f"Race_{now}.txt"), "w", encoding="utf-8") as f:
                f.write(st.session_state["res"])

            st.rerun()
        except Exception as e:
            st.error(f"解析エラー: {e}")

# --- 結果表示（レースごとにタブ分割）---
if "results_per_race" in st.session_state and st.session_state["results_per_race"]:
    st.divider()
    st.subheader("📊 統合解析結果")
    race_labels = list(st.session_state["results_per_race"].keys())
    if len(race_labels) == 1:
        st.markdown(f"### 🏇 {race_labels[0]} 解析結果")
        st.markdown(st.session_state["results_per_race"][race_labels[0]])
    else:
        result_tabs = st.tabs([f"🏇 {lbl}" for lbl in race_labels])
        for tab, lbl in zip(result_tabs, race_labels):
            with tab:
                st.markdown(st.session_state["results_per_race"][lbl])
elif "res" in st.session_state and st.session_state["res"]:
    # 過去ログ呼び出し時のフォールバック表示
    st.divider()
    st.subheader("📊 統合解析結果")
    st.markdown(st.session_state["res"])
