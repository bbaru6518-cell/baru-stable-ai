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
        "b": "JRA（中央競馬）の高速馬場・トラックバイアス、芝・ダートのキレ、血統適性（スピード・持続力）、上がり3Fを統合解析せよ。"
    }

cfg = load_cfg()
st.set_page_config(page_title="Baru JRA AI Pro", layout="wide")
st.title("🏇 Baru 競馬AI Pro - 【JRA中央・血統適性＆15点極限絞り込み版】")

def get_netkeiba_data(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, headers=headers)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")
        main_data = soup.find_all("table")
        combined_text = ""
        for table in main_data:
            combined_text += table.get_text(separator="\n", strip=True) + "\n"
        return combined_text[:40000] # 中央競馬の膨大なデータ量に対応して上限を拡張
    except Exception as e:
        return f"Error: {e}"

with st.sidebar:
    st.header("⚙️ 総監督ルーム（JRA特化）")
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 総監督バイアス（JRA馬場・展開）", value=cfg.get("b"), height=150)
    budget = st.number_input("予算(円)", value=1500, step=100)
    if st.button("💾 設定保存"):
        save_cfg(api_key, bias)
        st.success("JRA特化設定を保存しました。")

if "res" not in st.session_state:
    st.session_state["res"] = ""

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 JRAデータ・調教・コピペ入力")
    url_input = st.text_input("🔗 netkeiba等のJRAレースURL（出馬表・調教・厩舎）")
    manual_data = st.text_area("✍️ スマホ画面からのコピペデータ（不整形・ズレデータもそのまま可）", height=450)
    
    if st.button("🚀 JRA精密血統スキャン・15点投資解析開始"):
        target_data = ""
        if url_input:
            with st.spinner("JRAレースデータをスクレイピング中..."):
                target_data = get_netkeiba_data(url_input)
        else:
            target_data = manual_data

        if not api_key or not target_data:
            st.error("APIキーとレースデータ（またはURL）が必要です")
        else:
            try:
                genai.configure(api_key=api_key)
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # 最もパース能力の高い高性能モデルを自動選択
                m_name = next((x for x in models if "1.5-pro" in x), 
                             next((x for x in models if "pro" in x), 
                             models[0]))
                
                model = genai.GenerativeModel(m_name)
                
                # --- LLM側にパースとフォーマットを完全強制するプロンプト ---
                prompt = f"""
                あなたは中央競馬（JRA）解析のプロフェッショナルであり、競馬AI総監督Baruの右腕だ。
                入力されたJRAのデータ（不整形、数字の混入、行ズレ含む）から、正確に馬名・血統・人気を識別し、軸馬選定ミスを撲滅せよ。

                【解析における絶対掟】
                1. 入力データに「15129」や「547815」のようなスピード指数・馬体重等の大きな数字が混ざっていても、それを馬番と誤認するな。本来の「正しい馬番（1〜18）」をデータから超精密にパースせよ。
                2. 「ロードカナロア」「モーリス」「エピファネイア」「ハービンジャー」等の有名な種牡馬名が「馬名」の欄に入り込むバグを徹底的に排除せよ。これらは「父」である。真の馬名をデータから執念深く抜き出せ。
                3. 出走取消の馬（例: オタルグリーン等）がある場合は、評価を「消」とし、理由に【出走取消】と明記せよ。

                【出力フォーマット】
                以下の構成のみを出力し、余計な前置きは一切書くな。

                ### 📊 全頭精密診断・血統適性リスト
                必ず以下の列を持つMarkdownテーブル形式で全頭出力せよ。
                | 馬番 | 馬名 | 父 | 母 | 血統適性 | 人気 | 評価 | 理由 |
                ※血統適性は、父や母の系統から「【A】高速・瞬発型」「【B】持続・スタミナ型」「【C】洋芝・パワー型」「ダート型」等で分類せよ。
                ※評価は（◎、○、▲、△、注、消）で厳選。

                ### 💰 三連複フォーメーション：厳選15点指示書
                ガミりを防ぎ投資効率を最大化するため、以下のロジックで【合計15点】になるフォーメーション案を必ず生成せよ。
                - 1頭目（軸馬）：◎（1頭）
                - 2頭目（対抗）：○や▲から「厳選した2頭」のみを指定
                - 3頭目（紐・穴）：◎、○、▲、△、注を含めた「合計7頭」を指定（15番等の穴馬や爆弾馬は必ずここに滑り込ませろ）
                ※計算式：1頭×2頭×(7頭 - 2頭) ＝ 【15点】に完全固定。

                フォーマット例：
                **◎ 軸馬: 〇番 (馬名)**
                - **1頭目：** [軸馬の番号]
                - **2頭目：** [2頭の番号]
                - **3頭目：** [7頭の番号]
                ```text
                1頭目：〇
                2頭目：〇, 〇
                3頭目：〇, 〇, 〇, 〇, 〇, 〇, 〇
                ```

                JRAデータ: {target_data}
                総監督バイアス: {bias}
                予算: {budget}円
                """
                
                with st.spinner(f"🚀 JRA特化エンジン {m_name} が血統・データをパース中..."):
                    response = model.generate_content(prompt)
                    st.session_state["res"] = response.text
            except Exception as e:
                st.error(f"解析エラー: {e}")

with col2:
    st.subheader("📊 投資指示書")
    if st.session_state["res"]:
        st.markdown(st.session_state["res"])

st.caption("Baru Stable JRA AI Pro v22.0 - Genealogy & 15-Point Precision Edition")
