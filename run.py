# coding:utf-8
import json
import os
import urllib2

import config
from util import log

logger = log.logger()


def dmtracedump():
    pass

class TraceUtils(object):
    def __init__(self, convert_jar, trace_path, mapping_url=None, mapping_file=None, out_path=None):
        """traceview解析的工具类
        :params convert_jar: convert_jar文件
        :params trace_path: traceview文件
        :params trace_root: traceview文件所在路径
        :params trace_name: traceview文件的名字
        :params mapping_url: traceview文件的路径
        :params mapping_file: mapping文件为路径时使用
        :params mapping_path: mapping文件输出路径(mapping_urls存在时使用)
        :params out_path: traceview反混淆文件输出的路径
        """
        self.convert_jar = convert_jar
        self.trace_path = trace_path
        self.trace_root, self.trace_name = os.path.split(trace_path)
        self.mapping_url = mapping_url
        self.mapping_file = mapping_file
        self.mapping_path = os.path.join(self.trace_root, "mapping.txt")
        self.out_path = out_path if out_path is not None else os.path.join(self.trace_root,"out")

    def readContent(self, mapping_path):
        req = urllib2.urlopen(url)
        return req.read()

    def createMappingFile(self):
        mapping_txt = json.loads(self.readUrlContent(self.mapping_url))['url']
        return self.saveMappingFile(mapping_txt)

    def saveMappingFile(self, mapping_txt):
        content = self.readUrlContent(mapping_txt)
        if os.path.isfile(self.mapping_path):
            os.remove(self.mapping_path)
        with open(self.mapping_path, "wb") as f:
            f.write(content)

    def convert(self):
        if self.mapping_url is not None:
            self.createMappingFile()
            convert_cmd = "java -jar {0:s} -i {1:s} -m {2:s} -o {3:s}".format(self.convert_jar, self.trace_path,
                                                                              self.mapping_path, self.out_path)
            logger.info("convert_cmd: " + convert_cmd)
        elif self.mapping_path is not None:
            convert_cmd = "java -jar {0:s} -i {1:s} -m {2:s} -o {3:s}".format(self.convert_jar, self.trace_path,
                                                                              self.mapping_file, self.out_path)
            logger.info("convert_cmd: " + convert_cmd)
        else:
            raise Exception("error mapping format!")
        try:
            os.system(convert_cmd)
        except Exception as e:
            self.logger.info("trace文件解混淆失败: " + str(e))

class TraceAnalysis(object):
    def __init__(self, base_traces, compare_traces, antiflag):
        self.base_traces = base_traces
        self.compare_traces = compare_traces
        self.antiflag = antiflag
        self.base_out = None
        self.compare_out = None


    def anti_trace(self):
        if self.antiflag:



def run():
    base_traces = config.BASE_TRACES
    compare_traces = config.COMPARE_TRACES


if __name__ == '__main__':
    run()
