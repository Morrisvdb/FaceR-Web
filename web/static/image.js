document.addEventListener('DOMContentLoaded', () => {
    // Get access to the video element
    const video = document.getElementById('video');

    const ctx = document.getElementById('confidenceChart').getContext('2d');
    const progressText = document.getElementById('progressText');
    const shutterButton = document.getElementById('shutterButton');
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
            video.onloadedmetadata = () => {
                video.play();
            };
        })
        .catch(error => {
            console.error('Error accessing webcam: ', error);
        });

    // Function to capture a frame and send it to the server
    function sendFrame() {
        // Pause the video feed
        video.pause();
        progressText.innerHTML = '<i class="fa-solid fa-spinner"></i> Loading...';
        shutterButton.innerHTML = '<i class="fa-solid fa-trash"></i>';

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
                updateChart(data);
                console.log('Success:', data);
                // const time = data.pop();
                // console.log('Last item:', lastItem);
                progressText.innerHTML = '<i class="fa-solid fa-check-double"></i> Done!';
            })
            .catch(error => {
                console.error('Error:', error);
                // Resume the video feed in case of error
                video.play();
            });
        }, 'image/png');
    }

    function clear() {
        confidenceChart.data.labels = [];
        confidenceChart.data.datasets[0].data = [];
        confidenceChart.update();
        const boxCanvas = document.getElementById('boxCanvas');
        if (boxCanvas) {
            boxCanvas.remove();
        }
        progressText.innerHTML = '<i class="fa-solid fa-check"></i> Ready...';
        shutterButton.innerHTML = '<i class="fa-solid fa-camera"></i>';
        video.play();
    }

    function updateChart(predictions) {
        confidenceChart.data.labels = predictions.map(prediction => prediction['class']);
        confidenceChart.data.datasets[0].data = predictions.map(prediction => prediction['confidence']);
        confidenceChart.update();
        const canvas = document.createElement('canvas', {id: 'chartCanvas'});
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const boxCanvas = document.createElement('canvas');
        boxCanvas.id = 'boxCanvas';
        boxCanvas.width = video.videoWidth;
        boxCanvas.height = video.videoHeight;
        boxCanvas.style.position = 'absolute';
        boxCanvas.style.top = video.offsetTop + 'px';
        boxCanvas.style.left = video.offsetLeft + 'px';
        document.body.appendChild(boxCanvas);
        const boxContext = boxCanvas.getContext('2d');
        predictions.forEach(prediction => {
            console.log(prediction['confidence']);
            const [x, y, width, height] = prediction['box'];
            boxContext.strokeStyle = 'rgba(255, 0, 0, 1)';
            boxContext.lineWidth = 2;
            boxContext.strokeRect(x, y, width, height);
            boxContext.font = '16px Arial';
            boxContext.fillStyle = 'rgba(255, 0, 0, 1)';
            boxContext.fillText(prediction['class'], x+5, y + 15);
            boxContext.fillText(prediction['confidence'].toFixed(2), x+5,y + 30);
        });

    }

    // Add an event listener to the button
    document.getElementById('shutterButton').addEventListener('click', 
        function() {
            if (video.paused) {
                clear();
            }
            else {
                sendFrame();
            }
        }
    );

    clear();
});