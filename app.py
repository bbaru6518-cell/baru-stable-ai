import streamlit as st
import google.generativeai as genai
import json
import os
import requests
from bs4 import BeautifulSoup

# --- 設定保存 ---
CONFIG_FILE = "baru_pro_config.json"
def save_cfg(k, b):
    with open(CONFIG_FILE, "w") as f: json.dump({"k": k, "b": b}, f)
def load_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f: return json.load(f)
        except: pass
    return {"k": "", "b": ""}

cfg = load_cfg()
st.set_page_config(page_title="Baru 競馬AI Pro", layout="wide")
st.title("🏇 Baru 競馬AI Pro - 【URL解析・馬名厳守版】")

# --- スクレイピング関数 (文字化け対策済み) ---
def get_netkeiba_data(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers)
        res.encoding = res.apparent_encoding # 文字コード自動判別
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 不要なタグを削除して軽量化
        for s in soup(['script', 'style']): s.decompose()
        
        # 出馬表メイン部分を狙い撃ち
        main_data = soup.find("table", class_="db_table") or soup.find("div", class_="RaceTableArea") or soup
        text = main_data.get_text(separator="\n", strip=True)
        return text[:7000] # トークン節約のためカット
    except Exception as e:
        return f"取得エラー: {e}"

with st.sidebar:
    st.header("⚙️ 設定")
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 総監督バイアス", value=cfg.get("b", "地方の深い砂、小回り、内枠先行を最優先。"), height=150)
    budget = st.number_input("1レースの予算(円)", value=1000, step=100)
    if st.button("💾 保存"):
        save_cfg(api_key, bias)
        st.success("設定を保存しました。")

col1, col2 = st.columns([1, 1])

with col1:
    url_input = st.text_input("🔗 netkeibaのレースURLを貼り付け")
    if st.button("🚀 URLから解析開始"):
        if not api_key or not url_input:
            st.error("キーとURLが必要です")
        else:
            with st.spinner("砂のデータを抽出中..."):
                target_data = get_netkeiba_data(url_input)
                
                try:
                    genai.configure(api_key=api_key)
                    # 利用可能なモデルを自動取得
                    ms = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model_name = next((x for x in ms if "flash" in x), ms[0])
                    
                    model = genai.GenerativeModel(model_name)
                    prompt = f"""
                    あなたは競馬AI総監督Baruの右腕だ。
                    【絶対ルール】馬名は提供されたデータにあるもののみを使用せよ。勝手に名馬の名前に置き換えるな。
                    
                    以下の構成で出力せよ：
                    1. 砂の王 (POWER-AXIS): 砂適性NO.1の馬
                    2. 先行優位ジャッジ: 展開の鍵を握る馬
                    3. 下剋上・勝負気配: 期待値の高い穴馬
                    4. 全頭短評: 全馬の「買い/消し」理由
                    5. 最終結論: ◎○▲△×の印
                    6. 資金配分: 予算{budget}円を三連単・馬単に最適配分せよ。
                    
                    データ: {target_data}
                    バイアス: {bias}
                    """
                    
                    response = model.generate_content(prompt)
                    st.session_state["res"] = response.text
                except Exception as e:
                    st.error(f"解析エラー: {e}")

with col2:
    st.subheader("📊 投資指示書")
    if "res" in st.session_state:
        st.markdown(st.session_state["res"])

st.caption("Baru Stable AI Pro v10.0")
