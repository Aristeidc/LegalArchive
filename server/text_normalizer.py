import unicodedata,re


def normalizer(name:str):
    compose = unicodedata.normalize('NFC',name)
    decomposed = unicodedata.normalize('NFD',compose)
    #accent removal
    no_accents = ''.join(i for i in decomposed if not unicodedata.category(i).startswith('M') )
    #make all lowercase, casefold also folds final ς to σ
    casefolded = no_accents.casefold() 
    #remove hyphens commas etc and replace with space 
    clean_text = re.sub(r'[^\w\s]',' ',casefolded)
    #delete extra spaces
    final_name = re.sub(r'\s+',' ',clean_text).strip()
    return final_name
                         