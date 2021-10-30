#!/usr/bin/python3
import configparser
import glob
import os.path
import re
'''
Собрать языковые файлы со всех доступных модов в один пакет
'''
en = '_l_english.yml'
ru = '_l_russian.yml'

regex = r"\s*(\S*):\d* \"(.*)\""

'''
localisation_old
localisation_synced
'''

def has_rus(s):
    regex_rus = r"[а-яА-Я]"
    return re.match(regex_rus, s, re.MULTILINE)

def load_file(base, config, locpath, exclisive=False):
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


def save_ru(config):
    mark = "l_russian:"
    dirn = 'russian'
    ru = '_l_russian.yml'

    if not os.path.exists('localisation'):
        os.makedirs('localisation')
    if not os.path.exists('localisation/russian'):
        os.makedirs('localisation/russian')

    for fn in config.sections():
        f = open('localisation/' + fn + ru, "w", encoding = 'utf-8-sig')
        f.write(mark + "\n\n")
        for key in config[fn]:
            f.write("{}: \"{}\"\n".format(key, config.get(fn, key, raw = True).replace('%%', '%')))
        f.close()


module_path = "C:/Program Files (x86)/Steam/steamapps/workshop/content/281990/"
modules = [
    1595876588, 1688887083, 946222466, 1067631798,
    1890399946, 1121692237, 1311725711, 1333526620,
    1623423360, 1780481482, 2604778880, 683230077,
    1587178040, 1630649870, 2458945473, 2484636075,
    2466607238, 2411818376, 2555609401, 1701916892,
    1701915595, 1796418794, 1796402967, 1302897684,
    1419304439, 1489142966, 1313138123, 2509070395,
    727000451,  1885775216, 2028826064, 2458024521,
    2293169684, 790903721,
    # loc
    1487654111, 1375388095, 1670045745, 2486026362,
    2166824852, 2617298932, 2615894270, 2609978732,
    2037347735, 1982183037, 1830669482
    ]

config = configparser.ConfigParser()
config.optionxform = str

for module in modules:
    locpath = module_path + str(module) + "/localisation/"
    print(locpath)
    for fn in glob.iglob(locpath + "*" + en):
        load_file(fn, config, locpath)

    for fn in glob.iglob(locpath + "*" + ru):
        load_file(fn, config, locpath, True)

    for fn in glob.iglob(locpath + "english/*" + en):
        load_file(fn, config, locpath)

    for fn in glob.iglob(locpath + "russian/*" + ru):
        load_file(fn, config, locpath, True)

save_ru(config)
# with open('en.ini', "w", encoding = 'utf-8') as config_file:
#     config_en.write(config_file)
#
# for s in config_ru.sections():
#     if not config_en.has_section(s):
#         config_ru.remove_section(s)
# with open('ru.ini', "w", encoding = 'utf-8') as config_file:
#     config_ru.write(config_file)