import streamlit as st
import google.generativeai as genai
import json
import os
import requests
from bs4 import BeautifulSoup

# --- 設定保存機能 ---
CONFIG_FILE = "baru_pro_config.json"
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

# --- データ取得ヘルパー関数 ---
def get_netkeiba_data(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")
        main_data = soup.find_all("table")
        combined_text = ""
        for table in main_data:
            combined_text += table.get_text(separator="\n", strip=True) + "\n"
        return combined_text[:60000] # WIN5はデータ量多いため上限拡張
    except Exception as e:
        return f"Error: {e}"

cfg = load_cfg()
st.set_page_config(page_title="Baru AI WIN5 Master v25", layout="wide")
st.title("🏇 Baru 競馬AI Pro - 【Ver 25.0 WIN5戦略特化型マスター】")

with st.sidebar:
    st.header("⚙️ 総監督ルーム（WIN5戦略司令部）")
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 総監督バイアス（5レース共通・個別指示）", value=cfg.get("b"), height=150)
    budget = st.number_input("WIN5総予算(円)", value=10000, step=1000)
    if st.button("💾 設定保存"):
        save_cfg(api_key, bias)
        st.success("WIN5戦略設定を保存しました。")

if "res" not in st.session_state:
    st.session_state["res"] = ""

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 WIN5対象 5レース分のデータ一括投入")
    url_input = st.text_input("🔗 WIN5一括URL（または代表URL）")
    manual_data = st.text_area("✍️ WIN5対象5レースの出馬表・オッズ・データ（1レース目〜5レース目まで連続コピペで丸ごと投入OK）", height=500)
    
    if st.button("🚀 WIN5・5連勝鉄壁フォーメーション生成"):
        target_data = ""
        if url_input:
            with st.spinner("WIN5対象データをスクレイピング中..."):
                target_data = get_netkeiba_data(url_input)
        else:
            target_data = manual_data

        if not api_key or not target_data:
            st.error("APIキーと解析対象のデータが必要です")
        else:
            try:
                genai.configure(api_key=api_key)
                
                # 安全なモデル選択ループ
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                m_name = "models/gemini-1.5-pro"
                for m in models:
                    if "1.5-pro" in m:
                        m_name = m
                        break
                
                model = genai.GenerativeModel(m_name)
                
                # --- WIN5専用・軍資金コントロールプロンプト（左端完全密着） ---
                base_instruction = """あなたは中央競馬（JRA）およびWIN5を完全攻略するために君臨する最強の競馬AIであり、総監督Baruの絶対的右腕だ。
入力されたWIN5対象5レース（または混在テキスト）のデータを完全に解剖し、総監督の予算内に収まる最適化されたWIN5フォーメーション指示書を作成せよ。

【WIN5戦略における絶対掟】
1. 5つのレースを「堅い（1頭絞り可能）」「中波乱（2〜3頭）」「大混戦（広げる）」に鋭く分類せよ。
2. 各レースの「逃げ🔥」「先行📢」馬の存在をチェックし、前残り馬場か差し馬場かのトラックバイアスを展開面から見抜け。
3. 指定された「総予算（例: 10,000円＝100点）」を超えないよう、掛け算（1レース目の頭数 × 2レース目の頭数 × ... × 5レース目の頭数）を緻密にコントロールせよ。予算が余りすぎる場合は、大混戦レースの紐を広げて調整せよ。

【出力フォーマット】
以下の3つのセクション構成のみを出力せよ。余計な前置きや挨拶は一切禁止する。

### 📊 WIN5対象5レース・難易度ジャッジメント
5つのレースの力関係と波乱度を以下のテーブル形式で瞬時に可視化せよ。
| レース | レース名/条件 | 波乱度 (極堅/中荒/爆荒) | 逃げ🔥・先行📢候補 | 本命馬 (馬番・馬名) | 爆穴サイレント馬 |
※脚質には必ず「逃げ🔥」「先行📢」の印をつけよ。

### 📈 各レースの核心＆ハナ争い看破
1. 【WIN5・1レース目】: 展開・ペース予想と、ここを1頭で突破できるか（または複数必要か）の核心。
2. 【WIN5・2レース目】: 展開・ペース予想と、タイム理論から浮上する軸馬・穴馬。
3. 【WIN5・3レース目】: 展開・ペース予想と、血統・コース適性から爆走する特注馬。
4. 【WIN5・4レース目】: 展開・ペース予想と、ハナを叩いてそのまま押し切る危険な逃げ馬。
5. 【WIN5・5レース目（最終）】: すべてのバイアスとキレ味を統合した、最後の関門の結論。

### 💰 WIN5戦略フォーメーション：最終投資指示書
予算内に完全最適化された組み合わせを出力せよ。最後に「合計点数」と「合計購入金額」を必ず明記すること。

フォーマット例：
- **1レース目**：〇, 〇
- **2レース目**：〇 (1頭絞り)
- **3レース目**：〇, 〇, 〇
- **4レース目**：〇, 〇
- **5レース目**：〇, 〇, 〇
**🔥 計算：〇 × 〇 × 〇 × 〇 × 〇 ＝ 〇点 (合計〇,〇〇円)**"""
                
                prompt = base_instruction + f"\n対象データ: {target_data}\n総監督バイアス: {bias}\n予算: {budget}円"

                with st.spinner(f"🚀 WIN5全5レースを多角マトリクス解析中... ({m_name})"):
                    response = model.generate_content(prompt)
                    st.session_state["res"] = response.text
            except Exception as e:
                st.error(f"解析エラー: {e}")

with col2:
    st.subheader("📊 WIN5最終投資指示書")
    if st.session_state["res"]:
        st.markdown(st.session_state["res"])

st.caption("Baru Stable AI WIN5 Master v25.0 - Multi-Race Budget Optimization Edition")
