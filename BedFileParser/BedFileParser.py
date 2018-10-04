import pandas as pd
import re


# Exception for incorrect chromosome namings
class IncorrectChr(Exception):
    def __init__(self):
        Exception.__init__(self, "Incorrect chromosome naming in file: Chromosomes must be named chr1 - chr22.")

# Exception for incorrect positional coordinates
class IncorrectCoord(Exception):
    def __init__(self):
        Exception.__init__(self,
                           "Incorrect start and end coordinates. coordinates must not be larger than 2^32 or less than "
                           "1. End coordinates must be greater than start coordinates")

# Exception for incorrect feature name
class IncorrectFeatureName(Exception):
    def __init__(self):
        Exception.__init__(self,
                           "feature name must be alphanumeric and can only contain hyphen, underscore and parentheses")

# Exception for incorrect strand characters
class IncorrectStrand(Exception):
    def __init__(self):
        Exception.__init__(self, "Strand must be + or -")

# Function to read BED file, parse and add to pandas dataframe 
def load_file(filename):
    #Try to open file and throw error if cannot be opened/found. 
    try:
        fd = open(filename, 'r')
    except FileNotFoundError as fnf_error:
        print(fnf_error)
    else:
        #definition of max and min allowed coordinates
        max_coord = 2 ** 32
        min_coord = 1

        bed_list = []
        #Read BED file line by line
        for line in fd:
            bed_temp = line.strip().split("\t")
            # Check if chromosome is correctly named. Chr1 - chr22
            try:
                if not re.match("^(chr2[0-2]|chr1[0-9]|chr[1-9])$", bed_temp[0]):
                    raise IncorrectChr()
            except IncorrectChr:
                print("Offending Line: %s" % (line.strip()))
                fd.close()
                raise
            else:
                #Remove chr string as per specification
                bed_temp[0] = bed_temp[0].replace("chr", "")

            bed_temp[1] = int(bed_temp[1])
            bed_temp[2] = int(bed_temp[2])
            
            # Check if start and end coordinates are as per specification
            try:
                if bed_temp[1] > max_coord or bed_temp[2] > max_coord or bed_temp[1] < min_coord or \
                        bed_temp[2] < min_coord or bed_temp[2] < bed_temp[1]:
                    raise IncorrectCoord()
            except IncorrectCoord:
                print("Offending Line: %s" % (line.strip()))
                fd.close()
                raise
            
            # Check if feature name contains acceptable characters only
            try:
                if re.match('^[a-zA-Z0-9-_()]+$', bed_temp[3]) is None:
                    raise IncorrectFeatureName()
            except IncorrectFeatureName:
                print("Offending Line: %s" % (line.strip()))
                fd.close()
                raise
            
            # Check if strand contains acceptable characters only
            try:
                if bed_temp[4] not in ["-", "+"]:
                    raise IncorrectStrand()
            except IncorrectStrand:
                print("Offending Line: %s" % (line.strip()))
                fd.close()
                raise
            #If passed all checks, add line to list
            bed_list.append(bed_temp)

        # Create pandas dataframe
        header = ["chrom", "start", "end", "name", "strand"]
        bed = pd.DataFrame(bed_list, columns=header)
        fd.close()

        return bed


def search_position(df, chrom, start=None, end=None):
    max_coord = 2 ** 32
    min_coord = 1
    
    # Check if chromosome is correctly named. Chr1 - chr22
    try:
        if not re.match("^(chr2[0-2]|chr1[0-9]|chr[1-9])$", chrom):
            raise IncorrectChr()
    except IncorrectChr:
        print("Search Input: %s" % chrom)
        raise
    else:
        chrom = chrom.replace("chr", "")
        
    # If start and end are provided, do positional subset
    if (start is not None) and (end is not None):
        # Check if input start and end coordinates are as per specification
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
    # Otherwise, just subset on chromosome
    else:
        subset = df.loc[df['chrom'] == chrom].reset_index(drop=True)
        if subset.empty:
            return None
        else:
            return subset


def search_featurename(df, name):
    # Check if feature name contains acceptable characters only
    try:
        if re.match('^[a-zA-Z0-9-_()]+$', name) is None:
            raise IncorrectFeatureName()
    except IncorrectFeatureName:
        print("Search feature name input: %s" % name)
        raise
    else:
        # Subset based on feature name.
        subset = df.loc[df['name'] == name].reset_index(drop=True)
    if subset.empty:
        return None
    else:
        return subset


def summary_statistics(data):
    # Copy data to not overwrite original dataframe
    df_copy = data.copy()
    # Calculate length as end - start 
    df_copy['length'] = df_copy['end'] - df_copy['start']
    
    # Calculate number of features per chromosome
    stats = df_copy.groupby(['chrom'])['chrom'].count()
    stats = pd.DataFrame(stats)
    stats.rename(columns={'chrom': 'TotalFeatures'}, inplace=True)
    
    #Calculate number of features per strand
    stats['NumFeaturesPos'] = df_copy[df_copy['strand'] == '+'].groupby(['chrom'])['chrom'].count()
    stats['NumFeaturesNeg'] = df_copy[df_copy['strand'] == '-'].groupby(['chrom'])['chrom'].count()
    
    # Calculate summary statistics per chromosome 
    stats_2 = df_copy.groupby(['chrom'])['length'].agg(['min', 'max', 'mean'])
    stats = stats.join(stats_2)
    stats.fillna(0, inplace=True)
    return stats
