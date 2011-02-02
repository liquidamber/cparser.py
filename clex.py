import re
import sys

class Token(object):
    def __init__(self, tokentype, value, line, char):
        self.tokentype = tokentype
        self.value     = value
        self.linecount = line
        self.charcount = char
        self.whitespace = ""
    def __str__(self):
        return ((str(self.value) if self.value else str(self.tokentype))
                + self.whitespace)
    def get_type(self):
        return self.tokentype
    def get_val(self):
        return self.value
    def give_back(self):
        return [self]

class Tokenizer(object):
    def __init__(self, string, ignore_errors=True):
        self.result = []
        self.linecount = 0
        self.charcount = 0
        self.ignore_errors = ignore_errors
        self.initializer = [
                ("auto"     , self.reserve),
                ("break"    , self.reserve),
                ("case"     , self.reserve),
                ("char"     , self.reserve),
                ("const"    , self.reserve),
                ("continue" , self.reserve),
                ("default"  , self.reserve),
                ("double"   , self.reserve),
                ("do"       , self.reserve),
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
                ("return"   , self.reserve),
                ("short"    , self.reserve),
                ("signed"   , self.reserve),
                ("sizeof"   , self.reserve),
                ("static"   , self.reserve),
                ("struct"   , self.reserve),
                ("switch"   , self.reserve),
                ("syncfor"  , self.reserve),
                ("sync"     , self.reserve),
                ("typedef"  , self.reserve),
                ("union"    , self.reserve),
                ("unsigned" , self.reserve),
                ("void"     , self.reserve),
                ("volatile" , self.reserve),
                ("while"    , self.reserve),

                (r"[a-zA-Z_]\w*" , self.identifier),

            # real
                (r"\d+[Ee][+-]?\d+[fFlL]?"         , self.constant),
                (r"\d*\.\d+([Ee][+-]?\d+)?[fFlL]?" , self.constant),
                (r"\d+\.\d*([Ee][+-]?\d+)?[fFlL]?" , self.constant),

            # integer
                (r"0[xX][a-fA-F0-9]+[uUlL]{0,2}"   , self.constant),
                (r"0\d+[uUlL]{0,2}"                , self.constant),
                (r"\d+[uUlL]{0,2}"                 , self.constant),
                (r"[a-zA-Z_]?'(\\.|[^\\'])*'"      , self.constant),

                (r'[a-zA-Z_]?"(\\.|[^\\"])*"' , self.string_literal),

                (r"/\*(?:[^*]|\*[^/])*\*/" , self.comment_block),
                (r"//[^\n]*\n"             , self.newline),

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
                #Empty
                (r"[ \t\v\f]+"             , self.empty),
                (r"\r\n?"                  , self.newline),
                (r"\n"                     , self.newline),
                #Other
                (r"#[^\r\n]*(?:\r\n?|\n)"  , self.directive),
                (r".*"                     , self.other)
                ]
        self.scanner = re.Scanner(self.initializer)
        self.scanner.scan(string)
        self.result.append(Token("terminal", "", self.linecount, self.charcount))
    def __iter__(self):
        return iter(self.result)
    def reserve(self, scanner, s):
        self.result.append(Token(s, "", self.linecount, self.charcount))
        self.charcount += len(s)
    def identifier(self, scanner, s):
        self.result.append(Token("identifier", s, self.linecount, self.charcount))
        self.charcount += len(s)
    def constant(self, scanner, s):
        self.result.append(Token("literal", s, self.linecount, self.charcount))
        self.charcount += len(s)
    def string_literal(self, scanner, s):
        self.result.append(Token("literal", s, self.linecount, self.charcount))
        self.charcount += len(s)
    def operator(self, scanner, s):
        self.result.append(Token(s, "", self.linecount, self.charcount))
        self.charcount += len(s)
    def empty(self, scanner, s):
        self.charcount += len(s)
        if len(self.result) > 0: self.result[-1].whitespace += s
    def newline(self, scanner, s):
        self.linecount += 1
        self.charcount  = 0
        if len(self.result) > 0: self.result[-1].whitespace += s
    def comment_block(self, scanner, s):
        self.linecount += s.count('\n')
        self.charcount  = len(s) - s.rfind('\n') - 1
    def other(self, scanner, s):
        if not self.ignore_errors:
            print >>sys.stderr, "Error Token: line %d: char %d: " % (self.linecount, self.charcount) + s
            exit(1)
        else:
            self.result.append(Token("other", s, self.linecount, self.charcount))
            self.charcount += len(s)
    def directive(self, scanner, s):
        if not self.ignore_errors:
            print >>sys.stderr, "Error Token: line %d: char %d: " % (self.linecount, self.charcount) + s
            exit(1)
        else:
            self.result.append(Token("directive", s, self.linecount, self.charcount))

TEST_STRING = r"""for(int i=9l; i<100; ++i) {
   ptr += hoge[i]+fuga(x)*2 % 4 >> 2 - L'X' + '\n';
   // hoge
   a >>= (x <= 4 ? y : z);
   char * hoge = "TEST" "This\tis\ta\"Pen\n";
   /***************
    **  COMMENT  **
    ***************/
} return ptr;
"""
def test(string):
    x = Tokenizer(string)
    print "\n".join(["%d %d "%(i.linecount, i.charcount) + str(i) for i in x])

if __name__=="__main__":
    if len(sys.argv) == 1:
        test(TEST_STRING)
    else:
        if sys.argv[1] == "-":
            test(sys.stdin.read())
        else:
            test(open(sys.argv[1]).read())
