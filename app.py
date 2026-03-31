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
st.title("🏇 Baru 競馬AI Pro - 【URL＆テキスト両対応版】")

# --- スクレイピング関数 (16頭以上・広告除去) ---
def get_netkeiba_data(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")
        # 広告を排除
        for ad in soup.find_all(class_=["rev_list", "ads_area", "p_ad", "taboola", "footer"]):
            ad.decompose()
        # メインテーブルを狙い撃ち
        main_data = soup.find("table", class_=["RaceTable01", "db_table"]) or soup.find("div", id="netkeiba_db") or soup
        text = main_data.get_text(separator="\n", strip=True)
        return text[:15000] # 15,000文字まで拡張（18頭立て対応）
    except Exception as e:
        return f"取得エラー: {e}"

# --- 状態管理 ---
if "res" not in st.session_state:
    st.session_state["res"] = ""

def clear_data():
    st.session_state["url_field"] = ""
    st.session_state["manual_field"] = ""
    st.session_state["res"] = ""

with st.sidebar:
    st.header("⚙️ 設定")
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 総監督バイアス", value=cfg.get("b", "地方の深い砂、小回り、内枠先行を最優先。"), height=150)
    budget = st.number_input("1レースの予算(円)", value=1000, step=100)
    if st.button("💾 設定保存"):
        save_cfg(api_key, bias)
        st.success("設定保存完了")
    
    st.divider()
    # データクリアボタン
    st.button("🧹 全データをクリア", on_click=clear_data)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 データ入力")
    url_input = st.text_input("🔗 netkeibaのURLを貼り付け", key="url_field")
    st.write("--- または ---")
    manual_data = st.text_area("✍️ 馬柱テキストを直接貼り付け", height=450, key="manual_field", placeholder="ここにコピーしたデータを貼り付け...")
    
    if st.button("🚀 解析スタート"):
        # URLがあれば優先、なければテキストを使う
        target_data = ""
        if url_input:
            with st.spinner("URLから全頭データを抽出中..."):
                target_data = get_netkeiba_data(url_input)
        else:
            target_data = manual_data

        if not api_key or not target_data:
            st.error("APIキーとデータが必要です")
        else:
            try:
                genai.configure(api_key=api_key)
                ms = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model_name = next((x for x in ms if "flash" in x), ms[0])
                
                model = genai.GenerativeModel(model_name)
                prompt = f"""
                あなたは競馬AI総監督Baruの右腕だ。
                【絶対厳守】12番以降の馬もデータにあれば必ず解析せよ。馬名は一文字も変えるな。
                構成：
                1. 砂の王/芝の覇者 (適性NO.1)
                2. 先行優位ジャッジ
                3. 下剋上・勝負気配
                4. 全頭短評 (1番から全頭もれなく書け)
                5. 最終結論: ◎○▲△×
                6. 資金配分: 予算{budget}円の投資指示
                
                データ: {target_data}
                バイアス: {bias}
                """
                with st.spinner("全頭スキャン中..."):
                    response = model.generate_content(prompt)
                    st.session_state["res"] = response.text
            except Exception as e:
                st.error(f"解析エラー: {e}")

with col2:
    st.subheader("📊 投資指示書")
    if st.session_state["res"]:
        st.markdown(st.session_state["res"])

st.caption("Baru Stable AI Pro v11.0 - Full Visibility Edition")
