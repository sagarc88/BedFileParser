import argparse
from BedFileParser import load_file, search_featurename, search_position, summary_statistics


def main():
    parser = argparse.ArgumentParser(description='A script to process a bedfile and return a '
                                                 'subset or summary statistics')
    group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('-f', '--file', type=str,
                        help='Name of the file (Required)', dest="file", required=True)
    group.add_argument('--summary', action="store_true",
                       help='Output statistics across all chromosomes to screen', dest="summary")
    group.add_argument('--chrom', type=str,
                       help='Chromosome name for subset. Providing this option without start/end will '
                            'result in all entries of that chromosome to be outputted', dest="chrom")
    group.add_argument('--feature', type=str,
                       help='Search by feature name', dest="feature")
    parser.add_argument('--pos', nargs=2, metavar=('start', 'end'), type=int,
                        help='Start and end position on chromosome to subset (Optional)', dest="pos")
    parser.add_argument('--outfile', type=str,
                        help='name of output file. printed to cmd-line if not specified (Optional)', dest="outfile")
    args = parser.parse_args()

    if args.pos:
        start_in = args.pos[0]
        end_in = args.pos[1]
    else:
        start_in = None
        end_in = None

    file = load_file(args.file)

    if args.summary:
        result = summary_statistics(file)
    elif args.feature:
        result = search_featurename(file, name=args.feature)
    elif args.chrom and start_in and end_in:
        result = search_position(file, chrom=args.chrom, start=start_in, end=end_in)
    elif args.chrom:
        result = search_position(file, chrom=args.chrom)
    else:
        result = None
        print("Nothing to do!")

    if not result.empty:
        if args.outfile:
            if args.summary:
                result.to_csv(args.outfile, sep="\t", header=True, index=True)
            else:
                result.to_csv(args.outfile, sep="\t", header=False, index=False)
        else:
            if args.summary:
                print(result)
            else:
                print(result.to_csv(sep="\t", header=False, index=False))


if __name__ == '__main__':
    main()