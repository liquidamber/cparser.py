import os, sys
import clex

class Expr:
    pass

class BinExpr(Expr):
    def __init__(self, a, op, b):
        self.a  = a
        self.b  = b
        self.op = op
#        print "(%s, %s, %s)" % (a, op, b)
    def __str__(self):
        return str(self.a)+str(self.op)+str(self.b)
    def give_back(self):
        return self.a.give_back() + self.op.give_back() + self.b.give_back()

class UniExpr(Expr):
    def __init__(self, a, op):
        self.a  = a
        self.op = op
#        print "(%s, %s)" % (a, op)
    def __str__(self):
        return str(self.op)+str(self.a)
    def give_back(self):
        return self.op.give_back() + self.a.give_back()

class PostExpr(UniExpr):
    def __init__(self, *args):
        UniExpr.__init__(self, *args)
    def __str__(self):
        return str(self.a)+str(self.op)
    def give_back(self):
        return self.a.give_back() + self.op.give_back()

class ParenOperateExpr(BinExpr):
    def __init__(self, a, b, beg, end):
        self.beg = beg
        self.end = end
        BinExpr.__init__(self, a, None, b)
    def give_back(self):
        return self.a.give_back() + [self.beg] + self.b.give_back() + [self.end]

class SelectExpr(ParenOperateExpr):
    def __str__(self):
        return "%s[%s]" % ( str(self.a), str(self.b) )

class FuncExpr(ParenOperateExpr):
    def __str__(self):
        return "%s(%s)" % ( str(self.a), str(self.b) )

class ParenExpr(UniExpr):
    def __init__(self, a, beg, end):
        self.beg = beg
        self.end = end
        UniExpr.__init__(self, a, None)
#        print "(%s)" % a
    def __str__(self):
        return "(%s)" % str(self.a)
    def give_back(self):
        return [self.beg] + self.a.give_back() + [self.end]

class CastExpr(UniExpr):
    def __init__(self, a, typename):
        UniExpr.__init__(self, a, typename)
    def __str__(self):
        return "%s%s" % (str(self.op), str(self.a))
    def give_back(self):
        return self.op.give_back()+self.a.give_back()

class CondExpr(Expr):
    def __init__(self, a, b, c, cond_op_if, cond_op_else):
        self.a = a
        self.b = b
        self.c = c
        self.cond_op_if = cond_op_if
        self.cond_op_else = cond_op_else
#        print "(%s ? %s : %s)" % (a, b, c)
    def __str__(self):
        return "%s ? %s : %s" % (str(self.a), str(self.b), str(self.c))
    def give_back(self):
        return (self.a.give_back()+self.cond_op_if.give_back()+
                self.b.give_back()+self.cond_op_else.give_back()+
                self.c.give_back())


class MyList(object):
    def __init__(self, a=None):
        self.list = [] if a is None else [a]
    def append(self, x):
        self.list.append(x)

class SimpleList(MyList):
    def __str__(self):
        return "".join([str(x) for x in self.list])
    def give_back(self):
        return reduce(lambda x,y: x+y, [i.give_back() for i in self.list])

class ExprList(MyList):
    def __str__(self):
        return ", ".join([str(x) for x in self.list])
    def give_back(self):
        ret = self.list[0].give_back()
        for i in self.list[1:]:
            ret += [clex.Token(",", "", -1, -1)] + i.give_back()
        return ret

class TokenList(SimpleList):
    def __str__(self):
        return " ".join([str(x) for x in self.list])


class Stmt(object):
    pass

class JumpStmt(Stmt):
    def __init__(self, op, semic, target=None):
        self.op = op
        self.semic = semic
        self.target = target
    def __str__(self):
        return "".join((str(self.op),
                        " " + str(self.target) if self.target is not None else "",
                        str(self.semic)))

class WordHeadStmt(Stmt):
    def __init__(self, op, open_paren, expr, close_paren, stmt):
        self.op = op
        self.po = open_paren
        self.expr = expr
        self.pc = close_paren
        self.stmt = stmt
    def __str__(self):
        return (str(self.op) +
                str(self.po) +
                str(self.expr) +
                str(self.pc) +
                str(self.stmt))

class IfStmt(WordHeadStmt):
    def __init__(self, op, po, expr, pc, then_stmt, else_word=None, else_stmt=None):
        self.else_word = else_word
        self.else_stmt = else_stmt
        WordHeadStmt.__init__(self, op, po, expr, pc, then_stmt)
    def __str__(self):
        s = WordHeadStmt.__str__(self)
        if self.else_word is None:
            return s
        return s + str(self.else_word) + str(self.else_stmt)

class DoWhileStmt(WordHeadStmt):
    def __init__(self, do_word, stmt, while_word, po, expr, pc, semic):
        self.do_word = do_word
        self.semic = semic
        WordHeadStmt.__init__(self, while_word, po, expr, pc, stmt)
    def __str__(self):
        return (str(self.do_word) +
                str(self.stmt) +
                str(self.op) +
                str(self.po) +
                str(self.expr) +
                str(self.pc) +
                str(self.semic))

class ForExprs(object):
    def __init__(self, expr_init, semic_a, expr_cont, semic_b, expr_step):
        self.exprs = (expr_init, semic_a, expr_cont, semic_b, expr_step)
    def __str__(self):
        return "".join(str(x) if x is not None else " " for x in self.exprs)

class ForStmt(WordHeadStmt):
    def __init__(self, op, po, ei, sa, ec, sb, es, pc, stmt):
        exprs = ForExprs(ei, sa, ec, sb, es)
        WordHeadStmt.__init__(self, op, po, exprs, pc, stmt)

class ExprStmt(Stmt):
    def __init__(self, expr, semic):
        self.expr = expr
        self.semic = semic
    def __str__(self):
        return "".join(map(str, (self.expr, self.semic)))

class LabelStmt(Stmt):
    def __init__(self, label, colon, stmt):
        self.label = label
        self.colon = colon
        self.stmt = stmt
    def __str__(self):
        return "".join(map(str, (self.label, self.colon, self.stmt)))

class CaseStmt(LabelStmt):
    def __init__(self, case_word, expr, colon, stmt):
        self.op = case_word
        LabelStmt.__init__(self, expr, colon, stmt)
    def __str__(self):
        return str(self.op) + str(LabelStmt.__str__(self))

class SingleLabelStmt(Stmt):
    def __init__(self, op, colon, stmt):
        self.op = op
        self.colon = colon
        self.stmt = stmt
    def __str__(self):
        return (str(self.op) +
                str(self.colon) +
                str(self.stmt))

class ExprLabelStmt(SingleLabelStmt):
    def __init__(self, case_word, expr, colon, stmt):
        self.expr = expr
        SingleLabelStmt.__init__(self, case_word, colon, stmt)
    def __str__(self):
        return "".join(map(str, (self.op,
                                 self.expr,
                                 self.colon,
                                 self.stmt)))

class CompoundStmt(Stmt, MyList):
    def __init__(self, open_brace):
        self.op = open_brace
        MyList.__init__(self)
    def __str__(self):
        return "\n".join((str(self.op),
                          "\n".join(str(x) for x in self.list),
                          str(self.cl)))
    def close(self, close_brace):
        self.cl = close_brace

class CParserSyntaxError(Exception):
    def __init__(self, token, format_string="parser syntax error: "):
        self.token = token
        Exception.__init__(self, "line %d: char %d: " % (self.token.linecount+1,
                                                         self.token.charcount+1) +
                           format_string + str(self.token))

class CParser(object):
    def __init__(self, string, tokenizer=clex.Tokenizer):
        self.tokenizer = tokenizer(string)
        self.tok_iter  = iter(self.tokenizer)
        self.rev = []

    def get_tok(self):
        if len(self.rev):
            return self.rev.pop()
        else:
            return self.tok_iter.next()

    def rev_tok(self, expr):
        tmp = expr.give_back()
        tmp.reverse()
        self.rev += tmp

    def cur_tok(self):
        if not len(self.rev):
            self.rev.append(self.get_tok())
        return self.rev[-1]

    def parse_tok(self, tok_type, format="unexpected token: "):
        t = self.get_tok()
        if t.get_type() != tok_type:
            self.rev_tok(t)
            raise CParserSyntaxError(t, format)
        return t

    def parse_tok_if_possible(self, tok_type):
        t = self.cur_tok()
        if t.get_type() != tok_type:
            return None
        else:
            self.get_tok()
            return t

    def parse_paren_match(self):
        a = self.parse_tok("(", "not paren open: %s")
        l = TokenList(a)
        while True:
            a = self.cur_tok()
            if a.get_type() == "(":
                l.append(self.parse_paren_match())
            else:
                l.append(a)
                self.get_tok()
                if a.get_type() == ")":
                    return l

    def is_type_name(self, a):
        at = a.get_type()
        if (at == "void" or at == "char"  or at == "short"  or at == "int" or
            at == "long" or at == "float" or at == "double" or at == "signed" or
            at == "unsigned" or at == "struct" or at == "union" or at == "enum" or
            at == "const" or at == "volatile"):
            return True
        else:
            return False

    def parse_prim_expr(self):
        a = self.get_tok()
        if(a.get_type() == "literal" or a.get_type() == "identifier"):
            return a
        elif(a.get_type() == "("):
            op1 = a
            a = self.parse_expr()
            op2 = self.parse_tok(")", "paren close expected: %s")
            return ParenExpr(a, op1, op2)
        else:
            self.rev_tok(a)
            raise CParserSyntaxError(a, "Not Primitive Expression: ")

    def parse_post_expr(self):
        a = self.parse_prim_expr()
        while True:
            op = self.get_tok()
            if(op.get_type() == "." or op.get_type() == "->"):
                b = self.get_tok()
                if(b.get_type() != "identifier"):
                    self.rev_tok(b)
                    self.rev_tok(op)
                    self.rev_tok(a)
                    raise CParserSyntaxError(b, "Not member of struct: ")
                a = BinExpr(a, op, b)
            elif(op.get_type() == "++" or op.get_type() == "--"):
                a = PostExpr(a, op)
            elif(op.get_type() == "("):
                b, c = self.parse_arg_expr_list()
                a = FuncExpr(a, b, op, c)
            elif(op.get_type() == "["):
                b = self.parse_expr()
                c = self.get_tok()
                if(c.get_type() != "]"):
                    self.rev_tok(c)
                    self.rev_tok(b)
                    self.rev_tok(op)
                    self.rev_tok(a)
                    raise CParserSyntaxError(b, "Paren Match Error")
                a = SelectExpr(a, b, op, c)
            else:
                self.rev_tok(op)
                return a

    def parse_arg_expr_list(self):
        a = self.get_tok()
        if a.get_type() == ")":
            return (ExprList(), a)
        self.rev_tok(a)
        a = self.parse_assign_expr()
        l = ExprList(a)
        op = self.get_tok()
        while op.get_type() == ",":
            b = self.parse_assign_expr()
            l.append(b)
            op = self.get_tok()
        if op.get_type() == ")":
            return (l, op)
        else:
            self.rev_tok(op)
            self.rev_tok(l)
            self.rev_tok(a)
            raise CParserSyntaxError(op, "Paren Match Error")

    def parse_unary_expr(self):
        a = self.get_tok()
        atype = a.get_type()
        if atype == "++" or atype == "--":
            b = self.parse_unary_expr()
            return UniExpr(b, a)
        elif (atype == "&" or atype == "*" or atype == "+" or
              atype == "-" or atype == "~" or atype == "!"):
            b = self.parse_cast_expr()
            return UniExpr(b, a)
#Not complete support for sizeof
        elif atype == "sizeof":
            if self.cur_tok().get_type() != "(":
                b = self.parse_unary_expr()
            else:
                b = self.parse_paren_match()
            return UniExpr(b, a)
        else:
            self.rev_tok(a)
            a = self.parse_post_expr()
            return a

#Not support for cast (typedef-name)
    def parse_cast_expr(self):
        a = self.cur_tok()
        if a.get_type() == "(":
            a = self.get_tok()
            b = self.cur_tok()
            if self.is_type_name(b):
                self.rev_tok(a)
                a = self.parse_paren_match()
                b = self.parse_cast_expr()
                return CastExpr(b, a)
            else:
                self.rev_tok(a)
        return self.parse_unary_expr()

    def parse_mult_expr(self):
        a = self.parse_cast_expr()
        while (self.cur_tok().get_type() == "*" or
               self.cur_tok().get_type() == "/" or
               self.cur_tok().get_type() == "%"):
            op = self.get_tok()
            b  = self.parse_cast_expr()
            a  = BinExpr(a, op, b)
        return a

    def parse_add_expr(self):
        a = self.parse_mult_expr()
        while (self.cur_tok().get_type() == "+" or
               self.cur_tok().get_type() == "-"):
            op = self.get_tok()
            b  = self.parse_mult_expr()
            a  = BinExpr(a, op, b)
        return a

    def parse_shift_expr(self):
        a = self.parse_add_expr()
        while (self.cur_tok().get_type() == "<<" or
               self.cur_tok().get_type() == ">>"):
            op = self.get_tok()
            b  = self.parse_add_expr()
            a  = BinExpr(a, op, b)
        return a

    def parse_relate_expr(self):
        a = self.parse_shift_expr()
        while (self.cur_tok().get_type() == "<"  or
               self.cur_tok().get_type() == ">"  or
               self.cur_tok().get_type() == "<=" or
               self.cur_tok().get_type() == ">="):
            op = self.get_tok()
            b  = self.parse_shift_expr()
            a  = BinExpr(a, op, b)
        return a

    def parse_equal_expr(self):
        a = self.parse_relate_expr()
        while (self.cur_tok().get_type() == "==" or
               self.cur_tok().get_type() == "!="):
            op = self.get_tok()
            b  = self.parse_relate_expr()
            a  = BinExpr(a, op, b)
        return a

    def parse_bit_and_expr(self):
        a = self.parse_equal_expr()
        while self.cur_tok().get_type() == "&":
            op = self.get_tok()
            b  = self.parse_equal_expr()
            a  = BinExpr(a, op, b)
        return a

    def parse_bit_xor_expr(self):
        a = self.parse_bit_and_expr()
        while self.cur_tok().get_type() == "^":
            op = self.get_tok()
            b  = self.parse_bit_and_expr()
            a  = BinExpr(a, op, b)
        return a

    def parse_bit_or_expr(self):
        a = self.parse_bit_xor_expr()
        while self.cur_tok().get_type() == "|":
            op = self.get_tok()
            b  = self.parse_bit_xor_expr()
            a  = BinExpr(a, op, b)
        return a

    def parse_logic_and_expr(self):
        a = self.parse_bit_or_expr()
        while self.cur_tok().get_type() == "&&":
            op = self.get_tok()
            b  = self.parse_bit_or_expr()
            a  = BinExpr(a, op, b)
        return a

    def parse_logic_or_expr(self):
        a = self.parse_logic_and_expr()
        while self.cur_tok().get_type() == "||":
            op = self.get_tok()
            b  = self.parse_logic_and_expr()
            a  = BinExpr(a, op, b)
        return a

    def parse_cond_expr(self):
        cond = self.parse_logic_or_expr()
        op1 = self.parse_tok_if_possible("?")
        if not op1:
            return cond
        b  = self.parse_expr()
        op2 = self.parse_tok(":", "conditonal operator expected: %s")
        c  = self.parse_cond_expr()
        return CondExpr(cond, b, c, op1, op2)

    def parse_assign_expr(self):
        while True:
            a  = self.parse_unary_expr()
            op = self.get_tok()
            if (op.get_type() == ">>=" or
                op.get_type() == "<<=" or
                op.get_type() == "+=" or
                op.get_type() == "-=" or
                op.get_type() == "*=" or
                op.get_type() == "/=" or
                op.get_type() == "%=" or
                op.get_type() == "|=" or
                op.get_type() == "&=" or
                op.get_type() == "^=" or
                op.get_type() == "="):
                c = self.parse_assign_expr()
                return BinExpr(a, op, c)
            else:
                self.rev_tok(op)
                self.rev_tok(a)
                return self.parse_cond_expr()

    def parse_expr(self):
        a  = ExprList(self.parse_assign_expr())
        op = self.cur_tok()
        while op.get_type() == ",":
            self.get_tok()
            a.append(self.parse_assign_expr())
            op = self.cur_tok()
        return a

    def parse_stmt(self):
        op = self.cur_tok().get_type()
        if op == "goto":
            self.get_tok()
            a = self.parse_tok("identifier")
            semic = self.parse_tok(";")
            return JumpStmt(op, semic, a)
        elif (op == "continue" or
              op == "break"):
            op = self.get_tok()
            semic = self.parse_tok(";")
            return JumpStmt(op, semic)
        elif op == "return":
            op = self.get_tok()
            if self.cur_tok().get_type() == ";":
                semic = self.parse_tok(";")
                return JumpStmt(op, semic)
            else:
                try:
                    expr = self.parse_expr()
                    semic = self.parse_tok(";")
                    return JumpStmt(op, semic, expr)
                except CParserSyntaxError:
                    l = TokenList()
                    a = self.get_tok()
                    while a.get_type() != ";":
                        l.append(a)
                        a = self.get_tok()
                    return JumpStmt(op, a, l)
        elif op == "{":
            op = self.get_tok()
            l = CompoundStmt(op)
            while(self.cur_tok().get_type() != "}"):
                l.append(self.parse_stmt())
            l.close(self.parse_tok("}"))
            return l
        elif op == "while" or op == "switch":
            op = self.get_tok()
            po = self.parse_tok("(")
            ex = self.parse_expr()
            pc = self.parse_tok(")")
            st = self.parse_stmt()
            return WordHeadStmt(op, po, ex, pc, st)
        elif op == "do":
            op1 = self.get_tok()
            stmt = self.parse_stmt()
            op2 = self.parse_tok("while")
            po = self.parse_tok("(")
            expr = self.parse_expr()
            pc = self.parse_tok(")")
            semic = self.parse_tok(";")
            return DoWhileStmt(op1, stmt, op2, po, expr, pc, semic)
        elif op == "for":
            op = self.get_tok()
            po = self.parse_tok("(")
            e1 = self.parse_expr() if self.cur_tok().get_type() != ";" else None
            s1 = self.parse_tok(";")
            e2 = self.parse_expr() if self.cur_tok().get_type() != ";" else None
            s2 = self.parse_tok(";")
            e3 = self.parse_expr() if self.cur_tok().get_type() != ")" else None
            pc = self.parse_tok(")")
            stmt = self.parse_stmt()
            return ForStmt(op, po, e1, s1, e2, s2, e3, pc, stmt)
        elif op == "if":
            op = self.get_tok()
            po = self.parse_tok("(")
            ex = self.parse_expr()
            pc = self.parse_tok(")")
            s1 = self.parse_stmt()
            if self.cur_tok().get_type() != "else":
                return IfStmt(op, po, ex, pc, s1)
            el = self.parse_tok("else")
            s2 = self.parse_stmt()
            return IfStmt(op, po, ex, pc, s1, el, s2)
        elif op == "identifier":
            op = self.get_tok()
            colon = self.cur_tok()
            if colon.get_type() == ":":
                self.get_tok()
                stmt = self.parse_stmt()
                return LabelStmt(op, colon, stmt)
            self.rev_tok(op)
        elif op == "case":
            op = self.parse_tok("case")
            ex = self.parse_expr()
            co = self.parse_tok(":")
            st = self.parse_stmt()
            return CaseStmt(op, ex, co, st)
        elif op == "default":
            op = self.parse_tok("default")
            co = self.parse_tok(":")
            st = self.parse_stmt()
            return LabelStmt(op, co, st)
        try:
            expr = self.parse_expr()
            semic = self.parse_tok(";")
            return ExprStmt(expr, semic)
        except CParserSyntaxError:
            l = TokenList()
            a = self.get_tok()
            while a.get_type() != ";":
                l.append(a)
                a = self.get_tok()
            return ExprStmt(l, a)

def test(string):
    x = CParser(string)
    p = x.parse_expr()
    print p

def stmt_test(string):
    x = CParser(string)
    p = x.parse_stmt()
    print p

if __name__=="__main__":
    test(r'x <<= (4 > 5 && 5 == k%2&3!=4 ? a[2] : f(++*ptr, NULL)), hoge = "This\tis\ta\"Pen\n"')
    test(r'y = fuga ? x==5 : (short)(++y + 20) * 8 & (4 >> 2 | 3) && org--')
    stmt_test("""if (x == 480 || x != a) {
    y= (int)5.60 >> 3; continue;
    } else return ((stmt_t *)x)->a.b;""")
    stmt_test(r"switch (x) {case 1: x += 5; goto LABEL0; case 5: case 9: x *= 3; break; default : x = 0; LABEL0 : return 5; }")
