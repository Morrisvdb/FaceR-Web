document.addEventListener('DOMContentLoaded', () => {
    // Get access to the video element
    const video = document.getElementById('video');

    const ctx = document.getElementById('confidenceChart').getContext('2d');
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

    // Request access to the user's webcam
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(error => {
            console.error('Error accessing webcam: ', error);
        });

    // Function to capture a frame and send it to the server
    function sendFrame() {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(blob => {
            const formData = new FormData();
            formData.append('frame', blob, 'frame.png');

            fetch('/post_frame', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                updateChart(data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }, 'image/png');
    }

    // Function to update the chart
    function updateChart(predictions) {
        confidenceChart.data.labels = predictions.map(prediction => prediction[0]);
        confidenceChart.data.datasets[0].data = predictions.map(prediction => prediction[1]);
        confidenceChart.update();
        const predictedElement = document.getElementById('predicted');
        predictedElement.textContent = "Predicted Class: " + predictions[0][0].charAt(0).toUpperCase() + predictions[0][0].slice(1);
        const predictedConfidence = document.getElementById('predicted-confidence');
        predictedConfidence.textContent = "Confidence: " + (predictions[0][1]*100).toFixed(2) + "%";
    }


    // Capture and send a frame every 2 seconds
    setInterval(sendFrame, 2000);
});