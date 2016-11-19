###########################
Setting up a FreeIPA Client
###########################

:date: 2016-08-17
:modified: 2016-11-18
:author: omiday
:tags: fedora, freeipa, screen
:summary: FreeIPA Client setup on Fedora 25


This is the second, and perhaps not last ;) in the `FreeIPA series`_ of 
articles.  After setting up the `FreeIPA server`_ the next step is adding 
clients to the IPA domain.

Installation
============

1. Install the RPM package::

      [root@omiday]# dnf install freeipa-client

2. Run the installer::

      [root@omiday]# ipa-client-install

Done...or so I thought, moving on to the troubleshooting section...


Fixing ``ipa-client-install`` errors
====================================

:Error:
   *Inconsistency detected by ld.so: dl-close.c: 811: _dl_close: Assertion 
   `map->l_init_called' failed!*

   `Ubuntu bug 1231459`_ is still not fixed. Nothing helpful on `FreeIPA Trac`_ 
   either. Doing an *ALL* search on `RedHat Bugzilla`_ I came across the 
   `Aug-19,2016 comment in bug 1189856`_ which points to `this glibc bug`_.

   Noticed this right after logging out::

      Shared connection to stuff.can.local closed.
      pc96 ~ $ logout
      Shared connection to 192.168.0.5 closed.
      Inconsistency detected by ld.so: dl-close.c: 811: _dl_close: Assertion 
      `map->l_init_called' failed!

   *Solution*:
      None thus far.

   *Workaround*:
      `Disable gssapi-with-mic`_. Easiest in ``ssh_config`` with::

         PreferredAuthentications=gssapi-keyex,hostbased,publickey 


.. _screenlog: https://www.gnu.org/software/screen/manual/screen.html#Log 
.. _FreeIPA: https://www.freeipa.org/page/Main_Page 
.. _pudb: https://pypi.python.org/pypi/pudb 
.. _etckeeper: https://etckeeper.branchable.com/ 
.. _Radicale: http://radicale.org/ 
.. _`CA manually`: https://bugzilla.redhat.com/show_bug.cgi?id=953488#c4 
.. _`another good reason`: 
   https://www.happyassassin.net/2014/09/07/freeipa-for-amateurs-why/ 
.. _`DNS server`: 
   https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Deployment_Guide/ch-DNS_Servers.html 
.. _`leftover directories`: https://bugzilla.redhat.com/show_bug.cgi?id=953488#c4 
.. _`Fedora QA Monkey`: https://www.happyassassin.net/about/ 
.. _`Adam's FreeIPA setup notes`: 
   https://www.happyassassin.net/2013/09/27/further-sysadmin-adventures-wheres-my-freeipa-badge/ 
.. _`Fedora QA`: https://fedoraproject.org/wiki/QA 
.. _`Ubuntu bug 1231459`:  https://bugs.launchpad.net/ubuntu/+source/krb5/+bug/1231459 
.. _`FreeIPA Trac`: https://fedorahosted.org/freeipa/ 
.. _`this glibc bug`: https://bugzilla.redhat.com/show_bug.cgi?id=1264556 
.. _`Aug-19,2016 comment in bug 1189856`: https://bugzilla.redhat.com/show_bug.cgi?id=1189856#c8 
.. _`RedHat Bugzilla`: https://bugzilla.redhat.com/ 
.. _`give back`: https://fedoraproject.org/wiki/Join 
.. _`FreeIPA server`: {filename}./freeipa-server-setup.rst
.. _`FreeIPA series`: {tag}freeipa
.. _`Disable gssapi-with-mic`: https://bugzilla.redhat.com/show_bug.cgi?id=1264556#c10
