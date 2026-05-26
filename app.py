if st.button("🚀 全頭精密診断・中央芝ダート適性解析"):
        if not api_key:
            st.error("⚠️ APIキーが未設定です。")
        elif not manual_data:
            st.warning("⚠️ データが空です。")
        else:
            with st.spinner("AIモデルを探索し、解析を開始しています..."):
                try:
                    genai.configure(api_key=api_key)
                    
                    # 💡 【重要修正】利用可能なモデルをリストアップして、その中から選ぶ
                    models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    # 'flash'系が現在最も安定しています。なければ最初に見つかったものを使用
                    selected_model = next((m for m in models if "gemini-1.5-flash" in m.name), models[0])
                    model = genai.GenerativeModel(selected_model.name)
                    
                    st.write(f"使用中モデル: {selected_model.name}") # 動作確認用
                    
                    prompt = f"データ: {manual_data}\nバイアス: {bias}\n指示: JRA芝・ダート適性を◎○▲△で評価せよ。"
                    response = model.generate_content(prompt)
                    
                    st.session_state["res"] = response.text
                    st.success("✅ 解析完了")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 解析エラー: {e}")
                    st.info("💡 ヒント: APIキーが正しいか、Google AI Studioで有効化されているか確認してください。")
