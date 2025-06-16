import { useState, useEffect} from "react";
import '../css/style.css'; 

// defining state variables that update upon user interaction/input 
function TextInput() {
  const [text, setText] = useState(""); // For managing input value
  const [title, setTitle] = useState(''); //manage title
  const [tags, setTags] = useState('');  //manage tags
  const [response, setResponse] = useState(""); // For storing backend response
  const [storedData, setStoredData] = useState([]);  //managing and updating stored data 
  const [replyingTo, setReplyingTo] = useState(null); //state whether user is writing entry or replying
  const [tagIndex, setTagIndex] = useState({});   //store tag mappings in dict
  const [selectedTag, setSelectedTag] = useState(null); //button state for selecting tags 
  const [filteredEntries, setFilteredEntries] = useState([]); //state for sselecting entries associated with a tag to visualize
  
  //function that gets data from the backend app.py 
  const fetchStoredData = async () => {
    try{ 
      //first fetch the prexisting data 
      const res = await fetch("http://127.0.0.1:5050/get-data"); 
      const data = await res.json(); 
      ///log response 
      console.log("Fetched Data:", data);
      setStoredData(data.entries || []);  //load entries or return empty list if there are none
      setTagIndex(data.tag_dict || {});  //load tag mappings or return empty dict if there are none
    }
    catch (error) {
      //if this happens, backend error might be occuring 
      console.error("Cannot fetch stored data:", error); 
    }
  };

  useEffect(() => {
    fetchStoredData(); // Load stored data on component mount
  }, []);

  //function handles when user's hit submit button 
  const handleSubmit = async () => {
    //make sure they have entered at least a title and body 
    if (!title.trim() || !text.trim()){
      alert("Both title and text required"); 
      return 
    }
    //log message when user hits submit (for debugging) 
    console.log('hello sending'); 
    console.log(tags); 

    //send input to the backend function for handling submits 
    try {
      const res = await fetch("http://127.0.0.1:5050/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          title, 
          text, 
          tags,
          parent_id: replyingTo,
         }), // Sending input text
      });
  
      const data = await res.json();

      //log what was sent (for debugging) 
      console.log("Backend Response:", data); 
      setResponse(data.message);  // show the backend response

      //revert the state of everything to be ready for next input 
      setText(""); 
      setTitle(""); 
      setTags(''); 
      setReplyingTo(null); //reset reply mode 
      fetchStoredData(); 

    } catch (error) {
      console.error("Error adding entry:", error);
    }
  };
  
  //function for when user clicks reply button 
  const handleReply = (entry) => {
    console.log("Entry object:", entry); //log the parent entry (for debugging) 
    console.log("Entry ID: ", entry.id); 

    setTitle(`Re: ${entry.title}`); //update to change to user defined title
    setText(''); 
    setTags(entry.tags); 
    setReplyingTo(entry.id); //give the current reply a parent ID
  }; 

  //function for when user clicks a Tag 
  const handleTagClick = (tag) => {
    //show backend response (for debugig) 
    console.log(`highlighting entries for tag: ${tag}"`); 
    //first check that there are items in the dict
    if (tagIndex[tag]){
      // get relatedEntries by  filtering all entries by the tag
      const relatedEntries = storedData.filter((entry) => 
      tagIndex[tag].includes(entry.id)); 
      //set states
      setSelectedTag(tag);  
      setFilteredEntries(relatedEntries); 
    }
  }


  return (
    <div>
      {/* if Reply is chosen, dispay first message, else, latter */}
      <h2>{replyingTo ? "Reply to entry" : "Create new Entry"} </h2>
      <textarea
        type = 'text' 
        value = {title}
        onChange={(e)=> setTitle(e.target.value)}
        placeholder = "Title"
      />

      {/* {Body text } */}
      <textarea
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)} // Update state as user types
        placeholder="Enter text"
      />

      {/* {Tags (optional)} */}
      <textarea
        type="text"
        value={tags}
        onChange={(e) => setTags(e.target.value)}
        placeholder="Add optional tags (separated by spaces)"
      />

      <button onClick={handleSubmit}>Submit</button>
      <p>{response}</p> {/* Display backend's response */}

      {/* display unique IDs per tag that exists */}
      <h3> Tags: </h3>
      {/* iterating through the tag_dict and displaying a button for each one */}
      {Object.keys(tagIndex || {}).map((tag) => (
        <button key={tag} onClick={() => handleTagClick(tag)}>
          {tag} ({tagIndex[tag].length})
        </button>
      ))}

      {/* display the stored data  */}
      <h3>Stored Entries:</h3>
      <ul>
        {/* iterate through each item of the stored data */}
        {storedData.map((item, index) => (
          <li key={index}>
            <strong>{item.title}</strong>:{item.text} <br/>

            {/* only show tags if they exist and separated by commas */}
            {item.tags && item.tags.length > 0 && (
              <>
                <em>Tags:</em> {item.tags.join(", ")} <br/>
              </>
            )}
            {/* call handleReply function when user clicks reply button */}
            <button onClick= {() => handleReply(item)}> Reply </button>
          </li>
        ))}
      </ul>

      {/* display popup of entries for selected tag */}
      {/* display the popup if user clicks a tag button  */}
      {selectedTag && (
        <div className = 'popup'> 
          <div className='popup-content'> 
            <h3>Entries tagged: {selectedTag}</h3> 
            <ul>
              {filteredEntries.map((entry) => (
                <li key={entry.id}>
                  <strong>{entry.title}</strong>: {entry.text}
                </li>
              ))}
            </ul>
          </div> 
          <button onClick={() => setSelectedTag(null)}> X </button>

        </div>
      )}

    </div>
  );
}

export default TextInput; 