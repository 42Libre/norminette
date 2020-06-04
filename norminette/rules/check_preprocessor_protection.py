from rules import Rule
from lexer import Lexer, TokenError
from scope import *


class CheckPreprocessorProtection(Rule):
    def __init__(self):
        super().__init__()
        self.depends_on = ["IsPreprocessorStatement"]

    def run(self, context):
        i = 0
        if type(context.scope) is not GlobalScope:
            return False, 0
        if context.check_token(i, ["IFNDEF", "ENDIF"]) is False or context.filetype != 'h':
            return False, 0
        protection = context.filename.upper().split('/')[-1].replace('.', '_')
        val = context.peek_token(i).value.split(' ')[-1]
        content = Lexer(val)
        tkns = content.get_tokens()
        if context.check_token(i, "IFNDEF") is True:
            if tkns[0].value == protection and context.scope.header_protection == -1 and context.preproc_scope_indent == 1:
                if len(context.history) > 1:
                    for i in range(len(context.history) - 2, 0, -1):
                        if context.history[i] != "IsEmptyLine" and context.history[i] != "IsComment":
                            context.new_error("HEADER_PROT_ALL", context.peek_token(0))
                            break
                context.scope.header_protection = 0
            elif tkns[0].value != protection and context.scope.header_protection == -1:
                context.new_error("HEADER_PROT_NAME", context.peek_token(0))
        elif context.check_token(i, "ENDIF") is True:
            if context.scope.header_protection == 1 and context.preproc_scope_indent == 0:
                context.scope.header_protection = 2
        return False, 0