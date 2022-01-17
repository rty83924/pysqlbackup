from tkinter import N
import yaml
import os
a = os.path.dirname(os.path.abspath(__file__))

with open('{}/config/config.yaml'.format(a)) as f:
    cfg = yaml.safe_load(f)
    f.close()
print(cfg)
oscfg = os.environ
print(oscfg)
for i in cfg.keys():
    if oscfg[i] != None:
        print(oscfg[])
    print(i)
