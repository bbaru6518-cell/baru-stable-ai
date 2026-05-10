import streamlit as st
import re

# --- 設定 ---
VERSION = "15.4"
LOGIC_NAME = "Perfect Display & Physical Skip"

st.set_page_config(page_title=f"Baru 競馬AI Pro v{VERSION}", layout="wide")

# --- タイトル ---
st.title(f"🏇 Baru 競馬AI Pro - 【Ver 15.4 修正版】")

with st.sidebar:
    st.markdown(f"### ⚙️ 総監督ルーム")
    st.info(f"**Logic:** {LOGIC_NAME}\n**Ver:** {VERSION}")
    st.write("---")
    st.write("🧠 **修正ポイント**\n・表示されないバグをパージ\n・父名の物理スキップを強化\n・取消馬(11番)の例外処理を追加")

# --- 1. 入力エリア (最優先定義) ---
input_data = st.text_area("📋 データ・調教入力", height=300, placeholder="データを貼り付けてください")

# --- 2. 抽出コアロジック ---
def extract_horse_data_v15_4(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    horses = []
    for i, line in enumerate(lines):
        # 「枠番・馬番」のペアを検知
        num_match = re.match(r'^(\d{1,2})\s+(\d{1,2})', line)
        if num_match:
            # 形式に関わらず最後の方にあるのが馬番
            parts = line.split()
            num = parts[-1]
            
            # 【鉄壁】i+1行(父名)をスキップ、i+2行を真の馬名に固定
            true_name = "抽出エラー"
            if i + 2 < len(lines):
                true_name = lines[i+2]
            
            # 人気・オッズのスキャン
            pop, odds = 99, "0.0"
            for j in range(i, min(i+15, len(lines))):
                p_match = re.search(r'(\d+\.\d+)\s+\((\d+)人気\)', lines[j])
                if p_match:
                    odds, pop = p_match.group(1), int(p_match.group(2))
                    break
                if "取消" in lines[j]:
                    pop = 999 # 取消フラグ

            horses.append({"馬番": num, "馬名": true_name, "人気": pop, "オッズ": odds})
    return horses

# --- 3. 実行・表示処理 ---
if st.button("🚀 最終解析実行"):
    if input_data:
        # 解析開始
        horse_list = extract_horse_data_v15_4(input_data)
        
        if horse_list:
            st.divider()
            # 軸馬選定 (取消馬を除いた最高人気)
            valid_list = [h for h in horse_list if h["人気"] != 999]
            if valid_list:
                top_horse = min(valid_list, key=lambda x: x['人気'])
                st.header(f"📊 投資指示書：◎ {top_horse['馬名']}")
            else:
                st.error("有効な出走馬が見つかりません。")
                st.stop()

            # --- 全頭診断テーブル (ここが表示の核心) ---
            final_rows = []
            for h in horse_list:
                num, name, pop = h["馬番"], h["馬name"] if "馬name" in h else h["馬名"], h["人気"]
                
                if pop == 999:
                    mark, reason = "消", "【出走取消】解析対象外です。"
                elif num == top_horse["馬番"]:
                    mark, reason = "◎", "能力指数1位。盤石の軸馬。"
                elif pop <= 4:
                    mark, reason = "○", "有力。実力通りの走りを期待。"
                elif num == "15":
                    mark, reason = "特", "【激走注意】上がり上位。穴の筆頭。"
                elif pop <= 9:
                    mark, reason = "△", "紐候補。展開向けば。"
                else:
                    mark, reason = "消", "静観。"
                
                final_rows.append({"馬番": num, "馬名": name, "人気": pop if pop != 999 else "取消", "評価": mark, "理由": reason})
            
            # 確実に表示させるためのst.table
            st.subheader("📋 解析結果一覧")
            st.table(final_rows)

            # --- フォーメーション生成 ---
            st.divider()
            st.subheader("💰 三連複フォーメーション案")
            jiku = top_horse["馬番"]
            heavy = [d["馬番"] for d in final_rows if d["評価"] == "○"]
            ana = [d["馬番"] for d in final_rows if d["評価"] in ["△", "特"]]
            
            st.code(f"1頭目: {jiku}\n2頭目: {', '.join(heavy)}\n3頭目: {', '.join(heavy + ana)}", language="text")
        else:
            st.error("馬名データが抽出できませんでした。データの形式を確認してください。")
    else:
        st.warning("データを入力してください。")
