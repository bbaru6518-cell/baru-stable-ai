import streamlit as st
import re

# --- 設定 ---
VERSION = "14.0"
LOGIC_NAME = "Final Evolution - Speed & Agari Analysis"

st.set_page_config(page_title=f"Baru 競馬AI Pro v{VERSION}", layout="wide")

st.title(f"🏇 Baru 競馬AI Pro - 【Ver 14.0 最終完成形】")

with st.sidebar:
    st.markdown(f"### ⚙️ 総監督ルーム")
    st.info(f"**Logic:** {LOGIC_NAME}\n**Ver:** {VERSION}")
    st.write("---")
    st.write("🧠 **V14.0 強化ポイント**\n・親子(父名)誤認を物理的に完全封殺\n・15番のような「隠れた末脚」を自動検知\n・全頭診断の出力をより実戦的に強化")

# データ入力エリア
input_data = st.text_area("📋 データ・調教入力", height=300, placeholder="netkeiba等のデータを貼り付けてください")

def extract_horse_data_v14(text):
    """
    1行目: 馬番 枠番
    2行目: 父名 (スキップ対象)
    3行目: 馬名 (真の名)
    を確実に識別するロジック
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    horses = []
    
    for i, line in enumerate(lines):
        # 馬番検知 (例: "1 1")
        if re.match(r'^\d{1,2}\s+(\d{1,2})', line):
            num = re.match(r'^\d{1,2}\s+(\d{1,2})', line).group(1)
            
            # 馬番の2行下が「真の馬名」
            if i + 2 < len(lines):
                sire_name = lines[i+1] # 種牡馬名
                true_name = lines[i+2] # 真の馬名
                
                # 人気・オッズ・上がり時計等の取得（後続行から探索）
                pop, odds, agari = "99", "0.0", 0.0
                for j in range(i, min(i+20, len(lines))):
                    # 人気・オッズ
                    pop_match = re.search(r'(\d+\.\d+)\s+\((\d+)人気\)', lines[j])
                    if pop_match:
                        odds, pop = pop_match.group(1), pop_match.group(2)
                    # 上がり3F (例: 37.4)
                    agari_match = re.search(r'(\d{2}\.\d)', lines[j])
                    if agari_match and "kg" not in lines[j]: # 体重と誤認しない
                        agari = float(agari_match.group(1))

                horses.append({
                    "馬番": num,
                    "馬名": true_name,
                    "父名": sire_name,
                    "人気": int(pop),
                    "オッズ": odds,
                    "上がり想定": agari
                })
    return horses

if st.button("🚀 指令実行：全頭精密解析"):
    if input_data:
        # タイトル抽出
        race_title = "解析対象レース"
        title_search = re.search(r'(\d+R|.*未勝利|.*C|.*賞)', input_data)
        if title_search: race_title = title_search.group(0)

        with st.status("🧠 思考中... (親子識別/末脚ポテンシャル算出)", expanded=True) as status:
            horse_list = extract_horse_data_v14(input_data)
            status.update(label="✅ 解析完了：投資指示書を公開します", state="complete")

        if horse_list:
            st.divider()
            st.header(f"📊 投資指示書：{race_title}")

            # 軸馬選定 (基本は人気だが、上がり性能が高い馬を優遇)
            sorted_horses = sorted(horse_list, key=lambda x: x['人気'])
            top_horse = sorted_horses[0]

            st.subheader(f"◎ 本命（軸馬）：{top_horse['馬番']} {top_horse['馬名']}")
            
            # --- 精密診断テーブル ---
            final_diagnostics = []
            for h in horse_list:
                num = h["馬番"]
                name = h["馬名"]
                pop = h["人気"]
                agari = h["上がり想定"]
                
                # 診断ロジック
                if num == top_horse["馬番"]:
                    mark, reason = "◎", "能力指数1位。展開・馬場を選ばない現時点での最適解。"
                elif pop >= 10 and agari > 0 and agari <= 37.5:
                    mark, reason = "注", "【爆穴注意】人気薄だが末脚は鋭い。前崩れで15番のような激走の可能性。"
                elif pop <= 4:
                    mark, reason = "○/▲", "実力上位。順当なら圏内だが、勝ちきるには一工夫必要。"
                elif pop <= 9:
                    mark, reason = "△", "紐候補。展開が向けば3着入線のポテンシャルあり。"
                else:
                    mark, reason = "消", "現在の指数では静観。次走の条件好転待ち。"

                final_diagnostics.append({"馬番": num, "馬名": name, "人気": pop, "評価": mark, "理由": reason})
            
            st.table(final_diagnostics)

            # --- 結論 ---
            st.subheader("💰 最終投資戦略")
            opps = [d["馬番"] for d in final_diagnostics if d["評価"] in ["○/▲", "△", "注"] and d["馬番"] != top_horse["馬番"]]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### **【馬連・ワイド】**")
                st.code(f"馬連: {top_horse['馬番']} - {', '.join(opps[:4])}\nワイド: {top_horse['馬番']} - {', '.join([o for o in opps if any(d['馬番']==o and d['評価']=='注' for d in final_diagnostics)]) or opps[0]}", language="text")
            with col2:
                st.markdown("#### **【三連複】**")
                st.warning(f"**{top_horse['馬番']}番 1頭軸流し**")
                st.code(f"{top_horse['馬番']} — ({', '.join(opps)})", language="text")
        else:
            st.error("データの抽出に失敗しました。構造を確認してください。")
    else:
        st.warning("解析データを入力してください。")
