def _parse_symbs(self):
    self._iter_lines(self._parse_macro)
    # Prvo parsiramo deklaracije oznaka. Npr. "(LOOP)".
    self._iter_lines(self._parse_lab)

    # Na kraju parsiramo varijable i reference na oznake te ih pretvaramo u
    # konstante. Npr. "@SCREEN" pretvaramo u "@16384" ili "@END" kojemu je
    # oznaka "(END)" bila u trecoj liniji pretvaramo u "@3".
    self._n = 16
    self._iter_lines(self._parse_var)

def _parse_macro(self, line, m, n):
    if line[0] != "$":
        return line
    
    self._macro = True
    
    if line[len(line)-1] != ")" and line[len(line)-1] != "D":
        self._flag = False
        self._errm = "Invalid macro operation."
        return ""
    
    operation = line[1:].split("(")[0]
    if operation == "MV":
        if len(line[4:len(line)-1].split(",")) != 2:
            self._flag = False
            self._errm = "Invalid macro operation."
            return ""
        a = line[4:len(line)-1].split(",")[0]
        b = line[4:len(line)-1].split(",")[1]
        if a.isdigit():
            a = str(a)
        if b.isdigit():
            b = str(b)
        return ["@"+a,"D=M", "@"+b, "M=D"]
        
    elif operation == "SWP":
        if len(line[5:len(line)-1].split(",")) != 2:
            self._flag = False
            self._errm = "Invalid macro operation."
            return ""
        a = line[5:len(line)-1].split(",")[0]
        b = line[5:len(line)-1].split(",")[1]
        if a.isdigit():
            a = str(a)
        if b.isdigit():
            b = str(b)
        
        return ["@" + a,"D=M", "@" + "H","M=D","@"+b,"D=M","@"+a,"M=D","@"+"H","D=M","@" + b,"M=D"]
        
    elif operation == "SUM":
        if len(line[5:len(line)-1].split(",")) != 3:
            self._flag = False
            self._errm = "Invalid macro operation."
            return ""
        a = line[5:len(line)-1].split(",")[0]
        b = line[5:len(line)-1].split(",")[1]
        c = line[5:len(line)-1].split(",")[2]
        if a.isdigit():
            a = str(a)
        if b.isdigit():
            b = str(b)
        if c.isdigit():
            c = str(c)
        
        return ["@"+a,"D=M","@"+b,"D=M+D","@"+c,"M=D"]
        
    elif operation == "WHILE":
        a = line[7:len(line)-1]
        if a.isdigit():
            a = str(a)
        self._z.update({str(self._i):a})
        vrati = ["(WHILE" + str(self._i) + ")","@"+self._z[str(self._i)],"D=M","@"+"END"+str(self._i),"D;JEQ"]
        self._i = self._i+1
        return vrati
    
    elif operation == "END":
        r=self._z.popitem()
        return ["@"+r[1],"M=M-1","@"+"WHILE"+r[0],"0;JMP","(END"+r[0]+")"]
        
    
    else:
        self._flag = False
        self._errm = "Invalid macro operation."
        return ""

# Svaka oznaka mora biti sadrzana unutar oblih zagrada. Npr. "(LOOP)". Svaka
# oznaka koju procitamo treba zapamtiti broj linije u kojoj se nalazi i biti
# izbrisana iz nje. Koristimo dictionary _labels.
def _parse_lab(self, line, m, n):
    if line[0] != "(":
        return line
    l = line[1:].split(")")[0]
    if len(l) == 0:
        self._flag = False
        self._errm = "Invalid label."
    else:
        self._labels[l] = str(m)
    return ""

# Svaki poziv na varijablu ili oznaku je oblika "@NAZIV", gdje naziv nije broj.
# Prvo provjeriti oznake ("_labels"), a potom varijable ("_vars"). Varijablama
# dodjeljujemo memorijske adrese pocevsi od 16. Ova funkcija nikad ne vraca
# prazan string!
def _parse_var(self, line, m, n):
    if line[0] != '@' or (line[0] == '@' and line[1:].isdigit()):
        return line
    l = line[1:]
    if l in self._labels.keys():
        return "@" + self._labels[l]
    elif l in self._vars.keys():
        return "@" + self._vars[l]
    else:
        self._vars[l] = str(self._n)
        self._n += 1
        return "@" + str(self._n - 1)

# Inicijalizacija predefiniranih oznaka.
def _init_symbs(self):
    self._labels = {
        "SCREEN" : "16384",
        "KBD" : "24576",
        "SP" : "0",
        "LCL" : "1",
        "ARG" : "2",
        "THIS" : "3",
        "THAT" : "4"
    }
    for i in range(0, 16):
        self._labels["R" + str(i)] = str(i)