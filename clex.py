import re

class Token(object):
    def __init__(self, tokentype, value):
        self.tokentype = tokentype
        self.value = value
    def __str__(self):
        return str(self.value) if self.value else str(self.tokentype)
    def get_type(self):
        return self.tokentype
    def get_val(self):
        return self.value

class Tokenizer(object):
    def __init__(self, string):
        self.result = []
        self.scanner = re.Scanner([
                ("auto"     , self.reserve),
                ("break"    , self.reserve),
                ("case"     , self.reserve),
                ("char"     , self.reserve),
                ("const"    , self.reserve),
                ("continue" , self.reserve),
                ("default"  , self.reserve),
                ("do"       , self.reserve),
                ("double"   , self.reserve),
                ("else"     , self.reserve),
                ("enum"     , self.reserve),
                ("extern"   , self.reserve),
                ("float"    , self.reserve),
                ("for"      , self.reserve),
                ("goto"     , self.reserve),
                ("if"       , self.reserve),
                ("int"      , self.reserve),
                ("long"     , self.reserve),
                ("register" , self.reserve),
                ("return "  , self.reserve),
                ("short"    , self.reserve),
                ("signed"   , self.reserve),
                ("sizeof"   , self.reserve),
                ("static"   , self.reserve),
                ("struct"   , self.reserve),
                ("switch"   , self.reserve),
                ("typedef"  , self.reserve),
                ("union"    , self.reserve),
                ("unsigned" , self.reserve),
                ("void"     , self.reserve),
                ("volatile" , self.reserve),
                ("while"    , self.reserve),

                (r"[a-zA-Z_]\w*" , self.identifier),

                (r"0[xX][a-fA-F0-9]+[uUlL]{0,2}"   , self.constant),
                (r"0\d+[uUlL]{0,2}"                , self.constant),
                (r"\d+[uUlL]{0,2}"                 , self.constant),
                (r"[a-zA-Z_]?'(\\.|[^\\'])*'"      , self.constant),

                (r"\d+[Ee][+-]?\d+[fFlL]?"         , self.constant),
                (r"\d*\.\d+([Ee][+-]?\d+)?[fFlL]?" , self.constant),
                (r"\d+\.\d*([Ee][+-]?\d+)?[fFlL]?" , self.constant),

                (r'[a-zA-Z_]?"(\\.|[^\\"])*"' , self.string_literal),

                (r">>="   , self.operator),
                (r"<<="   , self.operator),
                (r"\+="   , self.operator),
                (r"-="    , self.operator),
                (r"\*="   , self.operator),
                (r"/="    , self.operator),
                (r"%="    , self.operator),
                (r"\|="   , self.operator),
                (r"&="    , self.operator),
                (r"\^="   , self.operator),
                (r">>"    , self.operator),
                (r"<<"    , self.operator),
                (r"\+\+"  , self.operator),
                (r"--"    , self.operator),
                (r"->"    , self.operator),
                (r"&&"    , self.operator),
                (r"\|\|"  , self.operator),
                (r"<="    , self.operator),
                (r">="    , self.operator),
                (r"=="    , self.operator),
                (r"!="    , self.operator),
                (r";"     , self.operator),
                (r"\{"    , self.operator),
                (r"\}"    , self.operator),
                (r","     , self.operator),
                (r":"     , self.operator),
                (r"="     , self.operator),
                (r"\("    , self.operator),
                (r"\)"    , self.operator),
                (r"\["    , self.operator),
                (r"\]"    , self.operator),
                (r"\."    , self.operator),
                (r"&"     , self.operator),
                (r"!"     , self.operator),
                (r"~"     , self.operator),
                (r"-"     , self.operator),
                (r"\+"    , self.operator),
                (r"\*"    , self.operator),
                (r"/"     , self.operator),
                (r"%"     , self.operator),
                (r"<"     , self.operator),
                (r">"     , self.operator),
                (r"\^"    , self.operator),
                (r"\|"    , self.operator),
                (r"\?"    , self.operator),

                (r"\s*"                    , None),
                (r"/\*(?:[^*]|\*[^/])*\*/" , None),
                (r"//[^\n]*\n"             , None),
                ])
        self.scanner.scan(string)
        self.result.append(Token("terminal", ""))
    def __iter__(self):
        return iter(self.result)
    def reserve(self, scanner, s):
        self.result.append(Token(s, ""))
    def identifier(self, scanner, s):
        self.result.append(Token("identifier", s))
    def constant(self, scanner, s):
        self.result.append(Token("literal", s))
    def string_literal(self, scanner, s):
        self.result.append(Token("literal", s))
    def operator(self, scanner, s):
        self.result.append(Token(s, ""))

def test():
    x = Tokenizer(r"""for(int i=9l; i<100; ++i) {
   ptr += hoge[i]+fuga(x)*2 % 4 >> 2 - L'X' + '\n';
   // hoge
   a >>= (x <= 4 ? y : z);
   char * hoge = "TEST" "This\tis\ta\"Pen\n";
} return ptr;
""")
    print "\n".join([str(i) for i in x])

if __name__=="__main__":
    test()
