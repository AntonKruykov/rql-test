from django.db.models import Q
from pyparsing import ZeroOrMore, Literal, Word, alphas, alphanums, Group, \
    nestedExpr, Forward, delimitedList, ParseException


"""
Грамматика поддерживает: 
- Сравниения == != < > <= >= in
- Логические И, ИЛИ
- Скобки и вложенность
"""

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
    """
    парсим rql строку, получаем вложенный список с разобранными элементами
    параметр - значение
    Пример::
            parse_rql('a=gt=b')  # -> [['a', 'gt', 'b']]
            parse_rql(''a=in=(1,2,3),b==4'')  # ->
            [['a', 'in', ['1', '2', '3']], 'OR', ['b', 'exact', '4']]

    :param expr: строка rql
    :return: вложенный список
    """
    try:
        parse_results = QUERY.parseString(expr)
    except ParseException:
        raise
    # pyparsing возвращает результат, который предствляются в удобном строковом
    #  виде, но в реальности это вложенная стуктура с дополнительными
    # элементами, которые нам не нужны
    # Чтобы облегчить работу, беру строковой вид результата и получаю из него
    # список с вложениями
    return eval(str(parse_results))


def create_django_orm_condition(values):
    """
    из распарсенной rql строки, поученной в результате parse_rql, строится
    Q выражение Django

    Пример::
        create_django_orm_condition(['a', 'exact', 'b']) # -> Q(a__exact='b')
        create_django_orm_condition([['a', 'in', ['1', '2', '3']], 'OR',
                                    ['b', 'exact', '4']]) # ->
                                    Q(a__in=['1', '2', '3']) | Q(b__exact='4')

    :param values: распарсенное rql выражение в виде вложенного списка
    :return: Q - выражение Django ORM
    """

    q = None
    # случай простой вложенности [[...]]
    # такое может быть при первой итерации или при излишних скобках
    if len(values) == 1:
        return create_django_orm_condition(values[0])

    # разбираем сложное выражение с разделением логичиискими элементами
    # [[...] AND [...] OR [...]]
    if values[1] in ['OR', 'AND']:
        op = None
        for value in values:
            # перебираем элементы, если это логически оператор, то его
            # запоминаем, чтобы потом им склеить выражения
            if value in ['OR', 'AND']:
                op = value
                continue
            elif len(value) == 1:
                # попалось [[...]], добавляем скобки, углубляемся в рекурсию
                qq = (create_django_orm_condition(value[0]))
            elif value[1] in ['OR', 'AND']:
                # попалось [[...] AND [...] ...], углубляемся в рекурсию
                qq = (create_django_orm_condition(value))
            else:
                # остается простое выражение
                field = '%s__%s' % (value[0], value[1])
                qq = Q(**{field: value[2]})

            # собираем цепочку выражений текущего уровня
            if q:
                if op == 'AND':
                    q = q & qq
                else:
                    q = q | qq
            else:
                q = qq

        return q  # выход из рекурсии для выражения с логичекими операторами

    # выход из рекурсии для простого случая
    # обрабатываем простые выражения вида [a, exact, b] или [a in [1,2 3]]
    if len(values) == 3:
        field = '%s__%s' % (values[0], values[1])
        return Q(**{field: values[2]})
