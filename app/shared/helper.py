import base64
import random
import string
import hashlib
import uuid
import time

from app.constants.stop_words_list import english_stop_words

## files
def get_file_name(filename):
    name = filename.rsplit('.', 1)[0]
    return name

def read_file(file):
    res = file.read()
    file.seek(0)
    return res

#upload posts
ALLOWED_POST_FILES = ['png', 'jpg', 'jpeg']

def is_allowed_for_post(p_filename):
    return '.' in p_filename and p_filename.rsplit('.', 1)[1].lower() in ALLOWED_POST_FILES

def image2base64(file):
    str = base64.b64encode(file)
    return str.decode('utf-8')

## strings
def get_sanitize_string(p_string):
    return [word for word in p_string.lower().translate(str.maketrans('', '', string.punctuation)).split(' ') if not word in english_stop_words]

def string2md5(p_string):
    res_md5 = hashlib.md5(p_string.encode('utf-8')).hexdigest()
    return res_md5

def generate_unique_string(p_string):
    res = f"{p_string}_{uuid.uuid4().hex[:10]}_{int(time.time())}"
    return res

def generate_random_string(string_length = 10):
    letters = string.ascii_lowercase
    rand = ''.join(random.choice(letters) for i in range(string_length))
    return rand

#validate password
def validate_password(password):        
    vals = {
        # 'Password must contain an uppercase letter.': lambda s: any(x.isupper() for x in s),
        # 'Password must contain a lowercase letter.': lambda s: any(x.islower() for x in s),
        # 'Password must contain a digit.': lambda s: any(x.isdigit() for x in s),
        # 'Password must be at least 8 characters.': lambda s: len(s) >= 8,
        # 'Password cannot contain white spaces.': lambda s: not any(x.isspace() for x in s)            
        'Password must be at least 2 characters.': lambda s: len(s) >= 2
        } 
    valid = True
    for n, val in vals.items():                         
        if not val(password):                   
            valid = False
            return n
    return valid

## generate hastags from string (nr of hastags must be less than nr setup in config)
def generate_hastags(text, hastags_nr=3):
    tokenize_string = [word for word in text.lower().translate(str.maketrans('', '', string.punctuation)).split(' ') if not word in english_stop_words]
    uniq = set(tokenize_string)
    # i = 0
    hs = set()
    while len(hs) < min(len(uniq), hastags_nr):
        # i += 1
        hs.add("#" + random.choice(list(uniq)))
    return list(hs)

def get_string_from_inside_list(p_string, p_list):
    sanitize_string = get_sanitize_string(p_string)
    filtered_list = []
    for word in sanitize_string:
        for line in p_list:
            if word in line:
                filtered_list.append(line) ## TODO: for larger list this should pe optimize, maybe return only the first item found
    res = random.choice(filtered_list) if len(filtered_list) != 0 else random.choice(p_list)
    return res