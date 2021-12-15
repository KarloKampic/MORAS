def _parse_lines(self):
    self._comment = False # Zastavica koja oznacava nalazimo li se trenutno u
                          # viselinijskom komentaru.
    # Za svaku liniju u izvornoj datoteci pozivamo funkciju _parse_comments.
    self._iter_lines(self._parse_comments)

# Funkcija prima originalnu liniju iz asemblerske datoteke, trenutni broj linije
# u kojoj se nalazimo i originalan broj linije iz asemblerske datoteke.
#
# Vraca liniju bez razmaka i komentara. Ukoliko je cijela linija prazna ili
# unutar komentara, vracamo prazan string. Viselinijske komentare parsiramo
# koristeci zastavicu "_comment".
#
# Jednolinijski komentar zapocinjemo s "//", dok se viselinijski komentar nalazi
# unutar znakova "/*" i "*/".
def _parse_comments(self, line, m, n):
    l = ""
    i = 0
    while i < len(line) - 1:
        p = line[i : i + 2]
        if (not self._comment and p == "*/"):
            self._flag = False
            self._errm = "Unbalanced delimited comments."
            return ""
        if ((not self._comment and p == "/*") or (self._comment and p == "*/")):
            self._comment = not self._comment
            i += 1
        elif (not self._comment and p == "//"):
            break
        elif (not self._comment and not line[i].isspace()):
            l += line[i]
        i += 1
    return l