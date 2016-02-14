#!/usr/bin/env python
import os
import sys
import subprocess
import pkg_resources
import circus
import tempfile
import numpy, h5py
from circus.shared.files import print_error, print_info, write_datasets, get_results, read_probe, load_data, get_nodes_and_edges, load_data

def main():

    argv = sys.argv

    filename       = os.path.abspath(sys.argv[1])

    if len(sys.argv) == 2:
        filename   = os.path.abspath(sys.argv[1])
        extension  = ''
    elif len(sys.argv) == 3:
        filename   = os.path.abspath(sys.argv[1])
        extension  = sys.argv[2]

    params         = circus.shared.utils.io.load_parameters(filename)
    sampling_rate  = float(params.getint('data', 'sampling_rate'))
    data_dtype     = params.get('data', 'data_dtype')
    gain           = 1
    file_out_suff  = params.get('data', 'file_out_suff')
    data_offset    = params.getint('data', 'data_offset')
    probe          = read_probe(params)
    output_path    = params.get('data', 'file_out_suff') + '.GUI'
    N_e            = params.getint('data', 'N_e')
    N_t            = params.getint('data', 'N_t')

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    def generate_matlab_mapping(probe):
        p         = {}
        positions = []
        nodes     = []
        for key in probe['channel_groups'].keys():
            p.update(probe['channel_groups'][key]['geometry'])
            nodes     +=  probe['channel_groups'][key]['channels']
            positions += [p[channel] for channel in probe['channel_groups'][key]['channels']]
        idx       = numpy.argsort(nodes)
        positions = numpy.array(positions)[idx]
        return positions

    def get_max_loc_channel(params):
        nodes, edges    = circus.shared.utils.io.get_nodes_and_edges(params)
        max_loc_channel = 0
        for key in edges.keys():
            if len(edges[key]) > max_loc_channel:
                max_loc_channel = len(edges[key])
        return max_loc_channel

    def write_results(path, result):
        spikes     = numpy.zeros(0, dtype=numpy.int64)
        clusters   = numpy.zeros(0, dtype=numpy.int32)
        amplitudes = numpy.zeros(0, dtype=numpy.float32)
        for key in result['spiketimes'].keys():
            temp_id    = int(key.split('_')[-1])
            data       = result['spiketimes'].pop(key)
            spikes     = numpy.concatenate((spikes, data.astype(numpy.int64)))
            amplitudes = numpy.concatenate((amplitudes, result['amplitudes'][key][:, 0]))
            clusters   = numpy.concatenate((clusters, temp_id*numpy.ones(len(data), dtype=numpy.int32)))
        
        idx = numpy.argsort(spikes)

        numpy.save(os.path.join(output_path, 'spike_templates'), clusters[idx])
        numpy.save(os.path.join(output_path, 'spike_times'), spikes[idx])
        numpy.save(os.path.join(output_path, 'amplitudes'), amplitudes[idx])

    def write_pcs(path, clusters, params):

        max_loc_channel = get_max_loc_channel(params)
        electrodes      = clusters['electrodes']
        for target in xrange(len(electrodes)):
            elec     = clusters['electrodes'][target]
            nic      = target - numpy.where(clusters['electrodes'] == elec)[0][0]
            mask     = clusters['clusters_' + str(elec)] > -1
            tmp      = numpy.unique(clusters['clusters_' + str(elec)][mask])
            indices  = numpy.where(result['clusters_' + str(elec)] == tmp[nic])[0]

        #numpy.save(os.path.join(output_path, 'pc_features'), clusters[idx]) # nspikes, nfeat, n_loc_chan
        #numpy.save(os.path.join(output_path, 'pc_features_ind'), clusters[idx]) #n_templates, n_loc_chan


    print_info(["Exporting data..."])
    
    write_results(output_path, get_results(params, extension))
    #write_pcs(output_path, load_data(params, 'clusters', extension))

    numpy.save(os.path.join(output_path, 'whitening_mat'), numpy.linalg.inv(load_data(params, 'spatial_whitening')))
    numpy.save(os.path.join(output_path, 'channel_positions'), generate_matlab_mapping(probe))
    nodes, edges   = get_nodes_and_edges(params)
    numpy.save(os.path.join(output_path, 'channel_map'), nodes)

    templates = load_data(params, 'templates', extension).toarray()
    N_tm      = templates.shape[1]
    templates = templates.reshape(N_e, N_t, N_tm)[:,:,:N_tm/2]

    numpy.save(os.path.join(output_path, 'templates'), templates.transpose())
    temp_mapping = numpy.ones((N_tm/2, len(nodes)), dtype=numpy.int32)*nodes
    numpy.save(os.path.join(output_path, 'templates_ind'), temp_mapping)



    

