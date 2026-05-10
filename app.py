import streamlit as st
import re

# --- 設定 ---
VERSION = "17.0"
LOGIC_NAME = "Genealogy & Formation Master"

st.set_page_config(page_title=f"Baru 競馬AI Pro v{VERSION}", layout="wide")
st.title(f"🏇 Baru 競馬AI Pro - 【Ver 17.0 血統・構成完全版】")

# --- 1. 種牡馬辞書（判定強化用） ---
SIRE_LIST = ["ロードカナロア", "モーリス", "エピファネイア", "ドゥラメンテ", "キズナ", "ハーツクライ", "サンダースノー", "ハービンジャー"]

# --- 2. 抽出ロジック（内容判別方式） ---
def extract_horse_data_v17(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    horses = []
    
    for i, line in enumerate(lines):
        # 起点：馬番（数字2つの行など）
        if re.match(r'^(\d{1,2})\s+(\d{1,2})', line):
            num = line.split()[-1]
            
            sire, horse_name, mother = "不明", "抽出エラー", "不明"
            
            # 馬番の行から下に向かって、役割を判定しながら取得
            scan_range = lines[i+1 : i+8]
            found_names = []
            for l in scan_range:
                # 純粋なカタカナのみの行を名前候補としてストック
                if re.match(r'^[ァ-ヶー・]+$', l):
                    found_names.append(l)
            
            if len(found_names) >= 2:
                sire = found_names[0]      # 1番目のカタカナは父
                horse_name = found_names[1] # 2番目のカタカナが真の馬名
                if len(found_names) >= 3:
                    mother = found_names[2] # 3番目があれば母（または母父）
            
            # 人気・オッズ・上がり
            pop, odds, agari = 99, "0.0", 0.0
            for j in range(i, min(i+20, len(lines))):
                p_match = re.search(r'(\d+\.\d+)\s+\((\d+)人気\)', lines[j])
                if p_match:
                    odds, pop = p_match.group(1), int(p_match.group(2))
                a_match = re.search(r'(\d{2}\.\d)', lines[j])
                if a_match and "kg" not in lines[j]:
                    agari = float(a_match.group(1))
                if "取消" in lines[j]: pop = 999

            horses.append({
                "馬番": num, "馬名": horse_name, "父": sire, "母": mother,
                "人気": pop, "オッズ": odds, "上がり": agari
            })
    return horses

# --- 3. メイン画面 ---
input_data = st.text_area("📋 解析データ入力", height=300)

if st.button("🚀 血統・適性・フォーメーション全展開"):
    if input_data:
        horse_list = extract_horse_data_v17(input_data)
        if horse_list:
            valid_list = [h for h in horse_list if h["人気"] != 999]
            top_horse = min(valid_list, key=lambda x: x['人気']) if valid_list else horse_list[0]

            st.header("📊 全頭精密診断・血統適性リスト")
            
            final_rows = []
            for h in horse_list:
                pop_val = h["人気"]
                # 血統適性ロジック（簡易版：父系統で判定）
                aptitude = "普通"
                if any(s in h["父"] for s in ["カナロア", "モーリス"]): aptitude = "短距離・高速"
                if any(s in h["父"] for s in ["エピファ", "ハーツ"]): aptitude = "中長距離・持続"
                if any(s in h["父"] for s in ["サンダー", "ハービン"]): aptitude = "洋芝・重馬場"

                if pop_val == 999: mark, reason = "消", "【取消】"
                elif h["馬番"] == top_horse["馬番"]: mark, reason = "◎", "指数1位。盤石。"
                elif h["上がり"] > 0 and h["上がり"] <= 34.0: mark, reason = "注", "【末脚警戒】"
                elif pop_val <= 4: mark, reason = "○", "有力。"
                else: mark, reason = "△", "紐候補。"

                final_rows.append({
                    "馬番": h["馬番"], "馬名": h["馬名"], "父": h["父"], "母": h["母"],
                    "血統適性": aptitude, "人気": pop_val if pop_val != 999 else "取消",
                    "評価": mark, "理由": reason
                })
            
            st.table(final_rows)

            # --- 4. 三連複フォーメーション表示 ---
            st.divider()
            st.subheader("💰 三連複フォーメーション推奨")
            jiku = top_horse["馬番"]
            heavy = [d["馬番"] for d in final_rows if d["評価"] in ["○", "◎"]] # 1, 2頭目
            ana = [d["馬番"] for d in final_rows if d["評価"] in ["△", "注"]]   # 3頭目

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**【フォーメーション：基本】**")
                st.code(f"1頭目：{jiku}\n2頭目：{', '.join(heavy)}\n3頭目：{', '.join(heavy + ana)}", language="text")
            with col2:
                st.markdown("**【点数計算】**")
                count = len(heavy) * (len(heavy + ana) - 2) # 簡易計算
                st.write(f"推奨投資：各100円〜\n想定点数：約{max(1, count)}点")
