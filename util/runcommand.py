# -*- coding: utf-8 -*-

import subprocess
import tempfile
import threading
import platform
from log import logger
logger = logger()

_abort_on_error = True


def runNonblockMode(cmd):
    """新建一个子进程以非阻塞的形式执行命令

    :param cmd: 需要执行的命令
    :type cmd: string
    """
    logger.debug("新建一个子进程以非阻塞的形式执行命令，cmd=%s" % cmd)
    if platform.system().upper == "Windows".upper():
        subprocess.Popen(cmd, stdout=subprocess.PIPE)
    else:
        subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)


def runCommand(cmd, timeout_time=120, retry_count=3, return_output=True,
               stdin_input=None, block=True):
    """新建一个子进程执行命令

    :param cmd: 需要执行的命令
    :type cmd: string

    :param timeout_time: 超时时间，当命令执行超过该限定时间时将会被kill掉。默认为 ``None`` ,表示无设置超时时间
    :type timeout_time: int

    :param retry_count: 重试次数，当任务执行超时或者失败，将会按照重试次数重新执行
    :type retry_count: int

    :param return_output: 如果值为 ``True`` ，将命令执行后的输出按照 ``string`` 类型输出，否则直接输出到控制台
    :type return_output: bool

    :param stdin_input: 数据输入流

    :param block: 如果值为 ``True`` ，则该命令执行为阻塞式
    :type block: bool

    :returns: 当 ``return_output`` 值为 ``True`` 并且 ``block`` 值为 ``False`` 时，以 ``string`` 类型返回命令执行结果;其他情况返回 ``None``

    :raises errors.WaitForResponseTimedOutError: 当命令多次重试仍然超时没有响应的时候跑出该异常
    """
    if not block:
        logger.debug("run cmd in nonblock mode, cmd = %s" % cmd)
        runNonblockMode(cmd)
        return

    logger.debug("run cmd in block mode, cmd = %s" % cmd)
    while True:
        try:
            return runBlockMode(cmd, timeout_time=timeout_time,
                                return_output=return_output, stdin_input=stdin_input)
        except Exception as e:
            logger.warning("currently, retry_count = %d" % retry_count)
            if retry_count == 0:
                raise Exception("waiting for command shell response timeout. retried 3 times, all failed!!!: " + str(e))
            retry_count -= 1
            # logger.warning("restart adb server with os.system command.")
            # os.system('adb kill-server')
            # time.sleep(5)
            # os.system('adb start-server')
            # time.sleep(30)
            # logger.warning("adb server has been restarted.")


def runBlockMode(cmd, timeout_time=120, return_output=True, stdin_input=None):
    """新建一个子进程以阻塞的形式执行命令

    :param cmd: 需要执行的命令
    :type cmd: string

    :param timeout_time: 超时时间，当命令执行超过该限定时间时将会被kill掉。默认为 ``None`` ,表示无设置超时时间
    :type timeout_time: int

    :param return_output: 如果值为 ``True`` ，将命令执行后的输出按照 ``string`` 类型输出，否则直接输出到控制台
    :type return_output: bool

    :param stdin_input: 数据输入流

    :returns: 当 ``return_output`` 值为 ``True`` 时，返回输出结果

    :raises errors.WaitForResponseTimedOutError: 当命令在规定的时间内没有执行完毕时将会抛出该异常
    :raises errors.AbortError: 当命令执行失败并且需要终止程序执行时，抛出该异常
    """
    logger.debug("新建一个子进程以阻塞的形式执行命令，cmd=%s" % cmd)
    so = []
    global _abort_on_error, error_occurred
    error_occurred = False

    if return_output:
        output_dest = tempfile.TemporaryFile(bufsize=0)
    else:
        # None means direct to stdout
        output_dest = None
    if stdin_input:
        stdin_dest = subprocess.PIPE
    else:
        stdin_dest = None

    pipe = None
    if platform.system().upper == "Windows".upper():
        pipe = subprocess.Popen(
            cmd,
            stdin=stdin_dest,
            stdout=output_dest,
            stderr=subprocess.STDOUT)
    else:
        pipe = subprocess.Popen(
            cmd,
            stdin=stdin_dest,
            stdout=output_dest,
            stderr=subprocess.STDOUT,
            shell=True)

    def Run():
        global error_occurred
        try:
            logger.debug("run command in a new thread, cmd = %s" % cmd)
            pipe.communicate(input=stdin_input)
            output = None
            if return_output:
                output_dest.seek(0)
                output = output_dest.read()
                output_dest.close()
            if output is not None and len(output) > 0:
                so.append(output)
        except OSError as e:
            so.append("OSError: " + str(e))
            error_occurred = True
            logger.error("EXCEPTION: " + str(e))

    t = threading.Thread(target=Run)
    t.start()

    logger.debug("Wait until the thread terminates. timeout_time = %s" % timeout_time)
    t.join(timeout_time)
    if t.isAlive():
        logger.warning("timeout, thread is still alive")
        try:
            logger.info("try to kill thread!!!")
            pipe.kill()
        except OSError:
            logger.error("WARNING: Can't kill a dead thread!!!")
        finally:
            logger.warning("WARNING: raise an exception: errors.WaitForResponseTimedOutError. The Command is : " + cmd + "\n Timeout_time is : " + str(timeout_time))
            raise Exception("waiting for response timeout.")
    else:
        logger.debug("process is terminated.")
    output = "".join(so)

    if _abort_on_error and error_occurred:
        logger.info("output: %s" % str(output))
        error_string_array = ['error', 'not found']
        for error_string in error_string_array:
            assert error_string not in output
        raise Exception(msg=output)
    return output
