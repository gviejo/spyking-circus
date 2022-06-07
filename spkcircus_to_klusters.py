# -*- coding: utf-8 -*-
# @Author: Guillaume Viejo
# @Date:   2022-05-20 13:51:18
# @Last Modified by:   Guillaume Viejo
# @Last Modified time: 2022-06-06 12:00:34
import numpy as np
import os
from ufo_detection import *

def convert_spkcircus_to_klusters(path):
    outputpath = os.path.dirname(os.path.dirname(path))

    files = os.listdir(path)

    data = {}
    for f in files:
        if 'npy' in f:
            data[f.split(".")[0]] = np.load(os.path.join(path, f))


    basename = os.path.basename(outputpath)

    #sys.exit()

    # Writing clu
    clu_file = os.path.join(outputpath, basename + '.clu.1')
    #f = open(clu_file, "w")
    clu  = data["spike_clusters"]
    clu += 2
    n = len(np.unique(clu))
    # f.write(str(n)+"\n")
    # for c in data["spike_clusters"]:
    #     f.write(str(c+2)+"\n")
    # f.close()

    clu = np.hstack(([n], clu))
    np.savetxt(clu_file, clu, delimiter = '\n', fmt='%i')

    # Writing res
    res_file = os.path.join(outputpath, basename + '.res.1')
    res = data["spike_times"]
    f = open(res_file, "w")
    for t in res:
        f.write(str(t)+"\n")
    f.close()



    # Writing spk
    spk_file = os.path.join(outputpath, basename + '.spk.1')
    f = open(spk_file, "wb")
    fp, timestep = get_memory_map(os.path.join(outputpath, basename+'.dat'), 16)
    waveforms = np.zeros((len(data["spike_times"]),20,16), dtype=np.int16)
    for j, t in enumerate(data["spike_times"]):
        idx = np.arange(t-10,t+10, dtype=np.int64)
        waveforms[j] = fp[idx,:]

    for i in range(waveforms.shape[0]):
        print(i/waveforms.shape[0], end="\r", flush=True)
        for j in range(waveforms.shape[1]):
            for k in range(waveforms.shape[2]):
                f.write(waveforms[i,j,k])
    f.close()


    # Writing fet
    from sklearn.decomposition import PCA

    fet_file = os.path.join(outputpath, basename + '.fet.1')

    features = np.zeros((len(data['spike_times']),16*3+3))
    for j in range(16):
        features[:,j*3:j*3+3] = PCA(n_components=3).fit_transform(waveforms[:,:,j])
    features = features.astype(np.int64)


    features[:,-1] = data['spike_times']

    f = open(fet_file, 'w')
    f.writelines(str(features.shape[-1])+'\n')
    for j in range(len(features)):
        tmp = waveforms[j].astype(np.int64)
        features[j,-3] = int(np.sqrt(np.sum(np.power(tmp, 2))))
        features[j,-2] = np.abs(tmp.max() - tmp.min())
        f.writelines('\t'.join(features[j].astype('str'))+'\n')
    f.close()
