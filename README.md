# DocumentOCR
googleのAPIを利用した書類の解析（titleの判別、表の認識等。。。）

# 1環境
- python3.6
- ライブラリ等
使用したライブラリのバージョン等は **requirements.txt** に保存する

## 1.1環境構築
- python3.6のインストール(使用OSによってインストール方法が違うので各自でググりましょう。。。）
- 1.4の方法で必要なライブラリをインストール

## 1.2作業フォルダのダウンロード
まず、任意のディレクトリで`git clone https://github.com/tnct-spc/TendocLetterOCR.git` とターミナルで実行します。
そうすると、作業フォルダをダウンロードすることができる。

## 1.3使用したライブラリを保存する方法
`pip freeze > requirements.txt` と実行環境で行えば **requirements.txt** に保存される。

## 1.4**requirements.txt** からライブラリをインストールする方法
`pip install -r requirements.txt` と実行するとライブラリがインストールされる。
