####################################
What I learned from ``iptables`` log
####################################

:date: 2016-09-18
:tags: iptables


Not much, until I decided to filter out outbound traffic and then lots of 
interesting stuff surfaced, for example `UDP is preferable with Google 
Hangouts`_ or `what is QUIC`_.

From the comfort of command line::

   [root@mha ~]# journalctl -k -S yesterday | sed 's/.* \(SRC=[0-9.]\+ \).*\(DST=[0-9.]\+ \).*\(PROTO=[a-zA-Z]\+ \).*\(SPT=[0-9]\+ \).*\(DPT=[0-9]\+ \).*/\3 \5 \4 \1 
   \2/g' | grep "^PROTO" | sort -k 4,4 -k 5,5 -k 1,2 | uniq | column -t
   PROTO=TCP  DPT=22     SPT=65190  SRC=103.207.39.44    DST=192.168.254.3
   PROTO=TCP  DPT=53030  SPT=443    SRC=104.244.43.108   DST=192.168.254.3
   PROTO=TCP  DPT=22     SPT=55252  SRC=109.236.80.12    DST=192.168.254.3
   PROTO=TCP  DPT=22     SPT=62361  SRC=112.217.150.112  DST=192.168.254.3
   PROTO=TCP  DPT=22     SPT=6000   SRC=115.239.230.228  DST=192.168.254.3
   PROTO=TCP  DPT=22     SPT=6000   SRC=115.239.248.54   DST=192.168.254.3
   PROTO=TCP  DPT=22     SPT=25614  SRC=115.47.12.162    DST=192.168.254.3
   ....

I quite like that ugly command actually. The special part is using ``sort`` to 
filter on multiple columns.

Back to the listing. I don't care about SSH inbound attempts as I only allow a 
limited number of addresses::

   [root@mha ~]# journalctl -k -S yesterday | sed 's/.* \(SRC=[0-9.]\+ \).*\(DST=[0-9.]\+ \).*\(PROTO=[a-zA-Z]\+ \).*\(SPT=[0-9]\+ \).*\(DPT=[0-9]\+ \).*/\3 \5 \4 \1 \2/g' | grep "^PROTO" | sort -k 4,4 -k 5,5 -k 1,2 | uniq | column -t | grep -v "PROTO=TCP *DPT=22"
   PROTO=TCP  DPT=53030  SPT=443    SRC=104.244.43.108   DST=192.168.254.3
   PROTO=UDP  DPT=443    SPT=47281  SRC=192.168.0.11     DST=172.217.4.226
   PROTO=UDP  DPT=443    SPT=54725  SRC=192.168.0.11     DST=172.217.4.226
   PROTO=UDP  DPT=443    SPT=57885  SRC=192.168.0.11     DST=172.217.4.98
   PROTO=UDP  DPT=443    SPT=60093  SRC=192.168.0.11     DST=172.217.4.99
   PROTO=UDP  DPT=443    SPT=46422  SRC=192.168.0.11     DST=216.58.192.174
   PROTO=UDP  DPT=443    SPT=49422  SRC=192.168.0.11     DST=216.58.192.174
   ...and a whole lot of other Google IP addresses with the same DST...
   PROTO=UDP  DPT=443    SPT=48219  SRC=192.168.0.11     DST=216.58.216.99
   PROTO=UDP  DPT=443    SPT=55416  SRC=192.168.0.11     DST=216.58.216.99
   PROTO=TCP  DPT=465    SPT=43340  SRC=192.168.0.11     DST=74.125.129.16
   PROTO=UDP  DPT=27036  SPT=27036  SRC=192.168.254.251  DST=192.168.254.255
   PROTO=UDP  DPT=7533   SPT=51410  SRC=192.168.254.251  DST=255.255.255.255
   PROTO=TCP  DPT=52316  SPT=443    SRC=52.84.17.45      DST=192.168.254.3
   PROTO=TCP  DPT=36722  SPT=443    SRC=64.233.191.155   DST=192.168.254.3
   PROTO=TCP  DPT=60304  SPT=993    SRC=69.89.31.130     DST=192.168.254.3
 
I've learned that UDP/443 is `QUIC`_ so with that one out the door::

   [root@mha ~]# journalctl -k -S yesterday | sed 's/.* \(SRC=[0-9.]\+ \).*\(DST=[0-9.]\+ \).*\(PROTO=[a-zA-Z]\+ \).*\(SPT=[0-9]\+ \).*\(DPT=[0-9]\+ \).*/\3 \5 \4 \1 \2/g' | grep "^PROTO" | sort -k 4,4 -k 5,5 -k 1,2 | uniq | column -t | grep -v -e "PROTO=TCP *DPT=22" -e "PROTO=UDP *DPT=443"
   PROTO=TCP  DPT=53030  SPT=443    SRC=104.244.43.108   DST=192.168.254.3
   PROTO=TCP  DPT=465    SPT=43340  SRC=192.168.0.11     DST=74.125.129.16
   PROTO=UDP  DPT=27036  SPT=27036  SRC=192.168.254.251  DST=192.168.254.255
   PROTO=UDP  DPT=7533   SPT=51410  SRC=192.168.254.251  DST=255.255.255.255
   PROTO=TCP  DPT=52316  SPT=443    SRC=52.84.17.45      DST=192.168.254.3
   PROTO=TCP  DPT=36722  SPT=443    SRC=64.233.191.155   DST=192.168.254.3
   PROTO=TCP  DPT=60304  SPT=993    SRC=69.89.31.130     DST=192.168.254.3
 

The interesting ones from the listing above are those with a SPT in the low 
range (<1024) so let's look at the full log::

   [root@mha ~]# journalctl -k -S yesterday | egrep " SPT=[0-9]{3} "
   Sep 17 22:26:23 mha.can.local kernel: filter/INPUT: IN=enp0s29f7u2 OUT= MAC=00:24:9b:17:3a:fa:50:39:55:62:7b:5b:08:00 SRC=52.84.17.45 DST=192.168.254.3 LEN=40 TOS=0x00 PREC=0x00 TTL=247 ID=61276 DF PROTO=TCP SPT=443 DPT=52316 WINDOW=0 RES=0x00 RST URGP=0 
   Sep 17 22:26:23 mha.can.local kernel: filter/INPUT: IN=enp0s29f7u2 OUT= MAC=00:24:9b:17:3a:fa:50:39:55:62:7b:5b:08:00 SRC=64.233.191.155 DST=192.168.254.3 LEN=40 TOS=0x00 PREC=0x00 TTL=46 ID=37743 PROTO=TCP SPT=443 DPT=36722 WINDOW=0 RES=0x00 RST URGP=0 
   Sep 17 22:53:15 mha.can.local kernel: filter/INPUT: IN=enp0s29f7u2 OUT= MAC=00:24:9b:17:3a:fa:50:39:55:62:7b:5b:08:00 SRC=104.244.43.108 DST=192.168.254.3 LEN=40 TOS=0x00 PREC=0x00 TTL=58 ID=31996 DF PROTO=TCP SPT=443 DPT=53030 WINDOW=0 RES=0x00 RST URGP=0 
   Sep 17 23:32:04 mha.can.local kernel: filter/INPUT: IN=enp0s29f7u2 OUT= MAC=00:24:9b:17:3a:fa:50:39:55:62:7b:5b:08:00 SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48741 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   Sep 17 23:32:04 mha.can.local kernel: filter/INPUT: IN=enp0s29f7u2 OUT= MAC=00:24:9b:17:3a:fa:50:39:55:62:7b:5b:08:00 SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48742 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   Sep 17 23:32:05 mha.can.local kernel: filter/INPUT: IN=enp0s29f7u2 OUT= MAC=00:24:9b:17:3a:fa:50:39:55:62:7b:5b:08:00 SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48743 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   Sep 17 23:32:05 mha.can.local kernel: filter/INPUT: IN=enp0s29f7u2 OUT= MAC=00:24:9b:17:3a:fa:50:39:55:62:7b:5b:08:00 SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48744 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   Sep 17 23:32:06 mha.can.local kernel: filter/INPUT: IN=enp0s29f7u2 OUT= MAC=00:24:9b:17:3a:fa:50:39:55:62:7b:5b:08:00 SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48745 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   Sep 17 23:32:09 mha.can.local kernel: filter/INPUT: IN=enp0s29f7u2 OUT= MAC=00:24:9b:17:3a:fa:50:39:55:62:7b:5b:08:00 SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48746 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   Sep 17 23:32:14 mha.can.local kernel: filter/INPUT: IN=enp0s29f7u2 OUT= MAC=00:24:9b:17:3a:fa:50:39:55:62:7b:5b:08:00 SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48747 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   Sep 17 23:32:24 mha.can.local kernel: filter/INPUT: IN=enp0s29f7u2 OUT= MAC=00:24:9b:17:3a:fa:50:39:55:62:7b:5b:08:00 SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48748 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   Sep 17 23:32:44 mha.can.local kernel: filter/INPUT: IN=enp0s29f7u2 OUT= MAC=00:24:9b:17:3a:fa:50:39:55:62:7b:5b:08:00 SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48749 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   Sep 17 23:33:23 mha.can.local kernel: filter/INPUT: IN=enp0s29f7u2 OUT= MAC=00:24:9b:17:3a:fa:50:39:55:62:7b:5b:08:00 SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48750 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   Sep 17 23:34:43 mha.can.local kernel: filter/INPUT: IN=enp0s29f7u2 OUT= MAC=00:24:9b:17:3a:fa:50:39:55:62:7b:5b:08:00 SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48751 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 

I'm only concerned with the last part of each line, that is everything between 
``RES`` and ``UGRP``. As a side note, the most clear "official" documentation 
on ``RES`` I could ever find is on `CPAN POE::Filter::Log::IPTables`_ module 
description::

   tcp

       src_port
           The source port of the tcp packet.

       dst_port
           The destination port of the tcp packet.

       window
           The length of the TCP window.

       res
           The reserved bits.

       flags
           An arrayref. Can be any combination of "CWR" (Congestion Window 
           Reduced), "ECE" (Explicit Congestion Notification Echo), "URG" 
           (Urgent), "ACK" (Acknowledgement), "PSH" (Push), "RST" (Reset), 
           "SYN" (Synchronize), or "FIN" (Finished)

       urgp
           The urgent pointer.

Let's cleanup a bit the previous listing::

   SRC=52.84.17.45 DST=192.168.254.3 LEN=40 TOS=0x00 PREC=0x00 TTL=247 ID=61276 DF PROTO=TCP SPT=443 DPT=52316 WINDOW=0 RES=0x00 RST URGP=0 
   SRC=64.233.191.155 DST=192.168.254.3 LEN=40 TOS=0x00 PREC=0x00 TTL=46 ID=37743 PROTO=TCP SPT=443 DPT=36722 WINDOW=0 RES=0x00 RST URGP=0 
   SRC=104.244.43.108 DST=192.168.254.3 LEN=40 TOS=0x00 PREC=0x00 TTL=58 ID=31996 DF PROTO=TCP SPT=443 DPT=53030 WINDOW=0 RES=0x00 RST URGP=0 
   SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48741 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48742 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48743 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48744 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48745 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48746 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48747 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48748 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48749 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48750 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 
   SRC=69.89.31.130 DST=192.168.254.3 LEN=121 TOS=0x00 PREC=0x00 TTL=54 ID=48751 DF PROTO=TCP SPT=993 DPT=60304 WINDOW=405 RES=0x00 ACK PSH URGP=0 


The interesting fact is that TCP source port 443 is a ``RST`` flag coming from 
(in the order above) Amazon, Google and Twitter while the ``ACK PSH`` are sent 
by my host provider. The short explanation for those is that on ``iptables`` 
restart the state is lost and the packets still "on the wire" have no 
connection endpoint on my workstation's side and thus they are discarded.


.. _`UDP is preferable with Google Hangouts`: 
   https://support.google.com/a/answer/1279090?hl=en 
.. _`what is QUIC`: https://en.wikipedia.org/wiki/QUIC 
.. _`QUIC`: https://en.wikipedia.org/wiki/QUIC 
.. _`CPAN POE::Filter::Log::IPTables`: http://search.cpan.org/~paulv/POE-Filter-Log-IPTables-0.02/IPTables.pm 
