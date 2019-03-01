from __future__ import print_function, division, absolute_import, unicode_literals

from grako.buffering import Buffer
from grako.parsing import graken, Parser
from grako.util import re, RE_FLAGS, generic_main  # noqa


__all__ = [
    'RQLParser',
    'RQLSemantics',
    'main'
]

KEYWORDS = set([])


class RQLBuffer(Buffer):
    def __init__(self,
                 text,
                 whitespace=None,
                 nameguard=None,
                 comments_re=None,
                 eol_comments_re=None,
                 ignorecase=None,
                 namechars='',
                 **kwargs):
        super(RQLBuffer, self).__init__(
            text,
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re=comments_re,
            eol_comments_re=eol_comments_re,
            ignorecase=ignorecase,
            namechars=namechars,
            **kwargs
        )


class RQLParser(Parser):
    def __init__(self,
                 whitespace=None,
                 nameguard=None,
                 comments_re=None,
                 eol_comments_re=None,
                 ignorecase=None,
                 left_recursion=True,
                 keywords=KEYWORDS,
                 namechars='',
                 **kwargs):
        super(RQLParser, self).__init__(
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re=comments_re,
            eol_comments_re=eol_comments_re,
            ignorecase=ignorecase,
            left_recursion=left_recursion,
            keywords=keywords,
            namechars=namechars,
            **kwargs
        )

    def parse(self, text, *args, **kwargs):
        if not isinstance(text, Buffer):
            text = RQLBuffer(text, **kwargs)
        return super(RQLParser, self).parse(text, *args, **kwargs)

    @graken()
    def _start_(self):
        self._OREXPRESSION_()
        self._check_eof()

    @graken()
    def _OREXPRESSION_(self):

        def sep0():
            self._token(',')

        def block0():
            self._ANDEXPRESSION_()
        self._closure(block0, sep=sep0)

    @graken()
    def _ANDEXPRESSION_(self):

        def sep0():
            self._token(';')

        def block0():
            self._CONSTRAINT_()
        self._closure(block0, sep=sep0)

    @graken()
    def _CONSTRAINT_(self):
        with self._choice():
            with self._option():
                self._GROUP_()
            with self._option():
                self._COMPARISON_()
            self._error('no available options')

    @graken()
    def _GROUP_(self):
        self._token('(')
        self._OREXPRESSION_()
        self.name_last_node('@')
        self._token(')')

    @graken()
    def _COMPARISON_(self):
        self._SELECTOR_()
        self._OPERATOR_()
        self._ARGUMENTS_()

    @graken()
    def _SELECTOR_(self):
        self._pattern(r'[a-zA-Z_][a-zA-Z0-9_.]*')

    @graken()
    def _OPERATOR_(self):
        with self._choice():
            with self._option():
                self._FIQLOPERATOR_()
            with self._option():
                self._RSQLOPERATOR_()
            self._error('no available options')

    @graken()
    def _FIQLOPERATOR_(self):
        with self._choice():
            with self._option():
                self._token('==')
            with self._option():
                self._token('!=')
            with self._option():
                self._token('=lt=')
            with self._option():
                self._token('=gt=')
            with self._option():
                self._token('=le=')
            with self._option():
                self._token('=ge=')
            with self._option():
                self._token('=in=')
            with self._option():
                self._token('=out=')
            self._error('expecting one of: != == =ge= =gt= =in= =le= =lt= =out=')

    @graken()
    def _RSQLOPERATOR_(self):
        with self._choice():
            with self._option():
                self._token('<=')
            with self._option():
                self._token('>=')
            with self._option():
                self._token('<')
            with self._option():
                self._token('>')
            self._error('expecting one of: < <= > >=')

    @graken()
    def _ARGUMENTS_(self):
        with self._choice():
            with self._option():
                self._VALUELIST_()
            with self._option():
                self._VALUE_()
            self._error('no available options')

    @graken()
    def _VALUELIST_(self):
        self._token('(')

        def sep1():
            self._token(',')

        def block1():
            self._VALUE_()
        self._closure(block1, sep=sep1)
        self.name_last_node('@')
        self._token(')')

    @graken()
    def _VALUE_(self):
        with self._choice():
            with self._option():
                self._UNRESERVED_()
            with self._option():
                self._SINGLEQUOTED_()
            with self._option():
                self._DOUBLEQUOTED_()
            self._error('no available options')

    @graken()
    def _UNRESERVED_(self):
        self._pattern(r'[^\"\'();,=!~<> ]+')

    @graken()
    def _SINGLEQUOTED_(self):
        self._token("'")
        self._SINGLEQUOTEDCHARS_()
        self.name_last_node('@')
        self._token("'")

    @graken()
    def _SINGLEQUOTEDCHARS_(self):
        self._pattern(r"([^\\']|\\')*")

    @graken()
    def _DOUBLEQUOTED_(self):
        self._token('"')
        self._DOUBLEQUOTEDCHARS_()
        self.name_last_node('@')
        self._token('"')

    @graken()
    def _DOUBLEQUOTEDCHARS_(self):
        self._pattern(r'([^\\"]|\\")*')


class RQLSemantics(object):
    def start(self, ast):
        return ast

    def OREXPRESSION(self, ast):
        return ast

    def ANDEXPRESSION(self, ast):
        return ast

    def CONSTRAINT(self, ast):
        return ast

    def GROUP(self, ast):
        return ast

    def COMPARISON(self, ast):
        return ast

    def SELECTOR(self, ast):
        return ast

    def OPERATOR(self, ast):
        return ast

    def FIQLOPERATOR(self, ast):
        return ast

    def RSQLOPERATOR(self, ast):
        return ast

    def ARGUMENTS(self, ast):
        return ast

    def VALUELIST(self, ast):
        return ast

    def VALUE(self, ast):
        return ast

    def UNRESERVED(self, ast):
        return ast

    def SINGLEQUOTED(self, ast):
        return ast

    def SINGLEQUOTEDCHARS(self, ast):
        return ast

    def DOUBLEQUOTED(self, ast):
        return ast

    def DOUBLEQUOTEDCHARS(self, ast):
        return ast


def main(
        filename,
        startrule,
        trace=False,
        whitespace=None,
        nameguard=None,
        comments_re=None,
        eol_comments_re=None,
        ignorecase=None,
        left_recursion=True,
        **kwargs):

    with open(filename) as f:
        text = f.read()
    whitespace = whitespace or None
    parser = RQLParser(parseinfo=False)
    ast = parser.parse(
        text,
        startrule,
        filename=filename,
        trace=trace,
        whitespace=whitespace,
        nameguard=nameguard,
        ignorecase=ignorecase,
        **kwargs)
    return ast

if __name__ == '__main__':
    import json
    ast = generic_main(main, RQLParser, name='RQL')
    print('AST:')
    print(ast)
    print()
    print('JSON:')
    print(json.dumps(ast, indent=2))
    print()
