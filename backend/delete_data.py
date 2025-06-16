import json 
from datetime import datetime 

def read_json(filepath): 
    try:
        with open(filepath, 'r') as f:  #this line is from StackOverflow
            return json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return 

def write_json(filepath, data): 
    try: 
        with open(filepath, 'w') as f: 
            json.dump(data, f, indent=2)
    except Exception as e: 
        print(f"Error writing json: {e}")

def delete_entry(entry_id, cascade = True): 
    print(f"Deleting entry with the ID: {entry_id}")

    #first delete from raw user-text.json
    raw_path = "user-text.json"
    raw_data = read_json(raw_path)  #entire user-text file 

    if not raw_data or 'entries' not in raw_data:
        print("[!] Invalid or missing data in user-text.json")
        return
    
    original_len = len(raw_data['entries'])

    raw_data['entries'] = [entry for entry in raw_data['entries'] if entry.get('id') != entry_id]
    print(f"Deleted from user-text.json: {original_len - len(raw_data['entries'])} entries")

    #update tag_dict
    for tag in list(raw_data['tag_dict'].keys()):
        if entry_id in raw_data['tag_dict'][tag]: #access each tag
            raw_data['tag_dict'][tag].remove(entry_id)
            if not raw_data['tag_dict'][tag]: #if the list is now empty delete the key 
                del raw_data['tag_dict'][tag]

    #save updates in user-text 
    write_json(raw_path, raw_data) 

    #then delete from content_log_cleaned 
    log_path = 'content_log_cleaned.json'
    log_data = read_json(log_path)

    try: 
        new_log_data = []
        for entry in log_data: 
            if entry.get('id') != entry_id: 
                new_log_data.append(entry) 
        log_data = new_log_data 
        write_json(log_path, log_data)
        print("Deleted from content_log_cleaned.json")

    except Exception as e: 
        print(f"Error, content_logged_cleaned.json may be malformed: {e}")
    
    # Cascade delete for handling replies of a deleted entry 
    if cascade: 
        child_ids = [entry['id'] for entry in raw_data['entries'] if entry.get('parent_id') ==entry_id]
        for child in child_ids: 
            delete_entry(child, cascade = True) #recursively delete children 

def delete_before(timestamp, cascade = True):
    ''''Delete all entries before x timestamp, takes timestamp string as input'''
    raw_path = 'user-text.json'
    raw_data = read_json(raw_path)

    if not raw_data or 'entries' not in raw_data:
        print("[!] Invalid or missing data in user-text.json")
        return

    try: 
        cutoff = datetime.fromisoformat(timestamp)
    except ValueError: 
        print("[!] Invalid timestamp format. Accepts ISO format only") 
        return
    
    ids_to_delete = []
    for entry in raw_data['entries']: 
        if datetime.fromisoformat(entry['timestamp']) < cutoff:
            ids_to_delete.append(entry)
    
    print(f"Found {len(ids_to_delete)} entries before {timestamp}. Deleting...")
    print(ids_to_delete)
    for e in ids_to_delete: 
        delete_entry(e["id"], cascade = cascade)

if __name__ == "__main__":
    delete_entry("d19bbd51-0ee0-46df-befa-a775505ade4e")
    # delete_before("2025-06-08T13:08:00.093837")
