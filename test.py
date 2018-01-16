# -*- coding: utf-8 -*-
# @Author       : Shu
# @Email        : httpservlet@yeah.net
# @Date         : 2018/1/9
# @Description  :
import gettext

catalogs = gettext.find("example", localedir="locale", all=True)
print ('catalogs:', catalogs)
t = gettext.translation('example', "locale", fallback=True)
_ = t.ugettext
print(_("this message"+':'))