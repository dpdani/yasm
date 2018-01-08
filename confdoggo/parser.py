#!/usr/bin/python3
#
# Copyright (C) 2017  The confdoggo Authors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import ply
import ply.lex
import ply.yacc
from confdoggo import DoggoException
from . import settingstypes


class TokenizationException(DoggoException):
    pass

class ParsingException(DoggoException):
    pass


tokens = (
    'DOT',
    'PAREN_LX',
    'PAREN_RX',
    'OBJECT_BEGIN_LX',
    'OBJECT_BEGIN_RX',
    'OBJECT_END',
    'COLON',
    'EQUALS_TO',
    'MULTILINE_STRING_DELIMITER',
    'VAR_DELIMITER',
    'FLOAT',
    'INTEGER',
    'BOOLEAN',
    'STRING',
    'DATETIME',
#    'TIMEDELTA',
    'IF',
    'ELSE',
    'ELIF',
    'PASS',
    'INCLUDE',
    'IMPORT',
    'IDENTIFIER',
)


t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'

t_DOT = r'\.'
t_PAREN_LX = r'\('
t_PAREN_RX = r'\)'
t_OBJECT_BEGIN_LX = r'<'
t_OBJECT_BEGIN_RX = r'>'
t_OBJECT_END = r'</>'
t_COLON = ':'
t_EQUALS_TO = '='
t_MULTILINE_STRING_DELIMITER = r'(\"\"\".*\"\"\"|\'\'\'.*\'\'\')'
t_VAR_DELIMITER = r'\$'

# values are defined as functions (below)

t_IF = r'if'
t_ELSE = r'else'
t_ELIF = r'elif'
t_PASS = r'pass'
t_INCLUDE = r'include'
t_IMPORT = r'import'

# t_IDENTIFIER is defined as function (below)


def t_FLOAT(t):
    r"""[0-9]*\.[0-9]*"""
    # if t.value == '.':
    #     raise ParsingException('Cannot convert to float: \'.\'.')
    # t.value = float(t.value)
    # return t
    obj = settingstypes.Float(None)  # name will be set later
    obj.value_ = t.value
    obj.convert_pre_()
    t.value = obj
    return t


def t_INTEGER(t):
    r"""[0-9]+"""
    # t.value = int(t.value)
    # return t
    obj = settingstypes.Integer(None)  # name will be set later
    obj.value_ = t.value
    obj.convert_pre_()
    t.value = obj
    return t


def t_BOOLEAN(t):
    r"""(True|true|yes|on|False|false|no|off)"""
    # t.value = True
    # return t
    obj = settingstypes.Boolean(None)  # name will be set later
    obj.value_ = t.value
    obj.convert_pre_()
    t.value = obj
    return t


def t_STRING(t):
    r"""(\'.*\'|\".*\")"""
    obj = settingstypes.String(None)  # name will be set later
    obj.value_ = t.value
    obj.convert_pre_()
    t.value = obj
    return t


def t_DATETIME(t):
    r"""(\d{4})-(\d{2})-(\d{2}) ((\d{2}):(\d{2})(:(\d{2}))?)?"""
    obj = settingstypes.Datetime(None)  # name will be set later
    obj.value_ = t.value
    obj.convert_pre_()
    t.value = obj
    return t


def t_IDENTIFIER(t):
    r"""[a-zA-Z_][a-zA-Z_ ]*"""
    t.value = t.value.replace(' ', '_')
    return t


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


def t_error(t):
    raise TokenizationException(f'illegal character {t.value[0]} at line {t.lexer.lineno}')


lexer = ply.lex.lex()  # generate lex table


def p_error(p):
    if p is None:
        raise ParsingException("Unexpected EOF.")
    raise ParsingException("Syntax error around '{}' <{}> at line {}.".format(
        p.value, p, p.lexer.lineno))


def p_statement(p):
    """statement : stmt_assign
                 | stmt_conditional
                 | stmt_object
                 | stmt_include
                 | stmt_variable"""
    return p


def p_stmt_assign(p):
    """stmt_assign : key EQUALS_TO expression
                   | key EQUALS_TO value
                   | key EQUALS_TO inline_object"""
    return p


def p_stmt_conditional(p):
    """stmt_conditional : IF expression COLON block opt_elif_list opt_else"""
    return p


def p_stmt_object(p):
    """stmt_object : OBJECT_BEGIN_LX key OBJECT_BEGIN_RX block OBJECT_END"""
    # reconduct to stmt_assign?
    return p


def p_stmt_include(p):
    """stmt_include : INCLUDE STRING"""
    return p


def p_stmt_variable(p):
    """stmt_variable : VAR_DELIMITER IDENTIFIER EQUALS_TO expression
                     | VAR_DELIMITER IDENTIFIER EQUALS_TO IMPORT PAREN_LX STRING PAREN_RX"""
    return p


def p_opt_elif_list(p):
    """opt_elif_list :
                     | elif_list"""
    return p


def p_elif_list(p):
    """elif_list : elif
                 | elif_list elif"""
    return p


def p_elif(p):
    """elif : ELIF expression COLON block"""
    return p


def p_opt_else(p):
    """opt_else :
                | else"""
    return p


def p_else(p):
    """else : ELSE COLON block"""
    return p


def p_inline_object(p):
    """inline_object : OBJECT_BEGIN_LX OBJECT_BEGIN_RX block OBJECT_END"""
    return p


def p_key(p):
    """key : IDENTIFIER
           | IDENTIFIER DOT key"""
    return p


def p_block(p):
    """block : PASS
             | statement_list"""
    return p


def p_statement_list(p):
    """statement_list : statement
                      | statement_list statement"""
    return p


def p_value(p):
    """value : INTEGER
             | FLOAT
             | BOOLEAN
             | DATETIME
             | user_defined_value"""
    return p


def p_user_defined_value(p):
    """user_defined_value : PAREN_LX IDENTIFIER PAREN_RX expression"""
    return p


def p_expression(p):
    """expression : """
    return p


parser = ply.yacc.yacc()  # generate yacc table


def parse(path):
    global parsed
    parsed = { }
    with open(path, 'r') as f:
        contents = f.read()
    lexer.lineno = 1
    for line in contents.split('\n'):
        parser.parse(line)
        lexer.lineno += 1
    return parsed
