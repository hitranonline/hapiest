from parsy import *


class DSL:
    """
    hapi has support for a small lisp-like Domain Specific Language implemented using nested 
    python tuples. The following grammar was made in order to make the language look like a more
    proper lisp. The grammar is not perfect, there are a few optimizations that could be made
    quite readily (e.g. use case-independent regex instead of checking for upper and lower case).
    The DSL is used by hapi to query and filter tables stored in memory. The DSL class contains a
    static parser object for the DSL.
    """

    # Whitespace..
    whitespace_parse = whitespace.optional()

    # Literals / Constants
    int_parse = regex('[-+]?(0|([1-9][0-9]*))').map(int)
    float_parse = regex('[-+]?((\\d*\\.\\d+)|(\\d+(\\.\\d*)?))([Ee][+-]?\\d+)?').map(float)
    string_parse = regex(
        "(\"((\\\\[\\\\a-zA-Z\'])|[^\"])*\")|('((\\\\[\\\\a-zA-Z\'])|[^'])*')").map(eval)
    name_parse = regex('[a-zA-Z][a-zA-Z_\\-0-9]*')

    # Arithmetic
    add_parse = regex('\\+|(add)|(ADD)|(sum)|(SUM)').map(lambda x: '+')
    sub_parse = regex('\\-|(sub)|(SUB)|(diff)|(DIFF)').map(lambda x: '-')
    mul_parse = regex('\\*|(mul)|(MUL)').map(lambda x: '*')
    div_parse = regex('\\/|(DIV)|(div)').map(lambda x: '/')

    # Comparison / Conditionals
    between_parse = regex('(range)|(RANGE)|(between)|(BETWEEN)').map(lambda x: 'range')
    subset_parse = regex('(in)|(IN)|(subset)|(SUBSET)').map(lambda x: 'in')
    and_parse = regex('(and)|(AND)|(&&?)').map(lambda x: 'and')
    or_parse = regex('(or)|(OR)|(\\|\\|?)').map(lambda x: 'or')
    not_parse = regex('(not)|(NOT)|(!)').map(lambda x: 'not')
    lt_parse = regex('(<)|(less)|(LESS)|(lt)|(LT)').map(lambda x: '<')
    gt_parse = regex('(>)|(more)|(MORE)|(gt)|(GT)|(greater)|(GREATER)').map(lambda x: '>')
    lte_parse = regex('(<=)|(lessorequal)|(LESSOREQUAL)|(lte)|(LTE)').map(lambda x: '<=')
    gte_parse = regex(
        '(>=)|(moreorequal)|(MOREOREQUAL)|(gte)|(GTE)|(greaterorequal)|(GREATEROREQUAL)').map(
        lambda x: '>=')
    equal_parse = regex('(==?)|(eq)|(EQ)|(equal)|(EQUAL)').map(lambda x: '=')
    neq_parse = regex('(!=)|(<>)|(~=)|(ne)|(NE)|(neq)|(NEQ)|(note)|(NOTE)').map(lambda x: '!=')

    # Casting
    to_string_parse = regex('(to_string)|(TO_STRING)|(str)|(STR)|(string)|(STRING)').map(
        lambda x: 'str')
    to_list_parse = regex('(to_list)|(TO_LIST)|(list)|(LIST)').map(lambda x: 'list')

    # Search / Match / Count
    search_parse = regex('(search)|(SEARCH)').map(lambda x: 'search')
    match_parse = regex('(match)|(MATCH)|(like)|(LIKE)').map(lambda x: 'match')
    find_parse = regex('(findall)|(FINDALL)').map(lambda x: 'findall')
    count_parse = regex('(count)|(COUNT)').map(lambda: 'count')

    operation = add_parse | sub_parse | mul_parse | div_parse | between_parse | subset_parse | \
                and_parse | or_parse | not_parse | lt_parse | gt_parse | lte_parse | gte_parse | \
                equal_parse | neq_parse | to_string_parse | to_list_parse | search_parse | \
                match_parse | find_parse | count_parse

    p_open_parse = whitespace_parse >> string('(') >> whitespace_parse
    p_close_parse = whitespace_parse >> string(')') >> whitespace_parse
    list_parse = p_open_parse >> (
            (float_parse | int_parse | string_parse) << whitespace_parse).many().map(
        list) << p_close_parse

    @generate
    def call_parse():
        yield DSL.p_open_parse
        first = yield DSL.operation
        args = yield DSL.expression_parse.many()
        yield DSL.p_close_parse

        return tuple([first] + args)

    expression_parse = whitespace_parse >> (
            float_parse | int_parse | string_parse | name_parse | call_parse | list_parse) << \
                       whitespace_parse

    bracket_open = whitespace_parse >> string('[') >> whitespace_parse
    bracket_close = whitespace_parse >> string(']') >> whitespace_parse
    expression_list_parse = whitespace_parse >> bracket_open >> expression_parse.many() << \
                            bracket_close << whitespace_parse

    @staticmethod
    def parse_expression(expression):
        """
        Attempts to parse an expression into the nested-tuple format used by hapi.

        """
        try:
            x = DSL.expression_list_parse.parse(expression)
            return x
        except:
            try:
                z = DSL.expression_parse.parse(expression)
                return z
            except:
                return None
