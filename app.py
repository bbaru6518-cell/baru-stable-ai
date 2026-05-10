import streamlit as st
import re

# --- 設定 ---
VERSION = "18.0"
LOGIC_NAME = "Ultimate Formation & Bloodline Master"

st.set_page_config(page_title=f"Baru 競馬AI Pro v{VERSION}", layout="wide")
st.title(f"🏇 Baru 競馬AI Pro - 【Ver 18.0 究極版】")

# --- 1. 抽出ロジック（パターン認識方式へ変更） ---
def extract_horse_data_v18(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    horses = []
    
    for i, line in enumerate(lines):
        # 「枠番・馬番」の数字2つを起点にする
        if re.match(r'^(\d{1,2})\s+(\d{1,2})', line):
            num = line.split()[-1]
            
            # 馬番の行から下に向かって、役割を判定しながら取得
            # 1番目のカタカナ行 = 父
            # 2番目のカタカナ行 = 馬名 (ここが重要！)
            # 3番目のカタカナ行 = 母
            catakana_list = []
            for j in range(i + 1, min(i + 12, len(lines))):
                if re.match(r'^[ァ-ヶー・]+$', lines[j]):
                    catakana_list.append(lines[j])
                if len(catakana_list) >= 3: break
            
            sire = catakana_list[0] if len(catakana_list) >= 1 else "データ不足"
            h_name = catakana_list[1] if len(catakana_list) >= 2 else "データ不足"
            mother = catakana_list[2] if len(catakana_list) >= 3 else "データ不足"
            
            # 人気・オッズ・上がり
            pop, odds, agari = 99, "0.0", 0.0
            for k in range(i, min(i+25, len(lines))):
                p_match = re.search(r'(\d+\.\d+)\s+\((\d+)人気\)', lines[k])
                if p_match:
                    odds, pop = p_match.group(1), int(p_match.group(2))
                a_match = re.search(r'(\d{2}\.\d)', lines[k])
                if a_match and "kg" not in lines[k]:
                    agari = float(a_match.group(1))
                if "取消" in lines[k]: pop = 999

            horses.append({
                "馬番": num, "馬名": h_name, "父": sire, "母": mother,
                "人気": pop, "オッズ": odds, "上がり": agari
            })
    return horses

# --- 2. メイン画面 ---
input_data = st.text_area("📋 解析データ入力 (全頭分貼り付けてください)", height=300)

if st.button("🚀 15点勝負フォーメーション生成"):
    if input_data:
        horse_list = extract_horse_data_v18(input_data)
        if horse_list:
            valid_list = [h for h in horse_list if h["人気"] != 999]
            top_horse = min(valid_list, key=lambda x: x['人気']) if valid_list else horse_list[0]

            st.header("📊 最終精密解析：血統・適性診断")
            
            final_rows = []
            for h in horse_list:
                pop_val = h["人気"]
                # 血統適性判定（東京・高速馬場への適性）
                apt = "標準"
                if any(s in h["父"] for s in ["カナロア", "ディープ", "モーリス", "リアル"]): apt = "【A】高速・瞬発型"
                if any(s in h["父"] for s in ["ハーツ", "エピファ", "ルーラー"]): apt = "【B】持続・スタミナ型"
                if any(s in h["父"] for s in ["ハービン", "サンダー", "オルフェ"]): apt = "【C】重・洋芝型"

                if pop_val == 999: mark, reason = "消", "取消"
                elif h["馬番"] == top_horse["馬番"]: mark, reason = "◎", "軸不動。"
                elif pop_val <= 3: mark, reason = "○", "対抗。"
                elif h["上がり"] > 0 and h["上がり"] <= 34.0: mark, reason = "注", "激走注意。"
                elif pop_val <= 6: mark, reason = "△", "紐候補。"
                else: mark, reason = "消", "静観。"

                final_rows.append({
                    "馬番": h["馬番"], "馬名": h["馬名"], "父": h["父"], "母": h["母"],
                    "適性": apt, "人気": pop_val if pop_val != 999 else "取消",
                    "評価": mark
                })
            
            st.table(final_rows)

            # --- 3. 絞り込みフォーメーション (約15点) ---
            st.divider()
            st.subheader("💰 三連複フォーメーション：15点絞り込み案")
            
            jiku = top_horse["馬番"]
            heavy = [d["馬番"] for d in final_rows if d["評価"] in ["○", "◎"]] # 1-2頭目
            ana = [d["馬番"] for d in final_rows if d["評価"] in ["△", "注"]]   # 3頭目
            
            # フォーメーション構築：1頭目(1) - 2頭目(3) - 3頭目(7) ＝ 15点前後の計算
            # 2頭目を「○」評価の2〜3頭に限定することで絞る
            st.markdown(f"**◎ 軸馬: {jiku} ({top_horse['馬名']})**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**1頭目：** {jiku}")
                st.success(f"**2頭目：** {', '.join(heavy[:3])}")
                st.warning(f"**3頭目：** {', '.join((heavy + ana)[:8])}")
            
            with col2:
                st.markdown("#### **【三連複】指示書**")
                st.code(f"{jiku} — {', '.join(heavy[:3])} — {', '.join((heavy + ana)[:8])}", language="text")
                st.caption(f"※15番(スターシップ)等の穴馬は3頭目に配置し、高配当を狙います。")
