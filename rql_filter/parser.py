from django.db.models import Q
from pyparsing import ZeroOrMore, Literal, Word, alphas, alphanums, Group, \
    nestedExpr, Forward, delimitedList, ParseException


AND = Literal(';').setParseAction(lambda: 'AND')
OR = Literal(',').setParseAction(lambda: 'OR')

EQ = Literal('==').setParseAction(lambda: 'exact')
NE = Literal('=ne=').setParseAction(lambda: 'ne')
GE = Literal('=ge=').setParseAction(lambda: 'gte')
GT = Literal('=gt=').setParseAction(lambda: 'gt')
LE = Literal('=le=').setParseAction(lambda: 'lte')
LT = Literal('=lt=').setParseAction(lambda: 'lt')
COMPARISONS = EQ | NE | GE | GT | LE | LT


NAME = Word(alphas+'_', alphanums+'_')
VALUE = Word(alphanums) | \
        Literal('"').suppress() + Word(alphanums+' ') + Literal('"').suppress()


IN = Literal('=in=').setParseAction(lambda: 'in')
ARRAY = Literal('(').suppress() + delimitedList(VALUE, ',') + \
        Literal(')').suppress()
ARRAY = ARRAY.setParseAction(lambda s, loc, toks: [toks])


SIMPLE_COND = Group(NAME + COMPARISONS + VALUE) | \
              Group(NAME + IN + ARRAY)


NESTED_CONDS = Forward()
COND = SIMPLE_COND | nestedExpr('(', ')', NESTED_CONDS)
CONDS = COND + ZeroOrMore((AND | OR) + COND)
NESTED_CONDS << CONDS

QUERY = NESTED_CONDS


def parse_rql(expr):
    try:
        parse_results = QUERY.parseString(expr)
    except ParseException:
        raise

    return eval(str(parse_results))


def create_django_orm_condition(values):
    q = None
    if len(values) == 1:
        return create_django_orm_condition(values[0])

    if values[1] in ['OR', 'AND']:
        op = None
        for value in values:
            if value in ['OR', 'AND']:
                op = value
                continue
            elif len(value) == 1:
                qq = (create_django_orm_condition(value[0]))
            elif value[1] in ['OR', 'AND']:
                qq = (create_django_orm_condition(value))
            else:
                field = '%s__%s' % (value[0], value[1])
                qq = Q(**{field: value[2]})
            if q:
                if op == 'AND':
                    q = q & qq
                else:
                    q = q | qq
            else:
                q = qq

        return q

    if len(values) == 3:
        field = '%s__%s' % (values[0], values[1])
        return Q(**{field: values[2]})
