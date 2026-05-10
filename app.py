import streamlit as st
import re

# 抽出ロジックの核心：2行おきにデータを精査
def extract_correct_horse_data(text):
    horses = []
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for i, line in enumerate(lines):
        # 1. 馬番を探す (例: "1 1")
        num_match = re.match(r'^(\d{1,2})\s+(\d{1,2})', line)
        if num_match:
            # 2. 馬番の1行下は「父名」、2行下が「馬名」
            if i + 2 < len(lines):
                horse_num = num_match.group(2)
                true_horse_name = lines[i+2]
                # 3. 父名でないことをバリデーション
                sire_list = ["フィエールマン", "コントレイル", "キタサンブラック", "エピファネイア", "キズナ"]
                if true_horse_name in sire_list:
                    # 誤認防止：もし馬名の位置に父名が来ていたらさらに1行下をチェック
                    true_horse_name = lines[i+3] if i + 3 < len(lines) else true_horse_name
                
                horses.append({"馬番": horse_num, "馬名": true_horse_name})
    return horses

# ※この関数をメインロジックに統合
