#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from collections import defaultdict
import socket
from contextlib import closing  # ソケットのwith構文に必要

# 集計結果を入れる辞書
results = defaultdict(int)

def reduce(line):
    # 入力された行をスペースで区切る
    key, value = line.split()
    # キーごとに出現回数をカウントする
    results[key] += int(value)

def main():
    host = '192.168.100.101'
    port = 4000
    backlog = 10
    bufsize = 4096

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    with closing(sock):

        sock.bind((host, port))
        sock.listen(backlog)

        while True:

            conn, address = sock.accept()

            with closing(conn):

                while True:

                    msg = conn.recv(bufsize)

                    if len(msg) == 0:
                        break

                    text = msg.decode('utf-8')

                    for line in text.splitlines():

                        if not line:
                            continue

                        # Map処理終了通知
                        if line.strip() == 'EOM':
                            print("\n=== Result ===")

                            for key, value in results.items():
                                print(f"{key} : {value}")

                            return

                        # Reduce処理
                        reduce(line)

                        # Reduce完了通知
                        conn.send(b'EOR\n')

if __name__ == '__main__':
    main()