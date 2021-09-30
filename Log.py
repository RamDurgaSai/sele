from time import localtime


class Log():

    def __init__(self, file: str,debug_mode:bool = False):
        """
        Class Log for logging purpose
        :param file: file save logs
        """
        self.debug_mode = debug_mode
        self.file_path = file

    def debug(self, msg: str, to_print: bool = True):
        """
        to Debug some info
        :param msg: s string to log
        :param print: Pass True to print string n stdout(Defaults to True)
        :return: None
        """
        self._log(f"[DEBUG] {msg}", to_print)

    def error(self, msg, to_print: bool = True):
        """
       to Debug some Error
       :param msg: s string to log
       :param print: Pass True to print string n stdout(Defaults to True)
       :return: None
       """
        self._log(f'[ERROR] {msg}', to_print)

    def warn(self, msg, to_print: bool = True):
        """
       to Debug some Warning Strings
       :param msg: s string to log
       :param print: Pass True to print string n stdout(Defaults to True)
       :reoturn: None
       """
        self._log(f'[WARN] {msg}', to_print)

    def _log(self, msg, to_print):
        y, m, d, h, m, s, wd, yd, isd = localtime()
        s = f'[{h}:{m}:{s}]{msg}'
        if to_print or self.debug_mode:
            print(s)
        try:
            with open(self.file_path,"a") as file:
                file.write(f"\n{str(s)}")
        except Exception as e:
            self.error(f"logging Falied Due to {e}",to_print=True)

