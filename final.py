'''
Created on Nov 24, 2019

@author: katymitchell
'''
# This code is a modified version of https://github.com/marceloprates/Gender-
# Bias/blob/master/gender-bias.py. Currently, the code has been modified to
# remove all sections related to adjective translation and update occupation
# sections to fields of study (FOS). It was last modified on 11/24/19 by 
# Katy Mitchell, (kmitch64@uncc.edu) for ITCS 5111: Introduction to Natural 
# Language Processing

# import sys
from googletrans import Translator
# from googletrans import LANGUAGES
# from xpinyin import Pinyin
import csv
import numpy as np

translator = Translator()

# Define function to obtain the translated gender of a field of study (FOS) in a given language (through Google Translate)
def get_gender(language, fos=None, case=None):
    field_of_study_dict = dict()
    field_of_study_dict['Malay'] = 'Dia sedang mengkaji %s'  # he/she studies <subject>
    field_of_study_dict['Estonian'] = 'ta õppis %s'  # he/she studies <subject>
    field_of_study_dict['Swahili'] = 'Yeye anasoma %s'  # he/she is studying <subject>
    if fos is not None:
        phrase = field_of_study_dict[language] % fos
    else:
        raise Exception("Field of study has not been provided")
    # end if

    try:
        translation = translator.translate('fields.text',dest='.en', src = 'auto')
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

# p = Pinyin()


# Define language list
languages = ['Malay', 'Estonian', 'Swahili']

# Modified to use NCES files
# Read FOS list into table
fos_table = np.array(list(csv.reader(open('degrees-conferred-2014-2016.csv', 'r'), delimiter=',')))

"""
    Create a fos_table with the translated version (provided by Google Translate) of each field of study,
    in the following structure:
        1. Each line corresponds to a single FOS
        2. The following 3 columns give a translated version of that FOS for each of the three languages
"""
with open("Results/fos-translations.csv", "w") as output:
     
    # Write header
    # First column is field of study
    output.write("Field of Study")
    # Then follows one column per language
    output.write(",English")
    for language in languages:
        output.write(',' + language)
    # end for
    output.write('\n')

    major_table = np.array(list(csv.reader(open('degrees-conferred-2014-2016.csv','r'))))
    # Compute list of categories
    majors = list(set(major_table[1:,-3]))
    # Get dictionary of category -> jobs (jobs per category)
    majors_dict = dict([ (major, major_table[major_table[:,-3] == major,0]) for major in majors ])
        
    for fos in majors:
        print("Translating field of study \"{}\" ...".format(fos))
        output.write(fos)
        output.write(',' + fos)
        # For each language L in our list, translate 'job' from English to L
        for language in languages:
            try:
                translated_fos = (translator.translate(fos.rstrip().lower(),src='en',dest=language).text).lower()
            except Exception:
                print(",Could not translate field %s to language %s" % (fos.rstrip(),language))
                translated_fos = "?"
            #end try
            output.write(',' + translated_fos)
            output.write('\n')
        #end for
# end with

"""
    Now create
"""

def create_table():
    # Get table with one FOS per row, translated to every language (one per column)
    translated_fos = list(csv.reader(open('Results/fos-translations.csv', 'r')))
    print(translated_fos)
    with open('Results/fos-genders.csv', 'w') as output:
        # Write header
        output.write("Field of Study")
        for language in languages:
            output.write(',' + language)
        # end for
        output.write('\n')
    
        for entry in translated_fos[1:]:
            print(entry)
            english_name = entry[1]
            foreign_names = entry[2:]
    
            print("Translating field of study \"{}\" ...".format(english_name))
    
            output.write(',' + english_name)
            for (language, foreign_name) in zip(languages, foreign_names):
                gender = get_gender(language, fos=foreign_name)
                output.write(',%s' % gender)
            # end for    
            output.write('\n')
            output.flush()
        # end for
    # end with
# end def

create_table()