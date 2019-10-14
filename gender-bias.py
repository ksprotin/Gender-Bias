# This code is a modified version of https://github.com/marceloprates/Gender-
# Bias/blob/master/gender-bias.py. Currently, the code has been modified to
# remove all sections related to adjective translation and update occupation
# sections to fields of study (FOS). It was last modified on 10/13/19 by 
# Katy Mitchell, (kmitch64@uncc.edu) for ITCS 5111: Introduction to Natural 
# Language Processing


import sys
from googletrans import Translator
from googletrans import LANGUAGES
from xpinyin import Pinyin
import csv
import numpy as np


# Define function to obtain the translated gender of a field of study (FOS) in a given language (through Google Translate)
def get_gender(language, fos=None, case=None):

    field_of_study_dict = dict()
    field_of_study_dict['Malay'] = 'dia adalah %s' #change to education
    field_of_study_dict['Estonian'] = 'ta on %s' #change to education
    field_of_study_dict['Swahili'] = 'yeye ni %s' #change to education
    if fos is not None:
        phrase = field_of_study_dict[language] % fos
    else:
        raise Exception("Field of study has not been provided")
    # end if

    try:
        translation = translator.translate(phrase, src=language, dest='en').text
        translation = translation.lower()
        print("Language: {} | Phrase: {} | Translation: {}".format(language, phrase, translation))
        
        female_markers = ["she", "she's", "her"]
        male_markers = ["he", "he's", "his"]
        neuter_markers = ["it", "it's", "its", "they", "they're", "them", "who", "this", "that"]
        
        has_any = lambda markers, translation: any([ marker.lower() in translation.lower().split() for marker in markers ])

        if(has_any(female_markers, translation) or translation[0:10].find("that woman") != -1):
            return 'Female'  # Suggestion: (1,0,0)
        elif(has_any(male_markers, translation) or translation[0:8].find("that man") != -1):
            return 'Male'  # Suggestion: (0,1,0)
        elif(has_any(neuter_markers, translation)):
            return 'Neutral'  # Suggestion: (0,0,1)
        else:
            return '?'
    except:
        return '?'
    # end try
# end def


translator = Translator()
p = Pinyin()

do_fos = "fos" in sys.argv

# Get language list
languages = []
with open('/Users/katymitchell/Documents/GitHub/Gender-Bias/languages.csv', 'r') as f:
    f.readline()
    for line in f:
        language, family, pronomial_gender_system, supported = line.split(";")
        if(pronomial_gender_system != 'Yes' and supported.rstrip() == 'Yes'):
            languages.append(language)
# end with

# The remainder of this code needs to be modified to use NCES files
if do_fos:
    # Read FOS list into table
    fos_table = np.array(list(csv.reader(open('jobs/bureau_of_labor_statistics_profession_list_gender_filtered_expanded.tsv', 'r'), delimiter='\t')))
    # Compute list of categories
    categories = list(set(fos_table[1:, -3]))
    # Get dictionary of category -> jobs (jobs per category)
    categories_dict = dict([ (category, fos_table[fos_table[:, -3] == category, 0]) for category in categories ])
# end if

"""
    Create a fos_table with the translated version (provided by Google Translate) of each field of study,
    in the following structure:
        1. Each line corresponds to a single FOS
        2. The following 3 columns give a translated version of that FOS for each of the three languages
"""
if False and do_fos:
    with open("Results/jobs-translations.tsv", "w") as output:
     
        # Write header
        # First column is category
        output.write("Category")
        # Then follows one column per language
        output.write("\tEnglish")
        for language in languages:
            output.write('\t' + language)
        # end for
        output.write('\n')

# need to modify to use without categories

        # Now iterate over all categories
        for category in categories:
            print("Translating occupations from category {} ...".format(category))
            # Get all jobs for this category
            for fos in categories_dict[category]:
                print("\tTranslating occupation \"{}\" ...".format(fos))
                output.write(category)
                output.write('\t' + fos)
                # For each language L in our list, translate 'job' from English to L
                for language in languages:
                    try:
                        translated_fos = (translator.translate(fos.rstrip().lower(), src='en', dest=language).text).lower()
                    except Exception:
                        print("\tCould not translate FOS %s to language %s" % (fos.rstrip(), language))
                        translated_fos = "?"
                    # end try
                    output.write('\t' + translated_fos)
                # end for
                output.write('\n')
            # end for
        # end for
    # end with
# end if

"""
    Now create
"""

if do_fos:
    # Get table with one FOS for row, translated to every language (one per column)
    translated_fos = list(csv.reader(open('Results/jobs-translations.tsv', 'r'), delimiter='\t'))
    with open('Results/job-genders.tsv', 'w') as output:
        # Write header
        output.write("Category")
        output.write("\tField of Study")
        for language in languages:
            output.write('\t' + language)
        # end for
        output.write('\n')

        for entry in translated_fos[1:]:
        
            category = entry[0]
            english_name = entry[1]
            foreign_names = entry[2:]

            print("Translating field of study \"{}\" ...".format(english_name))

            output.write(category)
            output.write('\t' + english_name)

            for (language, foreign_name) in zip(languages, foreign_names):
                gender = get_gender(language, occupation=foreign_name)
                output.write('\t%s' % gender)
                    # end if
                # end if
            # end for

            output.write('\n')
            output.flush()
        # end for
    # end with
# end if
