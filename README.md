# Portfolio

個人のポートフォリオ用Webページです。

## 構成

- **index.html** … トップページ（About / Skills / Works / Contact）
- **styles.css** … スタイルシート

## ローカルで確認

ブラウザで `index.html` を開くか、簡易サーバーで表示できます。

```bash
# Python 3
python3 -m http.server 8000

# ブラウザで http://localhost:8000 を開く
```

## GitHub Pages で公開する場合

1. このリポジトリを GitHub にプッシュする
2. リポジトリの **Settings** → **Pages**
3. **Source** で「Deploy from a branch」を選択
4. **Branch** で `main`（または `master`）と `/ (root)` を選択して保存

しばらくすると `https://<ユーザー名>.github.io/<リポジトリ名>/` で公開されます。

## カスタマイズ

- **About** … `index.html` の「about」セクションのテキストを編集
- **Skills** … スキル名・説明を追加・変更
- **Works** … プロジェクト名・説明・リンク・画像（`work-placeholder` を `<img>` に差し替え可）を編集
- **Contact** … GitHub / Email / SNS のURLを自分のものに変更

フォントは [Google Fonts - Noto Sans JP](https://fonts.google.com/specimen/Noto+Sans+JP) を使用しています。
