#!/usr/bin/python3
import configparser
import glob
import os.path
import re
from bs4 import BeautifulSoup
import html
import click
from lxml import etree

'''
Собрать языковые файлы со всех доступных модов в один пакет
'''

# done: добавить свои строки
# done: сохранять не переведенные

en = '_l_english.yml'
ru = '_l_russian.yml'
subsections = ["diplo_phrases/", "events/"]


class LocString:
    def __init__(self, path, name, value):
        self.path = path
        self.name = name
        self.value = value

    def parse(self, s):
        return s

    def get(self):
        return self.value

    def get_subst(self):
        return []

    def __str__(self):
        return "{}/{}:{}".format(self.path, self.name, self.value)


class Storage:
    def __init__(self):
        self.data = {}

    def add(self, s: LocString):
        key = s.path
        if not key in self.data.keys():
            self.data[key] = {}
        self.data[key][s.name] = s

    def __str__(self):
        s = ""
        for i, f in self.data.items():
            s += "\n" + i
            for j, l in f.items():
                s += "\n    " + str(l)
        return s

def has_rus(s):
    for ch in s:
        if ch >= 'а' and ch <= 'я':
            return True
    return False

def load_strings(storage: Storage, path, relpath, russian:bool=False):
    regex = r"\s*(\S*):\d*\s*\"(.*)\""

    f = open(path, encoding = 'utf-8')
    data = "\n".join([x for x in f.read().split('\n') if x.strip() != '' and x.strip()[0] != '#'])
    f.close()

    matches = re.finditer(regex, data, re.MULTILINE)
    rdata = []

    for matchNum, match in enumerate(matches, start = 1):
        key = match.group(1)
        val = match.group(2)
        if not russian or has_rus(val):
            storage.add(LocString(relpath, key, val))

# todo: substitution
def make_maker(storage: Storage):
    f = open("update.py", "w", encoding = "utf-8")
    f.write(r'''import os
import gettext

# gettext.install('messages')    
lang_translations = gettext.translation('base', localedir='locales', languages=['ru'])
lang_translations.install()

def pre(s):
    return s.replace('\n', '\\n')
    
base = 'loc/'
if not os.path.exists(base+'russian'):
    os.makedirs(base+'russian')
if not os.path.exists(base+'diplo_phrases'):
    os.makedirs(base+'diplo_phrases')
if not os.path.exists(base+'events'):
    os.makedirs(base+'events')

''')

    for i, fdata in storage.data.items():
        of = i + '_l_russian.yml'
        f.write("f = open(base+'" + of + "', 'w', encoding='utf-8')\n")
        f.write('f.write("l_russian:\\n\\n")\n\n')
        for j, l in fdata.items():
            s = l.get()
            f.write('key="{}"\n'.format(j))
            if s.find('"') < 0:
                f.write("value=_(r\"{}\")\n".format(l.get()))
            elif s.find("'") < 0:
                f.write("value=_(r'{}')\n".format(l.get()))
            else:
                f.write("value=_('''{}''')\n".format(l.get()))
                # print(l)

            f.write('f.write(\'{}: \"{}\"\\n\'.format(key, pre(value)))\n')

        f.write("f.close()\n\n")
    pass


def make_memory(storage_en, storage_ru):
    po = open('memory.po', 'w', encoding = 'utf-8')

    for i, f_en in storage_en.data.items():
        if i in storage_ru.data.keys():
            f_ru = storage_ru.data[i]
            for j, e in f_en.items():
                if j in f_ru.keys():
                    r = f_ru[j]
                    if r.get() != e.get() and r.get() != '' and e.get()!='':
                        po.write('msgid "{}"\nmsgstr "{}"\n\n\n'.format(e.get().replace('"', '\\"').replace('\n', ' ').strip(),
                                                                        r.get().replace('"', '\\"').replace('\n', ' ').strip()))
    po.close()
    pass


storage = Storage()
module_path = "C:/Program Files (x86)/Steam/steamapps/workshop/content/281990/"
app_path = "C:/Program Files (x86)/Steam/steamapps/common/Stellaris/localisation/"


def get_plugin_strings(storage: Storage):
    # module_path = "test/"
    modules = [
        1595876588, 1688887083, 946222466, 1067631798,
        1890399946, 1121692237, 1311725711, 1333526620,
        1623423360, 1780481482, 2604778880, 683230077,
        1587178040, 1630649870, 2458945473, 2484636075,
        2466607238, 2555609401, 1701916892, 2411818376,
        1701915595, 1796418794, 1796402967, 1302897684,
        1419304439, 1489142966, 1313138123, 2509070395,
        727000451, 1885775216, 2028826064, 2458024521,
        2293169684, 790903721,
        2529002857, 2622652746, 2626285356, 2475302050,
        # плагины переводов
        # 1487654111, 1375388095, 1670045745, 2486026362,
        # 2166824852, 2617298932, 2615894270, 2609978732,
        # 2037347735, 1982183037, 1830669482, 2702693226
        ]
    for module in modules:
        locpath = module_path + str(module) + "/localisation/"
        for fn in glob.iglob(locpath + "*" + en):
            fr = os.path.basename(fn).replace(en, '')
            load_strings(storage, fn, fr)

        for subsection in subsections:
            for fn in glob.iglob(locpath + subsection + "*" + en):
                fr = subsection + os.path.basename(fn).replace(en, '')
                load_strings(storage, fn, fr)

        for fn in glob.iglob(locpath + "english/*" + en):
            fr = 'russian/' + os.path.basename(fn).replace(en, '')
            load_strings(storage, fn, fr)


def get_original_strings(storage):
    fr = 'base'
    for fn in glob.iglob(module_path + '*/*/*' + en):
        print(fn)
        load_strings(storage, fn, fr)
    for fn in glob.iglob(module_path + '*/*/*/*' + en):
        print(fn)
        load_strings(storage, fn, fr)
    for fn in glob.iglob(app_path + 'english/*' + en):
        print(fn)
        load_strings(storage, fn, fr)


def get_russian_strings(storage):
    fr = 'base'
    for fn in glob.iglob(module_path + '*/*/*' + ru):
        print(fn)
        load_strings(storage, fn, fr, True)
    for fn in glob.iglob(module_path + '*/*/*/*' + ru):
        print(fn)
        load_strings(storage, fn, fr, True)
    for fn in glob.iglob(app_path + 'russian/*' + ru):
        print(fn)
        load_strings(storage, fn, fr, True)
    local = 'localisation.old/'
    for fn in glob.iglob(local + '*' + ru):
        print(fn)
        load_strings(storage, fn, fr, True)
    for fn in glob.iglob(local + '*/*' + ru):
        print(fn)
        load_strings(storage, fn, fr, True)


get_plugin_strings(storage)

storage_en = Storage()
storage_ru = Storage()

get_original_strings(storage_en)
get_russian_strings(storage_ru)

make_maker(storage)
make_memory(storage_en, storage_ru)

#os.system("update.py")