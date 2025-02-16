# 経費精算エージェント

経費精算業務をサポートするAIチャットボットです。領収書の画像をアップロードして経費申請や承認の作業を行うことができます。

## 機能

- 経費精算に関する質問応答
- 領収書画像のアップロードと処理
- 経費レポートの作成・確認
- 承認待ち経費の確認・承認

## 使い方

1. 環境変数の設定
```
OPENAI_API_KEY=your-api-key
MONEYFORWARD_API_KEY=your-api-key
OFFICE_ID=your-office-id
```

2. パッケージ管理ツールuvのインストール
https://docs.astral.sh/uv/getting-started/installation/

3. 依存パッケージのインストール
`uv sync`

4. アプリケーションの実行
`uv run streamlit run agent_app.py`