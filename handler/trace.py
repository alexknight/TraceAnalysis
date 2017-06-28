# coding:utf-8
import os
from util import log
from util.analysis_tracefile import TraceDump, sortInclThreadCost

logger = log.logger()


class TraceUtils(object):
    def __init__(self,  trace_path, mapping_path=None, convert_jar=None, mode="exclusive"):
        """traceview解析的工具类
        :params convert_jar: convert_jar文件
        :params trace_path: traceview文件
        :params trace_root: traceview文件所在路径
        :params trace_name: traceview文件的名字
        :params mapping_path: mapping文件路径
        :params out_path: traceview反混淆文件输出的路径
        """
        self.trace_dump = TraceDump()
        self.convert_jar = convert_jar
        self.trace_path = trace_path
        self.trace_root, self.trace_name = os.path.split(trace_path)
        self.mapping_path = mapping_path
        self.mode = mode
        self.analysis_results = None

    def anti_mapping(self):
        """反混淆操作"""

        if self.convert_jar is None:
            return self

        if self.mapping_path is None:
            return self

        convert_cmd = "java -jar {0:s} -i {1:s} -m {2:s} -o {3:s}".format(self.convert_jar, self.trace_path,
                                                                              self.mapping_path, self.trace_path)
        logger.info("convert_cmd: " + convert_cmd)

        try:
            os.system(convert_cmd)
        except Exception as e:
            raise Exception("trace文件解混淆失败: " + str(e))
        return self

    def analysis(self, sort=True):
        """结果格式为
            {
                "inclusive": final_inclusive_time_result,
                "exclusive": final_exclusive_time_result,
                "method_thread": method_thread,
                "theads_pid": theads_pid,
                "call_times": call_times_result,
                "costs": costs,
                "sorted_dic": sorted_dic
            }

        """
        self.analysis_results = self.trace_dump.analysisTraceFile(self.trace_path, self.mode)
        sorted_dic = sortInclThreadCost(self.analysis_results, self.mode, sort)
        self.analysis_results['sorted_dic'] = sorted_dic
        return self.analysis_results

