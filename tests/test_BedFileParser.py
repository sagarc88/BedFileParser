import unittest
from BedFileParser import BedFileParser
import pandas as pd
import sys
import io


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.df = BedFileParser.load_file('data/test_bed_working.bed')

    def test_fileload_working(self):

        df_actual = BedFileParser.load_file("data/test_bed_working.bed")

        df_expected = pd.DataFrame(columns=["chrom", "start", "end", "name", "strand"],
                                   data=[["1", 1, 2999, "gene1", "+"],
                                         ["1", 3, 2442, "genex", "-"],
                                         ["2", 8000, 74000, "gene2", "+"],
                                         ["3", 3000, 9000, "gene3", "-"]])

        if df_actual.equals(df_expected):
            self.assertTrue("File loaded properly")
        else:
            self.assertFalse("File cannot be loaded")

    def test_fileload_chr(self):
        self.assertRaises(BedFileParser.IncorrectChr, lambda: BedFileParser.load_file("data/test_bed_chr.bed"))

    def test_fileload_coord(self):
        self.assertRaises(BedFileParser.IncorrectCoord, lambda: BedFileParser.load_file("data/test_bed_coord.bed"))

    def test_fileload_feature(self):
        self.assertRaises(BedFileParser.IncorrectFeatureName, lambda: BedFileParser.load_file("data/"
                                                                                              "test_bed_feature.bed"))

    def test_fileload_strand(self):
        self.assertRaises(BedFileParser.IncorrectStrand, lambda: BedFileParser.load_file("data/test_bed_strand.bed"))

    def test_subset_Chr_working(self):

        res = BedFileParser.search_position(self.df, chrom="chr1")
        expected = pd.DataFrame(columns=["chrom", "start", "end", "name", "strand"],
                                data=[["1", 1, 2999, "gene1", "+"],
                                      ["1", 3, 2442, "genex", "-"]])

        if res.equals(expected):
            self.assertTrue("Chromosome subset working")
        else:
            self.assertFalse("Chromosome subset not working")

    def test_subset_Pos_working(self):

        res = BedFileParser.search_position(self.df, chrom="chr1", start=1, end=2500)
        expected = pd.DataFrame(columns=["chrom", "start", "end", "name", "strand"],
                                data=[["1", 3, 2442, "genex", "-"]])

        if res.equals(expected):
            self.assertTrue("Positional subset working")
        else:
            self.assertFalse("Positional subset working")

    def test_subset_Feature_working(self):

        res = BedFileParser.search_featurename(self.df, name="genex")
        expected = pd.DataFrame(columns=["chrom", "start", "end", "name", "strand"],
                                data=[["1", 3, 2442, "genex", "-"]])

        if res.equals(expected):
            self.assertTrue("Feature subset working")
        else:
            self.assertFalse("Feature subset working")

    def test_summary_working(self):

        res = BedFileParser.summary_statistics(self.df).to_csv()
        expected = pd.DataFrame(
            columns=["chrom", "TotalFeatures", "NumFeaturesPos", "NumFeaturesNeg", "min", "max", "mean"],
            data=[[1, 2, 1.0, 1.0, 2439, 2998, 2718.5],
                  [2, 1, 1.0, 0.0, 66000, 66000, 66000.0],
                  [3, 1, 0.0, 1.0, 6000, 6000, 6000.0]]
            )
        expected.set_index('chrom', inplace=True)
        expected_csv = expected.to_csv()

        if res == expected_csv:
            self.assertTrue("Summary is working")
        else:
            self.assertFalse("Summary is not working")

    def test_subset_chr(self):

        self.assertRaises(BedFileParser.IncorrectChr, lambda: BedFileParser.search_position(self.df, chrom="1"))

    def test_subset_coord(self):
        self.assertRaises(BedFileParser.IncorrectCoord, lambda: BedFileParser.search_position(self.df, chrom="chr1",
                                                                                              start=3000, end=1))

    def test_subset_feature(self):
        self.assertRaises(BedFileParser.IncorrectFeatureName, lambda: BedFileParser.search_featurename(self.df,
                                                                                                       name="genex!"))


if __name__ == '__main__':
    # create a text trap and redirect stdout
    text_trap = io.StringIO()
    sys.stdout = text_trap

    unittest.main()

    # now restore stdout function
    sys.stdout = sys.__stdout__
