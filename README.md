# TRACK::FORGE

> Insta360 360°映像からレースシミュレータMODを自動生成するパイプライン管理アプリケーション

[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-blue)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF)](https://vite.dev/)

## 概要

TRACK::FORGEは、Insta360の360°映像からフォトグラメトリ＋3D Gaussian Splattingパイプラインを経て、複数のレースシミュレータ向けコースMODを生成するワークフロー管理アプリケーションです。レーシングテレメトリ風UIで全パイプラインを可視化・制御できます。

## 6フェーズ・パイプライン

### Phase 1 — 映像取込 (Video Ingest)
- Insta360 SDK `.insv` → equirectangularフレーム抽出
- FlowStateスタビライゼーション制御
- GPS/IMUメタデータ同期
- HDRトーンマッピング（ACES/Reinhard/Filmic）
- 走行速度に応じた1〜10fpsフレーム抽出レート
- 5760×2880 デフォルト出力解像度

### Phase 2 — SfM再構築 (Structure from Motion)
- COLMAP + SuperPoint/SuperGlue特徴点マッチング
- 360°全方位カメラモデル対応（equirectangular/fisheye/pinhole）
- GPSプリオールによるジオレファレンス
- バンドル調整＆ロバスト三角測量
- 最大8192特徴点/画像

### Phase 3 — 3D Gaussian Splatting
- SfM疎点群からの3D Gaussian配置・学習
- 位置・共分散・球面調和関数(SH)・不透明度の最適化
- 微分可能ラスタライゼーション
- Mip-Splattingアンチエイリアシング
- 最大200万Gaussian、30,000イテレーション

### Phase 4 — メッシュ変換 (Mesh Conversion)
- 表面抽出: SuGaR / 2DGS / Poisson から選択
- UV展開（xatlas/Smart UV/Lightmap）
- 4K/8Kテクスチャアトラス生成
- 法線マップ・AOマップベイク
- LOD生成（最大5段階）

### Phase 5 — コース構築 (Course Build)
- SAM2路面セグメンテーション
- GPS軌跡からのレーシングライン自動検出
- 路面材質分類（アスファルト/縁石/グラベル/芝/砂/ランブルストリップ）
- グリップマップ生成
- キャンバー・バリア・ピットレーン検出

### Phase 6 — SIMエクスポート
5つのシムフォーマットに対応:

| シム | ファイル形式 | 主な特徴 |
|------|------------|---------|
| **rFactor 2** | .MAS/.TDF/.AIW/.SCN/.GDB | ダイナミック天候、AIライン、ナイトレース |
| **Assetto Corsa** | .KN5/surfaces.ini/ai_line.fast/models.ini | カスタムシェーダー、グリップマップ |
| **ACC** | .KN5/surfaces.ini/track.json/weather.json | UE4レンダリング、ラバービルドアップ |
| **iRacing** | .W | レーザースキャン精度、マルチクラス |
| **BeamNG.drive** | .json/.prefab | ソフトボディ物理、地形変形 |

## デフォルト設定

**APG御殿場** (752mコース) がデフォルト設定として搭載されています:
- 位置: 35.3083°N, 138.9350°E
- 標高: 468m
- ターン数: 8
- コース幅: 8.5m

## セットアップ

```bash
# 依存関係のインストール
npm install

# 開発サーバー起動
npm run dev

# プロダクションビルド
npm run build

# リント実行
npm run lint
```

## 技術スタック

- **フロントエンド**: React 19 + TypeScript 6
- **ビルドツール**: Vite 8
- **UI**: レーシングテレメトリ風カスタムCSS（ダークテーマ、ネオンアクセント）
- **状態管理**: React Context + useReducer
- **パイプライン**: シミュレーションモード搭載（ブラウザ内デモ）

## プロジェクト構造

```
src/
├── types/
│   └── pipeline.ts              # 全TypeScript型定義
├── config/
│   ├── defaults.ts              # APG御殿場デフォルト設定
│   └── simFormats.ts            # シムフォーマット定義
├── store/
│   ├── pipelineContext.ts       # React Context定義
│   └── PipelineContext.tsx      # Provider & Reducer
├── hooks/
│   └── usePipeline.ts           # パイプライン操作フック
└── components/
    ├── layout/
    │   ├── Dashboard.tsx        # メインダッシュボード
    │   ├── Header.tsx           # ヘッダー（ステータス表示）
    │   └── Sidebar.tsx          # フェーズナビゲーション
    ├── pipeline/
    │   ├── PipelineOverview.tsx  # パイプラインフロー図
    │   ├── PhaseCard.tsx        # フェーズステータスカード
    │   └── PhaseProgress.tsx    # プログレスバー
    ├── phases/
    │   ├── Phase1Ingest.tsx     # 映像取込設定
    │   ├── Phase2SfM.tsx        # SfM設定
    │   ├── Phase3GaussianSplat.tsx # 3DGS設定
    │   ├── Phase4Mesh.tsx       # メッシュ変換設定
    │   ├── Phase5Course.tsx     # コース構築設定
    │   └── Phase6Export.tsx     # SIMエクスポート設定
    ├── controls/
    │   ├── PipelineControls.tsx # パイプライン制御
    │   └── ConsoleOutput.tsx    # ログ出力表示
    ├── visualization/
    │   ├── Preview3D.tsx        # 3Dプレビュー
    │   ├── MetricsPanel.tsx     # メトリクス表示
    │   └── GaussianViewer.tsx   # Gaussianビューア
    └── common/
        ├── StatusBadge.tsx      # ステータスバッジ
        ├── ParameterSlider.tsx  # パラメータスライダー
        ├── ParameterInput.tsx   # パラメータ入力
        ├── ProgressRing.tsx     # 円形プログレス
        └── Tooltip.tsx          # ツールチップ
```

## ライセンス

MIT
