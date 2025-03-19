from flask import Flask, request, jsonify
import json 
from flask_cors import CORS
from datetime import datetime 
import uuid #package for creating parent ids

app = Flask(__name__)
CORS(app)  # Allow frontend requests

#global variable storing all data 
DATA = "user-text.json"

#function for reading data (entries only) 
#because tag_dict is not reacted from the front end, only created in the back end (in this file) 
#we only want to send and request entries
def read_data():
    try: 
        with open(DATA, "r") as file: 
            data = json.load(file)  
            return data.get("entries", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

#function for writing data 
#at this stage we build/update the tag_dict 
def write_data(entries): 
    data = {
        "entries": entries, 
        "tag_dict": build_tag_dict(entries)
    }
    with open(DATA, "w") as file: 
        json.dump(data, file, indent=4)

#connecting to front end react
@app.route("/get-data", methods=["GET"])
def get_data(): 
    #get data, returns input before splitting between entries and tags and writing into the json
    try: 
        with open(DATA, "r") as file: 
            data = json.load(file) 
            return jsonify(data), 200
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({"entries":[], "tag_dict": {}}), 200

@app.route('/submit', methods=['POST'])
#function for getting user text input 
def submit_entry():
    data = request.json
    #get elements of the user input or return empty string 
    text = data.get("text", "")
    title = data.get("title", "")
    tags = data.get("tags",[]) #set as an empty list if user enters nothing 
    parent_id = data.get('parent_id', None) #set as None if it is not a reply 

    #double checking back end to make sure it received input 
    if not title or not text: 
        return jsonify({"error": "no text or title was sent"}), 400 

    # tags optional to add, converting input which takes a string into a list for storage
    if tags:
        tags_list = tags.split(",")
        temp = []
        for i in tags_list:
            temp.append(i.strip())
        tags_list = temp
    else: 
        tags_list = []

    #initalize a new json entry object 
    #id points to the unique id of each post 
    #parent_id identifies traces of replies, but some entries may not have a parent id 
    new_entry = {
        "title": title, 
        "text": text,
        "tags": tags_list, 
        "timestamp": datetime.now().isoformat(),  #create a timestamp when submitted
        'id': str(uuid.uuid4()), #creating unique ID
        'parent_id': parent_id
    }
    stored_data = read_data()
    #add the user input to the json file 
    stored_data.append(new_entry)
    write_data(stored_data)

    #display feedback that user entered 
    return jsonify({"message": "Entry saved."}), 200

#creating a dictionary to map each tag to unique IDs that contain them
def build_tag_dict(entries):
    tag_dict = {}
    #iterate through each entry and map tags into the dict, do nothing when 
    #user enters no tags 
    for entry in entries: 
        for tag in entry.get("tags", []): 
            if tag not in tag_dict: 
                tag_dict[tag] = [] #creeate a new list when a new tag appears
            tag_dict[tag].append(entry["id"])

    return tag_dict


if __name__ == '__main__':
    app.run(debug=True, port=5050)