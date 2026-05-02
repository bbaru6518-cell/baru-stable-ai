import streamlit as st
import google.generativeai as genai
import json
import os
import requests
from bs4 import BeautifulSoup

# --- 設定保存機能 ---
CONFIG_FILE = "baru_pro_config.json"
def save_cfg(k, b):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"k": k, "b": b}, f)

def load_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"k": "", "b": "芝の決め手、血統適性、上がり3F、トラックバイアスを統合解析せよ。"}

cfg = load_cfg()
st.set_page_config(page_title="Baru AI Pro", layout="wide")
st.title("🏇 Baru 競馬AI Pro - 【調教スキャン・下剋上連動版】")

# --- スクレイピング関数 ---
def get_netkeiba_data(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")
        # 複数のテーブルやテキストを広範囲に取得するように強化
        main_data = soup.find_all("table")
        combined_text = ""
        for table in main_data:
            combined_text += table.get_text(separator="\n", strip=True) + "\n"
        return combined_text[:25000] # 調教データ含め多めに取得
    except Exception as e:
        return f"Error: {e}"

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 総監督バイアス", value=cfg.get("b"), height=200)
    budget = st.number_input("予算(円)", value=1000, step=100)
    if st.button("💾 設定保存"):
        save_cfg(api_key, bias)
        st.success("設定を保存しました。")

# --- メイン解析 ---
if "res" not in st.session_state:
    st.session_state["res"] = ""

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 データ・調教入力")
    url_input = st.text_input("🔗 URLを入力（調教タブURLも可）")
    manual_data = st.text_area("✍️ 貼り付け（調教タイム等もここへ）", height=400)
    
    if st.button("🚀 調教・フルスキャン解析開始"):
        target_data = ""
        if url_input:
            with st.spinner("データを抽出中..."):
                target_data = get_netkeiba_data(url_input)
        else:
            target_data = manual_data

        if not api_key or not target_data:
            st.error("APIキーとデータが必要です")
        else:
            try:
                genai.configure(api_key=api_key)
                # モデル自動選択（Pro優先）
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                m_name = next((x for x in available_models if "pro" in x), 
                             next((x for x in available_models if "flash" in x), 
                             available_models[0]))
                
                model = genai.GenerativeModel(m_name)
                prompt = f"""
                あなたは競馬AI総監督Baruの右腕だ。18頭フルゲートまで全頭を精密に解析せよ。
                
                【今回の重点解析：調教・追い切り】
                - 提供されたデータから「調教タイム」「追い切り評価」「脚色（馬なり・一杯）」を読み解け。
                - 終い重点の加速ラップや、併せ馬での先着、自己ベスト更新馬を「勝負気配」として高く評価せよ。
                
                【絶対ルール】
                1. 調教評価の高い穴馬は必ず「3. 下剋上」に指名し、最終結論（印）と買い目に100%含めること。
                2. 全頭短評に [単勝%/複勝%] を記載せよ。
                
                構成：
                1. 砂の王/芝の覇者 (血統・適性)
                2. 追い切り特注馬 (調教時計・動きからの抜粋)
                3. 下剋上・勝負気配 (展開＋調教で狙える穴馬)
                4. 全頭解析＆勝率予測 [単%/複%] (全頭点呼)
                5. 最終結論 (◎○▲△×)
                6. 🚀 1軸流し馬券(予算{budget}円)
                   - 【メイン】3連複 1軸流し
                   - 【厚め】◎から下剋上馬(×)へのワイドまたは馬連
                
                データ: {target_data}
                バイアス: {bias}
                """
                with st.spinner(f"エンジン {m_name} で調教スキャン中..."):
                    response = model.generate_content(prompt)
                    st.session_state["res"] = response.text
            except Exception as e:
                st.error(f"解析エラー: {e}")

with col2:
    st.subheader("📊 投資指示書")
    if st.session_state["res"]:
        st.markdown(st.session_state["res"])
    else:
        st.info("URLかテキストを入力して解析を開始してください。")

st.caption("Baru Stable AI Pro v12.8 - Training Scan Edition")
