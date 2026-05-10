import streamlit as st
import re

# --- 設定 ---
VERSION = "18.5"
LOGIC_NAME = "Perfect Alignment & 15-Point Strategy"

st.set_page_config(page_title=f"Baru 競馬AI Pro v{VERSION}", layout="wide")
st.title(f"🏇 Baru 競馬AI Pro - 【Ver 18.5 最終解】")

# --- 1. 抽出ロジック（行の内容を精密に評価する新アルゴリズム） ---
def extract_horse_data_v18_5(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    horses = []
    
    for i, line in enumerate(lines):
        # 起点：枠番・馬番（例：「1 5」「8 10」など数字が2つ並ぶ行）
        if re.match(r'^(\d{1,2})\s+(\d{1,2})', line):
            num = line.split()[-1]
            
            # --- 馬名・血統情報の動的抽出 ---
            name_pool = []
            # 馬番の行から最大12行先までを精査
            for j in range(i + 1, min(i + 13, len(lines))):
                candidate = lines[j]
                # 純粋なカタカナ行（スペースや記号を含まない馬名・父名候補）
                if re.match(r'^[ァ-ヶー・]+$', candidate):
                    name_pool.append(candidate)
                # 万が一、母名が抽出エラー（データ不足）にならないよう記号混じりも許容する
                elif len(name_pool) >= 2 and re.match(r'^[ァ-ヶー・★▲☆]+$', candidate):
                    name_pool.append(re.sub(r'[★▲☆]', '', candidate))
                
                if len(name_pool) >= 3: break
            
            sire = name_pool[0] if len(name_pool) >= 1 else "不明"
            h_name = name_pool[1] if len(name_pool) >= 2 else "不明"
            mother = name_pool[2] if len(name_pool) >= 3 else "不明"
            
            # 人気・オッズ・上がりの取得
            pop, odds, agari = 99, "0.0", 0.0
            for k in range(i, min(i+25, len(lines))):
                p_match = re.search(r'(\d+\.\d+)\s+\((\d+)人気\)', lines[k])
                if p_match:
                    odds, pop = p_match.group(1), int(p_match.group(2))
                # 上がり3F (例: 33.5)
                a_match = re.search(r'(\d{2}\.\d)', lines[k])
                if a_match and "kg" not in lines[k]:
                    agari = float(a_match.group(1))
                if "取消" in lines[k]: pop = 999

            horses.append({
                "馬番": num, "馬名": h_name, "父": sire, "母": mother,
                "人気": pop, "オッズ": odds, "上がり": agari
            })
    return horses

# --- 2. 実行処理 ---
input_data = st.text_area("📋 解析データ入力", height=300)

if st.button("🚀 最終解析：15点勝負指示書生成"):
    if input_data:
        horse_list = extract_horse_data_v18_5(input_data)
        if horse_list:
            valid_list = [h for h in horse_list if h["人気"] != 999]
            top_horse = min(valid_list, key=lambda x: x['人気']) if valid_list else horse_list[0]

            st.header("📊 最終精密解析：血統・適性診断")
            
            final_rows = []
            for h in horse_list:
                pop_val = h["人気"]
                # 血統適性判定
                apt = "標準"
                if any(s in h["父"] for s in ["カナロア", "モーリス", "リアル"]): apt = "【A】高速・瞬発型"
                elif any(s in h["父"] for s in ["エピファ", "ハーツ", "ドゥラ"]): apt = "【B】持続・スタミナ型"
                elif any(s in h["父"] for s in ["ハービン", "サンダー"]): apt = "【C】洋芝・パワー型"

                if pop_val == 999: mark, reason = "消", "取消"
                elif h["馬番"] == top_horse["馬番"]: mark, reason = "◎", "軸不動。"
                elif pop_val <= 3: mark, reason = "○", "有力。"
                elif h["上がり"] > 0 and h["上がり"] <= 34.0: mark, reason = "注", f"激走注意({h['上がり']})"
                elif pop_val <= 6: mark, reason = "△", "紐候補。"
                else: mark, reason = "消", "静観。"

                final_rows.append({
                    "馬番": h["馬番"], "馬名": h["馬名"], "父": h["父"], "母": h["母"],
                    "適性": apt, "人気": pop_val if pop_val != 999 else "取消", "評価": mark
                })
            
            st.table(final_rows)

            # --- 3. 15点絞り込みフォーメーション ---
            st.divider()
            st.subheader("💰 三連複フォーメーション：厳選15点指示書")
            
            jiku = top_horse["馬番"]
            # 2頭目は上位評価の最大3頭に限定
            heavy = [d["馬番"] for d in final_rows if d["評価"] in ["◎", "○"]][:3]
            # 3頭目は広めに流すが、全体を調整
            ana = [d["馬番"] for d in final_rows if d["評価"] in ["△", "注"]]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**◎ 軸馬: {jiku} ({top_horse['馬名']})**")
                st.info(f"**1頭目：** {jiku}")
                st.success(f"**2頭目：** {', '.join(heavy)}")
                st.warning(f"**3頭目：** {', '.join((heavy + ana)[:8])}")
            
            with col2:
                st.markdown("#### **【三連複】買い目合計：15点**")
                st.code(f"{jiku} — {', '.join(heavy)} — {', '.join((heavy + ana)[:8])}", language="text")
                st.write("・15番(スターシップ)等の穴馬は必ず3頭目に入れてください。\n・ガミり防止のため上位人気同士は厚めに。")
