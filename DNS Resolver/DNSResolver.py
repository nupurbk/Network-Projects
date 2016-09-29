import dns.message
import dns.query
import random
from dns.rrset import RRset
from dns import rdatatype, rdata
from codecs import StreamReader
import sys
import time
from _abcoll import ItemsView
import dns.update
from dns.update import Update
#from __builtin__ import None



class Resolver():
    
    def __init__(self):
        self.referal={'rootserver':{'.NS':['a.root-servers.net.','c.root-servers.net.','k.root-servers.net.'],'Type':['A','A','A'],'IP':{'a.root-servers.net':'198.41.0.4','c.root-servers.net.':'192.33.4.12','k.root-servers.net.':'193.0.14.129'}}}
        self.answercache={}
        self.finalreferal={'rootserver':[['a.root-servers.net.','c.root-servers.net.','k.root-servers.net.'],['198.41.0.4','192.33.4.12','193.0.14.129']]}
        
    def printcache(self,answercache,finalreferal):
        
        print "\nAnswer Cache Contents:"
        for dname,result in answercache.items():
            print '\nAnswer for Query :',dname
            print '\n',result
            
        
        i=0
        print "\nReferral cache content:"
        for sname,sdata in finalreferal.items():
            print "\n",sname
            
            for i in range(len(sdata[0])):
                print sdata[0][i],":",sdata[1][i]
                i+=1
           
   
        
        
        
    def resolve(self,domainname,dnsrdatatype):
            
                aflag=1
                t0=time.clock()
                for keys in self.answercache:
                    if keys[0]==domainname and keys[1]==dnsrdatatype:
                        print "\n ***Answer is found in Answer cache"
                        print "\n***Final Answer found with latency:",str(time.clock()-t0)
                        aflag=0
                        break
                        
                if aflag==0: 
                    for dname,result in self.answercache.items():
                        if dname[0]==domainname and dname[1]==dnsrdatatype:
                            print '\n',result
                            break
                    print"*"*100
                else:  
                
                    parsedomain=domainname.split(".")
                    for keys in self.referal:
                        if keys==parsedomain[-2]+"."+parsedomain[-1]+".":
                            print "\n***NS servers for [",keys, "]present in referal section"
                            flag=1
                            break
                        
                        elif(keys==parsedomain[-1]+"."):
                            print "\n***Name servers present in referal section"
                            flag=2
                            break
                        
                        else:
                            flag=0
                        
                        
                    if(flag==0):
                        
                        print "\n***NS records fetched from referal cache :"
                        print self.referal['rootserver']['.NS']
                        dnsservernames={}
                        dnsservernames=self.referal['rootserver']['IP']
                    #print dnsservernames
                    #print dnsserverip
                        dnsservertuple=random.choice(dnsservernames.items())
                        print '\n***Name server has ',dnsservertuple[0],'Ip "%s"'%(dnsservertuple[1])
                        print '\n***QUERY name server',dnsservertuple[0],'has Ip "%s"'%(dnsservertuple[1])
                        print 'for ',domainname,'',dnsrdatatype
                        dnsserver=dnsservertuple[1]
                        t0=time.clock()
                        response=self.processquery(self.referal,self.answercache,dnsserver,dnsrdatatype,domainname,self.finalreferal)
                        #print "return response"
                        # response
                        print"*"*100
                        print "\n***QUERY ",domainname,"for RRType",dnsrdatatype
                        print "\n***Final Answer found with latency:",time.clock()-t0
                        for dname,result in self.answercache.items():
                            if dname[0]==domainname and dname[1]==dnsrdatatype:
                                print '\n',result
                                break
                        print"*"*100
                        return response
                    
                    elif (flag==1):
                        print ""
                        keyname1=parsedomain[-2]+"."+parsedomain[-1]+"."
                        print "\n***NS Server are fetched from referral cache for ",keyname1
                    
                        nsserver=random.choice(self.referal[keyname1])
                        print "\n***Name servers are for domain name",keyname1
                        #print self.referal[keyname1]
                        print "\n***NSSERVER fetched for ",nsserver
                    #nsserver
                        print '\n***QUERY name server has Ip "%s"'%(nsserver),'for ',domainname,dnsrdatatype
                     
                        t0=time.clock()
                        response=self.processquery(self.referal,self.answercache,nsserver,dnsrdatatype,domainname,self.finalreferal)
                        print"*"*100
                        print "\n***QUERY ",domainname,"for RRType",dnsrdatatype
                        print "\n***Final Answer found with latency:",time.clock()-t0
                        for dname,result in self.answercache.items():
                            if dname[0]==domainname and dname[1]==dnsrdatatype:
                                print '\n',result
                                break
                        print"*"*100
                        return response
                    
                    elif flag==2:
                        keyname1=parsedomain[-1]+"."
                        print "\n***NS Server are fetched from referral cache for ",keyname1
                        nsserver=random.choice(self.referal[keyname1])
                        print "\n***Name servers are for domain name",keyname1
                        #print self.referal[keyname1]
                        print "\n***NSSERVER fetched for ",nsserver
                    
                        print '\n***QUERY name server has Ip "%s"'%(nsserver)
                        print 'for ',domainname,dnsrdatatype
                        t0=time.clock()
                        response=self.processquery(self.referal,self.answercache,nsserver,dnsrdatatype,domainname,self.finalreferal)
                    #part repeating code
                        print"*"*100
                        print "\n***QUERY ",domainname,"for RRType",dnsrdatatype
                        print "\n***Final Answer found with latency:",time.clock()-t0
                        for dname,result in self.answercache.items():
                            if dname[0]==domainname and dname[1]==dnsrdatatype:
                                print '\n',result
                                break
                        print"*"*100
                        
                        return response
                    
    def errorValidation(self, response):
        #validations  for domain not exist
            rcode = response.rcode()
            
        #print rode
            if rcode != dns.rcode.NOERROR:
                if rcode == dns.rcode.NXDOMAIN:
                    print "\nDomain name does not exist"
                    
                    
                elif rcode==dns.rcode.REFUSED:
                    print "\nThe server refused to answer for the query"
                    
                elif rcode==dns.rcode.SERVFAIL:
                    print "\nServer failed to complete the DNS request"
                   
                else:
                    raise Exception('Error %s' % dns.rcode.to_text(rcode))
                
            
                return 1 
            else:
                return 0                   
                    
                            
    def processquery(self,referal,answercache,dnsserver,dnsrdatatype,domainname,finalreferal):
        query=dns.message.make_query(domainname,dnsrdatatype,want_dnssec=True)
        partdomain=domainname.split(".")
        querySplit1 = str(query.question).split(' ')
        t0=time.clock()
        try:
            response=dns.query.udp(query,dnsserver,timeout=10.0)
        
        except dns.exception.Timeout:
            response=None
        
        print '\n****Response Received with latency :',time.clock()-t0   
        if response==None:
            print "\n***QUERY time out error "
            #break
        print response
                    
        rcode=self.errorValidation(response)
        if rcode==1:
            answercache[domainname,dnsrdatatype]=str(response)
            return;  
        
                  
        if(len(response.authority)>=1):    
                rdatasets=response.authority
                rdataset=rdatasets[0]
                reco=str(rdataset)
                keynamelist=reco.split()
                keyname=keynamelist[0]
        
        for rr in rdatasets:
            if rr.rdtype==6:
                print "\n***Final answer is stored in cache for domain name",domainname
                answercache[domainname,dnsrdatatype]=str(response)
                return;            
                    
        while(len(response.answer)==0):
            rcode=self.errorValidation(response)
            #print "rcode is :",rcode
            if rcode==1:
                answercache[domainname,dnsrdatatype]=str(response)
                break
            if(len(response.additional)==0 or len(response.authority)==0):
                print "\n****further iteration is not possible"
                break
            rdatasets=response.authority
            rrset = response.additional
            if len(response.authority)>=1:
                rdataset=rdatasets[0]
                for rr in rdataset:
                    if rr.rdtype==6:
                        print "\n***Final answer is stored in cache for domain name",domainname
                        answercache[domainname,dnsrdatatype]=str(response)
                        return;
                reco=str(rdataset)
                keynamelist=reco.split()
                keyname=keynamelist[0]
                #print "\n Domain Name :",keyname
                nsip=[]
                nsip1=[]
                i=0
                            
                count=0         
                for rr in rrset:
                    nsip.append(rr.items[i].address)
                    resp=str(rr)
                    nsnamelist=resp.split()
                    nsname=nsnamelist[0]
                    nsip1.append(nsname)
                    count+=1
                
            count-=1   
            self.referal[keyname]=nsip
            
            finalreferal.setdefault(keyname,[]).append(nsip1)
            #print self.finalreferal[keyname]
            finalreferal.setdefault(keyname,[]).append(nsip)
            
            ns =random.choice(referal[keyname])
            print "\n***Start next iteration with domain name ",keyname
            print'\n***Name server and ip chosen for next iteration :',ns
            t0=time.clock()
            try:            
                response=dns.query.udp(query,ns,timeout=5.0)
            except dns.exception.Timeout:
                response=None
            print '\n****Response Received with latency :',time.clock()-t0    
            #print"\n***Error while querying the name server",ns
            while response==None and count!=0:
                print "\n***Query Time out"
                ns1=random.choice(referal[keyname])
                while(ns==ns1):
                   ns1=random.choice(referal[keyname]) 
                print "\n***Try with another Name server :",ns1
                try:            
                    response=dns.query.udp(query,ns,timeout=5.0)
                except dns.exception.Timeout:
                    response=None
                count-=1
                print"\n***Error while querying the name server",ns1
            if count==0 and response==None:
                print "\nServerFAIL due to time out"
                break
                #break
                
            print response
         
        
        if(response!=None and len(response.answer)>=1):
            flaga=0
            rrsets=response.answer[0]
            for rcode in rrsets:
                if rcode.rdtype==1:
                    flaga=1
                        
            #print len(rrsets)
            if len(rrsets)==1:
                if flaga==1:
                        #if rrsets.rdtype==1:
                    print("\n***Final answer is stored in cache for domain name",domainname)
                    answercache[domainname,dnsrdatatype]=str(response)
                elif rrsets.rdtype==15:
                    print "\n***Final response for MX record of domain name",domainname,"is store in Cache"
                                #print adata
                    answercache[domainname,dnsrdatatype]=str(response)
                elif rrsets.rdtype==16:
                    print "\n***Final response for TXT record of domain name",domainname,"is store in Cache"
                                #print adata
                    answercache[domainname,dnsrdatatype]=str(response)
                elif rrsets.rdtype==5:
                    print("\n***Resolve CNAME")
                    for rdata in rrsets:
                        dnscname=rdata.target#response1=Resolver.resolve1()
                    print "\nCNAME for domain name ",domainname,"is ",dnscname
                        
                    response1=self.resolve(str(dnscname),"A")
                    #print "returned response"
                    #print response1
                    for rdata in response1.answer:
                        response.answer.append(rdata)
                    
                    print "\n***Final response for A record of domain name",domainname,"is store in Cache"
                    answercache[domainname,dnsrdatatype]=str(response)
                    pass   
                    
            else:
                    rrsets=response.answer[0]
                    for adata in rrsets:
                        if adata.rdtype==1:
                            flaga=1  
                    
                    if flaga==1:
                                
                        print "\n***Final response for A record of domain name",domainname,"is store in Cache"
                        answercache[domainname,dnsrdatatype]=str(response)
                        pass
                    if adata.rdtype==15:
                        print "\n***Final response for MX record of domain name",domainname,"is store in Cache"
                                #print adata
                        answercache[domainname,dnsrdatatype]=str(response)
                    if adata.rdtype==16:
                        print "\n***Final response for TXT record of domain name",domainname,"is store in Cache"
                                #print adata
                        answercache[domainname,dnsrdatatype]=str(response)
        return response

def mainstart(): 
                   
        print "-"*25,"Dns Resolver","-"*25
        resolve1=Resolver()
        

        with open("trialfile.txt","r") as infile:
            data = infile.read()  
        my_list = data.splitlines()
        
        #print file 
        #print my_list
        i=-1
        while(i < len(my_list)):
            
            i+=1
            if my_list[i]=="print cache":
                print"Command :%s"%(my_list[i])
                resolve1.printcache(resolve1.answercache,resolve1.finalreferal)
                print '-'*100
                continue
                          
            elif my_list[i]=="quit":
                #print"-"*100
                print"Command :%s"%(my_list[i])
                print"\nProgram Terminated"
                break
            
            else:
                #read firstdomain name
                firstdomain=my_list[i].split()
                
                #print firstdomain
                domainname=firstdomain[1]
                dnsrdatatype=firstdomain[2]
                #print"-"*100
                print "\nCommand :",my_list[i]
                resolve1.resolve(domainname,dnsrdatatype)
                
                           
                    
                             
if __name__ == "__main__": mainstart()






  
    