#!/usr/bin/env python

# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

#Author: Bakar Chargeishvili (rakab) <bakar.chargeishvili@gmx.de>

import re
import glob
from rootpy.plotting import Canvas, Graph, Pad, Hist

bins_pt = [
        8,9,10,11,12,13,14,15,16,17,18,19,
        20,22,24,26,28,30,35,40,45,50,55,
        60,70,80,90,100,120,140,160,180,200
        ]

colors = ['black','red','blue']

class RooParameters(object):
    def __init__(self,filename):
        self.parameters = {}
        sys_name = re.search('Output/(\w+)/',filename).group(1)
        file_list = glob.glob(filename+'/*.txt')

        # Get parameter names and corresponding line numbers
        with open(file_list[1]) as f:
            lines = [line.rstrip('\n') for line in f]
            candidates = [[item.split()[0],  i] for i, item in enumerate(lines) if re.search(u"\+\/\-.*|Chi2", item)]
        for cand in candidates:
            self.parameters[cand[0]] = [cand[1], []]

        print(self.parameters)

        for ifile in file_list:
            [iy, ipt] = re.search(r"y(\d)_pt(\d+)",ifile).groups()
            iy = int(iy)
            ipt = int(ipt)

            with open(ifile) as ftmp:
                lines = [line.rstrip('\n') for line in ftmp]
                mean_pt = float(lines[0].split()[1])

                for par in self.parameters:
                    graphs = self.parameters[par][1]
                    parno = self.parameters[par][0]

                    try:
                        graph = next(igraph for igraph in graphs if
                                igraph.name == 'g_{0}_y{1}_{2}'.format(sys_name, iy, par))
                    except StopIteration:
                        graph = Graph(len(bins_pt)-1, name='g_{0}_y{1}_{2}'.format(sys_name, iy, par), type='asymm')
                        graphs.append(graph)

                    try:
                        data = lines[parno].split()
                    except IndexError:
                        continue;

                    if par == 'Chi2/nDOF:':
                        par_value = float(data[1])
                        par_error = [0, 0]
                    else:
                        par_value = float(data[2])
                        if(data[3] == "+/-"):
                            if(data[4][0] == "("):
                                par_error = [float(data[4][2:-1]), float(data[5][:-1])]
                            else:
                                if float(data[4]) > 0.3*par_value:
                                    par_error = [0.3*par_value, 0.3*par_value]
                                else:
                                    par_error = [float(data[4]), float(data[4])]
                        else:
                            par_error = [999, 999]

                    graph[ipt] = (mean_pt, par_value)
                    graph[ipt].x.error_hi = bins_pt[ipt+1]-mean_pt
                    graph[ipt].x.error_low = -bins_pt[ipt]+mean_pt
                    graph[ipt].y.error_low = par_error[0]
                    graph[ipt].y.error_hi = par_error[1]

        for par in self.parameters:
            graphs = self.parameters[par][1]
            for graph, color in zip(graphs, colors):
                graph.color = color

    def __getitem__(self, item):
        return self.parameters[item][1]

    def __getattr__(self, name):
        return self[name]
