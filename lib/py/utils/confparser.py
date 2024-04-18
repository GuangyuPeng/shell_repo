import configparser

class ConfParser(object):
    """ Parse .conf files

    Format of conf file:
        key = value
        key = "value"
        key = 'value'
        # comments

    For example, we have a `test.conf` file whose contents are
      foo = hello world
      bar = "world hello"

    Then after `parser = ConfParser(); parser.read('test.conf')`, we can get

        parser["foo"] = "hello world"
        parser["bar"] = "world hello"

    Attributes:
    """

    def __init__(self):
        self._parser = configparser.ConfigParser()
        self._vars = {}
        self._keyiteridx = 0

    def read(self, fname):
        """ Read and parse a file

        Args:
            fname: conf file name
        """
        with open(fname) as fp:
            self._parser.read_string("[dummysection]\n" + fp.read())
        for sec in self._parser.sections():
            for key in self._parser[sec]:
                val = self._parser[sec][key]
                val = val.strip()
                val = val.strip('"')
                val = val.strip("'")
                self._vars[key] = val

    def __getitem__(self, key):
        return self._vars[key]

    def __setitem__(self, key, value):
        self._vars[key] = value

    def __len__(self):
        return len(self._vars)

    def __delitem__(self, key):
        del self._vars[key]

    def __contains__(self, key):
        return (key in self._vars)

    def __iter__(self):
        return self._vars.__iter__()
