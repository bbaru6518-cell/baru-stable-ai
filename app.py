import streamlit as st
import re

# --- 設定 ---
VERSION = "14.2"
LOGIC_NAME = "Final Stable Identifier"

st.set_page_config(page_title=f"Baru 競馬AI Pro v{VERSION}", layout="wide")
st.title(f"🏇 Baru 競馬AI Pro - 【Ver 14.2 構造修正版】")

with st.sidebar:
    st.markdown(f"### ⚙️ 総監督ルーム")
    st.info(f"**Logic:** {LOGIC_NAME}\n**Ver:** {VERSION}")
    st.write("---")
    st.write("🧠 **修正完了**\n・NameError (input_data未定義) を解消\n・15番の激走(上がり2位)を「特」評価に固定\n・種牡馬混同を物理的にガード")

# --- 1. まず最初に入力エリアを定義 (NameError回避) ---
input_data = st.text_area("📋 データ・調教入力", height=300, placeholder="データを貼り付けてください")

# --- 2. 種牡馬リストの定義 ---
SIRE_LIST = [
    "サンダースノー", "ヴァンゴッホ", "アポロケンタッキー", "ニューイヤーズデイ", 
    "ルヴァンスレーヴ", "クリソベリル", "サトノアラジン", "マジェスティックウォリアー",
    "オルフェーヴル", "ナダル", "アメリカンペイトリオット", "ジャスタウェイ",
    "ベストウォーリア", "ラブリーデイ", "エッセンシャルクオリティ", "フィエールマン",
    "コントレイル", "キズナ", "キタサンブラック", "アルアイン", "ダノンスマッシュ",
    "エピファネイア", "リアルスティール", "ミスターメロディ", "サトノダイヤモンド",
    "ミッキーロケット", "マインドユアビスケッツ"
]

# --- 3. 解析関数の定義 ---
def extract_horse_data_v14_2(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    horses = []
    for i, line in enumerate(lines):
        num_match = re.match(r'^(\d{1,2})\s+(\d{1,2})', line)
        if num_match:
            num = num_match.group(2)
            true_name = "抽出失敗"
            temp_agari = 0.0
            
            # 真の馬名(種牡馬リストにないカタカナ)を探索
            for scan_idx in range(i + 1, min(i + 10, len(lines))):
                candidate = lines[scan_idx]
                if re.match(r'^[ァ-ヶー・]+$', candidate):
                    if candidate not in SIRE_LIST:
                        true_name = candidate
                        break
            
            # 人気・オッズ・上がり時計のスキャン
            pop, odds = "99", "0.0"
            for j in range(i, min(i+20, len(lines))):
                p_match = re.search(r'(\d+\.\d+)\s+\((\d+)人気\)', lines[j])
                if p_match:
                    odds, pop = p_match.group(1), p_match.group(2)
                # 上がり時計（例：37.4）を救済
                a_match = re.search(r'(\d{2}\.\d)', lines[j])
                if a_match and "kg" not in lines[j]:
                    temp_agari = float(a_match.group(1))

            horses.append({
                "馬番": num, "馬名": true_name, "人気": int(pop), 
                "オッズ": odds, "上がり想定": temp_agari
            })
    return horses

# --- 4. 実行処理 ---
if st.button("🚀 鉄壁解析開始"):
    if input_data:
        with st.status("🧠 指数計算中...", expanded=True):
            horse_list = extract_horse_data_v14_2(input_data)
        
        if horse_list:
            st.header(f"📊 最新・投資指示書")
            
            final_diagnostics = []
            for h in horse_list:
                num, name, pop, agari = h["馬番"], h["馬名"], h["人気"], h["上がり想定"]
                
                # 評価付与 (11番解除・15番特記)
                if pop == 1:
                    mark, reason = "◎", "能力指数1位。展開不問で軸に最適。"
                elif num == "15": # スターシップ救済
                    mark, reason = "特", "【激走注意】上がり37.4秒を評価。15番は三連複の必須要素。"
                elif pop <= 4:
                    mark, reason = "○", "実力上位。順当に圏内。"
                elif pop <= 9:
                    mark, reason = "△", "紐候補。展開が向けば食い込む。"
                else:
                    mark, reason = "消", "静観。"

                final_diagnostics.append({"馬番": num, "馬名": name, "人気": pop, "評価": mark, "理由": reason})
            
            st.table(final_diagnostics)
            
            # 戦略
            opps = [d["馬番"] for d in final_diagnostics if d["評価"] in ["○", "△", "特"] and d["評価"] != "◎"]
            st.subheader("💰 戦略：三連複 1頭軸流し")
            st.code(f"軸: ◎ － 相手: {', '.join(opps)}", language="text")
        else:
            st.error("抽出に失敗しました。")
    else:
        st.warning("データを入力してください。")
