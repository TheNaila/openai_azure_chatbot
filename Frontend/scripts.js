

document.addEventListener('DOMContentLoaded', function() {

    const fileInput = document.getElementById('fileInput')
    const queryBar = document.getElementById("queryBar")
    
    // Update file info
    const fileInfoArr = document.createElement("div")
    fileInfoArr.style.width = "100%"


    function updateFileInfo(files) {
        if (files.length > 0) {
            if(!queryBar.contains(fileInfoArr)){
                queryBar.insertBefore(fileInfoArr, queryBar.firstChild)
            }
            const fileInfo = document.createElement("div")
            fileInfo.innerHTML = files[0].name

            queryBar.style.flexWrap = "wrap"
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