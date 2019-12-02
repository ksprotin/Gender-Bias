'''
Created on Dec 1, 2019

@author: katymitchell
'''
# This code is a modified version of https://github.com/marceloprates/Gender-
# Bias/blob/master/gender-bias.py. It has been modified to
# remove all sections related to adjective translation and update occupation
# sections to fields of study (FOS). It was last modified on 12/1/19 by 
# Katy Mitchell, (kmitch64@uncc.edu) for ITCS 5111: Introduction to Natural 
# Language Processing

from googletrans import Translator
import csv
import numpy as np

translator = Translator()

# Define function to obtain the translated gender of a field of study (FOS) in a given language (through Google Translate)
# Due to limitations of googletrans, this step was performed manually
def get_gender(language, fos=None, case=None):
    field_of_study_dict = dict()
    field_of_study_dict['Malay'] = 'Dia sedang mengkaji %s'  # he/she studies <subject>
    field_of_study_dict['Estonian'] = 'Ta õpib %s'  # he/she studies <subject>
    field_of_study_dict['Swahili'] = 'Anasoma %s'  # he/she is studying <subject>
    if fos is not None:
        phrase = field_of_study_dict[language] % fos
    else:
        raise Exception("Field of study has not been provided")
    # end if

    try:
        translation = translator.translate('fields.text',dest='en', src = 'auto')
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

# Define language list
languages = ['Malay', 'Estonian', 'Swahili']

# Modified to use NCES files
# Read FOS list into table
fos_table = np.array(list(csv.reader(open('degrees-conferred-2014-2016.csv', 'r'), delimiter=',')))

# Identify gender of translated phrases using markers

def identify_gender(translation):
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
    
def create_table():
    # Get table with one FOS per row, translated to every language (one per column)
    translated_fos = list(csv.reader(open('all-language-degrees.csv', 'r')))
    with open('Results/fos-genders.tsv', 'w') as output:
        # Write header
        output.write("Field of Study")
        for language in languages:
            output.write('\t' + language)
        # end for
        output.write('\n')
    
        for entry in translated_fos[1:]:
#            print(entry)
            english_name = entry[0]
            foreign_names = entry[4:7]
            output.write(english_name)
            for (language, foreign_name) in zip(languages, foreign_names):
             #   gender = get_gender(language, fos=foreign_name)
                gender = identify_gender(foreign_name)
                output.write('\t%s' % gender)
            # end for    
            output.write('\n')
            output.flush()
        # end for
    # end with
# end def

create_table()

