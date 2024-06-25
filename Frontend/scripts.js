
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
    // // encapsulate css in css class
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
    return arg
}

async function updateFileInfo(files) {
    const filesBar = document.getElementById("filesBar")
    const container = document.getElementById("container")
    
    // Update file info
    const fileInfoArr = document.createElement("div")
    fileInfoArr.style.width = "100%"
    fileInfoArr.style.display = "flex"
    fileInfoArr.style.flexDirection = "row"
    fileInfoArr.id = "fileInfoArr"
    var file_result = ''

    if (files.length > 0 && fileInfoArr.children.length < 1) {
        if(!filesBar.contains(fileInfoArr)){
            filesBar.insertBefore(fileInfoArr, filesBar.firstChild)
        }
        const fileInfo = document.createElement("div")
        fileInfo.innerHTML = files[0].name
        fileInfo.style.flexGrow = "1"

        container.style.flexWrap = "wrap"
        filesBar.style.width = "100%"
        fileInfoArr.appendChild(fileInfo)

        file_result = files[0].name

        if(file_result.toString().includes(".pdf")) {
            
            const arrayBuffer = await files[0].arrayBuffer();
            const uint8Array = new Uint8Array(arrayBuffer);

            const pdf = await pdfjsLib.getDocument({ data: uint8Array }).promise;
            

            const pdfText = [];

            for (let i = 1; i <= pdf.numPages; i++) {
                const page = await pdf.getPage(i);
                const textContent = await page.getTextContent();
                const textItems = textContent.items.map(item => item.str).join(' ');
                pdfText.push(textItems);
            }

            const jsonOutput = JSON.stringify({ content: pdfText }, null, 2);
            const jsonObject = JSON.parse(jsonOutput);
            //remove file
            
            return jsonObject


        }else{

        const reader = new FileReader();
            reader.onload = function() {
                file_result = reader.result;
                return file_result
            };
            reader.readAsText(files[0]);
        }

    }
    else if(fileInfoArr.children.length == 1){
        alert("You've reached file limit")
    }
}

document.addEventListener('DOMContentLoaded', function() {

    var fileAdded = false
    var uploadedFile = null

    const submitButton = document.getElementById("queryButton")
    const queryInput = document.getElementById("queryInput")

    
    const convContainer = document.getElementById("convContainer")
    convContainer.style.padding = "10px"

    const fileInput = document.getElementById('fileInput')
    
    fileInput.addEventListener('change', async (e) => {
        uploadedFile = await updateFileInfo(e.target.files);
        fileAdded = true

    });

    submitButton.addEventListener("click", (e) => {
        const containsPrompt = queryInput.value.toString().toLowerCase()
        
        const key = isValidURL(queryInput.value) ? "contentFile" : "query"
        const payload = {
            sessionKey: "lxt6md89-phase" //generateUniqueSession(),   //CHANGE
        }
        //lxt6md89-phase2
        
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
        
        if(fileAdded) {
            payload["contentFile"] = uploadedFile["content"][0]
        }
        //else alert remove URL
        fetch('http://localhost:8000/', {
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
        if(fileAdded){
            fileInput.value = ""
            const filesBar = document.getElementById("filesBar")
            const fileInfoArr = document.getElementById("fileInfoArr")
            filesBar.removeChild(fileInfoArr)
            fileAdded = false
        }
    })
})





