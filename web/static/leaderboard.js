document.addEventListener('DOMContentLoaded', function() {

    // Initialise the chart
    const ctx = document.getElementById('leaderboardChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Score',
                data: [],
                backgroundColor: 'rgba(255, 0, 255, 0.3)',
                borderColor: 'rgba(255, 0, 255, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                },
                x: {
                    beginAtZero: true,
                    max: 5,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });


    function updateChart(data) {
        console.log(data);
        chart.data.labels = data.map(data => data['username']);
        chart.data.datasets[0].data = data.map(data => data['found_objects']);
        chart.update();
    }

    // Fetch the leaderboard data
    function fetchLeaderboard() {
        fetch('/leaderboard')
            .then(response => response.json())
            .then(data => {
                updateChart(data);
            });
    }

    fetchLeaderboard();
    // Call update every second
    setInterval(fetchLeaderboard, 1000);


});