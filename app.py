import streamlit as st
import google.generativeai as genai
import json
import os

# --- 設定保存 ---
CONFIG_FILE = "baru_config.json"
def save_cfg(k, b):
    with open(CONFIG_FILE, "w") as f: json.dump({"k": k, "b": b}, f)
def load_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f: return json.load(f)
        except: pass
    return {"k": "", "b": ""}

cfg = load_cfg()
st.set_page_config(page_title="Baru AI v5.0", layout="wide")
st.title("🏇 Baru 競馬AI - 【下剋上・期待値ダブル軸版】")

def reset_data():
    st.session_state["data_input"] = ""

with st.sidebar:
    st.header("⚙️ 設定")
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 総監督バイアス", value=cfg.get("b", ""), height=150)
    if st.button("💾 保存"):
        save_cfg(api_key, bias)
        st.success("下剋上ロジック、リミッター解除。")

col1, col2 = st.columns([2, 1])
with col1:
    data = st.text_area("📋 レースデータ", height=550, key="data_input")
with col2:
    if st.button("🔥 下剋上・究極ジャッジ"):
        if not api_key or not data:
            st.error("入力不足です")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                prompt = f"""
                競馬AI総監督Baruとして、AIの「人気忖度」を捨て、以下の【下剋上ロジック】で結論を出せ。
                【データ】: {data}
                【バイアス】: {bias}
                
                1.★ダブル本命(W-AXIS): 
                   - 【◎実績軸】: 安定した実績馬
                   - 【★下剋上軸】: 勢い・期待値・爆穴の筆頭
                   この2頭を対等に扱い、どちらかが飛んでも成立する買い目を作れ。
                2.人気馬の死角探し: 1番人気が負ける理由を1つ見つけ、積極的に「▲」以下へ落とす勇気を持て。
                3.掲示板ハンター網羅: 地味だが堅実な馬を必ず△で拾い、3連複の網から漏らすな。
                4.全頭診断: 1行。馬番、馬名、そして「その馬が1着でゴールする時の展開」を具体的に書け。
                5.買い目: 
                   - ◎と★の2頭軸マルチ(馬連・ワイド)
                   - 3連複は「◎,★のいずれか1頭目」→「上位5頭」→「全流し」の強気フォーメーション。
                """
                
                with st.spinner("人気を疑い、期待値を最大化中..."):
                    res = model.generate_content(prompt)
                    st.success("✅ 解析完了。人気に日和らず、真の勝ち馬を指名しました。")
                    st.markdown("---")
                    st.markdown(res.text)
            except Exception as e:
                st.error(f"エラー: {e}")

    st.button("🧹 データをクリア", on_click=reset_data)

st.caption("Baru Stable AI System v5.0 - 人気忖度撤廃・期待値下剋上ロジック")
