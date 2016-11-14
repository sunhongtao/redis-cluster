#!/bin/python

import sys
import os
from bottle import Bottle, request, run
'''
./create_clusters.py appname version clusters_ip numbers cpuset memset port
appname = "redis"
version = "20.26.25.148:5000/redis:3.0.7"
clusters_ip = "20.26.25.147,20.26.25.148,20.26.25.149"
instance_numbers = 3
cpuset = 4
memset = "100m"
port = 6379
'''
appname=sys.argv[1]
version=sys.argv[2]
clusters_ip=sys.argv[3]
numbers=sys.argv[4]
cpuset=sys.argv[5]
memset=sys.argv[6]
port=sys.argv[7]

print appname,version,clusters_ip,memset

def create_instance():
    cluster_ips = clusters_ip.split(',')
    print("begin to create the instances....")
   
    for ip in cluster_ips:
        print ip
        Strcmd = "ssh -t root@{} docker run -d --net=host --cpu-shares {} -m {} --name {} {}".format(ip,cpuset,memset,appname,version)
        a = check_instance(Strcmd)
        if a == 0:
            Strcmd1 = "ssh -t root@{} docker rm -f {}".format(ip, appname)
            os.popen(Strcmd1)
            os.popen(Strcmd)
        else:
            print("You are OK,Completing the instance created!")
    print("Completing the instances.....\n\n")

def check_instance(Strcmd):
	'''
	Judge whether the create operation is OK
	'''
    content = os.popen(Strcmd)
    logs = content.read()
    if len(logs) > 64:
        return 0
    else:
        return 1

def create_cluster():
    IPandPort = ""
    for ip in clusters_ip.split(','):
        ipport = ':'.join([str(ip),str(port)])
        IPandPort += ipport + ' '
    print(IPandPort)
    print("Now creating the cluster.......")
    
    redis_trib_ip=clusters_ip.split(',')[0]
    StrCmd1 = "ssh -t root@{} redis-trib.rb create --replicas 1 {}".format(redis_trib_ip,IPandPort)
    logs = os.popen(StrCmd1).read()
    if len(logs) < 250:
        print("Create master-slave clusters failed! try to create master clusters!")
        StrCmd2 = "ssh -t root@{} redis-trib.rb create {}".format(redis_trib_ip,IPandPort)
        logs = os.popen(StrCmd2).read()
    print(logs)
    print("Completing the clustering creating...")
	

def delete_clusters():
	'''
	传参：应用名和IP地址群
	'''
	for ip in cluster_ips:
		Strcmd1 = "ssh -t root@{} docker rm -f {}".format(ip, appname)
        os.popen(Strcmd1)
	print("Delete the redis_clusters ok")

def create_clusters():
	'''
	首先创建单个实例，再构建集群
	传参：
	appname：
	version:
	clusters_ip:
	instance_numbers:
	cpuset:
	memset:
	port：
	'''
	create_instance()
	create_cluster()

def reload_cluster(ip, appname):
	'''
	ip: redis node ip
	appname: 应用名
	'''
	Strcmd1 = "ssh -t root@{} docker restart {}".format(ip, appname)
    os.popen(Strcmd1)
	print("Restart the redis node OK")
	
def delete_cluster(ip, appname):
	'''
	ip: redis node ip
	appname: 应用名
	'''
	Strcmd1 = "ssh -t root@{} docker rm -f {}".format(ip, appname)
    os.popen(Strcmd1)
	print("Restart the redis node OK")
	
	
if __name__ == '__main__':
	#创建集群
	create_clusters()
	#删除集群
	delete_clusters()
	#重启单个节点
	reload_cluster(ip, appname)
	#删除单个节点
	delete_cluster(ip, appname)
