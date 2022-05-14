pygettext3  -d base -o locales/base.pot update.py
msgmerge --no-wrap -U locales/ru/LC_MESSAGES/base.po locales/base.pot
