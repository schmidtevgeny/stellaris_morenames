def has_rus(s):
    for ch in s:
        if (ch >= 'а' and ch <= 'я') or (ch >= 'А' and ch <= 'Я'):
            return True
    return False


f = open ('en.ini', encoding='utf-8')
data = f.read().split("\n")
f.close()

f=open("en.ru", "w",  encoding='utf-8')
f.write("\n".join([x for x in data if has_rus(x) or x.startswith('[')]))
f.close()

f=open("en.en", "w",  encoding='utf-8')
f.write("\n".join([x for x in data if not has_rus(x)]))
f.close()