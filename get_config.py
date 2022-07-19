import os
import yaml

def config(local_config=bool):
    a = os.path.dirname(os.path.abspath(__file__))
    if local_config:
        with open('{}/config/config.yaml'.format(a), 'r') as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
            f.close()
    else:
        cfg = os.environ
    #if not os.path.isfile('{}/config/config.yaml'.format(a)):
    #    cfg = os.environ
    #else:
    #    with open('{}/config/config.yaml'.format(a), 'r') as f:
    #        cfg = yaml.load(f, Loader=yaml.FullLoader)
    #        f.close()
    return cfg