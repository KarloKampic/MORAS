from JackOutput import *
from JackError import *
from JackTokenizer import *

xml= True

class Compiler:

    def read(self, filename):
        # Ime input datoteke.
        self._fname = filename
        # Input datoteka.
        self._ifile = open(filename + ".jack", 'r')
        # Output datoteka tipa OutputFile iz JackOutput.py.
        self._ofile = OutputFile(filename + ".vm", filename + ".xml")
        # Tokenizer napravljen na prijasnjim vjezbama. Glavna metoda tokenizera
        # je next. Osim next, koristimo i razne get metode.
        self._tokenizer = Tokenizer(self._ifile, None)
        # Interna varijabla koja prati uvlake u XML-u.
        self._XMLIndent = 0

        # Pocetak kompajliranja.
        self.compileClass()

        # Cistimo za sobom.
        self._ofile.close()
        self._ifile.close()

    # Glavne metode.

    # Na pocetku svakog programa ocekujemo klasu.
    def compileClass(self):
        """
        Compiles <class> :=
            'class' <class-name> '{' <class-var-dec>* <subroutine-dec>* '}'

        The tokenizer is expected to be positionsed at the beginning of the
        file.
        """
        self._writeXMLTag('<class>\n')

        self._nextToken()
        self._expectKeyword(KW_CLASS)
        self._writeXML('keyword', 'class')

        self._nextToken()
        className = self._expectIdentifier()
        self._writeXML('identifier', className)

        self._nextToken()
        self._expectSymbol('{')
        self._writeXML('symbol', '{')

        self._nextToken()

        while True:
            if self._tokenizer.tokenType() != TK_KEYWORD:
                break
            if self._tokenizer.keyword() not in (KW_STATIC, KW_FIELD):
                break
            self._compileClassVarDec()

        while True:
            if self._tokenizer.tokenType() != TK_KEYWORD:
                break
            if self._tokenizer.keyword() not in (KW_CONSTRUCTOR, KW_FUNCTION, KW_METHOD):
                break
            self._compileSubroutine()

        self._expectSymbol('}')
        self._writeXML('symbol', '}')

        self._writeXMLTag('</class>\n')

        if self._tokenizer.next():
            self._error("Junk after class declaration.")

    def _compileClassVarDec(self):
        """
        Compiles <class-var-dec> :=
            ('static' | 'field') <type> <var-name> (',' <var-name>)* ';'

        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._writeXMLTag('<classVarDec>\n')

        storageType = self._expectKeyword((KW_STATIC, KW_FIELD))
        self._writeXML('keyword', self._tokenizer.keywordStr())

        self._nextToken()
        if self._tokenizer.tokenType() == TK_KEYWORD:
            variableType = self._expectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
            variableTypeName = None
            self._writeXML('keyword', self._tokenizer.keywordStr())
        else:
            variableTypeName = self._expectIdentifier()
            variableType = None
            self._writeXML('identifier', self._tokenizer.identifier())

        self._nextToken()
        while True:
            variableName = self._expectIdentifier()
            self._writeXML('identifier', self._tokenizer.identifier())
            self._nextToken()
            if self._tokenizer.tokenType() != TK_SYMBOL or self._tokenizer.symbol() != ',':
                break
            self._writeXML('symbol', self._tokenizer.symbol())
            self._nextToken()

        self._expectSymbol(';')
        self._writeXML('symbol', self._tokenizer.symbol())
        self._nextToken()

        self._writeXMLTag('</classVarDec>\n')

    def _compileSubroutine(self):
        """
        Compiles <subroutine-dec> :=
            ('constructor' | 'function' | 'method') ('void' | <type>)
            <subroutine-name> '(' <parameter-list> ')' <subroutine-body>

        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after <subroutine-body>.
        """
        self._writeXMLTag('<subroutineDec>\n')
        self._writeXMLTag('</subroutineDec>\n')

    def _compileParameterList(self):
        """
        Compiles <parameter-list> :=
            ( <type> <var-name> (',' <type> <var-name>)* )?

        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after <subroutine-body>.
        """
        self._writeXMLTag('<parameterList>\n')
        self._writeXMLTag('</parameterList>\n')

    def _compileSubroutineBody(self):
        """
        Compiles <subroutine-body> :=
            '{' <var-dec>* <statements> '}'

        The tokenizer is expected to be positioned before the {
        ENTRY: Tokenizer positioned on the initial '{'.
        EXIT:  Tokenizer positioned after final '}'.
        """
        self._writeXMLTag('<subroutineBody>\n')
        self._writeXMLTag('</subroutineBody>\n')

    def _compileVarDec(self):
        """
        Compiles <var-dec> :=
            'var' <type> <var-name> (',' <var-name>)* ';'

        ENTRY: Tokenizer positioned on the initial 'var'.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._writeXMLTag('<varDec>\n')
        self._writeXMLTag('</varDec>\n')

    def _compileStatements(self):
        """
        Compiles <statements> := (<let-statement> | <if-statement> |
            <while-statement> | <do-statement> | <return-statement>)*

        The tokenizer is expected to be positioned on the first statement
        ENTRY: Tokenizer positioned on the first statement.
        EXIT:  Tokenizer positioned after final statement.
        """
        self._writeXMLTag('<statements>\n')
        self._writeXMLTag('</statements>\n')

    def _compileLet(self):
        """
        Compiles <let-statement> :=
            'let' <var-name> ('[' <expression> ']')? '=' <expression> ';'

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._writeXMLTag('<letStatement>\n')

        self._expectKeyword(KW_LET)
        self._writeXML('keyword', 'let')
        self._nextToken()
        self._compileTerm()
        if self._tokenizer.symbol()=="[":
            self._compileTerm()
        
        self._expectSymbol('=')
        self._writeXML('symbol',self._tokenizer.symbol())
        self._nextToken()
        self._compileExpression()
        self._expectSymbol(";")
        self._writeXML('symbol',";")

        self._writeXMLTag('</letStatement>\n')

    def _compileDo(self):
        """
        Compiles <do-statement> := 'do' <subroutine-call> ';'

        <subroutine-call> := (<subroutine-name> '(' <expression-list> ')') |
            ((<class-name> | <var-name>) '.' <subroutine-name> '('
            <expression-list> ')')

        <*-name> := <identifier>

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        pass

    def _compileCall(self, subroutineName = None):
        """
        <subroutine-call> := (<subroutine-name> '(' <expression-list> ')') |
            ((<class-name> | <var-name>) '.' <subroutine-name> '('
            <expression-list> ')')

        <*-name> := <identifier>

        ENTRY: Tokenizer positioned on the first identifier.
            If 'objectName' is supplied, tokenizer is on the '.'
        EXIT:  Tokenizer positioned after final ';'.
        """

        objectName = None

        if subroutineName == None:
            subroutineName = self._expectIdentifier()
            self._nextToken()
        self._writeXML('identifier', subroutineName)

        sym = self._expectSymbol('.(')
        self._writeXML('symbol', self._tokenizer.symbol())

        if sym == '.':
            objectName = subroutineName
            subroutineName = self._expectIdentifier()
            self._writeXML('identifier', subroutineName)
            self._nextToken()

            sym = self._expectSymbol('(')
            self._writeXML('symbol', self._tokenizer.symbol())
            self._nextToken()

        self._compileExpressionList()

        sym = self._expectSymbol(')')
        self._writeXML('symbol', self._tokenizer.symbol())
        self._nextToken()

    def _compileReturn(self):
        """
        Compiles <return-statement> :=
            'return' <expression>? ';'

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        pass

    def _compileIf(self):
        """
        Compiles <if-statement> :=
            'if' '(' <expression> ')' '{' <statements> '}' ( 'else'
            '{' <statements> '}' )?

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final '}'.
        """
        pass

    def _compileWhile(self):
        """
        Compiles <while-statement> :=
            'while' '(' <expression> ')' '{' <statements> '}'

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final '}'.
        """
        pass

    def _compileExpression(self):
        """
        Compiles <expression> :=
            <term> (op <term>)*

        The tokenizer is expected to be positioned on the expression.
        ENTRY: Tokenizer positioned on the expression.
        EXIT:  Tokenizer positioned after the expression.
        """
        pass

    def _compileTerm(self):
        """
        Compiles a <term> :=
            <int-const> | <string-const> | <keyword-const> | <var-name> |
            (<var-name> '[' <expression> ']') | <subroutine-call> |
            ( '(' <expression> ')' ) | (<unary-op> <term>)

        ENTRY: Tokenizer positioned on the term.
        EXIT:  Tokenizer positioned after the term.
        """

        self._writeXMLTag('<term>\n')

        if self._tokenizer.tokenType() == TK_INT_CONST:
            self._writeXML('integerConstant', str(self._tokenizer.intVal()))
            self._nextToken()

        elif self._tokenizer.tokenType() == TK_STRING_CONST:
            self._writeXML('stringConstant', self._tokenizer.stringVal())
            self._nextToken()

        elif self._tokenizer.tokenType() == TK_KEYWORD and self._tokenizer.keyword() in (KW_FALSE, KW_TRUE, KW_THIS, KW_NULL):
            self._writeXML('keyword', self._tokenizer.keywordStr())
            self._nextToken()

        elif self._tokenizer.tokenType() == TK_SYMBOL and self._tokenizer.symbol() in '-~':
            self._writeXML('symbol', self._tokenizer.symbol())
            self._nextToken()
            self._compileTerm()

        elif self._tokenizer.tokenType() == TK_SYMBOL and self._tokenizer.symbol() == '(':
            self._writeXML('symbol', self._tokenizer.symbol())
            self._nextToken()
            self._compileExpression()
            self._expectSymbol(')')
            self._writeXML('symbol', self._tokenizer.symbol())
            self._nextToken()

        else:
            variable = self._expectIdentifier()
            self._nextToken()

            if self._tokenizer.tokenType() == TK_SYMBOL and self._tokenizer.symbol() == '[':
                self._writeXML('indentifier', variable)
                self._writeXML('symbol', self._tokenizer.symbol())
                self._nextToken()
                self._compileExpression()
                self._expectSymbol(']')
                self._writeXML('symbol', self._tokenizer.symbol())
                self._nextToken()

            elif self._tokenizer.tokenType() == TK_SYMBOL and self._tokenizer.symbol() in '.(':
                self._compileCall()

            else:
                self._writeXML('indentifier', variable)

        self._writeXMLTag('</term>\n')

    def _compileExpressionList(self):
        """
        Compiles <expression-list> :=
            (<expression> (',' <expression>)* )?

        ENTRY: Tokenizer positioned on the first expression.
        EXIT:  Tokenizer positioned after the last expression.
        """
        pass

    # Pomocne metode.

    def _nextToken(self):
        if not self._tokenizer.next():
            self._error('Premature EOF')

    def _error(self, error):
        message = '%s line %d:\n  %s\n  %s' % (self._fname,
                  self._tokenizer.lineNum(), self._tokenizer.line(), error)
        raise JackError(message)

    # Provjerava je li sljedeci token kljucna rijec.
    def _expectKeyword(self, keywords):
    	if not self._tokenizer.tokenType() == TK_KEYWORD:
    		self._error('Expected ' + self._keywordStr(keywords) + ', got ' +
    					 self._tokenizer.tokenTypeStr())
    	if type(keywords) != tuple: keywords = (keywords,)
    	if self._tokenizer.keyword() in keywords:
    		return self._tokenizer.keyword()
    	self._error('Expected ' + self._keywordStr(keywords) + ', got ' +
    				 self._keywordStr(self._tokenizer.keyword()))

    # Provjerava je li sljedeci token naziv.
    def _expectIdentifier(self):
    	if not self._tokenizer.tokenType() == TK_IDENTIFIER:
    		self._error('Expected <identifier>, got '+ self._tokenizer.tokenTypeStr())
    	return self._tokenizer.identifier()

    # Provjerava je li sljedeci token symbol.
    def _expectSymbol(self, symbols):
    	if not self._tokenizer.tokenType() == TK_SYMBOL:
    		self._error('Expected ' + self._symbolStr(symbols) + ', got ' +
    					 self._tokenizer.TokenTypeStr())
    	if self._tokenizer.symbol() in symbols:
    		return self._tokenizer.symbol()
    	self._error('Expected ' + self._symbolStr(symbols) + ', got ' +
    				 self._symbolStr(self._tokenizer.symbol()))

    def _writeXMLTag(self, tag):
    	#if xml:
    	if '/' in tag: self._XMLIndent -= 1
    	self._ofile.write('  ' * self._XMLIndent)
    	self._ofile.write(tag)
    	if '/' not in tag: self._XMLIndent += 1

    def _writeXML(self, tag, value):
    	#if xml:
    	self._ofile.write('  ' * self._XMLIndent)
    	self._ofile.writeXML(tag, value)

    def _keywordStr(self, keywords):
    	if type(keywords) != tuple:
    		return '"' + self.tokenizer.KeywordStr(keywords) + '"'
    	ret = ''
    	for kw in keywords:
    		if len(ret): ret += ', '
    		ret += '"' + self.tokenizer.KeywordStr(kw) + '"'
    	if len(keywords) > 1:
    		ret = 'one of (' + ret + ')'
    	return ret

    def _symbolStr(self, symbols):
    	if type(symbols) != tuple:
    		return '"' + symbols + '"'
    	ret = ''
    	for symbol in symbols:
    		if len(ret): ret += ', '
    		ret += '"' + symbol + '"'
    	if len(symbols) > 1:
    		ret = 'one of (' + ret + ')'
    	return ret

def main():
    C = Compiler()
    C.read("1")

if __name__ == '__main__':
    main()
