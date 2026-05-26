import streamlit as st
import google.generativeai as genai
import os
import json
import datetime

# --- 設定・ディレクトリ ---
LOG_DIR = "racing_logs_standard"
CONFIG_FILE = "baru_pro_config.json"
os.makedirs(LOG_DIR, exist_ok=True)

# 設定保存・読込
def save_cfg(k, b):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"k": k, "b": b}, f, ensure_ascii=False, indent=4)

def load_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"k": "", "b": "トラックバイアス、高速馬場適性、上がり3F、展開・ハナ争いを統合解析せよ。"}

cfg = load_cfg()
st.set_page_config(page_title="Baru AI Pro", layout="wide", initial_sidebar_state="expanded")

# --- サイドバー：全機能搭載 ---
with st.sidebar:
    st.header("⚙️ 総監督ルーム")
    api_key = st.text_input("Gemini API KEY", value=cfg.get("k", ""), type="password")
    bias = st.text_area("🧠 バイアス補正", value=cfg.get("b"), height=100)
    if st.button("💾 設定保存"):
        save_cfg(api_key, bias)
        st.success("設定を保存しました。")

    st.markdown("---")
    st.header("📂 過去ログ・結果復習ルーム")
    log_files = sorted([f for f in os.listdir(LOG_DIR) if f.endswith(".txt")], reverse=True)
    if log_files:
        selected_log = st.selectbox("確認する過去ログ", log_files)
        if st.button("📖 予想を呼び出す"):
            with open(os.path.join(LOG_DIR, selected_log), "r", encoding="utf-8") as f:
                st.session_state["res"] = f.read()
            st.rerun()

    st.markdown("---")
    st.header("🏁 結果コピペ・猛省")
    result_copypaste = st.text_area("レース結果をコピペ", height=150)
    if st.button("🚨 照合して猛省レポート"):
        if "res" in st.session_state and result_copypaste:
            st.warning("猛省レポート生成中...")
            st.rerun()

# --- メインエリア：全頭精密診断 ---
st.title("🏇 Baru 競馬AI Pro - 最終完全版")
manual_data = st.text_area("✍️ 馬柱・オッズデータを貼り付け", height=300)

if st.button("🚀 構造解剖・全頭精密診断と3連複15点出力"):
    if not api_key:
        st.error("APIキーを入力してください")
    else:
        try:
            with st.spinner("接続先を探索し、精密解析中..."):
                genai.configure(api_key=api_key)
                # 利用可能なモデルを自動取得して接続エラーを回避
                models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(models[0].name)
                
                prompt = f"""
                【全頭精密診断】
                データ: {manual_data}
                バイアス: {bias}
                
                指示:
                1. 各馬を精密に診断しMarkdownテーブルで出力せよ。
                   カラム: | 馬番 | 馬名 | 父 | 母 | ダート適性 | 脚質 | 人気 | 評価 | 理由 |
                2. 【3連複15点フォーメーション】を以下の形式で出力せよ。
                   ・1列目(軸): ◎ 1頭
                   ・2列目(相手): ○, ▲ 2頭
                   ・3列目(紐): ◎, ○, ▲, △, 注 計5頭
                """
                response = model.generate_content(prompt)
                st.session_state["res"] = response.text
                
                # 自動ログ保存
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(os.path.join(LOG_DIR, f"Race_{now}.txt"), "w", encoding="utf-8") as f:
                    f.write(response.text)
                st.rerun()
        except Exception as e:
            st.error(f"接続エラー: {e}")
            st.info("💡 ヒント: APIキーとGoogle AI Studioのプロジェクト設定を確認してください。")

# 結果表示エリア
if "res" in st.session_state:
    st.markdown(st.session_state["res"])
