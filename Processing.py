#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
In this problem set you work with another type of infobox data, audit it,
clean it, come up with a data model, insert it into MongoDB and then run some
queries against your database. The set contains data about Arachnid class
animals.

Your task in this exercise is to parse the file, process only the fields that
are listed in the FIELDS dictionary as keys, and return a list of dictionaries
of cleaned values. 

The following things should be done:
- keys of the dictionary changed according to the mapping in FIELDS dictionary
- trim out redundant description in parenthesis from the 'rdf-schema#label'
  field, like "(spider)"
- if 'name' is "NULL" or contains non-alphanumeric characters, set it to the
  same value as 'label'.
- if a value of a field is "NULL", convert it to None
- if there is a value in 'synonym', it should be converted to an array (list)
  by stripping the "{}" characters and splitting the string on "|". Rest of the
  cleanup is up to you, e.g. removing "*" prefixes etc. If there is a singular
  synonym, the value should still be formatted in a list.
- strip leading and ending whitespace from all fields, if there is any
- the output structure should be as follows:

[ { 'label': 'Argiope',
    'uri': 'http://dbpedia.org/resource/Argiope_(spider)',
    'description': 'The genus Argiope includes rather large and spectacular spiders that often ...',
    'name': 'Argiope',
    'synonym': ["One", "Two"],
    'classification': {
                      'family': 'Orb-weaver spider',
                      'class': 'Arachnid',
                      'phylum': 'Arthropod',
                      'order': 'Spider',
                      'kingdom': 'Animal',
                      'genus': None
                      }
  },
  { 'label': ... , }, ...
]

  * Note that the value associated with the classification key is a dictionary
    with taxonomic labels.
"""
import codecs
import csv
import json
import pprint
import re

DATAFILE = 'arachnid.csv'
FIELDS ={'rdf-schema#label': 'label',
         'URI': 'uri',
         'rdf-schema#comment': 'description',
         'synonym': 'synonym',
         'name': 'name',
         'family_label': 'family',
         'class_label': 'class',
         'phylum_label': 'phylum',
         'order_label': 'order',
         'kingdom_label': 'kingdom',
         'genus_label': 'genus'}


def process_file(filename, fields):

    process_fields = fields.keys()
    data = []
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for i in range(3):
            l = next(reader)

        for line in reader:
            entry = {}

            label = line["rdf-schema#label"]
            name = line["name"]


            if (name == "NULL"):
              entry["name"] = label

            else:
              valid = re.match("^[\w-]+$", name)
              if valid is None: # contains non-alphanumeric characters
                entry["name"] = label
              else:
                entry["name"] = line["name"].strip()

            
            synonym = line["synonym"].strip()
            
            if (synonym == "NULL"):
              entry["synonym"] = None
            
            else:
              entry["synonym"] = []
              
              if ("{" in synonym):
                synonym_array = parse_array(synonym)
                
                for s in synonym_array:
                  if ("*" in s):
                    s = s[1:]
                  
                  entry["synonym"].append(s)
              
              else:
                entry["synonym"].append(synonym)
            
            
            entry["classification"] = {}
            
            if (line["kingdom_label"] == "NULL"):
              entry["classification"]["kingdom"] = None
            else:
              entry["classification"]["kingdom"] = line["kingdom_label"].strip()
            
            if(line["family_label"] == "NULL"):
               entry["classification"]["family"] = None 
            else:
              entry["classification"]["family"] = line["family_label"].strip()

            if(line["order_label"] == "NULL"):
              entry["classification"]["order"] = None
            else:
              entry["classification"]["order"] = line["order_label"].strip()
            
            if(line["phylum_label"] == "NULL"):
              entry["classification"]["phylum"] = None
            else:
              entry["classification"]["phylum"] = line["phylum_label"].strip()
            
            if(line["genus_label"] == "NULL"):
              entry["classification"]["genus"] = None
            else:
              entry["classification"]["genus"] = line["genus_label"].strip()
            
            if(line["class_label"] == "NULL"):
              entry["classification"]["class"] = None
            else:
              entry["classification"]["class"] = line["class_label"].strip()

            if(line["URI"] == "NULL"):
              entry["uri"] = None
            else:
              entry["uri"] = line["URI"].strip()
            

            
            if(label == "NULL"):
              entry["label"] = None
            
            else:
              if ("(" in label):
                index = label.find("(")
                label = label[:index]

              entry["label"] = label.strip()
            
            
            if(line["rdf-schema#comment"] == "NULL"):
              entry["description"] = None
            else:
              entry["description"] = line["rdf-schema#comment"].strip()

            data.append(entry)

    pprint.pprint(data)
    return data


def parse_array(v):
    if (v[0] == "{") and (v[-1] == "}"): # {* Hydracarina|* Hydrachnellae|* Hydrachnidia}
        v = v.lstrip("{")
        v = v.rstrip("}")
        v_array = v.split("|")
        v_array = [i.strip() for i in v_array]
        #print("v_array : ", v_array)
        return v_array
    return [v]

def insert_data(data, db):
    for entry in data:
        db.arachnid.insert(entry)
  


def writeJson(data):
  with open('arachnid.json', 'w') as f:
    for item in data:
        f.write("%s\n" % item)



def test():
    data = process_file(DATAFILE, FIELDS)
    print("Your first entry: ")
    pprint.pprint(data[0])
    first_entry = {
        "synonym": None,# synonym
        "name": "Argiope", # name
        "classification": {
            "kingdom": "Animal", # kingdom_label
            "family": "Orb-weaver spider", # family_label
            "order": "Spider", # order_label
            "phylum": "Arthropod", # phylum_label
            "genus": None,  # genus_label
            "class": "Arachnid" # class_label
        }, 
        "uri": "http://dbpedia.org/resource/Argiope_(spider)", # URI
        "label": "Argiope", # rdf-schema#label
        "description": "The genus Argiope includes rather large and spectacular spiders that often have a strikingly coloured abdomen. These spiders are distributed throughout the world. Most countries in tropical or temperate climates host one or more species that are similar in appearance. The etymology of the name is from a Greek name meaning silver-faced."
        # rdf-schema#comment
    }

    assert len(data) == 76
    assert data[0] == first_entry
    assert data[17]["name"] == "Ogdenia"
    assert data[48]["label"] == "Hydrachnidiae"
    assert data[14]["synonym"] == ["Cyrene Peckham & Peckham"]

    writeJson(data)



if __name__ == "__main__":
    test()

    
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.examples

    with open('arachnid.json') as f:
        data = json.loads(f.read())
        insert_data(data, db)
        print db.arachnid.find_one()