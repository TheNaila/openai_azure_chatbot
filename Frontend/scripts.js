

document.addEventListener('DOMContentLoaded', function() {

    const fileInput = document.getElementById('fileInput')
    const filesBar = document.getElementById("filesBar")
    const container = document.getElementById("container")
    
    // Update file info
    const fileInfoArr = document.createElement("div")
    fileInfoArr.style.width = "100%"
    fileInfoArr.style.display = "flex"
    fileInfoArr.style.flexDirection = "row"
    

    function updateFileInfo(files) {
        if (files.length > 0) {
            if(!filesBar.contains(fileInfoArr)){
                filesBar.insertBefore(fileInfoArr, filesBar.firstChild)
            }
            const fileInfo = document.createElement("div")
            fileInfo.innerHTML = files[0].name
            fileInfo.style.flexGrow = "1"

            container.style.flexWrap = "wrap"
            filesBar.style.width = "100%"
            fileInfoArr.appendChild(fileInfo)
        }
    }


    fileInput.addEventListener('change', (e) => {
        updateFileInfo(e.target.files);
    });
   

    //create thumbnail or filename for file and change paper clip to plus 

    // // Drag and Drop functionality
    // const dropZone = document.getElementById('drop-zone')

    // dropZone.addEventListener('dragover', (e) => {
    //     e.preventDefault();
    //     dropZone.classList.add('dragover');
    // });

    // dropZone.addEventListener('dragleave', (e) => {
    //     e.preventDefault();
    //     dropZone.classList.remove('dragover');
    // });

    // dropZone.addEventListener('drop', (e) => {
    //     e.preventDefault();
    //     dropZone.classList.remove('dragover');
    //     const files = e.dataTransfer.files;
    //     fileInput.files = files;
    // });

})