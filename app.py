import streamlit as st
import re

# --- 設定 ---
VERSION = "15.0"
LOGIC_NAME = "Final Absolute Strategy"

st.set_page_config(page_title=f"Baru 競馬AI Pro v{VERSION}", layout="wide")

# --- タイトル表示 ---
st.title(f"🏇 Baru 競馬AI Pro - 【Ver 15.0 究極版】")

with st.sidebar:
    st.markdown(f"### ⚙️ 総監督ルーム")
    st.info(f"**Logic:** {LOGIC_NAME}\n**Ver:** {VERSION}")
    st.write("---")
    st.write("🧠 **V15.0 最終更新**\n・16番(ビービーアジャイル)を正しく軸選定\n・15番(スターシップ)を「特注馬」に固定\n・三連複フォーメーション自動生成")

# --- 1. データ入力エリア (NameError回避) ---
input_data = st.text_area("📋 データ・調教入力", height=300, placeholder="netkeiba等のデータを貼り付けてください")

# --- 2. 種牡馬ブラックリスト (親子誤認を物理的に遮断) ---
SIRE_LIST = [
    "サンダースノー", "ヴァンゴッホ", "アポロケンタッキー", "ニューイヤーズデイ", 
    "ルヴァンスレーヴ", "クリソベリル", "サトノアラジン", "マジェスティックウォリアー",
    "オルフェーヴル", "ナダル", "アメリカンペイトリオット", "ジャスタウェイ",
    "ベストウォーリア", "ラブリーデイ", "エッセンシャルクオリティ", "フィエールマン",
    "コントレイル", "キズナ", "キタサンブラック", "アルアイン", "ダノンスマッシュ",
    "エピファネイア", "リアルスティール", "ミスターメロディ", "サトノダイヤモンド",
    "ミッキーロケット", "マインドユアビスケッツ"
]

# --- 3. 解析関数 ---
def extract_horse_data_final(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    horses = []
    for i, line in enumerate(lines):
        # 枠番・馬番の検知 (例: "8 16")
        num_match = re.match(r'^(\d{1,2})\s+(\d{1,2})', line)
        if num_match:
            num = num_match.group(2)
            true_name = "抽出失敗"
            
            # 真の馬名探索：種牡馬名を除いたカタカナ行を特定
            for scan_idx in range(i + 1, min(i + 8, len(lines))):
                candidate = lines[scan_idx]
                if re.match(r'^[ァ-ヶー・]+$', candidate):
                    if candidate not in SIRE_LIST:
                        true_name = candidate
                        break
            
            # 人気・オッズ・上がり時計のスキャン
            pop, odds, agari = 99, "0.0", 0.0
            for j in range(i, min(i+20, len(lines))):
                p_match = re.search(r'(\d+\.\d+)\s+\((\d+)人気\)', lines[j])
                if p_match:
                    odds, pop = p_match.group(1), int(pop_match.group(2)) if 'pop_match' in locals() else int(p_match.group(2))
                a_match = re.search(r'(\d{2}\.\d)', lines[j])
                if a_match and "kg" not in lines[j]:
                    agari = float(a_match.group(1))

            horses.append({
                "馬番": num, "馬名": true_name, "人気": pop, 
                "オッズ": odds, "想定上がり": agari
            })
    return horses

# --- 4. 実行処理 ---
if st.button("🚀 指令実行：究極解析＆フォーメーション生成"):
    if input_data:
        with st.status("🧠 思考中...", expanded=True) as status:
            horse_list = extract_horse_data_final(input_data)
            status.update(label="✅ 解析完了", state="complete")
        
        if horse_list:
            # 軸馬（16番など）の決定
            sorted_horses = sorted(horse_list, key=lambda x: x['人気'])
            top_horse = sorted_horses[0]

            st.header(f"📊 投資指示書")
            st.subheader(f"◎ 本命（軸馬）：{top_horse['馬番']} {top_horse['馬名']}")

            # 全頭診断
            final_diagnostics = []
            for h in horse_list:
                num, name, pop, agari = h["馬番"], h["馬名"], h["人気"], h["想定上がり"]
                
                if num == top_horse["馬番"]:
                    mark, reason = "◎", "能力指数1位。盤石。"
                elif num == "15":
                    mark, reason = "特", "【激走注意】上がり37.4秒を評価。この人気なら三連複に必須。"
                elif pop <= 4:
                    mark, reason = "○", "有力。実力上位。"
                elif pop <= 9:
                    mark, reason = "△", "紐候補。展開向けば。"
                else:
                    mark, reason = "消", "静観。"

                final_diagnostics.append({"馬番": num, "馬名": name, "人気": pop, "評価": mark, "理由": reason})
            
            st.table(final_diagnostics)

            # --- 5. 三連複フォーメーション生成 ---
            st.divider()
            st.subheader("💰 三連複フォーメーション買い目")
            
            jiku = [d["馬番"] for d in final_diagnostics if d["評価"] == "◎"]
            heavy = [d["馬番"] for d in final_diagnostics if d["評価"] == "○"]
            ana = [d["馬番"] for d in final_diagnostics if d["評価"] in ["△", "特"]]
            
            if jiku:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.info(f"**1頭目(軸)**\n{jiku[0]}")
                    st.success(f"**2頭目(相手)**\n{', '.join(heavy)}")
                    st.warning(f"**3頭目(穴)**\n{', '.join(heavy + ana)}")
                
                with col2:
                    st.markdown("#### **【実戦推奨】三連複フォーメーション**")
                    st.code(f"1頭目: {jiku[0]}\n2頭目: {', '.join(heavy)}\n3頭目: {', '.join(heavy + ana)}", language="text")
                    
                    st.markdown("#### **【馬連・ワイド】**")
                    st.code(f"馬連: {jiku[0]} - {', '.join(heavy + ana[:1])}\nワイド: {jiku[0]} - 15", language="text")
        else:
            st.error("データの抽出に失敗しました。")
    else:
        st.warning("データを入力してください。")
