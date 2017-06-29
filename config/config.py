# coding:utf-8
import os

# 基准trace文件路径
BASE_TRACES = "/tmp/data/475175/trace/StepBeforeFirstDraw.trace"

# 当前trace文件路径
COMPARE_TRACES = "/tmp/data/475176/trace/StepBeforeFirstDraw.trace"

# 反混淆工具，自带
ANTI_CONFUSE_TOOL = os.path.join(os.path.dirname(os.getcwd()), "util/convertutil.jar")

# 反混淆的mapping文件地址
MAPPING_FILE = None

# 解析的最大记录值
MAX_SAVE_RECORDS = 5000

# 关注的模块
# WATCH_MODULES = "com.(alipay.mobile.command|taobao|uc.(addon|annotation|application|base|browser|business|common|config|external|framework|jni|lowphone|model|search|security|shenma|shopping|stat|svg|syslinsener|wa)|UCMobile.(desktopwidget|jnibridge|main|model|receivers|service|shellassetsres|wxapi)|ucweb.activity)"
WATCH_MODULES = None

# 输出日志方式(debug/online)
LOG_LEVEL = "debug"
