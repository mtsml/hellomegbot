# Claude用プロジェクトコンテキスト

このファイルは、Claudeがhellomegbotプロジェクトを理解し、効率的に作業できるようにするためのガイドラインです。

## プロジェクト概要

hellomegbotは、Discord Bot「ハロめぐ」のソースコードです。めぐちゃんをテーマにしたガチャやイラスト生成機能を提供します。

## アーキテクチャの重要な原則

### 1. クリーンアーキテクチャ
- **サービス層**: ビジネスロジックのみ、Discord依存なし
- **コマンド層**: Discordインターフェースのみ
- 新機能追加時は必ずこの分離を維持してください

### 2. 依存性注入
- コマンドはサービスを注入して使用
- サービスは独立してテスト可能

## ディレクトリ構造

```
src/hellomegbot/
├── main.py              # エントリーポイント、コマンド登録
├── commands/            # Discordコマンド（薄いインターフェース層）
│   └── *.py            # 各コマンドファイル
├── services/            # ビジネスロジック（Discord非依存）
│   └── *.py            # 各サービスファイル
└── utils/              # 共通ユーティリティ

tests/
├── unit/               # ユニットテスト
│   ├── commands/       # コマンドのテスト
│   └── services/       # サービスのテスト
└── integration/        # 統合テスト
```

## 重要なコマンド

### テスト実行
```bash
# 全テストを実行（これを必ず実行）
pytest tests/

# カバレッジ付き
pytest --cov=src/ tests/
```

### リントとフォーマット
```bash
# まだ設定されていませんが、将来的に追加予定
# ruff check .
# black .
```

## 新機能追加の手順

1. **サービスクラスを作成** (`services/new_feature_service.py`)
   ```python
   class NewFeatureService:
       def __init__(self):
           pass
       
       def business_logic(self):
           # Discord依存なしのロジック
           pass
   ```

2. **コマンドクラスを作成** (`commands/new_feature.py`)
   ```python
   import discord
   from ..services import NewFeatureService
   
   class NewFeature:
       def __init__(self, service: NewFeatureService = None):
           self.service = service or NewFeatureService()
       
       def register_command(self, tree):
           @tree.command(name="newfeature")
           async def newfeature(interaction: discord.Interaction):
               # Discordインターフェース処理
               pass
   ```

3. **テストを作成**
   - `tests/unit/services/test_new_feature_service.py`
   - `tests/unit/commands/test_new_feature.py`

4. **main.pyに登録**
   ```python
   # /newfeature
   new_feature_service = NewFeatureService()
   new_feature_cmd = NewFeature(service=new_feature_service)
   new_feature_cmd.register_command(tree)
   ```

## 既存のコマンド一覧

- `/hellomeg` - ハロめぐガチャ（UR/SR/R）
- `/helloruri` - ハロるりガチャ
- `/mmm-mm-mmmmmmmm` - みらくらパークガチャ（特殊確率 0.012345679）
- `/999` - 999倍画像生成（2行のテキスト入力）
- `/meggen` - ハロめぐイラスト作成（複数種類から選択）
- `/keibaresult` - 競馬結果報告（勝ち/負け/引き分け）

## ガチャシステムの仕様

### 基本確率
- UR: 3% (デフォルト)
- SR: 18% (デフォルト)
- R: 79%

### フィーバータイム
- 特定の分（環境変数で設定）にUR確率が100%になる
- HellomegServiceのみ実装

### 画像管理
- 画像URLはJSONファイルで管理
- 初回実行時にダウンロードしてキャッシュ

## 環境変数

```bash
DISCORD_BOT_TOKEN=必須
HELLOMEG_FEVER_MINUTE=0
HELLOMEG_UR_PROBABILITY=0.03
HELLOMEG_SR_PROBABILITY=0.18
HELLORURI_UR_PROBABILITY=0.03
HELLORURI_SR_PROBABILITY=0.18
MMM_MM_MMMMMMMM_UR_PROBABILITY=0.012345679
MMM_MM_MMMMMMMM_SR_PROBABILITY=0.18
```

## コーディング規約

1. **インポート順序**
   - 標準ライブラリ
   - サードパーティ
   - ローカルモジュール

2. **命名規則**
   - クラス: PascalCase
   - 関数/変数: snake_case
   - 定数: UPPER_SNAKE_CASE

3. **ドキュメント**
   - クラスと公開メソッドにはdocstring必須
   - 日本語でOK

4. **エラーハンドリング**
   - ユーザー向けエラーは日本語
   - ログは簡潔に

## よくある作業

### バグ修正
1. まず該当するテストを書く（失敗することを確認）
2. バグを修正
3. テストが通ることを確認

### リファクタリング
1. 既存のテストが通ることを確認
2. リファクタリング実施
3. テストが変わらず通ることを確認

### 新しい画像の追加
1. `assets/`ディレクトリに配置
2. 必要に応じてJSONファイルを更新
3. サービスクラスで画像パスを設定

## デバッグのヒント

- `log()`関数が各所で使用されている（現在は`print`のラッパー）
- Discordのインタラクションは`ephemeral=True`でユーザーのみに表示可能
- 画像送信は`discord.File`を使用

## 注意事項

1. **絶対にやってはいけないこと**
   - サービス層にDiscord依存を持ち込む
   - テストなしでのコミット
   - main.pyの構造を大きく変更

2. **推奨事項**
   - 小さな変更でも必ずテストを実行
   - 不明な点は既存のコードパターンを参考に
   - コミットメッセージは明確に

## トラブルシューティング

### テストが失敗する場合
```bash
# キャッシュをクリア
find . -type d -name __pycache__ -exec rm -rf {} +
pytest --cache-clear tests/
```

### ImportError
- `pytest.ini`の`pythonpath = src`設定を確認
- 相対インポートが正しいか確認

### Discord.pyのasyncioエラー
- モーダルなどのUIコンポーネントはイベントループが必要
- テストではモックを使用すること