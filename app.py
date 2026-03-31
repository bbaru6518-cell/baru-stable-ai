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
st.set_page_config(page_title="Baru 競馬AI Pro 18", layout="wide")
st.title("🏇 Baru 競馬AI Pro - 【中央18頭フルゲート完全対応】")

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

# --- 状態管理 ---
if "res" not in st.session_state:
    st.session_state["res"] = ""

def clear_data():
    st.session_state["url_field"] = ""
    st.session_state["manual_field"] = ""
    st.session_state["res"] = ""

with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 総監督バイアス", value=cfg.get("b", "芝の決め手、血統適性、上がり3F、トラックバイアスを統合解析せよ。"), height=150)
    budget = st.number_input("1レースの予算(円)", value=1000, step=100)
    if st.button("💾 設定を保存"):
        save_cfg(api_key, bias)
        st.success("設定を保存しました。")
    
    st.divider()
    st.button("🧹 全データをクリア", on_click=clear_data)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 18頭データ入力")
    url_input = st.text_input("🔗 netkeiba PC版URL", key="url_field")
    st.write("--- または ---")
    manual_data = st.text_area("✍️ 18頭分の馬柱をコピペ", height=500, key="manual_field", placeholder="PC版の出馬表をガバッと貼ってください...")
    
    if st.button("🚀 18頭フルスキャン開始"):
        target_data = ""
        if url_input:
            with st.spinner("PC版サイトから全18頭を抽出中..."):
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
                # 18頭を絶対に飛ばさないための「鉄の掟」プロンプト
                prompt = f"""
                あなたは競馬AI総監督Baruの右腕だ。中央競馬18頭フルゲートに対応せよ。
                
                【絶対厳守ルール】
                1. 馬柱から「血統(父/母父)」「走破タイム」「上がり3F」「通過順」「トラックバイアス」を多角的に抽出せよ。
                2. 全頭短評は「1番から18番まで」番号順に、一頭も飛ばさず、一文字も馬名を変えずに出力せよ。
                3. 下剋上候補は「近走不振でも上がり3Fが上位」の馬を必ず1〜2頭ピックアップせよ。
                
                構成：
                1. 芝の覇者/砂の王 (血統・適性NO.1)
                2. 先行優位ジャッジ (展開・トラックバイアス)
                3. 下剋上・勝負気配 (上がり最速ポテンシャル馬)
                4. 全頭短評 (1〜18番まで全頭点呼)
                5. 最終結論 (◎○▲△×)
                6. 投資指示書 (予算{budget}円の最適配分)
                
                データ: {target_data}
                バイアス: {bias}
                """
                with st.spinner("18頭の血統・展開・走破データを統合解析中..."):
                    response = model.generate_content(prompt)
                    st.session_state["res"] = response.text
            except Exception as e:
                st.error(f"解析エラー: {e}")

with col2:
    st.subheader("📊 18頭・投資指示書")
    if st.session_state["res"]:
        st.markdown(st.session_state["res"])

st.caption("Baru Stable AI Pro v12.0 - Full Gate 18 Edition")
