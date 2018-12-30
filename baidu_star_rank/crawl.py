#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-12-26 23:39:55
# @Author  : ShengMo Long (shengmo.long@foxmail.com)
# @Link    : https://gitee.com/dragon417/
# @Version : $Id$

# -*- coding: utf-8 -*-
__author__ = "dragon"

from scrapy.cmdline import execute

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))
)

execute(["scrapy", "crawl", "bdstars"])
