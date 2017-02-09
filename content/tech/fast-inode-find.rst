###########################################
Quickly find file path when given its inode
###########################################

:date: 2016-11-30
:tags: debugfs, inode


`This tip`_ returns the file path almost instantly::

   [root@omiday ~]# time find / -xdev -inum 2883629
   /var/log/dnf.librepo.log-20161120

   real    0m17.867s
   user    0m0.575s
   sys     0m8.186s


   [root@omiday ~]# time debugfs -R 'ncheck 2883629' /dev/dm-1
   debugfs 1.43.3 (04-Sep-2016)
   Inode   Pathname
   2883629 /var/log/dnf.librepo.log-20161120

   real    0m0.316s
   user    0m0.149s
   sys     0m0.162s


.. _`This tip`: https://unix.stackexchange.com/questions/35292/quickly-find-which-files-belongs-to-a-specific-inode-number
