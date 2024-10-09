document.addEventListener('DOMContentLoaded', function() {
    const uploadButton = document.getElementById('uploadButton');
    const imageInput = document.getElementById('imageInput');
    uploadButton.innerHTML = '<i class="fa-solid fa-upload"></i>';
    imageInput.innerHTML = '<i class="fa-solid fa-file-import"></i>';
    const ctx = document.getElementById('resultChart').getContext('2d');
    const predictedClassField = document.getElementById('predicted');
    const predictedConfidenceField = document.getElementById('predicted-confidence');
    const confidenceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Confidence Score',
                data: [{x: 1, y: 1}],
                backgroundColor: 'rgba(255,0,255,0.3)',
                borderColor: 'rgba(255, 255, 255, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1
                }
            }
        }
    });

    document.getElementById('uploadButton').addEventListener('click', () => {
        const imageInput = document.getElementById('imageInput');
        const preview = document.getElementById('preview');
        const responseDiv = document.getElementById('response');
        const stateField = document.getElementById('state');
        stateField.innerHTML = '<i class="fa-solid fa-spinner"></i> Loading...';
        uploadButton.innerHTML = '<i class="fa-solid fa-spinner"></i>';
    
        if (imageInput.files.length === 0) {
            alert('Please select an image to upload.');
            return;
        }
        if (imageInput.files[0].size > 10 * 1024 * 1024) {
            alert('Please upload an image smaller than 10 MB.');
            return;
        }
        if (!['image/jpeg', 'image/png'].includes(imageInput.files[0].type)) {
            alert('Please upload an image in JPEG or PNG format.');
            return;
        }
    
        const file = imageInput.files[0];
        const formData = new FormData();
        formData.append('frame', file, file.name);
    
        // Display the image preview
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.innerHTML = `<img src="${e.target.result}" alt="Image Preview">`;
        };
        reader.readAsDataURL(file);
    
        // Send the image to the server
        fetch('/post_frame/h/0.5', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            stateField.innerHTML = '<i class="fa-solid fa-check-double"></i> Done...';
            uploadButton.innerHTML = '<i class="fa-solid fa-upload"></i>';
            updateChart(data);
            predictedClassField.innerText = "Predicted Class: " + data[0]['class'];
            let confidence = data[0]['confidence'] * 100;
            predictedConfidenceField.innerText = "Confidence: " + confidence.toFixed(2) + "%";
            // responseDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;

        })
        .catch(error => {
            console.error('Error:', error);
            responseDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        });
    });

    function updateChart(predictions) {
        confidenceChart.data.labels = predictions.map(prediction => prediction['class']);
        confidenceChart.data.datasets[0].data = predictions.map(prediction => prediction['confidence']);
        confidenceChart.update();
        for (let i = 0; i < predictions.length; i++) {
            drawBoxes(predictions[i]['boxes']);
        }
    }

    function drawBoxes(boxes) {
        const preview = document.getElementById('previewCanvas');
        const ctx = preview.getContext('2d');
        ctx.clearRect(0, 0, preview.width, preview.height);
        ctx.lineWidth = 2;
        ctx.strokeStyle = 'red';
        ctx.font = '16px Arial';
        for (let box of boxes) {
            ctx.strokeRect(box['left'], box['top'], box['width'], box['height']);
            ctx.fillStyle = 'red';
            ctx.fillText(box['class'], box['left'], box['top'] > 10 ? box['top'] - 5 : 10);
        }
    }
});