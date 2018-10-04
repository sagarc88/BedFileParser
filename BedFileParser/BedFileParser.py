import pandas as pd
import re



class IncorrectChr(Exception):
    def __init__(self):
        Exception.__init__(self, "Incorrect chromosome naming in file: Chromosomes must be named chr1 - chr22.")


class IncorrectCoord(Exception):
    def __init__(self):
        Exception.__init__(self,
                           "Incorrect start and end coordinates. coordinates must not be larger than 2^32 or less than "
                           "1. End coordinates must be greater than start coordinates")


class IncorrectFeatureName(Exception):
    def __init__(self):
        Exception.__init__(self,
                           "feature name must be alphanumeric and can only contain hyphen, underscore and parentheses")


class IncorrectStrand(Exception):
    def __init__(self):
        Exception.__init__(self, "Strand must be + or -")


def load_file(filename):
    try:
        fd = open(filename, 'r')
    except FileNotFoundError as fnf_error:
        print(fnf_error)
    else:
        max_coord = 2 ** 32
        min_coord = 1

        bed_list = []
        for line in fd:
            bed_temp = line.strip().split("\t")
            try:
                if not re.match("^(chr2[0-2]|chr1[0-9]|chr[1-9])$", bed_temp[0]):
                    raise IncorrectChr()
            except IncorrectChr:
                print("Offending Line: %s" % (line.strip()))
                fd.close()
                raise
            else:
                bed_temp[0] = bed_temp[0].replace("chr", "")

            # noinspection PyTypeChecker
            bed_temp[1] = int(bed_temp[1])
            # noinspection PyTypeChecker
            bed_temp[2] = int(bed_temp[2])

            try:
                # noinspection PyTypeChecker
                if bed_temp[1] > max_coord or bed_temp[2] > max_coord or bed_temp[1] < min_coord or \
                        bed_temp[2] < min_coord or bed_temp[2] < bed_temp[1]:
                    raise IncorrectCoord()
            except IncorrectCoord:
                print("Offending Line: %s" % (line.strip()))
                fd.close()
                raise

            try:
                if re.match('^[a-zA-Z0-9-_()]+$', bed_temp[3]) is None:
                    raise IncorrectFeatureName()
            except IncorrectFeatureName:
                print("Offending Line: %s" % (line.strip()))
                fd.close()
                raise

            try:
                if bed_temp[4] not in ["-", "+"]:
                    raise IncorrectStrand()
            except IncorrectStrand:
                print("Offending Line: %s" % (line.strip()))
                fd.close()
                raise

            bed_list.append(bed_temp)

        header = ["chrom", "start", "end", "name", "strand"]
        bed = pd.DataFrame(bed_list, columns=header)
        fd.close()

        return bed


def search_position(df, chrom, start=None, end=None):
    max_coord = 2 ** 32
    min_coord = 1

    try:
        if not re.match("^(chr2[0-2]|chr1[0-9]|chr[1-9])$", chrom):
            raise IncorrectChr()
    except IncorrectChr:
        print("Search Input: %s" % chrom)
        raise
    else:
        chrom = chrom.replace("chr", "")

    if (start is not None) and (end is not None):
        try:
            if start > max_coord or end > max_coord or start < min_coord or end < min_coord or end < start:
                raise IncorrectCoord()
        except IncorrectCoord:
            print("Search start and end input: %s %s" % (start, end))
            raise

        subset = df.loc[((df['chrom'] == chrom) & (df['start'] >= start) & (df['end'] < end))].reset_index(drop=True)
        if subset.empty:
            return None
        else:
            return subset
    else:
        subset = df.loc[df['chrom'] == chrom].reset_index(drop=True)
        if subset.empty:
            return None
        else:
            return subset


def search_featurename(df, name):
    try:
        if re.match('^[a-zA-Z0-9-_()]+$', name) is None:
            raise IncorrectFeatureName()
    except IncorrectFeatureName:
        print("Search feature name input: %s" % name)
        raise
    else:
        subset = df.loc[df['name'] == name].reset_index(drop=True)
    if subset.empty:
        return None
    else:
        return subset


def summary_statistics(data):
    df_copy = data.copy()
    df_copy['length'] = df_copy['end'] - df_copy['start']

    stats = df_copy.groupby(['chrom'])['chrom'].count()
    stats = pd.DataFrame(stats)
    stats.rename(columns={'chrom': 'TotalFeatures'}, inplace=True)

    stats['NumFeaturesPos'] = df_copy[df_copy['strand'] == '+'].groupby(['chrom'])['chrom'].count()
    stats['NumFeaturesNeg'] = df_copy[df_copy['strand'] == '-'].groupby(['chrom'])['chrom'].count()

    stats_2 = df_copy.groupby(['chrom'])['length'].agg(['min', 'max', 'mean'])
    stats = stats.join(stats_2)
    stats.fillna(0, inplace=True)
    return stats
