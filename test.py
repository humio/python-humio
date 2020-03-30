import re
from os.path import join
from os.path import dirname
import io

def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ) as fh:
        return fh.read()

match_badges = re.compile("^.. start-badges.*^.. end-badges", re.M | re.S)
s = "%s\n%s"  % (
        match_badges.sub("", read("README.rst")),
        re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
    )

print(s)