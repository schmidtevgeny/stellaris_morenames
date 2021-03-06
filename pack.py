#!/usr/bin/python3
import configparser
import glob
import os.path
import re

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
def load_file(base, config, locpath, exclisive = False):
    # print(base)
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

fixdata = [
    ['?blocker', '£blocker'],
    ['[event_target: ', '[event_target:']
    ]
def fix_data(s):
    s=s.replace('%%', '%')
    for row in fixdata:
        s=s.replace(row[0],row[1])
    return s

def save_ru(config):
    mark = "l_russian:"
    dirn = 'russian'
    ru = '_l_russian.yml'

    if not os.path.exists('localisation'):
        os.makedirs('localisation')
    for subsection in subsections:
        if not os.path.exists('localisation/'+subsection):
             os.makedirs('localisation/'+subsection)
    if not os.path.exists('localisation/russian'):
        os.makedirs('localisation/russian')

    for fn in config.sections():
        f = open('localisation/' + fn + ru, "w", encoding = 'utf-8-sig')
        f.write(mark + "\n\n")
        for key in config[fn]:
            f.write("{}: \"{}\"\n".format(key, fix_data(config.get(fn, key, raw = True))))
        f.close()


def remove_vars(s):
    regex = r"\$.*?\$"
    s = re.sub(regex, '', s, 0, re.MULTILINE)
    regex = r"£\w*£"
    s = re.sub(regex, '', s, 0, re.MULTILINE)
    return s


def remove_command(s):
    regex = r"\[.*?\]"
    return re.sub(regex, '', s, 0, re.MULTILINE)


def save_en(config):
    config_predef = configparser.ConfigParser()
    config_predef.optionxform = str
    config_predef.read('ru.ini', 'utf-8')

    for section in config.sections():
        for item in config.options(section):
            if config_predef.has_option(section, item):
                config.remove_option(section, item)
                continue
            data = config.get(section, item).replace('\\n', ' ').replace('/', ' ')
            data = remove_vars(data)
            data = remove_command(data)

            if  data.strip() == '' or has_rus(data) :
                config.remove_option(section, item)
    with open('en.ini', "w", encoding = 'utf-8') as config_file:
        config.write(config_file)


module_path = "C:/Program Files (x86)/Steam/steamapps/workshop/content/281990/"
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
config = configparser.ConfigParser()
config.optionxform = str
config.read('ru.ini', 'utf-8')

# config = configparser.ConfigParser()
# config.optionxform = str
print('scan')

for module in modules:
    locpath = module_path + str(module) + "/localisation/"
    for fn in glob.iglob(locpath + "*" + en):
        load_file(fn, config, locpath)

    for subsection in subsections:
        for fn in glob.iglob(locpath + subsection + "*" + en):
            load_file(fn, config, locpath)

    for fn in glob.iglob(locpath + "english/*" + en):
        load_file(fn, config, locpath)

with open('en.orig.ini', "w", encoding = 'utf-8') as config_file:
    config.write(config_file)

for module in modules:
    locpath = module_path + str(module) + "/localisation/"
    for fn in glob.iglob(locpath + "*" + ru):
        load_file(fn, config, locpath, True)

    for subsection in subsections:
        for fn in glob.iglob(locpath + subsection + "*" + ru):
            load_file(fn, config, locpath, True)

    for fn in glob.iglob(locpath + "russian/*" + ru):
        load_file(fn, config, locpath, True)

print('save langstring')
save_ru(config)
print('dump')

with open('dump.ini', "w", encoding = 'utf-8') as config_file:
    config.write(config_file)
print('save todo')

save_en(config)
print('done')