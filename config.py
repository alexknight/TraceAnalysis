# coding:utf-8
import os

# 基准trace文件路径
BASE_TRACES = "xx.trace"

# 当前trace文件路径
COMPARE_TRACES = "yy.trace"

# 反混淆工具，自带
ANTI_CONFUSE_TOOL = os.path.join(os.path.dirname(os.getcwd()), "util/convertutil.jar")

# 反混淆的mapping文件地址
MAPPING_FILE = os.path.join(os.path.dirname(os.getcwd()), "util/convertutil.jar")

# 解析的最大记录值
MAX_SAVE_RECORDS = 5000

# 关注的模块
WATCH_MODULES = "com.(taobao|xx.(yy|base|)|uu.(qq|ww|main|service)|pp.activity)"
