import sys
import os
import errno

# Utility functions

def check_input():
    """
    Checks input parameters.

    Prints usage and exits if invalid input.
    """
    if len(sys.argv) != 5:
        # Print usage
        print "Check input parameters! Usage: bigrams.py inputTextFile sequencesTextFile outputBigramsFile outputSequencesFile"
        sys.exit()

def load_file(input_file):
    """
    Returns file contents
    """

    output = ''
    with open(input_file, 'r') as f:
        output = f.read().replace(os.linesep, '')
    
    return output

def get_bigrams(input_text, bigram_dict):
    """
    Loads info about bigrams from text into dictionary

    Dictionary keys are bigrams, values are their counts in the given input_text
    
    param input_text: source text for bigrams calculation
    param bigram_dict: dictionary to load bigrams into
    """
    
    bigram_dict.clear()
    for i, c in enumerate(input_text):
        if i == 0:
            continue

        bigram = input_text[i-1:i+1]
        if bigram in bigram_dict:
            bigram_dict[bigram] = bigram_dict[bigram] + 1
        else:
            bigram_dict[bigram] = 1

def store_bigrams_to_file(bigram_dict, output_file):
    """
    Stores bigrams information into file

    param bigram_dict: source bigram dictionary
    param output_file: path/filename to the output file (folders will be created)
    """

    # Check if we need to create output folders
    if ('\\' in output_file or '/' in output_file) and \
            not os.path.exists(os.path.dirname(output_file)):
        
        try:
            os.makedirs(os.path.dirname(output_file))
        except OSError as exc: # Guard agains race condition
            if exc.errno != errno.EEXIST:
                raise

    item_count = len(bigram_dict)
    i = 0

    with open(output_file, 'w') as f:
        for bigram, count in bigram_dict.iteritems():
            i = i + 1
            f.write("{0} {1}".format(bigram, count))
            
            # Don't add newline if last item in file
            if i < item_count:
                f.write(os.linesep)

def store_to_file(content, output_file):
    """
    Stores content into file

    param content: content to be stored to file
    param output_file: path/filename to the output file (folders will be created)
    """

    # Check if we need to create output folders
    if ('\\' in output_file or '/' in output_file) and \
            not os.path.exists(os.path.dirname(output_file)):
        
        try:
            os.makedirs(os.path.dirname(output_file))
        except OSError as exc: # Guard agains race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(output_file, 'w') as f:
        f.write(content)

def get_most_likely_continuation_for_char(char, bigrams):
    """
    Gets most likely continuation for a character, based on calculated bigrams.

    param char: character we're looking the continuation for
    param bigrams: sorted (by count) tuple list of bigrams in format [(bigram, count)]
    
    Returns most likely continuation character if exists.
    """
    
    if len(char) != 1:
        print "Can't get continuation, invalid request"
        return ''
    
    if len(bigrams) < 1:
        print "Can't get continuation, not enough bigram information"
        return ''

    return next(bigram for bigram in bigrams if bigram[0].startswith(char))[0][1]

def get_continuation_for_sequence(sequence, bigrams, count):
    """
    Gets most likely continuation of count chars for the given sequence, based on calculated bigrams
    
    param sequence: sequence we're looking the continuation for
    param bigrams: sorted (by count) tuple list of bigrams in format [(bigram, count)]
    param count: count of continuation characters

    Returns the expected sequence.
    """

    if len(sequence) < 1:
        print "Can't get continuation, empty sequence"
        return ''

    for x in range(0, count):
        sequence = sequence + get_most_likely_continuation_for_char(sequence[len(sequence) - 1], bigrams)

    return sequence

# Main program

check_input()

# Globals
continuation_character_count = 3
input_text_filename = sys.argv[1]
input_sequences_filename = sys.argv[2]
output_bigrams_filename = sys.argv[3]
output_sequences_filename = sys.argv[4]
input_text = ''
input_sequences = ''
output_bigrams = ''
output_sequences = ''
bigram_dict = {}

# Load data
input_text = load_file(input_text_filename)
input_sequences = load_file(input_sequences_filename)

# Logic
get_bigrams(input_text, bigram_dict)
store_bigrams_to_file(bigram_dict, output_bigrams_filename)
sorted_bigram_list = sorted(bigram_dict.items(), key = lambda x: x[1], reverse = True)
store_to_file(get_continuation_for_sequence(input_sequences, sorted_bigram_list, continuation_character_count), output_sequences_filename)
