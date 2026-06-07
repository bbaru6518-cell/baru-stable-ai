import streamlit as st
import google.generativeai as genai
import json
import os
import datetime

# --- 設定保存・ログ管理 ---
CONFIG_FILE = "baru_pro_config.json"
LOG_DIR = "win5_logs"
os.makedirs(LOG_DIR, exist_ok=True)

def save_cfg(k, b):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"k": k, "b": b}, f, ensure_ascii=False, indent=4)

def load_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "k": "",
        "b": "WIN5対象5レースのトラックバイアス、芝・ダートのキレ、走破タイム理論（基準タイム・馬場補正）、展開・ハナ争い、そして『ガチガチ本命レース』と『大荒れ混戦レース』のメリハリを統合解析せよ。"
    }

cfg = load_cfg()
st.set_page_config(page_title="Baru AI WIN5 Master v25", layout="wide")

# --- サイドバー：総監督WIN5司令部 ---
with st.sidebar:
    st.header("⚙️ 総監督WIN5司令部")
    
    st.success("🌐 現在の司令部アプリURL")
    st.write("https://baru-stable-ai-atmit7psqdxrey5mz823xs.streamlit.app/")
    
    st.divider()
    
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 総監督バイアス（5レース共通・個別指示）", value=cfg.get("b"), height=150)
    budget = st.number_input("WIN5総予算(円)", value=10000, step=1000)
    
    if st.button("💾 設定保存"):
        save_cfg(api_key, bias)
        st.success("戦略設定を保存しました。")

    st.divider()
    
    # 過去ログエリア
    st.header("📂 過去のWIN5戦略ログ")
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    if log_files:
        selected_log = st.selectbox("確認する過去のWIN5戦略", log_files)
        if st.button("📖 指示書を呼び出す"):
            with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
                st.session_state["res"] = f.read()
            st.rerun()
    else:
        st.info("ログはまだありません")

    st.divider()

    # レース結果照合
    st.header("🏁 レース結果の照合")
    st.text_area("WIN5結果のコピペ", height=150, key="result_input")
    if st.button("🚨 実際の的中・結果と照合"):
        st.info("解析結果との照合準備中...")

# --- メインエリア ---
st.title("🏇 WIN5戦略特化型マスター")

# セッション初期化
for i in range(1, 6):
    key = f"race{i}"
    if key not in st.session_state:
        st.session_state[key] = ""

# --- 5レース個別入力タブ ---
st.subheader("📋 WIN5対象 5レース個別データ入力")

tabs = st.tabs([
    "🏇 第1レース",
    "🏇 第2レース",
    "🏇 第3レース",
    "🏇 第4レース",
    "🏇 第5レース",
])

race_labels = ["第1レース", "第2レース", "第3レース", "第4レース", "第5レース"]

for i, tab in enumerate(tabs, start=1):
    with tab:
        key = f"race{i}"
        st.session_state[key] = st.text_area(
            f"✍️ {race_labels[i-1]}の出馬表・オッズ",
            value=st.session_state[key],
            height=300,
            key=f"input_{key}",
            placeholder=f"{race_labels[i-1]}の出馬表、オッズ、馬場状態などをコピペしてください",
        )

# 入力状況サマリー
st.divider()
filled = [i for i in range(1, 6) if st.session_state.get(f"race{i}", "").strip()]
empty  = [i for i in range(1, 6) if not st.session_state.get(f"race{i}", "").strip()]

col_status, col_btn = st.columns([2, 1])
with col_status:
    if filled:
        st.success(f"✅ 入力済み: 第{', 第'.join(map(str, filled))}レース")
    if empty:
        st.warning(f"⚠️ 未入力: 第{', 第'.join(map(str, empty))}レース")

with col_btn:
    run_btn = st.button("🚀 WIN5・5連勝鉄壁フォーメーション生成", type="primary", use_container_width=True)

# --- AI解析 ---
if run_btn:
    if not api_key:
        st.error("Gemini APIキーを入力してください")
    elif not filled:
        st.error("少なくとも1レース分のデータを入力してください")
    else:
        # データ結合
        combined = ""
        for i in range(1, 6):
            data = st.session_state.get(f"race{i}", "").strip()
            if data:
                combined += f"\n\n【{race_labels[i-1]}】\n{data}"
            else:
                combined += f"\n\n【{race_labels[i-1]}】\n（データなし）"

        prompt = f"""あなたはWIN5を完全攻略する最強の競馬AIだ。
WIN5とは【各レースの1着馬を5レース連続で当てる】馬券である。
2着・3着は一切関係ない。各レースで「1着になる馬」だけを予想せよ。

対象データ（レースごとに分離済み）:
{combined}

総監督バイアス: {bias}
予算: {budget}円

【出力指示】
1. 各レースの難易度ジャッジメント（テーブル形式：レース名・難易度・理由）

2. 各レースの展開・ハナ争いの核心（1着に直結する要素のみ）

3. 各レースの1着予想（以下の形式で出力）
   本命（1着本線）: 馬番・馬名
   対抗（1着対抗）: 馬番・馬名
   穴（1着穴）: 馬番・馬名（あれば）
   推奨点数: このレースで何点買うか

4. WIN5買い目まとめ（表形式）
   第1R〜第5Rそれぞれの1着候補馬番リストを記載
   例：第1R：1,3 / 第2R：5 / 第3R：2,7 / 第4R：4 / 第5R：1,6
   合計点数と予算{budget}円での1点あたり購入額を明記

※2着・3着の予想は不要。1着になる馬の選定に集中せよ。
"""

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash-lite")

            with st.spinner("🚀 WIN5多角マトリクス解析中..."):
                response = model.generate_content(prompt, generation_config={"max_output_tokens": 3000})
                st.session_state["res"] = response.text

                # ログ保存
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(os.path.join(LOG_DIR, f"WIN5_{now}.txt"), "w", encoding="utf-8") as f:
                    f.write(response.text)

        except Exception as e:
            st.error(f"解析エラー: {e}")

# --- 結果表示 ---
if "res" in st.session_state:
    st.divider()
    st.subheader("📊 WIN5最終投資指示書")
    st.markdown(st.session_state["res"])
