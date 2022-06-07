#!/bin/sh
# @Author: Guillaume Viejo
# @Date:   2022-06-06 11:30:59
# @Last Modified by:   Guillaume Viejo
# @Last Modified time: 2022-06-06 11:49:15

spyking-circus A1407-190416.dat --method filtering,whitening,clustering,fitting,merging --cpu 6

circus-gui-python A1407-190416.dat