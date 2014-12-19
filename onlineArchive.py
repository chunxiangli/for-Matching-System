#!/usr/bin/python

# modification script based on onlinewikipedia.py: Demonstrates the use of online VB for LDA to
# analyze a bunch of random Wikipedia articles.
#
# Copyright (C) 2010  Matthew D. Hoffman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import string, numpy, getopt, sys, random, time, re
#import onlineldava from the source code directory of online_lda
import onlineldavb
data_dir = '/cs/fs2/home/czli/work/data/arChive/abstract'
def get_abstracts(iteration):
	docset = []
	with open('%s/data%d_abstract.txt'%(data_dir, iteration+1)) as dao:
		for line in dao:
			docset.append(" ".join(line.split()[1:]))
	return docset
		
def main():
    """
	using online VB for LDA on Archive data.
    """

    # The number of documents to analyze each iteration
    batchsize = 1000
    # The total number of documents in Wikipedia
    D = 7000
    # The number of topics
    K = 10
    # How many documents to look at
    documentstoanalyze = int(D/batchsize)
    if (len(sys.argv) > 1):
    	K = int(sys.argv[1])

    # Our vocabulary
    vocab = file(data_dir+'/dictionary_all.txt').readlines()
    W = len(vocab)

    # Initialize the algorithm with alpha=1/K, eta=1/K, tau_0=1024, kappa=0.7
    olda = onlineldavb.OnlineLDA(vocab, K, D, 1./K, 1./K, 1024., 0.7)
    # Run until we've seen D documents. (Feel free to interrupt *much*
    # sooner than this.)
    for iteration in range(0, documentstoanalyze):
        docset= get_abstracts(iteration)
        # Give them to online LDA
        (gamma, bound) = olda.update_lambda(docset)
        # Compute an estimate of held-out perplexity
        (wordids, wordcts) = onlineldavb.parse_doc_list(docset, olda._vocab)
        perwordbound = bound * len(docset) / (D * sum(map(sum, wordcts)))
        print '%d:  rho_t = %f,  held-out perplexity estimate = %f' % \
            (iteration, olda._rhot, numpy.exp(-perwordbound))

        # Save lambda, the parameters to the variational distributions
        # over topics, and gamma, the parameters to the variational
        # distributions over topic weights for the articles analyzed in
        # the last iteration.
    	numpy.savetxt('%darchive-lambda-%d.dat' % (K, iteration), olda._lambda)
    	numpy.savetxt('%darchive-gamma-%d.dat' % (K, iteration), gamma)

if __name__ == '__main__':
    main()
