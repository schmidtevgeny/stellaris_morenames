#!/usr/bin/python3
import configparser
import glob
import os.path
import re
from bs4 import BeautifulSoup
import html

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
def load_file(base, config, locpath, exclisive=False):
    print(base)
    f = open(base, encoding='utf-8')
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

    for matchNum, match in enumerate(matches, start=1):
        try:
            if not config.has_option(base, match.group(1)):
                config.set(base, match.group(1), match.group(2).replace('%', '%%'))
            else:
                new = match.group(2).replace('%', '%%')
                old = config.get(base, match.group(1))
                if has_rus(new):
                    config.set(base, match.group(1), new)
        except:
            print(match.group(1))

    pass


module_path = "C:/Program Files (x86)/Steam/steamapps/workshop/content/281990/"
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
print('load predef')
config_en = configparser.ConfigParser()
config_en.optionxform = str


class locstring:
    def __init__(self, path, value):
        self.path = path
        self.value = value

    def replace(self, fr, to):
        # print(fr, to)
        self.value = self.value.replace(fr, to)

    def parse(self):
        s = self.value.replace('\\"', '"')
        s = html.escape(s)

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


def process(config: configparser.ConfigParser, path, default={}):
    data = {}

    for i in config.sections():
        for j in config[i]:
            data[j] = locstring(i + '/' + j, config[i][j])

    for i in default:
        fr = '$' + i + '$'
        to = default[i]
        for j in data:
            data[j].replace(fr, to)

    for i in data:
        fr = '$' + i + '$'
        to = data[i].value
        for j in data:
            if i != j:
                data[j].replace(fr, to)

    soup = BeautifulSoup('<html><body></body></html>', 'lxml')

    for i in data:
        tag = soup.new_tag('div')
        tag['class'] = data[i].path
        ss = BeautifulSoup(data[i].parse(), 'lxml')
        # for it in ss.body:
        tag.append(ss.body.p)
        soup.body.append(tag)

    with open(path, "w", encoding='utf-8') as config_file:
        config_file.write(str(soup.prettify()))


# config = configparser.ConfigParser()
# config.optionxform = str
print('scan')

default_en = {'sr_dark_matter': 'dark matter'}
default_ru = {'sr_dark_matter': 'Темная материя'}

for module in modules:
    locpath = module_path + str(module) + "/localisation/"
    for fn in glob.iglob(locpath + "*" + en):
        load_file(fn, config_en, locpath)

    for subsection in subsections:
        for fn in glob.iglob(locpath + subsection + "*" + en):
            load_file(fn, config_en, locpath)

    for fn in glob.iglob(locpath + "english/*" + en):
        load_file(fn, config_en, locpath)

process(config_en, 'en-full.html', default_en)

config_ru = configparser.ConfigParser()
config_ru.optionxform = str

for module in modules:
    locpath = module_path + str(module) + "/localisation/"
    for fn in glob.iglob(locpath + "*" + ru):
        load_file(fn, config_ru, locpath)

    for subsection in subsections:
        for fn in glob.iglob(locpath + subsection + "*" + ru):
            load_file(fn, config_ru, locpath)

    for fn in glob.iglob(locpath + "russian/*" + ru):
        load_file(fn, config_ru, locpath)


def remove_old(process, template):
    for i in process.sections():
        if not i in template:
            process.remove_section(i)
        else:
            for j in process[i]:
                if not j in template[i]:
                    process.remove_option(i, j)


process(config_ru, 'ru.html', default_ru)
process(config_ru, 'en.html', default_en)

