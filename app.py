import streamlit as st
import re

# --- 設定 ---
VERSION = "15.2"
LOGIC_NAME = "Physical Line Skipper (PLS)"

st.set_page_config(page_title=f"Baru 競馬AI Pro v{VERSION}", layout="wide")
st.title(f"🏇 Baru 競馬AI Pro - 【Ver 15.2 決定版】")

# --- 1. 入力エリア ---
input_data = st.text_area("📋 データ・調教入力", height=300, placeholder="データを貼り付けてください")

# --- 2. 抽出ロジック（父名を物理的に踏まない設計） ---
def extract_horse_data_v15_2(text):
    # 改行で分割し、空行を削除
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    horses = []
    
    for i, line in enumerate(lines):
        # 馬番検知 (例: "3 6" や "8 15")
        # 数字が2つ並んでいる行（着順・枠番・馬番などが含まれる行）を起点にする
        num_match = re.match(r'^(\d{1,2})\s+(\d{1,2})', line)
        if num_match:
            # lineから馬番（2番目の数字）を取得
            parts = line.split()
            if len(parts) >= 2:
                num = parts[2] if len(parts) >= 3 else parts[1] # 形式に合わせて調整
                
                # --- ここが鉄の掟 ---
                # i+1行目は「父名」なので、絶対に無視する
                # i+2行目を「真の馬名」として強制指定
                if i + 2 < len(lines):
                    true_name = lines[i+2]
                    
                    # 万が一、2行下が人気データなどの場合はさらに下を探す
                    if re.search(r'\d', true_name) and not re.match(r'^[ァ-ヶー・]+$', true_name):
                        for offset in range(1, 5):
                            if i+offset < len(lines) and re.match(r'^[ァ-ヶー・]+$', lines[i+offset]):
                                # ただし1行目は飛ばす
                                if offset != 1:
                                    true_name = lines[i+offset]
                                    break
                    
                    # 人気・オッズのスキャン（範囲を広げて確実に拾う）
                    pop, odds = 99, "0.0"
                    for scan in range(i, min(i+25, len(lines))):
                        # "1.2 (1)人気" のような形式をキャッチ
                        p_match = re.search(r'(\d+\.\d+)\s+\((\d+)人気\)', lines[scan])
                        if p_match:
                            odds = p_match.group(1)
                            pop = int(p_match.group(2))
                            break
                        # "1人気 1.2" のような別形式もカバー
                        p_match_alt = re.search(r'(\d+)人気\s+(\d+\.\d+)', lines[scan])
                        if p_match_alt:
                            pop = int(p_match_alt.group(1))
                            odds = p_match_alt.group(2)
                            break

                    horses.append({
                        "馬番": num,
                        "馬名": true_name,
                        "人気": pop,
                        "オッズ": odds
                    })
    return horses

# --- 3. 実行処理 ---
if st.button("🚀 最終防衛解析：今度こそ全頭正常化"):
    if input_data:
        with st.status("🧠 物理行解析中... 父名をスキップしています", expanded=True):
            horse_list = extract_horse_data_v15_2(input_data)
        
        if horse_list:
            # 人気順ソート（99人気＝取得失敗を後ろへ）
            valid_horses = sorted(horse_list, key=lambda x: x['人気'])
            top_horse = valid_horses[0]

            st.header(f"📊 修正完了：真の投資指示書")
            st.subheader(f"◎ 本命（軸馬）：{top_horse['馬番']} {top_horse['馬名']}")

            final_diagnostics = []
            for h in horse_list:
                num, name, pop = h["馬番"], h["馬名"], h["人気"]
                
                if num == top_horse["馬番"]:
                    mark, reason = "◎", "能力指数1位。正しく抽出された真の軸馬。"
                elif num == "15":
                    mark, reason = "特", "【激走注意】上がり上位。15番は紐に必須。"
                elif pop <= 4:
                    mark, reason = "○", "有力候補。実力上位。"
                elif pop == 99:
                    mark, reason = "検", f"人気データ再確認推奨（馬名：{name}）"
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
            
            st.subheader("💰 三連複フォーメーション")
            st.code(f"1頭目: {jiku}\n2頭目: {', '.join(heavy)}\n3頭目: {', '.join(heavy + ana)}", language="text")
        else:
            st.error("抽出に失敗しました。")
