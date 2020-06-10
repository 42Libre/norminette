from lexer import Token
from rules import PrimaryRule
from scope import *
from context import GlobalScope, UserDefinedType, ControlStructure, Function


lbrackets = ["LBRACE", "LPARENTHESIS", "LBRACKET"]
rbrackets = ["RBRACE", "RPARENTHESIS", "RBRACKET"]


class IsEnumVarDecl(PrimaryRule):
    def __init__(self):
        super().__init__()
        self.priority = 5
        self.scope = [UserDefinedEnum]

    def assignment_right_side(self, context, pos):
        sep = ["COMMA", "ASSIGN"]
        i = context.skip_ws(pos, nl=True)
        while context.peek_token(i) and context.check_token(i, sep) is False:
            if context.check_token(i, lbrackets) is True:
                i = context.skip_nest(i)
            i += 1
        return True, i

    def var_declaration(self, context, pos):
        pclose = ["RPARENTHESIS", "NEWLINE", "SPACE", "TAB"]
        brackets = 0
        parenthesis = 0
        braces = 0
        i = pos
        identifier = False
        while context.peek_token(i) is not None and context.check_token(i, ["COMMA"]) is False:
            if context.check_token(i, "IDENTIFIER") is True and braces == 0 and brackets == 0 and parenthesis == 0:
                identifier = True
            elif context.check_token(i, lbrackets) is True:
                if context.check_token(i, "LBRACE") is True:
                    braces += 1
                if context.check_token(i, "LBRACKET") is True:
                    brackets += 1
                if context.check_token(i, "LPARENTHESIS") is True:
                    parenthesis += 1
            elif context.check_token(i, rbrackets) is True:
                if context.check_token(i, "RBRACE") is True:
                    braces -= 1
                if context.check_token(i, "RBRACKET") is True:
                    brackets -= 1
                if context.check_token(i, "RPARENTHESIS") is True:
                    parenthesis -= 1
            elif context.check_token(i, "ASSIGN") is True:
                if identifier == False:
                    return False, pos
                ret, i = self.assignment_right_side(context, i + 1)
                i -= 1
                if ret is False:
                    return False, pos
            elif context.check_token(i, ['SPACE', "TAB", "MULT", "BWISE_AND", "NEWLINE"]):
                pass
            elif parenthesis == 0 and brackets == 0 and braces == 0:
                return False, 0
            i += 1
        if identifier == False:
            return False, pos
        if context.check_token(i, "COMMA") is True:
            return True, i
        return False, pos

    def is_func_pointer(self, context, pos):
        i = context.skip_ws(pos)
        if context.check_token(i, "LPARENTHESIS") is False:
            return False, pos

        i += 1
        p = 1
        plvl= 0 # nesting level of the first pointer operator encountered

        while p and context.check_token(i, ["MULT", "LPARENTHESIS"] + ws):
            if context.check_token(i, "MULT") and not plvl:
                plvl = p
            elif context.check_token(i, "LPARENTHESIS"):
                p += 1
            i += 1

        while p and context.peek_token(i) is not None:
            if context.check_token(i, "LPARENTHESIS") is True:
                p += 1
                if identifier is True:
                    return False, pos
            elif context.check_token(i, "RPARENTHESIS") is True:
                p -= 1
                if identifier is True:
                    par_pos = i
                    break
            elif context.check_token(i, "IDENTIFIER") is True:
                identifier = True
            i += 1
        else:
            return False, pos

    def run(self, context):
        #ret, i = context.check_type_specifier(0)
        #if ret is False:
        #    return False, 0
        #if context.check_token(i, ['SPACE', 'TAB']) is False and context.check_token(i - 1, ['SPACE', 'TAB']) is False:
        #    return False, 0
        ret, i = self.var_declaration(context, 0)
        if ret is False:
            return False, 0
        while ret:
            ret, i = self.var_declaration(context, i)
            if context.check_token(i, "COMMA") is True:
                i += 1
                i = context.eol(i)
                return True, i
        return False, 0