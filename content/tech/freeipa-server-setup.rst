###########################
Setting up a FreeIPA Server
###########################

:date: 2016-08-17
:author: omiday
:tags: fedora, freeipa, screen
:summary: FreeIPA Server Setup on Fedora 24

.. contents::
.. sectnum::

As I `recently`_ started volunteering for `Fedora QA`_ one of the tasks was 
testing `this sssd bug`_. While I did test ``sssd`` `in the past`_ at the time 
I was using a freshly installed environment from the Fedora 24 Server ISO 
install which comes with FreeIPA_ pre-configured. This time I wanted to have my 
own FreeIPA environment just like the `Fedora QA Monkey`_. Monkey say, monkey 
do.

As it turned out the hardest part was finding the right `FreeIPA Quick Start  
Guide`_, unless you are like me and never try the easy way first. With a few 
preparatory steps the installation is surprisingly straightforward. The hard 
part is cleaning up after a failed install in order to allow the installer 
complete.

Besides being able to `give back`_ there is `another good reason`_ for having a 
local FreeIPA server.

Prerequisites
=============

I chose to setup my own `DNS server`_.

Also worth reading is `Adam's FreeIPA setup notes`_.


Installation
============

1. Start with the usual incantation::

      [root@stuff]# dnf install freeipa-server

2. Run the installer::

      [root@stuff]# ipa-server-install

3. Test the server install by following the steps in the `FreeIPA Quick Start  
   Guide`_

That's it! (???) ;)


Troubleshooting
===============


Cleaning up after a failed install
----------------------------------

1. Run the IPA uninstaller::

      [root]# ipa-server-install --uninstall

2. Remove `leftover directories`_::

      [root]# pkidestroy -s CA -i pki-tomcat; \
              rm -rf /var/log/pki/pki-tomcat; \
              rm -rf /etc/sysconfig/pki-tomcat; \
              rm -rf /etc/sysconfig/pki/tomcat/pki-tomcat; \
              rm -rf /var/lib/pki/pki-tomcat; \
              rm -rf /etc/pki/pki-tomcat
 

Fixing ``ipa-server-install`` errors
------------------------------------

:Error:
      *Cannot connect to the server due to generic error*::

            Cannot connect to the server due to generic error: cannot connect to 'https://freeipa.can.local/ipa/json': Could not connect to freeipa.can.local using any address
            : (PR_ADDRESS_NOT_SUPPORTED_ERROR) Network address type not supported.
            Installation failed. As this is IPA server, changes will not be rolled back.
            ipa.ipapython.install.cli.install_tool(Server): ERROR    Configuration of client side components failed!
            ipa.ipapython.install.cli.install_tool(Server): ERROR    The ipa-server-install command failed. See /var/log/ipaserver-install.log for more information

   *Solution*:

   This is a bit more involved:

   1. Undo the RPM install ``dnf`` transaction::

         [root]# dnf undo last

   2. Revert any custom changes ``httpd`` configuration. Luckily etckeeper_ makes 
      it easy::
         
         [root]# cd /etc
         [root]# git hist
         [root]# git co <commit>

      .. note::
         ``hist`` and ``co`` are the common one listed on Internet::

            co = checkout
            hist = log --pretty=format:\"%h %ad | %s%d [%an]\" --graph --date=short
   
   3. Kill any Python processes related to IPA::

         3341 /usr/bin/python2 /usr/sbin/custodia /etc/ipa/custodia/custodia.conf
   

:Error:
      *groupadd during subsequent ``dnf install``*::

         Installing  : mod_auth_gssapi-1.4.1-1.fc24.x86_64         39/99
         groupadd: failure while writing changes to /etc/gshadow

         Installing  : nuxwdog-client-java-1.0.3-6.fc24.x86_64     75/99
         groupadd: failure while writing changes to /etc/gshadow

         Installing  : mod_nss-1.0.12-4.fc24.x86_64                97/99
         mod_nss certificate database generated.
         groupadd: failure while writing changes to /etc/gshadow

   *Solution*:

   Checking SELinux AVCs::

      ausearch -m avc -ts recent | audit2allow groupadd

   turns out that a mislabelled ``/etc/gshadow``::

      [root@stuff etc]# cat ~/selinux/groupadd.te 

      module groupadd 1.0;

      require {
            type etc_t;
            type groupadd_t;
            class file write;
      }

      #============= groupadd_t ==============

      #!!!! WARNING: 'etc_t' is a base type.
      #!!!! The file '/etc/gshadow-' is mislabeled on your system.  
      #!!!! Fix with $ restorecon -R -v /etc/gshadow-
      allow groupadd_t etc_t:file write;

  
:Error:
      *ipa-server-upgrade failed*::

         IPA server upgrade failed: Inspect /var/log/ipaupgrade.log and run command ipa-server-upgrade manually.
         Unexpected error - see /var/log/ipaupgrade.log for details:
         IOError: [Errno 2] No such file or directory: u'/etc/dirsrv/slapd-EXAMPLE-COM/dse.ldif.modified.out'
         The ipa-server-upgrade command failed. See /var/log/ipaupgrade.log for more information

   ``freeipa-server`` post-install script shows::

      [root@stuff etc]# rpm -q --scripts --triggers freeipa-server
      preinstall scriptlet (using /bin/sh):
      ...
      posttrans scriptlet (using /bin/sh):
      # don't execute upgrade and restart of IPA when server is not installed
      python2 -c "import sys; from ipaserver.install import installutils; sys.exit(0 if installutils.is_ipa_configured() else 1);" > /dev/null 2>&1

      if [  $? -eq 0 ]; then
         # This must be run in posttrans so that updates from previous
         # execution that may no longer be shipped are not applied.
         /usr/sbin/ipa-server-upgrade --quiet >/dev/null || :

         # Restart IPA processes. This must be also run in postrans so that plugins
         # and software is in consistent state
         # NOTE: systemd specific section

         /bin/systemctl is-enabled ipa.service >/dev/null 2>&1
         if [  $? -eq 0 ]; then
            /bin/systemctl restart ipa.service >/dev/null 2>&1 || :
         fi
      fi
      # END
   
   Armed with that piece of information we can start debugging::

      709     def is_ipa_configured():
      710         """
      711         Using the state and index install files determine if IPA is already
      712         configured.
      713         """
      714         installed = False
      715     
      716         sstore = sysrestore.StateFile(paths.SYSRESTORE)
      717         fstore = sysrestore.FileStore(paths.SYSRESTORE)
      718     
      719  ->     for module in IPA_MODULES:
      720             if sstore.has_state(module):
      721                 root_logger.debug('%s is configured' % module)
      722                 installed = True
      723             else:
      724                 root_logger.debug('%s is not configured' % module)
      725     
      726         if fstore.has_files():
      727             root_logger.debug('filestore has files')
      728             installed = True
      729         else:
      730             root_logger.debug('filestore is tracking no files')
      731     
      732         return installed
   
   The important bits are ``sstore`` and ``fstore`` paths::

      (Pdb) sstore.__dict__
      {'modules': {}, '_path': '/var/lib/ipa/sysrestore/sysrestore.state'}
      (Pdb) fstore.__dict__
      {'random': <random.Random object at 0x55be410a8090>, 'files': {}, '_index': '/var/lib/ipa/sysrestore/sysrestore.index', '_path': '/var/lib/ipa/sysrestore'}
      (Pdb) 

   Hence we need to keep an eye on ``/var/lib/ipa`` and more precisely the 
   packages owning them::

      [root]# ls -d /var/lib/ipa* \
               | while read q ; do \
                     echo "${q}: $(rpm -qf ${q})" ; \
                 done

   should return::

      /var/lib/ipa: freeipa-server-common-4.3.2-1.fc24.noarch
      /var/lib/ipa-client: freeipa-client-common-4.3.2-1.fc24.noarch
 
   *Solution*:

   After removing ``freeipa-server`` (and its dependencies as shown in the 
   ``dnf`` transaction) remove the directories::

      /var/lib/ipa*


:Error:
      *Apache is already configured with a listener on port 443*::

         Apache is already configured with a listener on port 443:
         *:443                  freeipa.can.local (/etc/httpd/conf.d/ssl.conf:56) 
         ipa.ipapython.install.cli.install_tool(Server): ERROR    Aborting installation
         ipa.ipapython.install.cli.install_tool(Server): ERROR    The ipa-server-install command failed. See /var/log/ipaserver-install.log for more information

   *Solution*::

      [root@stuff etc]# git diff /etc/httpd/conf/httpd.conf
      diff --git a/httpd/conf/httpd.conf b/httpd/conf/httpd.conf
      index e61bfab..1f0bd8f 100644
      --- a/httpd/conf/httpd.conf
      +++ b/httpd/conf/httpd.conf
      @@ -353,6 +353,6 @@ EnableSendfile on
      ## no don't do this - too much cross pollution for vhosts
      # 
      # for freeipa install
      -IncludeOptional conf.d/*.conf
      +##IncludeOptional conf.d/*.conf
      # default vhost
      ##after freeipa## Include conf.d/vhost.d/*.conf

   Better yet remove ``mod_ssl`` altogether.   

:Error:
      *Failed to configure CA instance*::

         ipa.ipaserver.install.cainstance.CAInstance: CRITICAL Failed to configure CA instance: Command '/usr/sbin/pkispawn -s CA -f /tmp/tmpufFDF7' returned non-zero exit status 1
         ipa.ipaserver.install.cainstance.CAInstance: CRITICAL See the installation logs and the following files/directories for more information:
         ipa.ipaserver.install.cainstance.CAInstance: CRITICAL   /var/log/pki/pki-tomcat
           [error] RuntimeError: CA configuration failed.
         ipa.ipapython.install.cli.install_tool(Server): ERROR    CA configuration failed.
         ipa.ipapython.install.cli.install_tool(Server): ERROR    The ipa-server-install command failed. See /var/log/ipaserver-install.log for more information
 
   The logs at ``/var/log/pki/pki-tomcat`` show::

      [17/Aug/2016:19:49:43][http-bio-8443-exec-3]: createBaseDN: Unable to add o=ipaca: netscape.ldap.LDAPException: error result (68)
      Failed to create root entry: netscape.ldap.LDAPException: error result (68)
              at com.netscape.cms.servlet.csadmin.ConfigurationUtils.createBaseEntry(ConfigurationUtils.java:1530)
              ...
      Caused by: netscape.ldap.LDAPException: error result (68)
              at netscape.ldap.LDAPConnection.checkMsg(Unknown Source)
              at netscape.ldap.LDAPConnection.add(Unknown Source)
              at netscape.ldap.LDAPConnection.add(Unknown Source)
              at netscape.ldap.LDAPConnection.add(Unknown Source)
              at com.netscape.cms.servlet.csadmin.ConfigurationUtils.createBaseEntry(ConfigurationUtils.java:1527)
              ... 67 more
      [17/Aug/2016:19:49:43][http-bio-8443-exec-3]: Error in populating database: Failed to create root entry: netscape.ldap.LDAPException: error result (68)

   *Solution*:

   1. Uninstall ``freeipa-server``::

         [root]# ipa-server-install --uninstall

   2. Remove `CA manually`_::

         pkidestroy -s CA -i pki-tomcat
         rm -rf /var/log/pki/pki-tomcat
         rm -rf /etc/sysconfig/pki-tomcat
         rm -rf /etc/sysconfig/pki/tomcat/pki-tomcat
         rm -rf /var/lib/pki/pki-tomcat
         rm -rf /etc/pki/pki-tomcat

   3. Find and kill any ``java`` processes related to IPA::

         [root@stuff etc]# pgrep -f java -a
         7825 /usr/lib/jvm/jre-1.8.0-openjdk/bin/java -DRESTEASY_LIB=/usr/share/java/resteasy -Djava.library.path=/usr/lib64/nuxwdog-jni -classpath /usr/share/tomcat/bin/bootstrap.jar:/usr/share/tomcat/bin/tomcat-juli.jar:/usr/lib/java/commons-daemon.jar -Dcatalina.base=/var/lib/pki/pki-tomcat -Dcatalina.home=/usr/share/tomcat -Djava.endorsed.dirs= -Djava.io.tmpdir=/var/lib/pki/pki-tomcat/temp -Djava.util.logging.config.file=/var/lib/pki/pki-tomcat/conf/logging.properties -Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager -Djava.security.manager -Djava.security.policy==/var/lib/pki/pki-tomcat/conf/catalina.policy org.apache.catalina.startup.Bootstrap start


Conclusion
==========

Installing FreeIPA_ on my Fedora 24 box could have been quite straightforward, 
provided I had learned about pitfalls before starting the process. That is why 
`some may recommend` running the server on its own host. I was successful in 
running it alongside my other hosted applications.

``ipa-server-install`` works well, installing and uninstalling, provided that 
the cleanup process is done. Here's the installation screenlog_::

   [root@stuff]# ipa-server-install

   The log file for this installation can be found in /var/log/ipaserver-install.log
   ==============================================================================
   This program will set up the FreeIPA Server.

   This includes:
   * Configure a stand-alone CA (dogtag) for certificate management
   * Configure the Network Time Daemon (ntpd)
   * Create and configure an instance of Directory Server
   * Create and configure a Kerberos Key Distribution Center (KDC)
   * Configure Apache (httpd)

   To accept the default shown in brackets, press the Enter key.

   Do you want to configure integrated DNS (BIND)? [no]:

   Enter the fully qualified domain name of the computer
   on which you're setting up server software. Using the form
   <hostname>.<domainname>
   Example: master.example.com.


   Server host name [stuff.can.local]:

   The domain name has been determined based on the host name.

   Please confirm the domain name [can.local]:

   The kerberos protocol requires a Realm name to be defined.
   This is typically the domain name converted to uppercase.

   Please provide a realm name [CAN.LOCAL]:
   Certain directory server operations require an administrative user.
   This user is referred to as the Directory Manager and has full access
   to the Directory for system management tasks and will be added to the
   instance of directory server created for IPA.
   The password must be at least 8 characters long.

   Directory Manager password:

   Password (confirm):


   The IPA server requires an administrative user, named 'admin'.
   This user is a regular system account used for IPA server administration.

   IPA admin password:

   Password (confirm):



   The IPA Master Server will be configured with:
   Hostname:       stuff.can.local
   IP address(es): 192.168.0.9
   Domain name:    can.local
   Realm name:     CAN.LOCAL

   Continue to configure the system with these values? [no]: yes

   The following operations may take some minutes to complete.
   Please wait until the prompt is returned.

   Configuring NTP daemon (ntpd)
   [1/4]: stopping ntpd
   [2/4]: writing configuration
   [3/4]: configuring ntpd to start on boot
   [4/4]: starting ntpd
   Done configuring NTP daemon (ntpd).
   Configuring directory server (dirsrv). Estimated time: 1 minute
   [1/46]: creating directory server user
   [2/46]: creating directory server instance
   [3/46]: restarting directory server
   [4/46]: adding default schema
   [5/46]: enabling memberof plugin
   [6/46]: enabling winsync plugin
   [7/46]: configuring replication version plugin
   [8/46]: enabling IPA enrollment plugin
   [9/46]: enabling ldapi
   [10/46]: configuring uniqueness plugin
   [11/46]: configuring uuid plugin
   [12/46]: configuring modrdn plugin
   [13/46]: configuring DNS plugin
   [14/46]: enabling entryUSN plugin
   [15/46]: configuring lockout plugin
   [16/46]: configuring topology plugin
   [17/46]: creating indices
   [18/46]: enabling referential integrity plugin
   [19/46]: configuring certmap.conf
   [20/46]: configure autobind for root
   [21/46]: configure new location for managed entries
   [22/46]: configure dirsrv ccache
   [23/46]: enabling SASL mapping fallback
   [24/46]: restarting directory server
   [25/46]: adding sasl mappings to the directory
   [26/46]: adding default layout
   [27/46]: adding delegation layout
   [28/46]: creating container for managed entries
   [29/46]: configuring user private groups
   [30/46]: configuring netgroups from hostgroups
   [31/46]: creating default Sudo bind user
   [32/46]: creating default Auto Member layout
   [33/46]: adding range check plugin
   [34/46]: creating default HBAC rule allow_all
   [35/46]: adding sasl mappings to the directory
   [36/46]: adding entries for topology management
   [37/46]: initializing group membership
   [38/46]: adding master entry
   [39/46]: initializing domain level
   [40/46]: configuring Posix uid/gid generation
   [41/46]: adding replication acis
   [42/46]: enabling compatibility plugin
   [43/46]: activating sidgen plugin
   [44/46]: activating extdom plugin
   [45/46]: tuning directory server
   [46/46]: configuring directory to start on boot
   Done configuring directory server (dirsrv).
   Configuring certificate server (pki-tomcatd). Estimated time: 3 minutes 30 seconds
   [1/28]: creating certificate server user
   [2/28]: configuring certificate server instance
   [3/28]: stopping certificate server instance to update CS.cfg
   [4/28]: backing up CS.cfg
   [5/28]: disabling nonces
   [6/28]: set up CRL publishing
   [7/28]: enable PKIX certificate path discovery and validation
   [8/28]: starting certificate server instance
   [9/28]: creating RA agent certificate database
   [10/28]: importing CA chain to RA certificate database
   [11/28]: fixing RA database permissions
   [12/28]: setting up signing cert profile
   [13/28]: setting audit signing renewal to 2 years
   [14/28]: restarting certificate server
   [15/28]: requesting RA certificate from CA
   [16/28]: issuing RA agent certificate
   [17/28]: adding RA agent as a trusted user
   [18/28]: authorizing RA to modify profiles
   [19/28]: configure certmonger for renewals
   [20/28]: configure certificate renewals
   [21/28]: configure RA certificate renewal
   [22/28]: configure Server-Cert certificate renewal
   [23/28]: Configure HTTP to proxy connections
   [24/28]: restarting certificate server
   [25/28]: migrating certificate profiles to LDAP
   [26/28]: importing IPA certificate profiles
   [27/28]: adding default CA ACL
   [28/28]: updating IPA configuration
   Done configuring certificate server (pki-tomcatd).
   Configuring directory server (dirsrv). Estimated time: 10 seconds
   [1/3]: configuring ssl for ds instance
   [2/3]: restarting directory server
   [3/3]: adding CA certificate entry
   Done configuring directory server (dirsrv).
   Configuring Kerberos KDC (krb5kdc). Estimated time: 30 seconds
   [1/9]: adding kerberos container to the directory
   [2/9]: configuring KDC
   [3/9]: initialize kerberos container
   [4/9]: adding default ACIs
   [5/9]: creating a keytab for the directory
   [6/9]: creating a keytab for the machine
   [7/9]: adding the password extension to the directory
   [8/9]: starting the KDC
   [9/9]: configuring KDC to start on boot
   Done configuring Kerberos KDC (krb5kdc).
   Configuring kadmin
   [1/2]: starting kadmin
   [2/2]: configuring kadmin to start on boot
   Done configuring kadmin.
   Configuring ipa_memcached
   [1/2]: starting ipa_memcached
   [2/2]: configuring ipa_memcached to start on boot
   Done configuring ipa_memcached.
   Configuring ipa-otpd
   [1/2]: starting ipa-otpd
   [2/2]: configuring ipa-otpd to start on boot
   Done configuring ipa-otpd.
   Configuring ipa-custodia
   [1/5]: Generating ipa-custodia config file
   [2/5]: Making sure custodia container exists
   [3/5]: Generating ipa-custodia keys
   [4/5]: starting ipa-custodia
   [5/5]: configuring ipa-custodia to start on boot
   Done configuring ipa-custodia.
   Configuring the web interface (httpd). Estimated time: 1 minute
   [1/21]: setting mod_nss port to 443
   [2/21]: setting mod_nss cipher suite
   [3/21]: setting mod_nss protocol list to TLSv1.0 - TLSv1.2
   [4/21]: setting mod_nss password file
   [5/21]: enabling mod_nss renegotiate
   [6/21]: adding URL rewriting rules
   [7/21]: configuring httpd
   [8/21]: configure certmonger for renewals
   [9/21]: setting up httpd keytab
   [10/21]: setting up ssl
   [11/21]: importing CA certificates from LDAP
   [12/21]: setting up browser autoconfig
   [13/21]: publish CA cert
   [14/21]: clean up any existing httpd ccache
   [15/21]: configuring SELinux for httpd
   [16/21]: create KDC proxy user
   [17/21]: create KDC proxy config
   [18/21]: enable KDC proxy
   [19/21]: restarting httpd
   [20/21]: configuring httpd to start on boot
   [21/21]: enabling oddjobd
   Done configuring the web interface (httpd).
   Applying LDAP updates
   Upgrading IPA:
   [1/9]: stopping directory server
   [2/9]: saving configuration
   [3/9]: disabling listeners
   [4/9]: enabling DS global lock
   [5/9]: starting directory server
   [6/9]: upgrading server
   [7/9]: stopping directory server
   [8/9]: restoring configuration
   [9/9]: starting directory server
   Done.
   Restarting the directory server
   Restarting the KDC
   Sample zone file for bind has been created in /tmp/sample.zone.W0Qp3A.db
   Restarting the web server
   Configuring client side components
   Using existing certificate '/etc/ipa/ca.crt'.
   Client hostname: stuff.can.local
   Realm: CAN.LOCAL
   DNS Domain: can.local
   IPA Server: stuff.can.local
   BaseDN: dc=can,dc=local

   Skipping synchronizing time with NTP server.
   New SSSD config will be created
   Configured sudoers in /etc/nsswitch.conf
   Configured /etc/sssd/sssd.conf
   trying https://stuff.can.local/ipa/json
   Forwarding 'ping' to json server 'https://stuff.can.local/ipa/json'
   Forwarding 'ca_is_enabled' to json server 'https://stuff.can.local/ipa/json'
   Systemwide CA database updated.
   Adding SSH public key from /etc/ssh/ssh_host_ed25519_key.pub
   Adding SSH public key from /etc/ssh/ssh_host_rsa_key.pub
   Adding SSH public key from /etc/ssh/ssh_host_dsa_key.pub
   Adding SSH public key from /etc/ssh/ssh_host_ecdsa_key.pub
   Forwarding 'host_mod' to json server 'https://stuff.can.local/ipa/json'
   Could not update DNS SSHFP records.
   SSSD enabled
   Configured /etc/openldap/ldap.conf
   Configured /etc/ssh/ssh_config
   Configured /etc/ssh/sshd_config
   Configuring can.local as NIS domain.
   Client configuration complete.

   ==============================================================================
   Setup complete

   Next steps:
         1. You must make sure these network ports are open:
                  TCP Ports:
                     * 80, 443: HTTP/HTTPS
                     * 389, 636: LDAP/LDAPS
                     * 88, 464: kerberos
                  UDP Ports:
                     * 88, 464: kerberos
                     * 123: ntp

         2. You can now obtain a kerberos ticket using the command: 'kinit admin'
            This ticket will allow you to use the IPA tools (e.g., ipa user-add)
            and the web user interface.

   Be sure to back up the CA certificates stored in /root/cacert.p12
   These files are required to create replicas. The password for these
   files is the Directory Manager password
   [root@stuff]#
   [root@stuff]#
   [root@stuff]#
   [root@stuff]#
   [root@stuff]# kinit admin
   Password for admin@CAN.LOCAL:
   [root@stuff]# ipa user-add
   First name: Test1
   Last name: Fedora
   User login [tfedora]: test1
   ------------------
   Added user "test1"
   ------------------
   User login: test1
   First name: Test1
   Last name: Fedora
   Full name: Test1 Fedora
   Display name: Test1 Fedora
   Initials: TF
   Home directory: /home/test1
   GECOS: Test1 Fedora
   Login shell: /bin/sh
   Kerberos principal: test1@CAN.LOCAL
   Email address: test1@can.local
   UID: 586400001
   GID: 586400001
   Password: False
   Member of groups: ipausers
   Kerberos keys available: False
   [root@stuff]# ipa passwd test1
   New Password:

   Enter New Password again to verify:

   --------------------------------------
   Changed password for "test1@CAN.LOCAL"
   --------------------------------------
   [root@stuff]# kinit test1
   Password for test1@CAN.LOCAL:
   Password expired.  You must change it now.
   Enter new password:
   Enter it again:


**> Next**: `setting up the FreeIPA client 
<{filename}./freeipa-client-setup.rst>`_.

.. _`Fedora QA`: https://fedoraproject.org/wiki/QA 
.. _`this sssd bug`: https://bugzilla.redhat.com/show_bug.cgi?id=1366403
.. _in the past: https://bugzilla.redhat.com/show_bug.cgi?id=1330766
.. _`FreeIPA Quick Start Guide`: https://www.freeipa.org/page/Quick_Start_Guide
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
.. _`leftover directories`: 
   https://bugzilla.redhat.com/show_bug.cgi?id=953488#c4 

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
.. _`recently`: https://lists.fedoraproject.org/archives/list/test@lists.fedoraproject.org/message/AZEBYP5U4U5AZYUEN37JXBSP7J5A5ZI4/ 
