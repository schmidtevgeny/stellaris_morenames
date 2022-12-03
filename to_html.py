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

regex = r"\s*(\S*):\d*\s*\"(.*)\""

'''
localisation_old
localisation_synced
'''


def has_rus(s):
    for ch in s:
        if ch >= 'а' and ch <= 'я':
            return True
    return False


# giga_achievement_05_title
def load_file(base, config, locpath, substitute, exclisive = False):
    print(base)
    f = open(base, encoding = 'utf-8')
    data = "\n".join([x for x in f.read().split('\n') if x.strip() != '' and x.strip()[0] != '#'])
    f.close()
    base = os.path.relpath(base, locpath)
    base = base[:-14].replace('english', 'russian')

    if not config.has_section(base):
        if exclisive:
            return
        config.add_section(base)

    matches = re.finditer(regex, data, re.MULTILINE)
    rdata = []

    for matchNum, match in enumerate(matches, start = 1):
        try:
            key = match.group(1)
            val = match.group(2).replace('%', '%%')
            regex_sub = r"\$(.*?)\$"
            matches_sub = re.finditer(regex_sub, val, re.MULTILINE)

            for matchNum_sub, match_sub in enumerate(matches_sub, start = 1):
                subst = match_sub.group(1)
                if not subst in substitute:
                    substitute.append(subst)

            if not config.has_option(base, match.group(1)):
                config.set(base, key, val)
            else:
                new = val
                old = config.get(base, match.group(1))
                if has_rus(new):
                    config.set(base, match.group(1), new)
        except:
            print(match.group(1))

    pass


class locstring:
    def __init__(self, path, value):
        self.path = path
        self.value = value

    def replace(self, fr, to):
        self.value = self.value.replace(fr, to)

    def parse(self):
        s = self.value.replace('\\"', '"')
        s = html.escape(s)
        s = s.replace('⌠', '<').replace('⌡', '>')

        regex = r"\[(.*?)\]"
        subst = "<input value=\"\\g<1>\">"
        s = re.sub(regex, subst, s, 0, re.MULTILINE)
        regex = r"§(\w)(.*?)§!"
        subst = "<span class=\"\\g<1>\">\\g<2></span>"
        s = re.sub(regex, subst, s, 0, re.MULTILINE)
        regex = r"£(\S*?)[£\s]"
        subst = "<img src=\"\\g<1>\">"
        s = re.sub(regex, subst, s, 0, re.MULTILINE)
        s = '<html><body><p>' + s + '</p></body></html>'
        return s.replace('\\n', '<br/>')

    def split(self):
        s=self.value
        regex = r"\[(.*?)\]"
        subst = ""
        s = re.sub(regex, subst, s, 0, re.MULTILINE)
        regex = r"§(\w)(.*?)§!"
        subst = "\\g<2>"
        s = re.sub(regex, subst, s, 0, re.MULTILINE)
        regex = r"£(\S*?)[£\s]"
        subst = ""
        s = re.sub(regex, subst, s, 0, re.MULTILINE)
        regex = r"⌠.*?⌡"
        subst = ""
        s = re.sub(regex, subst, s, 0, re.MULTILINE)
        s.split()

        return re.split(r'[\.\?\!]|\\n', s)


def process(config: configparser.ConfigParser):
    data = {}
    cnt = 0
    for i in config.sections():
        for j in config[i]:
            data[j] = locstring(i + '/' + j, config[i][j])
            cnt += 1
    return data


def find_subst(data, substitute, default):
    print('find_subst')
    for i in substitute:
        if i in data.keys():
            default[i] = data[i].value
        else:
            lost_subst.append(i)


def update_subst(data, default):
    print('update_subst')
    with click.progressbar(length = len(default)) as bar:
        for i in default:
            fr = '$' + i + '$'
            to = '⌠a href="'+i+'"⌡'+default[i]+'⌠/a⌡'
            for j in data:
                data[j].replace(fr, to)
            bar.update(1)


def save_data(data, path):
    print('save_data')
    soup = BeautifulSoup('<html><body></body></html>', 'lxml')
    for i in data:
        tag = soup.new_tag('div')
        tag['class'] = data[i].path
        ss = BeautifulSoup(data[i].parse(), 'lxml')
        # for it in ss.body:
        tag.append(ss.body.p)
        soup.body.append(tag)
    with open(path, "w", encoding = 'utf-8') as config_file:
        config_file.write(str(soup.prettify()))


def save_data(data, path):
    print('save_data')
    soup = BeautifulSoup('<html><body></body></html>', 'lxml')
    for i in data:
        tag = soup.new_tag('div')
        tag['class'] = data[i].path
        ss = BeautifulSoup(data[i].parse(), 'lxml')
        # for it in ss.body:
        tag.append(ss.body.p)
        soup.body.append(tag)
    with open(path, "w", encoding = 'utf-8') as config_file:
        config_file.write(str(soup.prettify()))


def save_data_limit(data, path, limit):
    print('save_data')
    soup = BeautifulSoup('<html><body></body></html>', 'lxml')
    num = 1
    count = 0
    for i in data:
        count += 1
        if count >= limit:
            with open(path.format(num), "w", encoding = 'utf-8') as config_file:
                config_file.write(str(soup.prettify()))
            soup = BeautifulSoup('<html><body></body></html>', 'lxml')
            num += 1
            count = 0

        tag = soup.new_tag('div')
        tag['class'] = data[i].path
        ss = BeautifulSoup(data[i].parse(), 'lxml')
        # for it in ss.body:
        tag.append(ss.body.p)
        soup.body.append(tag)

    with open(path.format(num), "w", encoding = 'utf-8') as config_file:
        config_file.write(str(soup.prettify(formatter="minimal")))


#module_path = "C:/Program Files (x86)/Steam/steamapps/workshop/content/281990/"
module_path = "E:/SteamLibrary/steamapps/workshop/content/281990/"
#app_path = "C:/Program Files (x86)/Steam/steamapps/common/Stellaris/localisation/"
app_path = "E:/SteamLibrary/steamapps/common/Stellaris/localisation/"
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
    # loc
    1487654111, 1375388095, 1670045745, 2486026362,
    2166824852, 2617298932, 2615894270, 2609978732,
    2037347735, 1982183037, 1830669482, 2702693226
    ]
# print('load predef')
config_en = configparser.ConfigParser()
config_en.optionxform = str

config_en_orig = configparser.ConfigParser()
config_en_orig.optionxform = str

# config = configparser.ConfigParser()
# config.optionxform = str
print('scan')

default_en = {}
default_ru = {}
lost_subst = []
substitute = []

for module in modules:
    locpath = module_path + str(module) + "/localisation/"
    for fn in glob.iglob(locpath + "*" + en):
        load_file(fn, config_en, locpath, substitute)

    for subsection in subsections:
        for fn in glob.iglob(locpath + subsection + "*" + en):
            load_file(fn, config_en, locpath, substitute)

    for fn in glob.iglob(locpath + "english/*" + en):
        load_file(fn, config_en, locpath, substitute)

for fn in glob.iglob(app_path + "english/*.yml"):
    load_file(fn, config_en_orig, app_path + "english/", substitute)

# print(substitute)

data_en = process(config_en)
data_en_orig = process(config_en_orig)

find_subst(data_en, substitute, default_en)
find_subst(data_en_orig, substitute, default_en)

update_subst(data_en, default_en)
save_data(data_en, 'en-full.html')

config_ru = configparser.ConfigParser()
config_ru.optionxform = str
config_ru.read('ru.ini', 'utf-8')

config_ru_orig = configparser.ConfigParser()
config_ru_orig.optionxform = str

substitute = []
for module in modules:
    locpath = module_path + str(module) + "/localisation/"
    for fn in glob.iglob(locpath + "*" + ru):
        load_file(fn, config_ru, locpath, substitute)

    for subsection in subsections:
        for fn in glob.iglob(locpath + subsection + "*" + ru):
            load_file(fn, config_ru, locpath, substitute)

    for fn in glob.iglob(locpath + "russian/*" + ru):
        load_file(fn, config_ru, locpath, substitute)

for fn in glob.iglob(app_path + "russian/*.yml"):
    load_file(fn, config_ru_orig, app_path + "russian/", substitute)

data_ru = process(config_ru)
data_ru_orig = process(config_ru_orig)

find_subst(data_ru, substitute, default_ru)
find_subst(data_ru_orig, substitute, default_ru)

for key in default_en.keys():
    if not key in default_ru.keys():
        default_ru[key] = default_en[key]

update_subst(data_ru, default_ru)
save_data(data_ru, 'ru-full.html')
save_data(data_ru_orig, 'ru-orig.html')


data_en_crop = {}
data_ru_crop = {}
print('compare lang')
for i in data_ru.keys():
    if i in data_en.keys() and has_rus(data_ru[i].value):
        data_en_crop[i] = data_en[i]
        data_ru_crop[i] = data_ru[i]


def save_tmx(en, ru, path):
    root = etree.Element("tmx")
    body = etree.SubElement(root, "body")
    for i in ru.keys():
        e = en[i]
        r = ru[i]
        ei = e.split()
        ri=r.split()
        if len(ei)==len(ri):
            for j in range(len(ei)):
                if ei[j]=='' or ri[j]=='' or ei[j]==ri[j]:
                    continue
                tu = etree.SubElement(body, 'tu')
                tuv = etree.SubElement(tu, 'tuv', {'xml-lang': "en-US"})
                seg = etree.SubElement(tuv, 'seg')
                seg.text = ei[j]
                tuv = etree.SubElement(tu, 'tuv', {'xml-lang': "ru"})
                seg = etree.SubElement(tuv, 'seg')
                seg.text = ri[j]

    handle = etree.tostring(root, pretty_print = True, encoding = 'utf-8', xml_declaration = True)
    applic = open(path, "wb")
    applic.write(handle)
    applic.close()


save_tmx(data_en_crop, data_ru_crop, 'full.tmx')
# save_data_limit(data_ru_crop, '{}-tr-ru.html', 2000)
# save_data_limit(data_en_crop, '{}-tr-en.html', 2000)

print("done")