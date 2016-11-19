##################################################################
Wondering about circular definitions in Python Language Reference?
##################################################################

:date: 2016-09-02
:tags: python
:authors: omiday

If you have been reading the `Python Tutorial`_ and did follow the various 
references to `Python Language Reference`_ all the way you likely ended up with 
something along these lines:

1. enclosure_::

      enclosure ::=  parenth_form | list_display | dict_display | set_display
                     | generator_expression | yield_atom

2. parenth_form_::

      parenth_form ::=  "(" [starred_expression] ")"

3. starred_expression_::

      starred_expression ::=  expression | ( starred_item "," )* [starred_item] 

4. starred_item_::

      starred_item       ::=  expression | "*" or_expr 

5. expression_::

      expression             ::=  conditional_expression | lambda_expr 

6. conditional_expression_::

      conditional_expression ::=  or_test ["if" or_test "else" expression] 

   `circular definition`_::

      contitional_expression ::= expression (6)
      expression ::= conditional_expression (5)

7. or_test_::

      or_test  ::=  and_test | or_test "or" and_test 

8. and_test_::

      and_test ::=  not_test | and_test "and" not_test

9. not_test_::

      not_test ::=  comparison | "not" not_test 

10. comparison_::

       comparison    ::=  or_expr ( comp_operator or_expr )*

11. or_expr_::

       or_expr  ::=  xor_expr | or_expr "|" xor_expr

12. xor_expr_::

       xor_expr ::=  and_expr | xor_expr "^" and_expr 

13. and_expr_::

       and_expr ::=  shift_expr | and_expr "&" shift_expr

14. shift_expr_::

       shift_expr ::=  a_expr | shift_expr ( "<<" | ">>" ) a_expr

15. a_expr_::

       a_expr ::=  m_expr | a_expr "+" m_expr | a_expr "-" m_expr

16. m_expr_::

       m_expr ::=  u_expr | m_expr "*" u_expr | m_expr "@" m_expr |
            m_expr "//" u_expr| m_expr "/" u_expr |
            m_expr "%" u_expr

17. u_expr_::

       u_expr ::=  power | "-" u_expr | "+" u_expr | "~" u_expr

18. power_::

       power ::=  ( await_expr | primary ) ["**" u_expr]

19. await_expr_::

       await_expr ::=  "await" primary

20. primary_::

       primary ::=  atom | attributeref | subscription | slicing | call

21. atom_::

       atom      ::=  identifier | literal | enclosure

22. enclosure_::

      enclosure ::=  parenth_form | list_display | dict_display | set_display
                     | generator_expression | yield_atom

And we are back from where we started!

But fear not, there are other similar `circular definitions`_.

.. _enclosure: https://docs.python.org/3/reference/expressions.html#grammar-token-enclosure
.. _parenth_form: https://docs.python.org/3/reference/expressions.html#grammar-token-parenth_form
.. _starred_expression: https://docs.python.org/3/reference/expressions.html#grammar-token-starred_expression 
.. _starred_item: https://docs.python.org/3/reference/expressions.html#grammar-token-starred_item 
.. _expression: https://docs.python.org/3/reference/expressions.html#grammar-token-expression 
.. _conditional_expression: https://docs.python.org/3/reference/expressions.html#grammar-token-conditional_expression 
.. _or_test: https://docs.python.org/3/reference/expressions.html#grammar-token-or_test 
.. _and_test: https://docs.python.org/3/reference/expressions.html#grammar-token-and_test 
.. _not_test: https://docs.python.org/3/reference/expressions.html#grammar-token-not_test 
.. _comparison: https://docs.python.org/3/reference/expressions.html#grammar-token-comparison 
.. _or_expr: https://docs.python.org/3/reference/expressions.html#grammar-token-or_expr 
.. _xor_expr: https://docs.python.org/3/reference/expressions.html#grammar-token-xor_expr 
.. _and_expr: https://docs.python.org/3/reference/expressions.html#grammar-token-and_expr 
.. _shift_expr: https://docs.python.org/3/reference/expressions.html#grammar-token-shift_expr 
.. _a_expr: https://docs.python.org/3/reference/expressions.html#grammar-token-a_expr 
.. _m_expr: https://docs.python.org/3/reference/expressions.html#grammar-token-m_expr 
.. _u_expr: https://docs.python.org/3/reference/expressions.html#grammar-token-u_expr 
.. _power: https://docs.python.org/3/reference/expressions.html#grammar-token-power 
.. _await_expr: https://docs.python.org/3/reference/expressions.html#grammar-token-await_expr 
.. _primary: https://docs.python.org/3/reference/expressions.html#grammar-token-primary 
.. _atom: https://docs.python.org/3/reference/expressions.html#grammar-token-atom 
.. _`circular definition`: https://en.wikipedia.org/wiki/Circular_definition 
.. _`circular definitions`: `circular definition`_
.. _`Python Tutorial`: https://docs.python.org/3/tutorial/index.html 
.. _`Python Language Reference`: https://docs.python.org/3/reference/index.html 
