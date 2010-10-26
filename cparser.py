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

class SelectExpr(BinExpr):
    def __init__(self, a, b):
        BinExpr.__init__(self, a, None, b)
    def __str__(self):
        return "%s[%s]" % ( str(self.a), str(self.b) )
    def give_back(self):
        return self.a.give_back() + [clex.Token("[","")] + self.b.give_back() + [clex.Token("]","")]

class FuncExpr(BinExpr):
    def __init__(self, a, b):
        BinExpr.__init__(self, a, None, b)
    def __str__(self):
        return "%s(%s)" % ( str(self.a), str(self.b) )
    def give_back(self):
        return self.a.give_back() + [clex.Token("(","")] + self.b.give_back() + [clex.Token(")","")]

class ParenExpr(UniExpr):
    def __init__(self, a):
        UniExpr.__init__(self, a, None)
#        print "(%s)" % a
    def __str__(self):
        return "(%s)" % str(self.a)
    def give_back(self):
        return [clex.Token("(","")] + self.a.give_back() + [clex.Token(")","")]

class CastExpr(UniExpr):
    def __init__(self, a, typename):
        UniExpr.__init__(self, a, typename)
    def __str__(self):
        return "%s%s" % (str(self.op), str(self.a))
    def give_back(self):
        return self.op.give_back()+self.a.give_back()

class CondExpr(Expr):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
#        print "(%s ? %s : %s)" % (a, b, c)
    def __str__(self):
        return "%s ? %s : %s" % (str(self.a), str(self.b), str(self.c))
    def give_back(self):
        return (self.a.give_back()+[clex.Token("?","")]+
                self.b.give_back()+[clex.Token(":","")]+
                self.c.give_back())

class ExprList(object):
    def __init__(self, a=None):
        self.list = [] if a is None else [a]
    def __str__(self):
        return ", ".join([str(x) for x in self.list])
    def append(self,x):
        self.list.append(x)
    def give_back(self):
        ret = self.list[0].give_back()
        for i in self.list[1:]:
            ret += [clex.Token(",", "")] + i.give_back()
        return ret

class TokenList(object):
    def __init__(self, a=None):
        self.list = [] if a is None else [a]
    def __str__(self):
        return " ".join([str(x) for x in self.list])
    def append(self,x):
        self.list.append(x)
    def give_back(self):
        ret = self.list[0].give_back()
        for i in self.list[1:]:
            ret += i.give_back()
        return ret

class CParserSyntaxError(BaseException):
    pass

class CParser(object):
    def __init__(self, string):
        self.tokenizer = clex.Tokenizer(string)
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

    def parse_paren_match(self):
        a = self.get_tok()
        l = TokenList(a)
        if a.get_type() != "(":
            raise CParserSyntaxError, "Not open paren"+str(a)
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
            a = self.parse_expr()
            b = self.get_tok()
            if(b.get_type() == ")"):
                return ParenExpr(a)
            else:
                raise CParserSyntaxError, "Paren Match Error: "+str(b)
        else:
            raise CParserSyntaxError, "Not Primitive Expression: "+str(a)

    def parse_post_expr(self):
        a = self.parse_prim_expr()
        while True:
            op = self.get_tok()
            if(op.get_type() == "." or op.get_type() == "->"):
                b = self.get_tok()
                if(b.get_type() != "identifier"):
                    raise CParserSyntaxError, "Not member"+str(b)
                a = BinExpr(a, op, b)
            elif(op.get_type() == "++" or op.get_type() == "--"):
                a = PostExpr(a, op)
            elif(op.get_type() == "("):
                b = self.parse_arg_expr_list()
                a = FuncExpr(a, b)
            elif(op.get_type() == "["):
                b = self.parse_expr()
                c = self.get_tok()
                if(c.get_type() != "]"):
                    raise CParserSyntaxError, "Paren Match Error"+str(b)
                a = FuncExpr(a, b)
            else:
                self.rev_tok(op)
                return a

    def parse_arg_expr_list(self):
        a = self.get_tok()
        if a.get_type() == ")":
            return ExprList()
        self.rev_tok(a)
        a = self.parse_assign_expr()
        l = ExprList(a)
        op = self.get_tok()
        while op.get_type() == ",":
            b = self.parse_assign_expr()
            l.append(b)
            op = self.get_tok()
        if op.get_type() == ")":
            return l
        else:
            raise CParserSyntaxError, "Paren Match Error"+str(b)

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
        if self.cur_tok().get_type() != "?":
            return cond
        op = self.get_tok()
        b  = self.parse_expr()
        op = self.get_tok()
        if op.get_type() != ":":
            raise CParserSyntaxError, "Conditonal Operator Error"+str(op)
        c  = self.parse_cond_expr()
        return CondExpr(cond, b, c)

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

def test(string):
    x = CParser(string)
    p = x.parse_expr()
    print p

if __name__=="__main__":
    test(r'x <<= (4 > 5 && 5 == k%2&3!=4 ? a[2] : f(++*ptr)), hoge = "This\tis\ta\"Pen\n"')
    test(r'y = fuga ? x==5 : (short)(++y + 20) * 8 & (4 >> 2 | 3) && org--')
