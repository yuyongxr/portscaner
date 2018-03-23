#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: yuyongxr

import socket,time,re,sys,os,threading
import gevent
from gevent import monkey
monkey.patch_all()

socket.setdefaulttimeout(2)

#该方法用来处理用户数据的port范围，并计算范围内的port，将其添加到列表中，将列表返回
def handle_port(input_ports):
    try:
        pattern = re.compile('(^\d{1,5})-(\d{1,5}$)')
        match = pattern.match(input_ports)
        if match:
            start_port = int(match.group(1))
            end_port = int(match.group(2))
            if end_port <=65535 :
                if start_port < end_port:
                    list =[]
                    for i in range(start_port, end_port+1):
                        list.append(i)
                    return list
            else:
                print("端口范围输入有误")
                exit(0)
        else:
            print("端口格式输入格式有误。")
            exit(0)
    except Exception as err:
        print(err)
        exit(0)

#该方法用来处理用户数据的IP地址范围，并计算范围内的IP地址，将其添加到列表中，将列表返回
def handle_ip(input_addrs):

    try:
        pattern = re.compile('(\d{1,3}\.\d{1,3}\.\d{1,3}\.)(\d{1,3})-(\d{1,3})')  # 匹配标准点进制的IP
        match = pattern.match(input_addrs)
        if match:
            list = []
            for i in range(int(match.group(2)),int(match.group(3))+1):
                addr = match.group(1)+str(i)
                list.append(addr)
            return list
        else:
            print("ip地址格式输入有误")
            exit(0)
    except Exception as err:
        print(err)
        exit(0)

#调用socket方法进行tcp端口扫描，client.connect()方法的返回值如果为None，则说明端口开放，若无返回值，说明连接超时，就没有返回值
def scaner(ip,port):
    try:
        client = socket.socket()
        res = client.connect((ip,port))
        if not res:
            open_port = []
            print(ip,":",port," is open")
            open_port.append((ip,port))
            return open_port

    except Exception as e:
        pass

    finally:
        client.close()

#本方法对传递来的列表ports进行循环，每次循环启动一个协程，在协程内部将port和addr进行配对，并调用scaner方法进行扫描
def coroutine_scan(addr,ports):
    list = []
    for port in ports:
        eve = gevent.spawn(scaner, addr, port)
        list.append(eve)
    gevent.joinall(list)

#本方法对传递来的列表addrs进行循环，每一次循环启动一个进程，并将addrs循环出来的数据和ports列表传递给coroutine_scan方法
def thread_scan(addrs,ports):
    for addr in addrs:
        t = threading.Thread(target=coroutine_scan, args=(addr, ports))
        t.start()

#本方法用来接收参数，并调用handle_port,handle_ip对输入的内容进行处理，然后将返回的列表数据传递给thread_scan
def main():

    input_addrs = input("输入IP地址范围：如'192.168.0.1-45'\n>>").strip()
    input_ports = input("输入端口范围：如'1000-1005'\n>>").strip()

    if len(input_addrs) and len(input_addrs)> 0:

        ports = handle_port(input_ports)
        addrs = handle_ip(input_addrs)

        print("开始扫描.......")
        thread_scan(addrs,ports)

    else:
        print("请输入正确的IP地址范围和端口。")
        main()

if __name__ == "__main__":
    main()

