let progressImg = document.getElementById("progress-img");
let input = document.getElementById("url-input");

function saveBlob(blob, fileName) {
    var a = document.createElement("a");
    a.style = "display: none";
    var url = window.URL.createObjectURL(blob);
    a.href = url;
    a.download = fileName;
    a.click();
    window.URL.revokeObjectURL(url);
};

let filename = '';

document.getElementById("download-btn").addEventListener("click", ()=>{
    progressImg.src = "static/img/progress-bar.gif";
    progressImg.classList.remove("hidden");

    fetch("/download",
        {
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            method: "POST",
            body: JSON.stringify({url: input.value})
        })
        .then(res => {
            const header = res.headers.get('Content-Disposition');
            const parts = header.split(';');
            filename = parts[1].split('=')[1];
            filename = filename.replace(/\./g,' ')
            return res.blob()
        })
        .then(blob => {
            progressImg.classList.add("hidden");
            saveBlob(blob, filename);
        })
        .catch(function(res){
            progressImg.classList.add("hidden");
        });


});