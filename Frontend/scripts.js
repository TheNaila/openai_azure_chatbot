
var sessionKey = generateUniqueSession()

function generateUniqueSession(){
    const timestamp = new Date().getTime().toString(36);
    
    // Generate random values
    const randomValues = crypto.getRandomValues(new Uint8Array(16));
    let randomString = '';
    for (let i = 0; i < randomValues.length; i++) {
        randomString += randomValues[i].toString(36);
    }
    
    // Combine timestamp and random values
    const sessionKey = timestamp + '-' + randomString;
    
    return sessionKey;
}

function isValidURL(string) {
    //TODO: Ensure both quotes or no quotes
    try {
        string = string.trim();

        // Remove surrounding quotes if they exist
        if (string.startsWith('"') && string.endsWith('"')) {
            string = string.slice(1, -1);
        }
        new URL(string)
        //when this function is called, queryInput has been set 
        queryInput.value = string
        return true
    } catch (_) {
        return false
    }
}

function removeSystemPrompt(str) {
    // Create a regular expression to match "system prompt:" case-insensitively
    const regex = /system prompt:/gi;
    
    // Replace the matched phrase with an empty string
    return str.replace(regex, "").trim();
}

function includesAny(str, substrings) {
    return substrings.some(substring => str.includes(substring));
}


function parseOutput(arg, convContainer){
    // encapsulate css in css class
    const outputMessageContainer = document.createElement("div")
    outputMessageContainer.style.display = 'flex'
    outputMessageContainer.style.justifyContent = "flex-start"
    outputMessageContainer.style.minHeight = "min-content"

    const outputMessage = document.createElement("div")
    outputMessage.style.minWidth = "min-content"
    outputMessage.style.borderRadius = "20px"
    outputMessage.style.padding = "10px"
    outputMessage.style.margin = "10px"
    outputMessage.style.backgroundColor = "#FB8500"
    
    if("output" in arg){
        outputMessage.innerText = arg["output"]
        outputMessageContainer.appendChild(outputMessage)
        convContainer.appendChild(outputMessageContainer)
    }else if ("status" in arg){
        outputMessage.innerText = arg["status"]
        outputMessageContainer.appendChild(outputMessage)
        convContainer.appendChild(outputMessageContainer)
    }
}

/*
Create session key, store and send to backend with the text submitted through the form 
perform the POST request when button clicked 
On the backend, store all the incoming information and send it back/print it
On the frontend store the the recieved messages
*/


document.addEventListener('DOMContentLoaded', function() {
    const submitButton = document.getElementById("queryButton")
    const queryInput = document.getElementById("queryInput")

    //make content scrollable
    const convContainer = document.getElementById("convContainer")
    convContainer.style.padding = "10px"

   
    submitButton.addEventListener("click", (e) => {
        const containsPrompt = queryInput.value.toString().toLowerCase()
        
        const key = isValidURL(queryInput.value) ? "contentFile" : "query"
        const payload = {
            sessionKey: "lxt6md89-phase2" //generateUniqueSession(),   //CHANGE
        }
        //lxt6md89-phase2
        //make more comprehensive
        if (includesAny(containsPrompt, ["system prompt:", "system prompt :", " system prompt:", "systemprompt:"])){
            res = removeSystemPrompt(queryInput.value)
            payload["systemPrompt"] = res

            const sentMessageContainer = document.createElement("div")
            sentMessageContainer.style.display = 'flex'
            sentMessageContainer.style.justifyContent = "flex-end"
            sentMessageContainer.style.minHeight = "min-content"

            const message = document.createElement("div")
            message.style.minWidth = "min-content"
            message.style.borderRadius = "20px"
            message.style.padding = "10px"
            message.style.margin = "10px"
            message.style.backgroundColor = "#219EBC"
            message.innerText = res
            sentMessageContainer.appendChild(message)
            convContainer.appendChild(sentMessageContainer)
        }else{
            payload[key] = queryInput.value
            
            const sentMessageContainer = document.createElement("div")
            sentMessageContainer.style.display = 'flex'
            sentMessageContainer.style.justifyContent = "flex-end"
            sentMessageContainer.style.minHeight = "min-content"

            const message = document.createElement("div")
            message.style.minWidth = "min-content"
            message.style.borderRadius = "20px"
            message.style.padding = "10px"
            message.style.margin = "10px"
            message.style.backgroundColor = "#219EBC"
            message.innerHTML = queryInput.value
            sentMessageContainer.appendChild(message)
            convContainer.appendChild(sentMessageContainer)
        }
        //send warning that theres no prompt
        fetch('http://localhost:8000', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => console.log(parseOutput(data, convContainer)))
        .catch(error => console.error('Error:', error));

        queryInput.value = ""
       
    })
})

// document.addEventListener('DOMContentLoaded', function() {

//     const fileInput = document.getElementById('fileInput')
//     const filesBar = document.getElementById("filesBar")
//     const container = document.getElementById("container")
    
//     // Update file info
//     const fileInfoArr = document.createElement("div")
//     fileInfoArr.style.width = "100%"
//     fileInfoArr.style.display = "flex"
//     fileInfoArr.style.flexDirection = "row"
    
//     var file_result = ''

//     function updateFileInfo(files) {
//         if (files.length > 0 && fileInfoArr.children.length < 2) {
//             if(!filesBar.contains(fileInfoArr)){
//                 filesBar.insertBefore(fileInfoArr, filesBar.firstChild)
//             }
//             const fileInfo = document.createElement("div")
//             fileInfo.innerHTML = files[0].name
//             fileInfo.style.flexGrow = "1"

//             container.style.flexWrap = "wrap"
//             filesBar.style.width = "100%"
//             fileInfoArr.appendChild(fileInfo)

//             file_result = files[0].name

//             const reader = new FileReader();
//                 reader.onload = function() {
//                     file_result = reader.result;
//                     console.log(file_result)
//                 };
//                 reader.readAsText(files[0]);

//         }
//         else if(fileInfoArr.children.length == 2){
//             alert("You've reached file limit")
//         }
//     }

//     fileInput.addEventListener('change', (e) => {
//         updateFileInfo(e.target.files);
//     });

//     console.log(file_result)
// })