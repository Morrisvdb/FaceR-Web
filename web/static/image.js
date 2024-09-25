document.addEventListener('DOMContentLoaded', () => {
    // Get access to the webcam stream
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();

            // Wait for the video to start playing
            video.addEventListener('loadeddata', () => {
                captureAndSendFrame(video);
            });
        })
        .catch(error => {
            console.error('Error accessing webcam:', error);
        });
});

function captureAndSendFrame(video) {
    // Create a canvas to capture the frame
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');

    // Draw the current frame from the video onto the canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert the canvas to a data URL
    const dataURL = canvas.toDataURL('image/png');

    // Send the data URL to the server
    fetch('/post_frame', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: dataURL })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function updateChart(predictions) {
    confidenceChart.data.labels = predictions.map(prediction => prediction[0]);
    confidenceChart.data.datasets[0].data = predictions.map(prediction => prediction[1]);
    confidenceChart.update();
    const predictedElement = document.getElementById('predicted');
    predictedElement.textContent = "Predicted Class: " + predictions[0][0].charAt(0).toUpperCase() + predictions[0][0].slice(1);
    const predictedConfidence = document.getElementById('predicted-confidence');
    predictedConfidence.textContent = "Confidence: " + (predictions[0][1]*100).toFixed(2) + "%";
}