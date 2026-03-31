import streamlit as st
import google.generativeai as genai
import json
import os
import requests
from bs4 import BeautifulSoup

# --- 設定保存機能 ---
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
st.set_page_config(page_title="Baru 競馬AI Pro 18", layout="wide")
st.title("🏇 Baru 競馬AI Pro - 【18頭フルゲート・1軸4頭流し対応】")

# --- スクレイピング関数 (18頭・全成績データ対応) ---
def get_netkeiba_data(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 広告・不要セクションの徹底排除
        for ad in soup.find_all(class_=["rev_list", "ads_area", "p_ad", "taboola", "footer", "common_ad"]):
            ad.decompose()
            
        # メインデータ部分を抽出
        main_data = soup.find("table", class_=["RaceTable01", "db_table"]) or soup.find("div", id="netkeiba_db") or soup
        text = main_data.get_text(separator="\n", strip=True)
        
        # 18頭の全過去成績を含めても余裕を持てるよう20,000文字まで拡張
        return text[:20000]
    except Exception as e:
        return f"取得エラー: {e}"

# --- セッション状態の初期化 ---
if "res" not in st.session_state:
    st.session_state["res"] = ""

def clear_all():
    st.session_state["url_field"] = ""
    st.session_state["manual_field"] = ""
    st.session_state["res"] = ""

# --- サイドバー：総監督ルーム ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 総監督バイアス", value=cfg.get("b", "芝の決め手、血統適性、上がり3F
