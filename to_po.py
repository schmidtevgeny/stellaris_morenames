#!/usr/bin/python3
import configparser
import glob
import os.path
import re
import json


'''
Собрать языковые файлы со всех доступных модов в один пакет
'''

# done: добавить свои строки
# done: сохранять не переведенные

en = '_l_english.yml'
ru = '_l_russian.yml'
subsections = ["diplo_phrases/", "events/"]  # ,'formats/','namelists/']

#
# modules = [
#     # base
#     790903721, 2028826064, 1885775216, 1313138123, 1419304439, 1796418794, 1701916892, 2484636075, 683230077,
#     1121692237, 2509070395, 1630649870, 2466607238, 2608299476, 1890399946, 1623423360, 1333526620, 1311725711,
#     2293169684, 1067631798, 946222466, 1688887083, 1419304439, 2458945473, 1504307690, 2288335512,
#     2060393654, 2030472413, 2028670202, 2027064352,
#     1928831043, 1693982756, 1199002146,
#     # ext
#     1688887083,
#     946222466,
#     1333526620,
#     1067631798,
#     1890399946,
#     2293169684,
#     2466607238,
#     1311725711,
#     2458945473,
#     2509070395,
#     2458024521,
#     1121692237,
#     2608299476,
#     2484636075,
#     1623423360,
#     1796418794,
#     683230077,
#     1419304439,
#     1630649870,
#     2028826064,
#     1313138123,
#     1504307690,
#     1701916892,
#     1375388095,
#     1670045745,
#     1830669482,
#     1199002146,
#     2027064352,
#     2028670202,
#     2030472413,
#     1885775216,
#     2288335512,
#     790903721,
#     2060393654,
#     1489142966,
#     # 2660548454, # аналог гигаструктур. китайский. перевода нет
#     1780481482,
#     2111178476,
#     1928831043,
#
#     # full
#     1595876588, 1688887083, 946222466, 1067631798,
#     1890399946, 1121692237, 1311725711, 1333526620,
#     1623423360, 1780481482, 2604778880, 683230077,
#     1587178040, 1630649870, 2458945473, 2484636075,
#     2466607238, 2555609401, 1701916892, 2411818376,
#     1701915595, 1796418794, 1796402967, 1302897684,
#     1419304439, 1489142966, 1313138123, 2509070395,
#     727000451, 1885775216, 2028826064, 2458024521,
#     2293169684, 790903721,
#     2529002857, 2622652746, 2626285356, 2475302050,
#     # плагины переводов
#     # 1487654111, 1375388095, 1670045745, 2486026362,
#     # 2166824852, 2617298932, 2615894270, 2609978732,
#     # 2037347735, 1982183037, 1830669482, 2702693226
# ]
#

# --------
# localisation_synced

class LocString:
    def __init__(self, path, name, value, num):
        self.path = path
        self.name = name
        self.value = value
        self.num = num
        self.pos = 0

    def parse(self, s):
        return s

    def get(self):
        return self.value

    def get_subst(self):
        return []

    def __str__(self):
        return "{}/{}:{}".format(self.path, self.name, self.value)

    def __lt__(self, other):
        return self.pos < other.pos


class Storage:
    def __init__(self):
        self.data = {}

    def add(self, s: LocString):
        key = s.path
        s.pos = len(self.data)
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


def load_strings(storage: Storage, path, relpath, russian: bool = False):
    regex = r"\s*(\S*):(\d*)\s*\"(.*)\""

    f = open(path, encoding = 'utf-8')
    data = "\n".join([x for x in f.read().split('\n') if x.strip() != '' and x.strip()[0] != '#'])
    f.close()

    matches = re.finditer(regex, data, re.MULTILINE)
    rdata = []

    for matchNum, match in enumerate(matches, start = 1):
        key = match.group(1)
        num = match.group(2)
        val = match.group(3)
        if not russian or has_rus(val):
            storage.add(LocString(relpath, key, val, num))


# todo: substitution
def make_maker(storage: Storage):
    f = open("update.py", "w", encoding = "utf-8")
    f.write(r'''import os
import gettext

# gettext.install('messages')    
lang_translations = gettext.translation('base', localedir='locales', languages=['ru'])
lang_translations.install()

def pre(s):
    return s.replace('\n', '\\n').replace('"', "'")
    
base = 'localisation/'
if not os.path.exists(base+'russian'):
    os.makedirs(base+'russian')
''')
    for section in subsections:
        f.write("if not os.path.exists(base+'" + section + "'):\n    os.makedirs(base+'" + section + "')\n")
    for section in ['replace', 'replace/russian', 'russian/replace']:
        f.write("if not os.path.exists(base+'" + section + "'):\n    os.makedirs(base+'" + section + "')\n")

    for i, fdata in storage.data.items():
        of = os.path.basename(i + '_l_russian.yml')
        of = i + '_l_russian.yml'

        f.write("f = open(base+'" + of + "', 'w', encoding='utf-8-sig')\n")
        f.write('f.write("l_russian:\\n\\n")\n\n')
        keys = sorted(fdata)

        for j in keys:
            l = fdata[j]
            f.write('key="{}:{}"\n'.format(j, l.num))
            strings = l.get().replace('\\\\', '\\').replace('\\n', '\n').split('\n')

            valitems = []
            for s in strings:
                if s == '':
                    valitems.append("\"\"")
                    print('empty string {}'.format(j))
                elif s.find('"') < 0:
                    valitems.append("_(r\"{}\")".format(s))
                elif s.find("'") < 0:
                    valitems.append("_(r'{}')".format(s))
                else:
                    valitems.append("_('''{}''')".format(s))

            f.write('value="\\\\n".join([{}])\n'.format(', '.join(valitems)))

            f.write('f.write(\'  {} \"{}\"\\n\'.format(key, pre(value)))\n')

        f.write("f.close()\n\n")
    pass


def make_memory(storage_en, storage_ru):
    po = open('memory.po', 'w', encoding = 'utf-8')

    for i, f_en in storage_en.data.items():
        print('section ' + i )
        if i in storage_ru.data.keys():
            f_ru = storage_ru.data[i]
            for j, e in f_en.items():
                if j in f_ru.keys():
                    r = f_ru[j]
                    if r.get() != e.get() and r.get() != '' and e.get() != '':
                        po.write('msgid "{}"\nmsgstr "{}"\n\n\n'.format(
                            e.get().replace('"', '\\"').replace('\n', ' ').strip(),
                            r.get().replace('"', '\\"').replace('\n', ' ').strip()))
                        el = e.get().replace('"', '\\"').replace('\\\\', '\\n').replace('\\n', '\n').strip().split('\n')
                        rl = r.get().replace('"', '\\"').replace('\\\\', '\\n').replace('\\n', '\n').strip().split('\n')
                        if len(el) == len(rl):
                            for i in range(len(el)):
                                po.write('msgid "{}"\nmsgstr "{}"\n\n\n'.format(el[i], rl[i]))
    po.close()
    pass


storage = Storage()
#module_path = "C:/Program Files (x86)/Steam/steamapps/workshop/content/281990/"
#app_path = "C:/Program Files (x86)/Steam/steamapps/common/Stellaris/localisation/"
# module_path = "E:/SteamLibrary/steamapps/workshop/content/281990/"
module_path = "C:/Users/schmi/Documents/Paradox Interactive/Stellaris/mod/"
# app_path = "E:/SteamLibrary/steamapps/common/Stellaris/localisation/"
app_path = "E:/GOG Games/Stellaris/localisation/"

modules = [946222466
,1121692237
,1410753850
,1419304439
,1481972266
,1504307690
,1587178040
,1588784686
,1623423360
,1630649870
,1693982756
,1780481482
,1890399946
,2028670202
,2178603631
,2288335512
,2956750503
,2976573664
,"tl/681483874"
,"tl/2617298932"
,"tl/2645981075"
,"tl/2696538662"
,"tl/2810284852"
,"tl/2943075915"


]

# f = open ('mods.json', encoding='utf-8')
# config = f.read()
# f.close()
# config = json.loads(config)
# for mod in config['mods']:
#     modules.append(mod['steamId'])
#     print(mod)

# todo: localisation_synced
# common
# localisation_synced
# prescripted_countries
def get_plugin_strings(storage: Storage):
    # module_path = "test/"
    print(module_path)
    for module in modules:
        locpath = module_path + str(module) + "/localisation/"
        if module == 2660548454:
            ch = '_l_simp_chinese.yml'
            for fn in glob.iglob(locpath + "*" + ch):
                fr = os.path.basename(fn).replace(ch, '')
                load_strings(storage, fn, fr)

            for subsection in subsections:
                for fn in glob.iglob(locpath + subsection + "*" + ch):
                    fr = subsection + os.path.basename(fn).replace(ch, '')
                    load_strings(storage, fn, fr)

            for fn in glob.iglob(locpath + "simp_chinese/*" + ch):
                fr = 'russian/' + os.path.basename(fn).replace(ch, '')
                load_strings(storage, fn, fr)


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

        # replace
        for fn in glob.iglob(locpath + "replace/*" + en):
            fr = 'replace/' + os.path.basename(fn).replace(en, '')
            load_strings(storage, fn, fr)
        for fn in glob.iglob(locpath + "replace/english/*" + en):
            fr = 'replace/russian/' + os.path.basename(fn).replace(en, '')
            load_strings(storage, fn, fr)
        for fn in glob.iglob(locpath + "english/replace/*" + en):
            fr = 'russian/replace/' + os.path.basename(fn).replace(en, '')
            load_strings(storage, fn, fr)


def get_original_strings(storage):
    fr = 'base'
    for fn in glob.iglob(module_path + '*/*/*' + en):
        # print(fn)
        load_strings(storage, fn, fr)
    for fn in glob.iglob(module_path + '*/*/*/*' + en):
        # print(fn)
        load_strings(storage, fn, fr)
    for fn in glob.iglob(module_path + '*/*/*/*/*' + en):
        # print(fn)
        load_strings(storage, fn, fr)
    for fn in glob.iglob(app_path + 'english/*' + en):
        # print(fn)
        load_strings(storage, fn, fr)


def get_russian_strings(storage):
    fr = 'base'
    for fn in glob.iglob(module_path + '*/*/*' + ru):
        # print(fn)
        load_strings(storage, fn, fr, True)
    for fn in glob.iglob(module_path + '*/*/*/*' + ru):
        # print(fn)
        load_strings(storage, fn, fr, True)
    for fn in glob.iglob(module_path + '*/*/*/*/*' + ru):
        # print(fn)
        load_strings(storage, fn, fr, True)
    for fn in glob.iglob(app_path + 'russian/*' + ru):
        # print(fn)
        load_strings(storage, fn, fr, True)

    local = 'localisation.old/'
    for fn in glob.iglob(local + '*' + ru):
        # print(fn)
        load_strings(storage, fn, fr, True)
    for fn in glob.iglob(local + '*/*' + ru):
        # print(fn)
        load_strings(storage, fn, fr, True)


get_plugin_strings(storage)

storage_en = Storage()
storage_ru = Storage()

get_original_strings(storage_en)
get_russian_strings(storage_ru)

make_maker(storage)
make_memory(storage_en, storage_ru)

# os.system("update.py")