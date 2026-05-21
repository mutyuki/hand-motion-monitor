# hand-motion-monitor

両手の加速度センサー(KX122)のデータを取得し、動きの有無を判定して
ネットワーク送信・ログ保存・CSV化・FTPアップロードまで行う簡易モニタです。

## 構成概要

- Spresense x2 (左手/右手): KX122の加速度をシリアル送信
- sender: 2本のシリアルを読み取り、動き状態を判定してJSONを送信
- receiver: JSONを受信してログ保存・バッチCSV化・FTP送信
- ftp_mapreduce: CSVを読み取り、キー集計をソケットで送受信(実験用)

## データフロー

1. Spresenseが`L,ax,ay,az`/`R,ax,ay,az`形式で送信
2. senderが移動判定し、JSONイベントをreceiverへ送信
3. receiverが`motion_log.jsonl`へ保存
4. BATCH_SIZE件ごとにCSV化しFTPへ送信

## 主要フォルダ

- sender/: シリアル読込・動作判定・送信
- receiver/: サーバ受信・ログ・CSV生成・FTP送信
- spresense/: 左右のSpresense用スケッチ
- ftp_mapreduce/: CSV集計の簡易MapReduce
- common/: .env読み込みユーティリティ

## 必要なもの

- Python 3.9+ (sender/receiver用)
- pyserial (sender用)
- ネットワーク接続(送信先IPへ到達できること)
- Spresense + KX122 (任意、実機利用時)

## セットアップ

1. 依存パッケージを用意

```bash
pip install pyserial
```

2. .envを編集

- [/.env](.env) を自分の環境に合わせて修正
- 主に`SENDER_SERIAL_PORTS`、`RECEIVER_HOST`、FTP先を設定

## 実行方法

### receiver (受信側)

```bash
python receiver/receiver_pi.py
```

### sender (送信側)

```bash
python sender/sender_pi.py
```

## MapReduce(実験用)

receiverで生成されたCSVを集計する簡易ツールです。

1. reducerを起動

```bash
python ftp_mapreduce/reducer.py
```

2. mapperを実行 (CSVを標準入力で流す)

```bash
cat some.csv | python ftp_mapreduce/mapper.py
```

## 環境変数(.env)

主な項目:

- `SENDER_SERIAL_PORTS`: 例 `/dev/cu.usbserial-110,/dev/cu.usbserial-1240`
- `RECEIVER_HOST` / `RECEIVER_PORT`: senderが接続する受信先
- `RECEIVER_BIND_HOST` / `RECEIVER_BIND_PORT`: receiverの待受設定
- `BATCH_SIZE`: 何件ごとにCSV化するか
- `FTP_TARGETS_JSON`: FTP送信先リスト(JSON形式)

## イベントJSON例

```json
{
	"timestamp": 1778739295.333594,
	"summary_key": "stopped",
	"summary_text": "どちらも止まっています",
	"right": {"moving": false, "ax": 0.0, "ay": 0.0, "az": 0.0},
	"left": {"moving": false, "ax": 0.0, "ay": 0.0, "az": 0.0}
}
```

## トラブルシュート

- receiverに接続できない: `RECEIVER_HOST`/`RECEIVER_PORT`とFW設定を確認
- シリアルが開けない: `SENDER_SERIAL_PORTS`のデバイス名を確認
- FTP失敗: `FTP_TARGETS_JSON`のホスト/ユーザー/パスワードを確認
