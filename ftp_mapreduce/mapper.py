#IoT CSVを読み込んで、mapper処理してソケット送信
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import csv
import socket
from contextlib import closing

def map_(line):
    reader = csv.reader([line])
    # CSVの3列目をキーにして、個数を数えるために値は1とする
    for row in reader:
        # ヘッダスキップ
        if len(row) == 0 or row[2] == "summary_key":
            return []
        # summary_key をキーにする
        key = row[2]
        return [(key, 1)]
    return []


def main():
    host = '192.168.100.101'
    port = 4000
    bufsize = 4096


    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with closing(sock):
        sock.connect((host, port))
        for line in sys.stdin:
            # CSV→キー変換
            key_and_values = map_(line)
            # ソケット送信
            for key, value in key_and_values:
                msg = f"{key}\t{value}\n"
                sock.send(msg.encode('utf-8'))
        # 送信終了
        sock.send(b'EOM\n')
        # EOR待ち（Reducer完了）
        while True:
            msg = sock.recv(bufsize)
            if msg == b'EOR\n':
                print('EOR received')
                break


if __name__ == '__main__':
    main()