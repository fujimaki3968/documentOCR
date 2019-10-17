# TendocLetterOCR
:::docの日本語OCR部分です

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


# 2作業する上でのローカルルール
基本的なことは Kibela の　https://nittcprocon.kibe.la/notes/237　を参照

新しくライブラリをインストールした際は必ず**1.3**を実行

プログラムを書く際にはコメントなどを用いて**何を行っているのかを書き加える**
