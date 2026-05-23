import re
import pandas as pd
import streamlit as st

# --- Streamlitの画面設定 ---
st.set_page_config(page_title="競馬ブック能力表パサー", layout="wide")
st.title("🏇 競馬ブック 能力表データ整形ツール")
st.write("テキストデータから正しい馬番と馬名を抽出します。")

# --- 1. サンプルデータの用意（OCRやテキスト抽出された生のデータ） ---
# ※ここにパースしたいテキストを流し込めるようにしています
raw_data_input = st.text_area(
    "ここに能力表のテキストを貼り付けてください（現在はサンプルが入っています）",
    value="""1 1 56.9 ○ 小林凌 ロードカナロア (特)スペルキャスター スペルバインド 5走前 9着①11-12 2歳クラス 16頭 8 1着②1-2 2歳クラス 13頭 11 1着②5-3 通過2戦 16頭 5 1200芝内1:08.9 鮫島駿54 R 1200芝内1:09.4 藤岡康53 R 1000芝直0:55.0 小林凌大53 R H34.8-34.1 B468 前572 H34.0-35.4 B467 前578 M22.0-33.0 B478 ブルーアイド 0.7 478 11枠10人 キシードレ 1.1 486 9枠12人 カウンターセ 0.5 478 15枠4人
1 2 60.9 ◎ 西塚洸 ヴィクトワールピサ バルティクラール サンデスタッシュ 3走前 11着①11-24 2歳 16頭 4 2着②12-9 2歳クラス 16頭 4 1着②1-21 同地方 10頭 1800芝右1:47.5 西塚洸56 R 1600芝人1:35.1 プーシャ56 R 1400芝人1:20.2 0.0分春56 R S36.7-34.8 B498 前572 M35.9-36.1 B502 前576 M34.3-34.5 B502 ノーランサン 0.0 528 3枠3人 メダルスピー 0.6 524 6枠6人 ミトノオー 0.2 526 6枠7人
2 3 56.8 △ 上原豪 7/4（水）くるめ（岩手） 牡6 栗 鈴木啓（美） ライクアフラワー ビクトリーチャーム 4着①3-13 3歳2組 11頭 6 5着①12-6 2歳クラス 13頭 7 1着①4-5 サンク3歳 14頭 8 1200芝x1:08.6 石神深58 R 1200芝内1:07.8 石神深56 R 1200芝内1:08.8 石神深57 R S36.0-32.6 B508 前576 M34.3-33.5 B510 前579 H35.0-33.8 B514 前577 ギンシャリマ 0.3 508 8枠9人 サンドアイラ 0.3 510 4枠8人 ウインアイオ 0.1 514 5枠5人
2 4 61.1 ○ 丹内祐 ダイワメジャー ヴァンヴィーヴ サンデスタッシュ 1着①11-17 2歳クラス 16頭 1 1着①1-11 2歳クラス 16頭 4 1着②4-25 民友2戦 16頭 2 1200芝外1:08.1 戸崎圭58 R 1200芝人1:08.1 丹内祐58 R 1200芝新1:07.7 舟山駆58 R S34.8-33.3 B512 前582 M34.2-33.9 B516 前576 M34.0-33.7 B514 キンシャノ 0.1 512 9枠1人 アサクサグレ 0.4 512 4枠1人 ウィンストン 0.0 514 7枠2人""",
    height=200
)

# --- 2. 解析ロジック用の関数 ---
def parse_keibabook_line(line):
    line = line.strip()
    if not line:
        return None
        
    # 行頭の「枠番」「馬番」「騎手」を正確に抽出
    base_match = re.search(r'^(\d+)\s+(\d+)\s+[\d\.]+\s*[\u25ce\u25cb\u25b2\u25b3\u2605]*\s*([^\s]+)', line)
    if not base_match:
        return None
        
    waku = base_match.group(1)
    umaban = base_match.group(2)
    jockey = base_match.group(3)
    
    # 特有の馬名リストとパターンから馬名を特定
    horse_match = re.search(r'([ァ-ヴー・\s㎡\(\)（）]+(キャスター|クラール|フラワー|ヴィーヴ|イグニション|クイーン|トニトゥルス|ミリオレ|チーフ|フォティック|ラトルシェ|シチー|ローリー|カズラ|エフォート|セニョール|[ァ-ヴー]{4,}))', line)
    
    horse_name = "不明"
    if horse_match:
        horse_name = horse_match.group(1).replace("(特)", "").strip().split()[-1]

    # 1走前の対戦馬（数字の塊と合体するバグを回避）
    vs_horse = "データなし"
    vs_match = re.search(r'([ァ-ヴー・\s]+)\s+([\d\.\-]+)\s+(\d{3})\s+\d+枠\d+人', line)
    if vs_match:
        vs_horse = vs_match.group(1).strip().split()[-1]
    else:
        vs_match_fallback = re.findall(r'([ァ-ヴー]{2,})\s+[\d\.\-]+\s+\d{3}', line)
        if vs_match_fallback:
            vs_horse = vs_match_fallback[0]

    return {
        "枠番": int(waku),
        "馬番": int(umaban),
        "馬名": horse_name,
        "騎手": jockey,
        "1走前の対戦馬": vs_horse
    }

# --- 3. 実行および画面表示 ---
if st.button("データを解析する"):
    rows = []
    for line in raw_data_input.strip().split('\n'):
        result = parse_keibabook_line(line)
        if result:
            rows.append(result)

    if rows:
        # データフレームを作成
        df = pd.DataFrame(rows)
        
        st.success("データの抽出に成功しました！")
        
        # Streamlit標準のインタラクティブなテーブルで表示（タブリエイト不要）
        st.dataframe(df, use_container_width=True)
        
        # CSVダウンロードボタンもついでに配置
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSVファイルとしてダウンロード",
            data=csv,
            file_name="keiba_parsed_data.csv",
            mime="text/csv",
        )
    else:
        st.error("有効なデータが検出できませんでした。テキストの形式を確認してください。")