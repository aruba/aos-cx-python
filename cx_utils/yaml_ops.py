import yaml
from os.path import dirname, abspath, join


def read_yaml(filename):

    parentdirpath = dirname(dirname(abspath(__file__)))
    sampledatadir = join(parentdirpath, "sampledata")

    with open(abspath(join(sampledatadir, filename)), 'r') as yml_file:
        data = yaml.safe_load(yml_file)
    return data
