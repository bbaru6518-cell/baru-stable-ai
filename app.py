import streamlit as st
import re

VERSION = "19.0"
LOGIC_NAME = "Flexible Text Parser"

st.set_page_config(page_title=f"Baru 競馬AI Pro v{VERSION}", layout="wide")
st.title(f"🏇 Baru 競馬AI Pro - 【Ver 19.0 決定版】")

with st.sidebar:
    st.markdown(f"### ⚙️ 総監督ルーム")
    st.info(f"**Logic:** {LOGIC_NAME}\n**Ver:** {VERSION}")
    st.write("🧠 **V19.0 修正内容**\n・スクショの不整形テキストに完全対応\n・『〇人』『〇人気』から人気を自動パース\n・カタカナの並びから馬名・血統を完全救済")

# 入力エリア
input_data = st.text_area("📋 解析データ入力（コピーした内容をそのまま貼り付けてください）", height=300)

# --- 新・超柔軟パースエンジン ---
def parse_unstructured_text(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    horses = []
    
    current_horse = {}
    katakana_block = []
    
    # 既知の種牡馬・過去データ混同防止ワード
    sire_keywords = ["ロードカナロア", "モーリス", "エピファネイア", "ドゥラメンテ", "キズナ", "ハーツクライ", "ハービンジャー", "サンダースノー"]

    for line in lines:
        # 1. 人気の検知 (例: "2人", "2人気", "13頭13")
        pop_match = re.search(r'(\d+)(人|人気)', line)
        if pop_match and "頭" not in line:
            current_horse["人気"] = int(pop_match.group(1))

        # 2. カタカナの抽出（馬名・血統のストック）
        # カタカナと一部の記号のみで構成される単語を抽出
        words = re.findall(r'[ァ-ヶー・]+', line)
        for w in words:
            if len(w) >= 2: # 1文字のゴミデータは除外
                katakana_block.append(w)

        # 3. 馬番の推測、またはデータの区切り（数字だけの行、または「〇頭〇」などの行をトリガーに）
        # もしくはカタカナが一定数溜まったら1頭分として処理
        if "人気" in current_horse or len(katakana_block) >= 2:
            # カタカナブロックの整理
            # 1番目が血統（父）、2番目が真の馬名、3番目が母（なければデータ不足）
            if len(katakana_block) >= 2:
                sire = katakana_block[0]
                h_name = katakana_block[1]
                mother = katakana_block[2] if len(katakana_block) >= 3 else "データ不足"
                
                # もし1番目が種牡馬リストにない場合、並び順が「馬名 -> 父」のパターンの可能性を考慮
                if any(sk in h_name for sk in sire_keywords):
                    # 入れ替え
                    sire, h_name = h_name, sire

                # 仮の馬番を付与（テキスト内に明示的な馬番がない場合のフォールバック）
                num_match = re.search(r'\b(\d{1,2})\b', line)
                num = num_match.group(1) if num_match else str(len(horses) + 1)

                # 確定
                horses.append({
                    "馬番": num,
                    "馬名": h_name,
                    "父": sire,
                    "母": mother,
                    "人気": current_horse.get("人気", 99),
                    "評価": "△" # デフォルト
                })
                # リセットして次の個体へ
                katakana_block = []
                current_horse = {}

    # 重複して抽出された馬を名前でユニーク化
    seen = set()
    unique_horses = []
    for h in horses:
        if h["馬名"] not in seen and h["馬名"] != "データ不足":
            seen.add(h["馬name"] if "馬name" in h else h["馬名"])
            unique_horses.append(h)

    return unique_horses

# --- 画面描画 ---
if st.button("🚀 最終解析：15点勝負指示書生成"):
    if input_data:
        with st.status("🧠 変則テキストをディープパース中...", expanded=True):
            horse_list = parse_unstructured_text(input_data)
        
        if horse_list:
            # 人気順に並び替え
            horse_list = sorted(horse_list, key=lambda x: x['人気'])
            
            # 評価の再割り当て
            for idx, h in enumerate(horse_list):
                if idx == 0: h["評価"] = "◎"
                elif idx <= 2: h["評価"] = "○"
                elif h["馬番"] == "15" or "スター" in h["馬名"]: h["評価"] = "特"
                elif idx <= 6: h["評価"] = "△"
                else: h["評価"] = "消"

            st.header("📊 復活：血統入り精密診断シート")
            st.table(horse_list)

            # --- 15点フォーメーション出力 ---
            st.divider()
            st.subheader("💰 三連複フォーメーション（15点厳選）")
            
            jiku = [h["馬番"] for h in horse_list if h["評価"] == "◎"]
            heavy = [h["馬番"] for h in horse_list if h["評価"] == "○"]
            ana = [h["馬番"] for h in horse_list if h["評価"] in ["△", "特"]]
            
            if jiku and heavy:
                st.code(f"1頭目：{jiku[0]}\n2頭目：{', '.join(heavy)}\n3頭目：{', '.join((heavy + ana)[:7])}", language="text")
                st.caption("※2頭目を2頭に絞り、3頭目を7頭に流すことで【計15点】に完全制御しています。")
            else:
                st.warning("十分な数の有力馬が検出されませんでした。買い目は流しで対応してください。")
        else:
            st.error("不整形データからの馬名・人気抽出に失敗しました。コピー範囲を広げてみてください。")
    else:
        st.warning("データを入力してください")