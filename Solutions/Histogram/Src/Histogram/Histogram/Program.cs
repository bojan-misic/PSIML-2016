using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Histogram
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length != 2)
            {
                Console.WriteLine("Invalid arguments provided. Usage: histogram.exe inputFolderPath outputFolderPath");
                return;
            }

            var inputFolderPath = args[0];
            var outputFolderPath = args[1];
            var histogram = new Histogram();

            var fileList = new List<System.IO.FileInfo>();
            Helpers.TraverseTree(inputFolderPath, fileList);

            foreach (var file in fileList)
            {
                if (file.Extension != ".bmp")
                {
                    continue;
                }

                // We have a bitmap file at this point
                var textFileName = file.FullName.Replace("bmp", "txt");
                try
                {
                    var textFile = new System.IO.FileInfo(textFileName);
                    histogram.ProcessBitmap(file, textFile);
                }
                catch(Exception e)
                {
                    Console.WriteLine(e.Message);
                }
            }

            string globalCsv = histogram.ToCsv();
            string matchingCsv = histogram.toCsvScaled(100);

            var globalHistoFile = new System.IO.FileInfo(outputFolderPath + "\\GlobalHisto.csv");
            globalHistoFile.Directory.Create(); // If the directory already exists, this method does nothing.
            System.IO.File.WriteAllText(globalHistoFile.FullName, globalCsv);

            var matchingHistoFile = new System.IO.FileInfo(outputFolderPath + "\\MatchingHisto.csv");
            System.IO.File.WriteAllText(matchingHistoFile.FullName, matchingCsv);

            var matchedBitmap = histogram.GenerateRandomGrayscaleBitmapFromHistogram(100);
            matchedBitmap.Save(outputFolderPath + "\\MatchingImage.bmp");
        }
    }
}
