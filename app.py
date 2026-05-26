# サイドバーの猛省ボタン部分を以下のように修正してください
    st.header("🏁 結果コピペ・猛省")
    result_copypaste = st.text_area("レース結果をコピペ", height=150)
    
    if st.button("🚨 照合して猛省レポート"):
        if "res" not in st.session_state or not st.session_state["res"]:
            st.error("先に過去の予想指示書を呼び出してください。")
        elif not result_copypaste:
            st.error("レース結果を貼り付けてください。")
        else:
            with st.spinner("猛省レポート生成中..."):
                try:
                    genai.configure(api_key=api_key)
                    # 接続モデルを自動取得
                    models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model = genai.GenerativeModel(models[0].name)
                    
                    prompt = f"""
                    【当時の予想指示書】
                    {st.session_state['res']}
                    
                    【今回のレース結果】
                    {result_copypaste}
                    
                    指示: 上記を比較・分析し、展開の読み、トラックバイアスのズレ、軸馬の選定理由などを含めた厳しい「猛省レポート」を生成せよ。
                    """
                    response = model.generate_content(prompt)
                    
                    # 結果を上書き保存
                    st.session_state["res"] += f"\n\n--- 🏁 【猛省レポート】 ---\n{response.text}"
                    st.success("猛省レポートを作成しました！")
                    st.rerun() # ここで画面を更新して表示を反映させる
                except Exception as e:
                    st.error(f"猛省解析エラー: {e}")
