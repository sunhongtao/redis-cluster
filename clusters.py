#!/bin/python

import sys
import os
'''
./create_clusters.py appname version clusters_ip numbers cpuset memset port
'''

#print "Number of arguments:", len(sys.argv)
#print "Argument list:",str(sys.argv)
#print "sys.argv[0]",sys.argv[0],sys.argv[1],sys.argv[2]

#appname = "redis"
#version = "20.26.25.148:5000/redis:3.0.7"
#clusters_ip = "20.26.25.147,20.26.25.148,20.26.25.149"
#instance_numbers = 3
#cpuset = 4
#memset = "100m"
#port = 6379
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
            print("You are OK,Completing the instances created!")
    print("Completing the instances.....\n\n")

def check_instance(Strcmd):
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
    
    StrCmd1 = "redis-trib.rb create --replicas 1 {}".format(IPandPort)
    logs = os.popen(StrCmd1).read()
    #print(logs)
    #print(len(logs))
    if len(logs)<240:
        print("Create master-slave clusters failed! try to create master clusters!")
        StrCmd2 = "redis-trib.rb create {}".format(IPandPort)
        logs = os.popen(StrCmd2).read()
    print(logs)
    print("Completing the clustering creating...")

if __name__ == '__main__':
    create_instance()
    create_cluster()
