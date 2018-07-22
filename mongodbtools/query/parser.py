# simpleSQL.py
#
# simple demo of using the parsing library to do simple-minded SQL parsing
# could be extended to include where clauses etc.
#
# Copyright (c) 2003, Paul McGuire
#
# Originally from http://pyparsing.wikispaces.com/file/view/simpleSQL.py

import pyparsing


def test(str):
    print(str, "->")
    try:
        tokens = simpleSQL.parseString(str)
        print("tokens = ", tokens)
        print("tokens.columns =", tokens.columns)
        print("tokens.tables =", tokens.tables)
        print("tokens.where =", tokens.where)
    except pyparsing.ParseException as err:
        print(" " * err.loc + "^\n" + err.msg)
        print(err)
    print()


# define SQL tokens
selectStmt = pyparsing.Forward()
selectToken = pyparsing.Keyword("select", caseless=True)
fromToken = pyparsing.Keyword("from", caseless=True)
whereToken = pyparsing.Keyword("where", caseless=True)

ident = pyparsing.Word(pyparsing.alphas + "_", pyparsing.alphanums + "_$.").setName("identifier")
columnName = pyparsing.delimitedList(ident, ".", combine=True)
columnNameList = pyparsing.Group(pyparsing.delimitedList(columnName))
tableName = pyparsing.delimitedList(ident, ".", combine=True)
tableNameList = pyparsing.Group(pyparsing.delimitedList(tableName))

whereExpression = pyparsing.Forward()
and_ = pyparsing.Keyword("and", caseless=True)
or_ = pyparsing.Keyword("or", caseless=True)
in_ = pyparsing.Keyword("in", caseless=True)

E = pyparsing.CaselessLiteral("E")
binop = pyparsing.oneOf("= != < > >= <= eq ne lt le gt ge", caseless=True)
arithSign = pyparsing.Word("+-", exact=1)
realNum = pyparsing.Combine(pyparsing.Optional(arithSign) +
                            (pyparsing.Word(pyparsing.nums) + "." +
                             pyparsing.Optional(pyparsing.Word(pyparsing.nums)) |
                             ("." + pyparsing.Word(pyparsing.nums))) +
                            pyparsing.Optional(E + pyparsing.Optional(arithSign) +
                                               pyparsing.Word(pyparsing.nums)))
intNum = pyparsing.Combine(pyparsing.Optional(arithSign) +
                           pyparsing.Word(pyparsing.nums) +
                           pyparsing.Optional(E +
                                              pyparsing.Optional("+") +
                                              pyparsing.Word(pyparsing.nums)))

columnRval = realNum | intNum | pyparsing.quotedString | columnName  # need to add support for
# alg expressions
whereCondition = pyparsing.Group(
    (columnName + binop + columnRval) |
    (columnName + in_ + "(" + pyparsing.delimitedList(columnRval) + ")") |
    ("(" + whereExpression + ")")
)
whereExpression << whereCondition + pyparsing.ZeroOrMore((and_ | or_) + whereExpression)

# define the grammar
selectStmt << (selectToken +
               ('*' | columnNameList).setResultsName("columns") +
               fromToken +
               tableNameList.setResultsName("tables") +
               pyparsing.Optional(pyparsing.Group(whereToken + whereExpression), "").setResultsName("where"))

simpleSQL = selectStmt

# define Oracle comment format, and ignore them
oracleSqlComment = "--" + pyparsing.restOfLine
simpleSQL.ignore(oracleSqlComment)

"""
test( "SELECT * from XYZZY, ABC" )
test( "select * from SYS.XYZZY" )
test( "Select A from Sys.dual" )
test( "Select A,B,C from Sys.dual" )
test( "Select A, B, C from Sys.dual" )
test( "Select A, B, C from Sys.dual, Table2   " )
test( "Xelect A, B, C from Sys.dual" )
test( "Select A, B, C frox Sys.dual" )
test( "Select" )
test( "Select &&& frox Sys.dual" )
test( "Select A from Sys.dual where a in ('RED','GREEN','BLUE')" )
test( "Select A from Sys.dual where a in ('RED','GREEN','BLUE') and b in (10,20,30)" )
test( "Select A,b from table1,table2 where table1.id eq table2.id -- test out 
comparison operators" )
test( "Select * from User, RemoteAccount where user._id = user.user_id)" )


Test output:
>pythonw -u simpleSQL.py
SELECT * from XYZZY, ABC ->
tokens =  ['select', '*', 'from', ['XYZZY', 'ABC']]
tokens.columns = *
tokens.tables = ['XYZZY', 'ABC']

select * from SYS.XYZZY ->
tokens =  ['select', '*', 'from', ['SYS.XYZZY']]
tokens.columns = *
tokens.tables = ['SYS.XYZZY']

Select A from Sys.dual ->
tokens =  ['select', ['A'], 'from', ['SYS.DUAL']]
tokens.columns = ['A']
tokens.tables = ['SYS.DUAL']

Select A,B,C from Sys.dual ->
tokens =  ['select', ['A', 'B', 'C'], 'from', ['SYS.DUAL']]
tokens.columns = ['A', 'B', 'C']
tokens.tables = ['SYS.DUAL']

Select A, B, C from Sys.dual ->
tokens =  ['select', ['A', 'B', 'C'], 'from', ['SYS.DUAL']]
tokens.columns = ['A', 'B', 'C']
tokens.tables = ['SYS.DUAL']

Select A, B, C from Sys.dual, Table2    ->
tokens =  ['select', ['A', 'B', 'C'], 'from', ['SYS.DUAL', 'TABLE2']]
tokens.columns = ['A', 'B', 'C']
tokens.tables = ['SYS.DUAL', 'TABLE2']

Xelect A, B, C from Sys.dual ->
^
Expected 'select'
Expected 'select' (0), (1,1)

Select A, B, C frox Sys.dual ->
               ^
Expected 'from'
Expected 'from' (15), (1,16)

Select ->
      ^
Expected '*'
Expected '*' (6), (1,7)

Select &&& frox Sys.dual ->
       ^
Expected '*'
Expected '*' (7), (1,8)

>Exit code: 0
"""
