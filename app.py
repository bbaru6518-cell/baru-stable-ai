def extract_horse_data_v15_3(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    horses = []
    for i, line in enumerate(lines):
        # 「枠番・馬番」の数字2つを起点にする
        if re.match(r'^(\d{1,2})\s+(\d{1,2})', line):
            num = line.split()[-1] # 行の最後にある数字を馬番とする
            
            # 【鉄則】i+1行目(父名)はゴミ箱へ。i+2行目を真の馬名として固定。
            if i + 2 < len(lines):
                true_name = lines[i+2]
                
                # 人気・オッズはその後15行以内から探す
                pop, odds = 99, "0.0"
                for j in range(i, min(i+15, len(lines))):
                    p_match = re.search(r'(\d+\.\d+)\s+\((\d+)人気\)', lines[j])
                    if p_match:
                        odds, pop = p_match.group(1), int(p_match.group(2))
                        break
                
                horses.append({"馬番": num, "馬名": true_name, "人気": pop, "オッズ": odds})
    return horses
