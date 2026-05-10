import streamlit as st
import re

# --- 設定 ---
VERSION = "16.0"
LOGIC_NAME = "Bloodline & Line Skipper Logic"

st.set_page_config(page_title=f"Baru 競馬AI Pro v{VERSION}", layout="wide")
st.title(f"🏇 Baru 競馬AI Pro - 【Ver 16.0 血統実装版】")

# --- 1. 絶対に馬名として認めないキーワード (血統行として認識) ---
SIRE_KEYWORDS = [
    "ロードカナロア", "モーリス", "エピファネイア", "ドゥラメンテ", "キズナ", 
    "ハーツクライ", "ディープインパクト", "キングカメハメハ", "ハービンジャー",
    "ルーラーシップ", "ダイワメジャー", "オルフェーヴル", "スクリーンヒーロー",
    "ゴールドシップ", "ジャスタウェイ", "リアルスティール", "シャンハイボビー",
    "ロゴタイプ", "ディーマジェスティ", "コパノリッキー", "ガルボ", "サンダースノー"
]

# --- 2. 抽出コアロジック (血統取得版) ---
def extract_horse_data_v16(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    horses = []
    for i, line in enumerate(lines):
        # 馬番検知
        num_match = re.match(r'^(\d{1,2})\s+(\d{1,2})', line)
        if num_match:
            parts = line.split()
            num = parts[-1]
            
            sire_name = "不明"
            true_name = "抽出エラー"
            
            # 馬番の直後(i+1)は「父名(血統)」として取得
            if i + 1 < len(lines):
                sire_name = lines[i+1]
            
            # そのさらに下から「真の馬名」を探索
            for offset in range(2, 6):
                if i + offset >= len(lines): break
                candidate = lines[i + offset]
                if re.match(r'^[ァ-ヶー・]+$', candidate):
                    if not any(sire in candidate for sire in SIRE_KEYWORDS):
                        true_name = candidate
                        break
            
            # 人気・オッズ・上がり
            pop, odds, agari = 99, "0.0", 0.0
            for j in range(i, min(i+25, len(lines))):
                p_match = re.search(r'(\d+\.\d+)\s+\((\d+)人気\)', lines[j])
                if p_match:
                    odds, pop = p_match.group(1), int(p_match.group(2))
                a_match = re.search(r'(\d{2}\.\d)', lines[j])
                if a_match and "kg" not in lines[j]:
                    agari = float(a_match.group(1))
                if "取消" in lines[j]: pop = 999

            horses.append({
                "馬番": num, "馬名": true_name, "父名": sire_name, 
                "人気": pop, "オッズ": odds, "上がり": agari
            })
    return horses

# --- 3. メイン処理 ---
input_data = st.text_area("📋 データ・調教入力", height=300)

if st.button("🚀 血統含め全頭解析"):
    if input_data:
        horse_list = extract_horse_data_v16(input_data)
        if horse_list:
            valid_list = [h for h in horse_list if h["人気"] != 999]
            top_horse = min(valid_list, key=lambda x: x['人気']) if valid_list else horse_list[0]

            final_rows = []
            for h in horse_list:
                pop_val = h["人気"]
                # 評価ロジック
                if pop_val == 999: mark, reason = "消", "【出走取消】"
                elif h["馬番"] == top_horse["馬番"]: mark, reason = "◎", "指数1位。盤石。"
                elif h["上がり"] > 0 and h["上がり"] <= 34.0: mark, reason = "注", f"【末脚警戒】上がり{h['上がり']}。激走あり。"
                elif pop_val <= 4: mark, reason = "○", "有力。実力通り。"
                elif pop_val <= 9: mark, reason = "△", "紐候補。"
                else: mark, reason = "消", "静観。"

                final_rows.append({
                    "馬番": h["馬番"],
                    "馬名": h["馬名"],
                    "血統(父)": h["父名"],
                    "人気": pop_val if pop_val != 999 else "取消",
                    "評価": mark,
                    "理由": reason
                })
            
            # テーブル表示
            st.subheader("📋 血統入り・全頭精密診断テーブル")
            st.table(final_rows)
            
            # 買い目生成
            st.divider()
            jiku = top_horse["馬番"]
            opps = [d["馬番"] for d in final_rows if d["評価"] in ["○", "△", "注"]]
            st.subheader("💰 推奨フォーメーション")
            st.code(f"三連複 1頭軸: {jiku} — ({', '.join(opps)})", language="text")
    else:
        st.warning("データを入力してください")
