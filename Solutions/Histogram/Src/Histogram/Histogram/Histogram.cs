using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;
using System.Drawing.Imaging;

namespace Histogram
{
    public class Histogram
    {
        private Dictionary<byte, uint> histogram = new Dictionary<byte, uint>();
        private uint numberOfPixels = 0;
        private Random rand = new Random();

        public Histogram()
        {
            Clear();
        }

        public void Clear()
        {
            histogram.Clear();

            // Initialize histogram
            for (byte i = 0;; i++)
            {
                histogram[i] = 0;
                if (i == 255) break;
            }
        }

        public void ProcessBitmap(FileInfo bitmapFile, FileInfo textFile)
        {      
            uint[] cropArea = new uint[4];
            // Get crop area from text file
            using (StreamReader sr = textFile.OpenText())
            {
                var cropAreaString = sr.ReadToEnd().Split(' ');
                for (uint i = 0; i < cropAreaString.Length; i++)
                {
                    try
                    {
                        cropArea[i] = uint.Parse(cropAreaString[i]);
                    }
                    catch (Exception e)
                    {
                        Console.WriteLine(e.Message);
                    }
                }
            }

            uint left = cropArea[0];
            uint top = cropArea[1];
            uint width = cropArea[2];
            uint height = cropArea[3];

            var bitmap = new Bitmap(bitmapFile.FullName);
            for (uint x = left; x < left + width; x++)
            {
                for (uint y = top; y < top + height; y++)
                {
                    Color pixel = bitmap.GetPixel((int)x, (int)y);
                    byte grayscale = Convert.ToByte(pixel.R * 0.2126 + pixel.G * 0.7152 + pixel.B * 0.0722);

                    histogram[grayscale] = histogram[grayscale] + 1;
                    numberOfPixels++;
                }
            }
        }

        public Bitmap GenerateRandomGrayscaleBitmapFromHistogram(uint size)
        {
            var scaledHistogram = getScaledHistogram(size);

            var bitmap = new Bitmap((int)size, (int)size, PixelFormat.Format24bppRgb);
            var pixels = new byte[size * size];

            for (int i = 0; i < size*size; i++)
            {
                byte? nullableIntensity = getRandomIntensity(scaledHistogram);
                if (nullableIntensity.HasValue)
                {
                    byte intensity = nullableIntensity.Value;
                    scaledHistogram[intensity]--;

                    pixels[i] = intensity;
                }
                else
                {
                    pixels[i] = 0;
                }
            }

            new Random().Shuffle(pixels);

            for (uint x = 0; x < size; x++)
            {
                for (uint y = 0; y < size; y++)
                {
                    var intensity = pixels[x*size + y];

                    bitmap.SetPixel((int)x, (int)y, Color.FromArgb(intensity, intensity, intensity));
                }
            }

            return bitmap;
        }

        private byte? getRandomIntensity(Dictionary<byte, uint> histogram)
        {
            var filteredHistogram = histogram.Where(item => item.Value > 0);
            if (filteredHistogram.Any())
            {
                return filteredHistogram.ElementAt(rand.Next(0, filteredHistogram.Count())).Key;
            }

            return null;
        }

        private Dictionary<byte, uint> getScaledHistogram(uint size)
        {
            var scaledHistogram = new Dictionary<byte, uint>(histogram);
            if (numberOfPixels > 0)
            {
                uint ratio = size * size / numberOfPixels;

                for (byte i = 0; ; i++)
                {
                    scaledHistogram[i] = scaledHistogram[i] * ratio;
                    if (i == 255) break;
                }
            }

            return scaledHistogram;
        }

        private string toString(Dictionary<byte, uint> histogram)
        {
            var sb = new StringBuilder();

            for (byte i = 0;; i++)
            {
                sb.AppendFormat("{0},", histogram[i]);
                if (i == 255) break;
            }

            sb.Remove(sb.Length - 1, 1);

            return sb.ToString();
        }

        public override string ToString()
        {
            return toString(histogram);
        }

        public string ToCsv()
        {
            return ToString();
        }

        public string toCsvScaled(uint size)
        {
            return toString(getScaledHistogram(size));
        }

        public bool IsEmpty()
        {
            return histogram.Count == 0;
        }
    }
}
