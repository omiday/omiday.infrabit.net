#################################################
A Git saga or what I learned from a missed commit
#################################################


:date: 2016-11-16
:tags: git, pelican
:url: 7TLNH.html
:save_as: 7TLNH.html

tl;dr
=====

Start the Git journey with::

   man gittutorial
   man gittutorial-2
   man gitcore-tutorial
   man gitworkflows


The issue
=========

It all started with a comment in `one of my Pelican PRs`_. In that commit I 
converted the contents from `reStructuredText tables`_ into ``.. data::`` 
sections similar to `Python Built-in Constants`_ page.

As a Git freshman I followed to the letter the `Pelican Contributor Guide`_ 
when it came to change workflow. That is before pushing to my `PR branch`_ I 
made sure to::

   git checkout gh2037
   git fetch upstream
   git rebase -p upstream/master

followed by::

   git push --force origin/gh2037

And this is how to prove that it's  exactly what I did::

   >>> pelican (gh2037>) docs $ git reflog --follow settings.rst
   1d64d67 HEAD@{11}: rebase -i (finish): returning to refs/heads/gh2037
   1d64d67 HEAD@{12}: rebase -i (pick): Fix #2037. Major overhaul of settings page.
   4a6adb6 HEAD@{14}: rebase -i (finish): returning to refs/heads/gh2037
   4a6adb6 HEAD@{15}: rebase -i (squash): Fix #2037. Major overhaul of settings page.
   4d4c3f8 HEAD@{16}: rebase -i (squash): # This is a combination of 12 commits.
   783145b HEAD@{17}: rebase -i (squash): # This is a combination of 11 commits.
   328b4db HEAD@{18}: rebase -i (squash): # This is a combination of 10 commits.
   b2d3d93 HEAD@{19}: rebase -i (squash): # This is a combination of 9 commits.
   1141100 HEAD@{20}: rebase -i (squash): # This is a combination of 8 commits.
   ef06873 HEAD@{21}: rebase -i (squash): # This is a combination of 7 commits.
   5a0760c HEAD@{22}: rebase -i (squash): # This is a combination of 6 commits.
   750d65f HEAD@{23}: rebase -i (squash): # This is a combination of 5 commits.
   7fe004b HEAD@{24}: rebase -i (squash): # This is a combination of 4 commits.
   6021c44 HEAD@{25}: rebase -i (squash): # This is a combination of 3 commits.
   7e6e1fd HEAD@{26}: rebase -i (squash): # This is a combination of 2 commits.
   00cec5b HEAD@{27}: rebase -i (continue): Fixes #2037
   b25d717 HEAD@{29}: rebase: aborting
   b25d717 HEAD@{31}: rebase: aborting
   b25d717 HEAD@{33}: checkout: moving from gh1759 to gh2037
   b25d717 HEAD@{43}: commit: Use ".. warning::" instead of "**warning**".
   829dd47 HEAD@{44}: commit: Fix references for footnotes #2 and #3.
   57b7d19 HEAD@{45}: commit: Conevert example from inline literal to code block.
   b14e823 HEAD@{46}: commit: Remove unreferenced "_metadata" target.
   931751e HEAD@{47}: commit: Remove redundant subsections in "Time and Date".
   7b09b9a HEAD@{48}: commit: Relocate *_TEMPLATE settings.
   1bbbe62 HEAD@{49}: commit: Remove path_metada reference.
   7a5c3c0 HEAD@{50}: commit: Move RELATIVE_URL under 'URL settings'
   35bc3ce HEAD@{51}: commit: Move DEFAULT_DATE_FORMAT under "Date format and locale".
   9530d22 HEAD@{52}: commit: Move TIMEZONE under the "Timezone" section
   3d4b1bd HEAD@{53}: commit: Move the locale footnote where it belongs.
   3a27b51 HEAD@{54}: commit: Relocate some of the settings.
   91936e1 HEAD@{55}: commit: Fixes #2037

However, as pointed out earlier I missed the upstream changes to 
``settings.rst`` introduced by `PR#1927`_.


How did that happen?
====================

According to ``reflog`` it appears that I rebased at reflog ``b25d717`` so 
let's inspect the commit object::

   >>> pelican (gh2037>) docs $ git show -s b25d717
   commit b25d71758471f46f38dadda9630e275b0f0bccfe
   Author: Viorel Tabara <viorel.tabara@infrabit.net>
   Date:   Sun Oct 23 21:52:12 2016 -0600

      Use ".. warning::" instead of "**warning**".

A small diversion: Why is the date "Oct 23"?

Pelican's `Squashing commits`_ instructions read::

   When prompted, mark your initial commit with pick, and all your follow-on 
   commits with squash. 

which effectively sets the commit date to when the first commit was made::

   >>> pelican (gh2037>) docs $ git show -s 91936e1
   commit 91936e187cf4afb674f62d8600d59da9020537b2
   Author: Viorel Tabara <viorel.tabara@infrabit.net>
   Date:   Sun Oct 23 17:04:14 2016 -0600

      Fixes #2037

      First iteration: convert all tables to 'data::' directives. Also
      replaced two instances of inline code markup with code block which is
      more readable.

With that distraction out of the way let's rewind::

   >>> pelican (gh2037>) docs $ git co b25d717
   Note: checking out 'b25d717'.

   You are in 'detached HEAD' state. You can look around, make experimental
   changes and commit them, and you can discard any commits you make in this
   state without impacting any branches by performing another checkout.

   If you want to create a new branch to retain commits you create, you may
   do so (now or later) by using -b with the checkout command again. Example:

   git checkout -b <new-branch-name>

   HEAD is now at b25d717... Use ".. warning::" instead of "**warning**".

At this point Git moved the HEAD to::

   >>> pelican ((b25d717...)) docs $ git status 
   HEAD detached at b25d717
   nothing to commit, working tree clean

Or, another to view it::

   >>> pelican ((b25d717...)) docs $ cat ../.git/HEAD
   b25d71758471f46f38dadda9630e275b0f0bccfe

I can now replay the steps from Pelican's `Squashing commits`_ instructions 
and armed with knowledge I should be able to spot the mistake:

1. Check out the working branch --- as explained earlier I'm already here::

      >>> pelican ((b25d717...)) docs $ git status
      HEAD detached at b25d717
      nothing to commit, working tree clean

2. Fetch upstream changes::

      >>> pelican ((b25d717...)) docs $ git fetch -v upstream 
      From https://github.com/getpelican/pelican
      = [up to date]      3.0.1      -> upstream/3.0.1
      = [up to date]      3.2-series -> upstream/3.2-series
      = [up to date]      add_multi_theme_support -> upstream/add_multi_theme_support
      = [up to date]      cache-readers -> upstream/cache-readers
      = [up to date]      caching_warning -> upstream/caching_warning
      = [up to date]      content-written-signal -> upstream/content-written-signal
      = [up to date]      faq_index_save_as -> upstream/faq_index_save_as
      = [up to date]      fix-1493   -> upstream/fix-1493
      = [up to date]      master     -> upstream/master
      = [up to date]      multiple-authors -> upstream/multiple-authors
      = [up to date]      static_symlink_1042 -> upstream/static_symlink_1042

   ``'-v'`` is just to show that everything is up to date since I've already 
   done this while troubleshooting.

3. Rebase interactively with *pick and squash*::

      >>> pelican ((b25d717...)) docs $ git rebase -i upstream/master
      error: could not apply 91936e1... Fixes #2037

      When you have resolved this problem, run "git rebase --continue".
      If you prefer to skip this patch, run "git rebase --skip" instead.
      To check out the original branch and stop rebasing, run "git rebase --abort".
      Could not apply 91936e187cf4afb674f62d8600d59da9020537b2... Fixes #2037

   Oops! We've seen this before. However, at the time I *assumed* (wrongly!) 
   that all I needed to do was removing the `reStructuredText table`_ 
   introduced by ``upstream/master`` since that was the goal. But I never 
   questioned where the conflict was coming from!

   The answer lies in the output given with::

      >>> pelican ((b25d717...)) docs $ git log b25d717..upstream/master 
      settings.rst
      commit a80a707321937062a8d6fe4514f7fd8a3efc0e29
      Author: Bernhard Scheirle <bernhard+git@scheirle.de>
      Date:   Wed Nov 2 21:00:04 2016 +0100

         Set the Markdown output format to html5 by default

      commit 114e64dcf7e65145bc2b79afcb3df939c4f0cb4f
      Author: Bernhard Scheirle <bernhard+git@scheirle.de>
      Date:   Tue Nov 1 13:02:22 2016 +0100

         doc: updates MARKDOWN

So now we can explain in plain English why I didn't notice the changes: My work 
on ``settings.rst`` started on the *upsgream/master* branch dated Oct-23. While 
my PR was awaiting review the two commits were merged upstream and they changed 
the reST table contents and that is why Git stopped the rebase. Mea culpa, I 
should have investigated before blindly removing *all upstream changes*. Lesson 
learned.

With that one clarified it's now time to abort the rebase::

   >>> pelican (detached HEAD *+|REBASE-i 1/13) docs $ git rebase --abort 
   >>> pelican ((b25d717...)) docs $ 

...and find out what is causing the conflict.

Finding the conflict
====================

``man gittutorial`` section *USING GIT FOR COLLABORATION* has the answer::

       Alice can peek at what Bob did without merging first, using the "fetch" 
       command; this allows Alice to inspect what Bob did, using a special 
       symbol
       "FETCH_HEAD", in order to determine if he has anything worth pulling, 
       like this:

           alice$ git fetch /home/bob/myrepo master
           alice$ git log -p HEAD..FETCH_HEAD

FETCH_HEAD won't work in my case since it doesn't point to  ``master`` as shown 
by::

   >>> pelican (detached HEAD *+|REBASE-i 1/13) docs $ cat ../.git/FETCH_HEAD 
   22d2c786618cb3ffcb29ba70ae053087d5058ecc        not-for-merge   branch '3.0.1' of https://github.com/getpelican/pelican
   4d9197d13960997b892c1bdac48c35cbb6bb0543        not-for-merge   branch '3.2-series' of https://github.com/getpelican/pelican
   d71bae7ee523a8be12209e09af169173de4fb0b7        not-for-merge   branch 'add_multi_theme_support' of https://github.com/getpelican/pelican
   2b87eb7af63b856862d65e289fefe3f295409bda        not-for-merge   branch 'cache-readers' of https://github.com/getpelican/pelican
   2beefb89c51b624dd02e63825c42f3a9bffef37c        not-for-merge   branch 'caching_warning' of https://github.com/getpelican/pelican
   339955376e1f84fb5209dad9f18bc802f006d0e1        not-for-merge   branch 'content-written-signal' of https://github.com/getpelican/pelican
   9690a696b95bcc08c330bbed1e2feb779649b83a        not-for-merge   branch 'faq_index_save_as' of https://github.com/getpelican/pelican
   e39dc95c3bfed28fffc972e1fa780b772e61701c        not-for-merge   branch 'fix-1493' of https://github.com/getpelican/pelican
   6008f7e2ed2621f99224b437341cf4737c87e9a3        not-for-merge   branch 'master' of https://github.com/getpelican/pelican
   0550c6ef29b2129efe1fbd061669f2909f464559        not-for-merge   branch 'multiple-authors' of https://github.com/getpelican/pelican
   25a8ab1a5f12377865af19b89496b3449cb0076f        not-for-merge   branch 'static_symlink_1042' of https://github.com/getpelican/pelican

So the command to list changes introduced by ``upstream/master`` pertaining to 
my file ``settings.rst`` looks like this::

   >>> pelican ((b25d717...)) docs $ git log b25d717..upstream/master settings.rst
   commit a80a707321937062a8d6fe4514f7fd8a3efc0e29
   Author: Bernhard Scheirle <bernhard+git@scheirle.de>
   Date:   Wed Nov 2 21:00:04 2016 +0100

      Set the Markdown output format to html5 by default

   commit 114e64dcf7e65145bc2b79afcb3df939c4f0cb4f
   Author: Bernhard Scheirle <bernhard+git@scheirle.de>
   Date:   Tue Nov 1 13:02:22 2016 +0100

      doc: updates MARKDOWN

Note that I'm using the commit object since according to ``man gitrevisions`` 
HEAD means::

   HEAD names the commit on which you based the changes in the working tree. 

To show an output similar to the one `referenced in the PR comment`_ it's just 
a matter of passing ``-p`` to ``git log``.


Fixing it
=========

1. Create a branch off of the last good reflog ``b25d717``::

      >>> pelican (gh2037>) docs $ git checkout -b gh2037-at-b25d717 b25d717

2. Double check we are working with the right branch::

      >>> pelican (gh2037-at-b25d717) docs $ git branch
      gh1759
      gh2037
      * gh2037-at-b25d717
      master
      pep8

3. As per Pelican instructions update from *upstream/master*::

      >>> pelican (gh2037-at-b25d717) docs $ git fetch upstream

4. ...and ``rebase`` --- this should fail::

      >>> pelican (gh2037-at-b25d717) docs $ git rebase -i upstream/master
      error: could not apply 91936e1... Fixes #2037

      When you have resolved this problem, run "git rebase --continue".
      If you prefer to skip this patch, run "git rebase --skip" instead.
      To check out the original branch and stop rebasing, run "git rebase --abort".
      Could not apply 91936e187cf4afb674f62d8600d59da9020537b2... Fixes #2037

5. Let's have a closer look::

      >>> pelican (gh2037-at-b25d717 *+|REBASE-i 1/13) docs $ git status
      interactive rebase in progress; onto 6008f7e
      Last command done (1 command done):
         pick 91936e1 Fixes #2037
      Next commands to do (12 remaining commands):
         squash 3a27b51 Relocate some of the settings.
         squash 3d4b1bd Move the locale footnote where it belongs.
      (use "git rebase --edit-todo" to view and edit)
      You are currently rebasing branch 'gh2037-at-b25d717' on '6008f7e'.
      (fix conflicts and then run "git rebase --continue")
      (use "git rebase --skip" to skip this patch)
      (use "git rebase --abort" to check out the original branch)

      Unmerged paths:
      (use "git reset HEAD <file>..." to unstage)
      (use "git add <file>..." to mark resolution)

            both modified:   settings.rst

      no changes added to commit (use "git add" and/or "git commit -a")

6. For the sake of learning, let's confirm that the last commit in 
   *upstream/master* is the one reported in the above output as::

      interactive rebase in progress; onto 6008f7e

   We do that with::

      >>> pelican (gh2037-at-b25d717 *+|REBASE-i 1/13) docs $ git log --summary upstream/master -1 HEAD
      commit 6008f7e2ed2621f99224b437341cf4737c87e9a3
      Merge: 4fc2c6c a445e81
      Author: Justin Mayer <entroP@gmail.com>
      Date:   Tue Nov 15 10:45:42 2016 -0700

         Merge pull request #2050 from Scheirle/markdown_options2

         Make Markdown extensions order non-arbitrary

    I've got the right commit, looking good so far :)

7. Fix the conflict --- to do this right:

   A. Show the changes in *upstream/master* versus my current branch::

         >>> pelican (gh2037-at-b25d717 *+|REBASE-i 1/13) docs $ git log gh2037-at-b25d717..upstream/master settings.rst
         commit a80a707321937062a8d6fe4514f7fd8a3efc0e29
         Author: Bernhard Scheirle <bernhard+git@scheirle.de>
         Date:   Wed Nov 2 21:00:04 2016 +0100

            Set the Markdown output format to html5 by default

         commit 114e64dcf7e65145bc2b79afcb3df939c4f0cb4f
         Author: Bernhard Scheirle <bernhard+git@scheirle.de>
         Date:   Tue Nov 1 13:02:22 2016 +0100

            doc: updates MARKDOWN

      Worth mentioning that I cannot use HEAD since the ``rebase`` stashed all 
      the commits and moved the HEAD to::

         >>> pelican (gh2037-at-b25d717 *+|REBASE-i 1/13) docs $ cat ../.git/HEAD 
         6008f7e2ed2621f99224b437341cf4737c87e9a3

   B. Show the source diff so I can update *my changes* with *their changes*::

         >>> pelican (gh2037-at-b25d717 *+|REBASE-i 1/13) docs $ git log -p gh2037-at-b25d717..upstream/master settings.rst
         commit a80a707321937062a8d6fe4514f7fd8a3efc0e29
         Author: Bernhard Scheirle <bernhard+git@scheirle.de>
         Date:   Wed Nov 2 21:00:04 2016 +0100

            Set the Markdown output format to html5 by default

         diff --git a/docs/settings.rst b/docs/settings.rst
         index 231906e..bf20384 100644
         --- a/docs/settings.rst
         +++ b/docs/settings.rst
         @@ -121,9 +121,9 @@ Setting name (followed by default value, if any)
                                                                                          for a complete list of supported options.
                                                                                          The ``extensions`` option will be automatically computed from the 
                                                                                          ``extension_configs`` option.
         -                                                                                 Default is ``'extension_configs': {'markdown.extensions.codehilite':
         +                                                                                 Default is ``{'extension_configs': {'markdown.extensions.codehilite':
                                                                                          {'css_class': 'highlight'},'markdown.extensions.extra': {},
         -                                                                                 'markdown.extensions.meta': {},},``.
         +                                                                                 'markdown.extensions.meta': {},}, 'output_format': 'html5',}``.
         ``OUTPUT_PATH = 'output/'``                                                      Where to output the generated files.
         ``PATH``                                                                         Path to content directory to be processed by Pelican. If undefined,
                                                                                          and content path is not specified via an argument to the ``pelican``

         commit 114e64dcf7e65145bc2b79afcb3df939c4f0cb4f
         Author: Bernhard Scheirle <bernhard+git@scheirle.de>
         Date:   Tue Nov 1 13:02:22 2016 +0100

            doc: updates MARKDOWN

         diff --git a/docs/settings.rst b/docs/settings.rst
         index 6f695f9..231906e 100644
         --- a/docs/settings.rst
         +++ b/docs/settings.rst
         @@ -114,15 +114,16 @@ Setting name (followed by default value, if any)
                                                                                          of these patterns will be ignored by the processor. For example,
                                                                                          the default ``['.#*']`` will ignore emacs lock files, and
                                                                                          ``['__pycache__']`` would ignore Python 3's bytecode caches.
         -``MD_EXTENSIONS =`` ``{...}``                                                    A dict of the extensions that the Markdown processor
         -                                                                                 will use, with extensions' settings as the values.
         +``MARKDOWN =`` ``{...}``                                                         Extra configuration settings for the Markdown processor.
                                                                                          Refer to the Python Markdown documentation's
         -                                                                                 `Extensions section <http://pythonhosted.org/Markdown/extensions/>`_
         -                                                                                 for a complete list of supported extensions and their options.
         -                                                                                 Default is ``{'markdown.extensions.codehilite' : {'css_class': 'highlight'},
         -                                                                                 'markdown.extensions.extra': {}, 'markdown.extensions.meta': {}}``.
         -                                                                                 (Note that the dictionary defined in your settings file will
         -                                                                                 update this default one.)
         +                                                                                 `Options section 
         +                                                                                 <http://pythonhosted.org/Markdown/reference.html#markdown>`_
         +                                                                                 for a complete list of supported options.
         +                                                                                 The ``extensions`` option will be automatically computed from the 
         +                                                                                 ``extension_configs`` option.
         +                                                                                 Default is ``'extension_configs': {'markdown.extensions.codehilite':
         +                                                                                 {'css_class': 'highlight'},'markdown.extensions.extra': {},
         +                                                                                 'markdown.extensions.meta': {},},``.
         ``OUTPUT_PATH = 'output/'``                                                      Where to output the generated files.
         ``PATH``                                                                         Path to content directory to be processed by Pelican. If undefined,
                                                                                          and content path is not specified via an argument to the ``pelican``

      That looks identical to the diff `referenced in the PR comment`_. On to 
      the next step.

   C. Edit my changes to take in account the changes introduced by the two 
      above commits. This is manual work, that's how conflicts are resolved.  
      Just like in real life, you can't expect someone else to fix it for you.

      .. Note::
         If I want to view the file contents as it was at those two commits 
         without having to snapshot the full working tree::

            >>> pelican (gh2037-at-b25d717 *+|REBASE-i 1/13) docs $ git ls-tree  114e64dcf7e65145bc2b79afcb3df939c4f0cb4f settings.rst
            100644 blob 231906e6e6107ce5677993bb079095893d0965b6    settings.rst 
            >>> pelican (gh2037-at-b25d717 *+|REBASE-i 1/13) docs $ git cat-file -p 231906e6e6107ce5677993bb079095893d0965b6 | head
            Settings
            ########

            Pelican is configurable thanks to a settings file you can pass to
            the command line::

               pelican content -s path/to/your/pelicanconf.py

            (If you used the ``pelican-quickstart`` command, your primary settings file will
            be named ``pelicanconf.py`` by default.)

         and the 2nd commit::

            >>> pelican (gh2037-at-b25d717 *+|REBASE-i 1/13) docs $ git ls-tree  a80a707321937062a8d6fe4514f7fd8a3efc0e29 settings.rst
            100644 blob bf203841e2bd15ef4fcc7b62b91d133b82b87807    settings.rst 
            >>> pelican (gh2037-at-b25d717 *+|REBASE-i 1/13) docs $ git cat-file -p bf203841e2bd15ef4fcc7b62b91d133b82b87807 | head
            Settings
            ########

            Pelican is configurable thanks to a settings file you can pass to
            the command line::

               pelican content -s path/to/your/pelicanconf.py

            (If you used the ``pelican-quickstart`` command, your primary settings file will
            be named ``pelicanconf.py`` by default.)

        ``man gittutorial-2`` explains how the magic works.

   D. Confirm resolution::

         >>> pelican (gh2037-at-b25d717) docs $ git add settings.rst 

8. Continue ``rebase``::

      >>> pelican (gh2037-at-b25d717 +|REBASE-i 1/13) docs $ git rebase --continue
      [detached HEAD e80ecb5] Fix #2037. Major overhaul of settings page.
      1 file changed, 1226 insertions(+), 883 deletions(-)
      rewrite docs/settings.rst (68%)
      [detached HEAD bc2eafb] Fix #2037. Major overhaul of settings page.
      Date: Sun Oct 23 17:04:14 2016 -0600
      1 file changed, 1218 insertions(+), 883 deletions(-)
      rewrite docs/settings.rst (73%)
      Successfully rebased and updated refs/heads/gh2037-at-b25d717.

9. Check the changes between this version and the rejected one::

      >>> pelican (gh2037-at-b25d717) docs $ git diff origin/gh2037 settings.rst
      diff --git a/docs/settings.rst b/docs/settings.rst
      index 365e12a..96148a4 100644
      --- a/docs/settings.rst
      +++ b/docs/settings.rst
      @@ -125,21 +125,26 @@ Basic settings
         ``['.#*']`` will ignore emacs lock files, and ``['__pycache__']`` would
         ignore Python 3's bytecode caches.
      
      -.. data:: MD_EXTENSIONS = {...}
      +.. data:: MARKDOWN = {...}
      
      -   A dict of extensions that the Markdown processor will use, with
      -   extensions settings as the values.  Refer to the Python Markdown
      -   documentation `Extensions section
      -   <http://pythonhosted.org/Markdown/extensions/>`_ for a complete list of
      -   supported extensions and their options.
      +   Extra configuration settings for the Markdown processor. Refer to the Python 
      +   Markdown documentation's `Options section 
      +   <http://pythonhosted.org/Markdown/reference.html#markdown>`_ for a complete 
      +   list of supported options. The ``extensions`` option will be automatically 
      +   computed from the ``extension_configs`` option.
      
         Defaults to::
      
      -      MD_EXTENSIONS = {
      -          'markdown.extensions.codehilite' : {'css_class': 'highlight'},
      -          'markdown.extensions.extra': {},
      -          'markdown.extensions.meta': {}
      -      }
      +        MARKDOWN = {
      +            'extension_configs': {
      +                'markdown.extensions.codehilite': {
      +                    'css_class': 'highlight'
      +                },
      +                'markdown.extensions.extra': {},
      +                'markdown.extensions.meta': {},
      +            },
      +            'output_format': 'html5',
      +        }
      
         .. Note::
            The dictionary defined in your settings file will update this default 
      
   :Note:
      *origin/gh2037* refers to::

         >>> pelican (gh2037-at-b25d717) docs $ git remote -v 
         origin  ssh://github-omiday/omiday/pelican.git (fetch)
         origin  ssh://github-omiday/omiday/pelican.git (push)
         upstream        https://github.com/getpelican/pelican.git (fetch)
         upstream        https://github.com/getpelican/pelican.git (push)
         
10. Merge changes into the branch that my `PR#2038`_ is based off of::

      >>> pelican (upstream-merge-test>) docs $ git checkout gh2037
      >>> pelican (upstream-merge-test>) docs $ git merge gh2037-at-b25d717

11. In order to remove the merge commit I can ``rebase`` to *upstream/master* 
    (just as usual) and squash the merge commit. The commit log doesn't need 
    change.

12. As a last test, before pushing to *origin* I can check whether my changes 
    will merge cleanly into the current *upstream/master*, by pretending that 
    I'm on Github and merge my PR which in "local terms" is the ``gh2037`` 
    branch)::

      >>> pelican (upstream-merge-test>) docs $ git co -b upstream-merge-test upstream/master 
      >>> pelican (upstream-merge-test>) docs $ git merge gh2037

13. Let's check whether my commit was added on top of *upstream/master*::

      >>> pelican (upstream-merge-test>) docs $ git log --name-only -2 HEAD
      commit f30f4fe66b9fb88106ed56af11b270a86f414f1d
      Author: Viorel Tabara <viorel.tabara@infrabit.net>
      Date:   Sun Oct 23 17:04:14 2016 -0600

         Fix #2037. Major overhaul of settings page.
         
         Convert all tables to 'data::' directives.
         
         Replace inline literals with code blocks for better readability.
         
         Per suggestion from Avaris on IRC:
         - Section rename: "Path metadata" to "Metadata" and move over AUTHOR and
            all *_METADATA options.
         - Merge "Date format and locale" and "Timezone" into a new section "Time
            and Date" and move over TIMEZONE, DEFAULT_DATE, DATE_FORMATS,
            DEFAULT_DATE_FORMAT.
         - Move RELATIVE_URL under 'URL settings'. Here, convert URL settings
            example from a 4-bullet inline literal to a single code block for
            better readability in both source and output.
         - Move *_TEMPLATE options under "Templates".
         
         Cosmetic and wording updates to accommodate the above changes and
         provide a consistent layout.

      docs/settings.rst

      commit 6008f7e2ed2621f99224b437341cf4737c87e9a3
      Merge: 4fc2c6c a445e81
      Author: Justin Mayer <entroP@gmail.com>
      Date:   Tue Nov 15 10:45:42 2016 -0700

         Merge pull request #2050 from Scheirle/markdown_options2
         
         Make Markdown extensions order non-arbitrary

    Or a shorter version, using the newly learned tricks::

      >>> pelican (upstream-merge-test>) docs $ git log upstream/master..HEAD
      commit f30f4fe66b9fb88106ed56af11b270a86f414f1d
      Author: Viorel Tabara <viorel.tabara@infrabit.net>
      Date:   Sun Oct 23 17:04:14 2016 -0600

         Fix #2037. Major overhaul of settings page.
         
         Convert all tables to 'data::' directives.
         
         Replace inline literals with code blocks for better readability.
         
         Per suggestion from Avaris on IRC:
         - Section rename: "Path metadata" to "Metadata" and move over AUTHOR and
            all *_METADATA options.
         - Merge "Date format and locale" and "Timezone" into a new section "Time
            and Date" and move over TIMEZONE, DEFAULT_DATE, DATE_FORMATS,
            DEFAULT_DATE_FORMAT.
         - Move RELATIVE_URL under 'URL settings'. Here, convert URL settings
            example from a 4-bullet inline literal to a single code block for
            better readability in both source and output.
         - Move *_TEMPLATE options under "Templates".
         
         Cosmetic and wording updates to accommodate the above changes and
         provide a consistent layout.

14. All looking good I can push to remote::

      >>> pelican (upstream-merge-test>) docs $ git push --force origin gh2037 
      Counting objects: 9, done.
      Delta compression using up to 4 threads.
      Compressing objects: 100% (9/9), done.
      Writing objects: 100% (9/9), 6.44 KiB | 0 bytes/s, done.
      Total 9 (delta 6), reused 0 (delta 0)
      remote: Resolving deltas: 100% (6/6), completed with 5 local objects.
      To ssh://github-omiday/omiday/pelican.git
      + 4a6adb6...f30f4fe gh2037 -> gh2037 (forced update)

15. And because I'm in learning mode I will double check that my `PR#2038`_ 
    introduces changes to only the file(s) I expect::

      >>> pelican (upstream-merge-test>) docs $ git log --name-only upstream/master..origin/gh2037 
      commit f30f4fe66b9fb88106ed56af11b270a86f414f1d
      Author: Viorel Tabara <viorel.tabara@infrabit.net>
      Date:   Sun Oct 23 17:04:14 2016 -0600

         Fix #2037. Major overhaul of settings page.
         
         Convert all tables to 'data::' directives.
         
         Replace inline literals with code blocks for better readability.
         
         Per suggestion from Avaris on IRC:
         - Section rename: "Path metadata" to "Metadata" and move over AUTHOR and
            all *_METADATA options.
         - Merge "Date format and locale" and "Timezone" into a new section "Time
            and Date" and move over TIMEZONE, DEFAULT_DATE, DATE_FORMATS,
            DEFAULT_DATE_FORMAT.
         - Move RELATIVE_URL under 'URL settings'. Here, convert URL settings
            example from a 4-bullet inline literal to a single code block for
            better readability in both source and output.
         - Move *_TEMPLATE options under "Templates".
         
         Cosmetic and wording updates to accommodate the above changes and
         provide a consistent layout.

      docs/settings.rst
      

And That's All Folks!


.. _`one of my Pelican PRs`: https://github.com/getpelican/pelican/pull/2038#pullrequestreview-8598348 
.. _`Pelican Contributor Guide`: http://docs.getpelican.com/en/latest/contribute.html
.. _`PR#1927`: https://github.com/getpelican/pelican/pull/1927
.. _`reStructuredText tables`: http://docutils.sourceforge.net/docs/user/rst/demo.html#tables
.. _`Python Built-in Constants`: https://docs.python.org/3/library/constants.html
.. _`referenced in the PR comment`: https://github.com/getpelican/pelican/commit/a07c0e6e042a0b7a26a7f97ebd5e5eb977eea160#diff-f47f8ca652dac550c8bc9d449ca0d253
.. _`PR#2038`: https://github.com/getpelican/pelican/pull/2038
.. _`Squashing commits`: https://github.com/getpelican/pelican/wiki/Git-Tips#squashing-commits
.. _`reStructuredText table`: `reStructuredText tables`_
.. _`PR branch`: `PR#2038`_
