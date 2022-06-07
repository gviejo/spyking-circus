# -*- coding: utf-8 -*-
# @Author: Guillaume Viejo
# @Date:   2022-06-06 10:49:30
# @Last Modified by:   Guillaume Viejo
# @Last Modified time: 2022-06-06 12:01:13

import numpy as np
import os, sys
import pathlib
import shutil
import subprocess
from spkcircus_to_klusters import convert_spkcircus_to_klusters

data_directory = '/mnt/DataGuillaume/'
datasets = np.genfromtxt(os.path.join(data_directory,'datasets_LMN.list'), delimiter = '\n', dtype = str, comments = '#')



for s in datasets[0:1]:
    print(s)
    path = os.path.join(data_directory, s)


    # Backup Kilosort results
    backup_path = os.path.join(data_directory, s, 'KiloSort2')
    if not os.path.exists(backup_path): 
        os.mkdir(backup_path)

    files = []
    for ext in ('*.clu.*', '*.res.*', '*.fet.*', '*.spk.*'):
        files.extend(list(pathlib.Path(path).glob(ext)))

    for f in files:
        shutil.move(f, os.path.join(backup_path, f.name))

    # Check if prb file is here.
    if len(list(pathlib.Path(path).glob('*.prb'))) == 0:
        print("no prb file")
        sys.exit()

    # Check if params file exit.
    if len(list(pathlib.Path(path).glob('*.params'))) == 0:
        print("no params file")
        sys.exit()

    # Launch spyking circus
    os.chdir(path)
    datname = os.path.basename(path) + '.dat'
    subprocess.run(["spyking-circus", 
        datname, 
        "--method", "filtering,whitening,clustering,fitting,merging",
        "--cpu", "6"])

    # Export to phy
    subprocess.run(["circus-gui-python", 
        datname])

    # Convert to neurosuite
    convert_spkcircus_to_klusters(path)