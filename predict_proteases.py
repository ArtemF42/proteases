#!/usr/bin/env python3
from argparse import ArgumentParser, Namespace

from pyhmmer.easel import SequenceFile
from pyhmmer.hmmer import HMMFile, hmmscan

from Bio import SeqIO
from Bio.SeqUtils import molecular_weight
from Bio.SeqUtils.IsoelectricPoint import IsoelectricPoint


def main(args: Namespace) -> None:
    sequences = SeqIO.index(args.seqfile, 'fasta')

    with (
        SequenceFile(args.seqfile, digital=True) as queries,
        HMMFile(args.hmmfile) as profiles,
        open(args.tsv, mode='w') as tsv_outfile,
        open(args.faa, mode='w') as faa_outfile
    ):
        print('seq_id', 'family', 'molecular_weight', 'isoelectric_point', sep='\t', file=tsv_outfile)

        for hits in hmmscan(queries, profiles):
            if hits:
                seq_id = hits.query_name.decode()
                family = hits[0].name.decode()

                if not 'X' in (seq := sequences[seq_id]):
                    mw = round(molecular_weight(seq, seq_type='protein'))
                    pi = round(IsoelectricPoint(seq).pi(), 2)
                else:
                    mw, pi = None, None

                print(seq_id, family, mw, pi, sep='\t', file=tsv_outfile)
                SeqIO.write(seq, faa_outfile, 'fasta')
            

if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('--tsv', type=str, default='predicted_proteases.tsv')
    parser.add_argument('--faa', type=str, default='predicted_proteases.faa')

    parser.add_argument('--evalue', type=float, default=1e-3)

    parser.add_argument('hmmfile', type=str)
    parser.add_argument('seqfile', type=str)

    main(parser.parse_args())
