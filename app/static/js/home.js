const $ = jQuery;

function loadFile(event) {
    let blob = new Blob([event.target.files[0]], { type: "image/jpeg" });
    let fname = event.target.files[0].name;
    process(blob, fname, false);
}
  
function process(blob, fname, isDrop) {
    const image = document.getElementById("showUploadImage");
    const upload = document.getElementById("myUploadImage");
    const image_result = document.getElementById("showResultImage");
    const uploadview = document.getElementById("uploadview");
    
    // show_result_area.textContent = '';
    
    let srcBlobImg = URL.createObjectURL(blob);
    image.src = srcBlobImg;

    const data = new FormData();
    data.append("file", blob, fname);
    $.ajax({
        url: "/",
        type: "POST",
        processData: false,
        contentType: false,
        data: data,
        success: (ret) => {
            var data = ret.data
            str_src = "static/img_Detect/" + data['image_name']
            image_result.src = str_src
        },
    });
}

// drag and drop
$(document).ready(function () {
    const dropContainer = document.getElementById("dropContainer");
    const error = document.getElementById("err");
    // console.log(dropContainer)
    dropContainer.ondragover = function (e) {
        e.preventDefault();
        dropContainer.style.border = "4px dashed green";
        return false;
    };

    dropContainer.ondragleave = function (e) {
        e.preventDefault();
        dropContainer.style.border = "3px dashed #4e7efe";
        return false;
    };

    dropContainer.ondrop = function (e) {
        e.preventDefault();
        dropContainer.style.border = "3px dashed #4e7efe";
        let link = e.dataTransfer.getData("text/html");
        let dropContext = $("<div>").append(link);
        let imgURL = $(dropContext).find("img").attr("src");
        if (imgURL) {
        fetch(imgURL)
            .then((res) => res.blob())
            .then((blob) => {
            error.style.display = "none";
            let index = imgURL.lastIndexOf("/") + 1;
            let filename = imgURL.substr(index);
            let allowedName = /(\.jpg|\.jpeg|\.png|\.gif)$/i;
            if (imgURL.includes("base64")) {
                error.innerText = "⚠️ Không thể kéo ảnh này, hãy mở nó ra rồi kéo";
                error.style.display = "block";
                return;
            }
            if (!allowedName.exec(filename)) {
                error.innerText =
                "⚠️ Không thể upload file này, vui lòng upload file khác";
                error.style.display = "block";
                return;
            }
            if (!filename.includes(".")) {
                error.innerText =
                "⚠️ Không thể upload file này, vui lòng upload file khác";
                error.style.display = "block";
                return;
            }
            process(blob, filename, true);
            })
            .catch(() => {
            error.innerText =
                "⚠️ Không thể upload file này, vui lòng upload file khác";
            error.style.display = "block";
            });
        } else {
        const file = e.dataTransfer.files[0];
        const fileType = file["type"];
        const validImageTypes = ["image/gif", "image/jpeg", "image/png"];
        if (!validImageTypes.includes(fileType)) {
            error.innerText =
            "⚠️ Không thể upload file này, vui lòng upload file khác";
            error.style.display = "block";
        } else {
            error.style.display = "none";
            let blob = new Blob([file], { type: "image/jpeg" });
            let fname = file.name;
            process(blob, fname, true);
        }
        }
    };
});

