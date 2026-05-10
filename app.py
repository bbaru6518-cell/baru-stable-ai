import streamlit as st
import re

# --- 設定 ---
VERSION = "15.1"
LOGIC_NAME = "Final Defense Line - Zero Sire Logic"

st.set_page_config(page_title=f"Baru 競馬AI Pro v{VERSION}", layout="wide")
st.title(f"🏇 Baru 競馬AI Pro - 【Ver 15.1 最終防衛版】")

# --- 1. 入力エリア ---
input_data = st.text_area("📋 データ・調教入力", height=300, placeholder="ここにデータを貼り付けてください")

# --- 2. 抽出ロジック（ここを完全に書き換えました） ---
def extract_horse_data_v15_1(text):
    # 行ごとに分割
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    horses = []
    
    for i, line in enumerate(lines):
        # 馬番検知 (例: "3 6" や "8 16")
        num_match = re.match(r'^(\d{1,2})\s+(\d{1,2})', line)
        if num_match:
            num = num_match.group(2)
            
            # 【重要】馬番の行の「次」は必ず父名なので無視。
            # 「2行下」を馬名として取得する。
            true_name = "抽出エラー"
            if i + 2 < len(lines):
                # 2行下がカタカナであることを確認
                candidate = lines[i+2]
                if re.match(r'^[ァ-ヶー・]+$', candidate):
                    true_name = candidate
            
            # 人気・オッズのスキャン
            pop, odds = 99, "0.0"
            for j in range(i, min(i+20, len(lines))):
                p_match = re.search(r'(\d+\.\d+)\s+\((\d+)人気\)', lines[j])
                if p_match:
                    odds = p_match.group(1)
                    pop = int(p_match.group(2))
                    break
            
            horses.append({
                "馬番": num,
                "馬名": true_name,
                "人気": pop,
                "オッズ": odds
            })
    return horses

# --- 3. 実行処理 ---
if st.button("🚀 指令実行：全頭正常化解析"):
    if input_data:
        with st.status("🧠 父名データをパージし、真の個体を識別中...", expanded=True):
            horse_list = extract_horse_data_v15_1(input_data)
        
        if horse_list:
            # 11番の「99人気」を回避するため、人気順でソート（有効なデータがある場合）
            valid_horses = [h for h in horse_list if h["人気"] != 99]
            if valid_horses:
                top_horse = min(valid_horses, key=lambda x: x['人気'])
            else:
                top_horse = horse_list[0]

            st.header(f"📊 修正完了：投資指示書")
            st.subheader(f"◎ 本命（軸馬）：{top_horse['馬番']} {top_horse['馬名']}")

            final_diagnostics = []
            for h in horse_list:
                num, name, pop = h["馬番"], h["馬名"], h["人気"]
                
                # 評価ロジック
                if num == top_horse["馬番"]:
                    mark, reason = "◎", "能力指数1位。正しく抽出された軸馬です。"
                elif num == "15":
                    mark, reason = "特", "【激走注意】上がり上位のスターシップ。紐に必須。"
                elif pop <= 4:
                    mark, reason = "○", "有力候補。実力上位。"
                elif pop == 99:
                    mark, reason = "検", "データ不備あり。個別に再確認推奨。"
                elif pop <= 9:
                    mark, reason = "△", "紐候補。"
                else:
                    mark, reason = "消", "静観。"

                final_diagnostics.append({"馬番": num, "馬名": name, "人気": pop, "評価": mark, "理由": reason})
            
            st.table(final_diagnostics)

            # --- フォーメーション出力 ---
            st.divider()
            jiku = top_horse["馬番"]
            heavy = [d["馬番"] for d in final_diagnostics if d["評価"] == "○"]
            ana = [d["馬番"] for d in final_diagnostics if d["評価"] in ["△", "特"]]
            
            st.subheader("💰 三連複フォーメーション（完全版）")
            st.code(f"1頭目: {jiku}\n2頭目: {', '.join(heavy)}\n3頭目: {', '.join(heavy + ana)}", language="text")
        else:
            st.error("抽出失敗。形式を再確認してください。")
