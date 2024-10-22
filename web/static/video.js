document.addEventListener('DOMContentLoaded', () => {
    // Get access to the video element
    const video = document.getElementById('video');
    const predictedClassField = document.getElementById('predicted');
    const predictedConfidenceField = document.getElementById('predicted-confidence');
    const confidenceSlider = document.getElementById('confidenceSlider');
    const confidenceValueField = document.getElementById('confidenceValue');
    const classSelect = document.getElementById('classSelect');
    classSelect.selectedIndex = 0;
    if (confidenceSlider !== null) {
        confidenceSlider.value = 50;
        document.getElementById('confidenceSlider').addEventListener('input', (event) => {
            confidenceValueField.innerHTML = event.target.value + "%";
            confidenceValue = event.target.value;
        });
    }
    let selectedClass = null;
    let confidenceValue = 50;
    let isProcessing = false;

    // Maybe fix this for apple????
    video.setAttribute('autoplay', '');
    video.setAttribute('muted', '');
    video.setAttribute('playsinline', '');

    // Request access to the user's webcam
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
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
        if (isProcessing) {
            return;
        }
        isProcessing = true;
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(blob => {
            if (!blob) {
                console.error("Error creating blob from canvas, if it doesn't seem to be causing any issues, you can ignore this message.");
                isProcessing = false;
                return;
            }

            const formData = new FormData();
            formData.append('frame', blob, 'frame.png');

            fetch('/post_frame/l/' + confidenceValue/100, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                updateChart(data);
            })
            .catch(error => {
                console.error('Error:', error);
            })
            .finally(() => {
                isProcessing = false; // Reset the flag once processing is complete
            });
        }, 'image/png');
    }

    function updateChart(predictions) {
        clearBoxes();
        if (selectedClass) {
            passed = []
            predictions.forEach(predict => {
                if (predict['class'] === selectedClass) {
                    passed.push(predict);
                }
            });
            predictions = passed;
        }
    
        if (predictions.length === 0) {
            clearBoxes();
            return;
        }
    
        const boxCanvas = document.createElement('canvas');
        boxCanvas.id = 'boxCanvas';
        const videoRect = video.getBoundingClientRect();
        boxCanvas.width = video.videoWidth;
        boxCanvas.height = video.videoHeight;
        boxCanvas.style.position = 'absolute';
        boxCanvas.style.top = videoRect.top + 'px';
        boxCanvas.style.left = videoRect.left + 'px';
        boxCanvas.style.width = videoRect.width + 'px';
        boxCanvas.style.height = videoRect.height + 'px';
        boxCanvas.style.pointerEvents = 'none'; // Ensure the canvas does not interfere with video controls
        document.body.appendChild(boxCanvas);
        const boxContext = boxCanvas.getContext('2d');
    
        predictions.forEach(prediction => {
            if (prediction['box']) {
                const [x, y, width, height] = prediction['box'];
                boxContext.strokeStyle = 'rgba(255, 0, 0, 1)';
                boxContext.lineWidth = 2;
                boxContext.strokeRect(x, y, width, height);
                boxContext.font = '16px Arial';
                boxContext.fillStyle = 'rgba(255, 0, 0, 1)';
                boxContext.fillText(prediction['class'], x + 5, y + 15);
                boxContext.fillText(prediction['confidence'].toFixed(2), x + 5, y + 30);
            }
        });
    
        const predictedClass = predictions[0]['class'];
        const predictedConfidence = predictions[0]['confidence'] * 100;
        
        predictedClassField.innerHTML = "Predicted Class: " + predictedClass;
        predictedConfidenceField.innerHTML = "Confidence: " + predictedConfidence.toFixed(2) + "%";
    }

    function clearBoxes() { 
        const boxCanvas = document.getElementById('boxCanvas');
        if (boxCanvas) {
            boxCanvas.remove();
        }
    }


    document.getElementById('classSelect').addEventListener('change', (event) => {
        if (event.target.value === 'null') {
            selectedClass = null;
        } else {
            selectedClass = event.target.value;
            console.log(selectedClass);
        }
    });
    
    setInterval(sendFrame, (1000/30));
});