##############################
Searching Vim's internal pager
##############################

:date: 2016-09-02
:tags: vim


The problem::

   :map

How do I search that list when Vim only provides::

   -- More -- SPACE/d/j: screen/page/line down, b/u/k: up, q: quit 

Following the hint on `this StackOverflow`_ article the trick is `:redir`_ and 
assuming the editing mode is `buffers`_ it goes like this::

   :redir @a
   :map
   :redir END
   :enew
   :"ap

.. _`:redir`: http://vimdoc.sourceforge.net/htmldoc/various.html#:redir 
.. _`buffers`: http://vimdoc.sourceforge.net/htmldoc/windows.html#buffers 
.. _`this StackOverflow`: https://stackoverflow.com/questions/18817614/how-do-i-change-vims-internal-pager-to-something-else 
