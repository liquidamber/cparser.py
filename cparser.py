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
        return self.a.give_back() + [Token("[","")] + self.b.give_back() + [Token("]","")]

class FuncExpr(BinExpr):
    def __init__(self, a, b):
        BinExpr.__init__(self, a, None, b)
    def __str__(self):
        return "%s(%s)" % ( str(self.a), str(self.b) )
    def give_back(self):
        return self.a.give_back() + [Token("(","")] + self.b.give_back() + [Token(")","")]

class ParenExpr(UniExpr):
    def __init__(self, a):
        UniExpr.__init__(self, a, None)
#        print "(%s)" % a
    def __str__(self):
        return "(%s)" % str(self.a)
    def give_back(self):
        return [Token("(","")] + self.a.give_back() + [Token(")","")]

class CastExpr(UniExpr):
    def __init__(self, a, typename):
        UniExpr.__init__(self, a, typename)
    def __str__(self):
        return "(%s)%s" % str(self.op), str(self.a)
    def give_back(self):
        return [Token("(","")] + self.op.give_back()+[Token(")","")]+self.a.give_back()

class CondExpr(Expr):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
#        print "(%s ? %s : %s)" % (a, b, c)
    def __str__(self):
        return "%s ? %s : %s" % (str(self.a), str(self.b), str(self.c))
    def give_back(self):
        return (self.a.give_back()+[Token("?","")]+
                self.b.give_back()+[Token(":","")]+
                self.c.give_back())

class ExprList(object):
    def __init__(self, a=None):
        self.list = [] if a is None else [a]
    def __str__(self):
        return ", ".join([str(x) for x in self.list])
    def append(x):
        self.list.append(x)
    def give_back(self):
        ret = [self.list[0].give_back()]
        for i in self.list[1:]:
            ret += [Token(",", "") , i.give_back()]
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
#Unsupport for sizeof(int)
        elif atype == "sizeof":
            b = self.parse_unary_expr()
            return UniExpr(b, a)
        else:
            self.rev_tok(a)
            a = self.parse_post_expr()
            return a

    def parse_cast_expr(self):
        a = self.cur_tok()
        if a.get_type == "(":
            self.get_tok()
            a = self.parse_type_name()
            b = self.get_tok()
            if b.get_type != ")":
                raise CParserSyntaxError, "Paren Not Match"+str(b)
            b = self.parse_cast_expr()
            return CastExpr(b, a)
        else:
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
        return a

def test():
    # x = CParser(r'int x <<= (4 > 5 && 5 == k%2&3!=4 ? a[2] : f(++*ptr)), char * hoge = "TEST" "This\tis\ta\"Pen\n"')
    x = CParser(r'y = fuga ? x==5 : (++y + 20) * 8 & (4 >> 2 | 3) && org--')
    p = x.parse_expr()
    print p

if __name__=="__main__":
    test()
