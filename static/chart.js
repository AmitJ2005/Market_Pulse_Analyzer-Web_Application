// First Visualization: Line Chart
var dailyCtx = document.getElementById('dailyChart').getContext('2d');
var dailyChart = new Chart(dailyCtx, {
    type: 'line',
    data: {
        labels: dailyLabels,
        datasets: [{
            label: 'Stock Prices Over Time',
            data: dailyData,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1,
            fill: false,
            pointRadius: 0,
        }]
    },
    options: {
        animation: {
            duration: 3500,
        },
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'year',
                    tooltipFormat: 'YYYY',
                    displayFormats: {
                        year: 'YYYY'
                    }
                },
                grid: {
                    display: false
                }
            },
            y: {
                beginAtZero: false,
                position: 'right',
                grid: {
                    display: true
                }
            }
        }
    }
});

// Second Visualization: Bar Chart for Monthly Data
var monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
var monthlyChart = new Chart(monthlyCtx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'Returns',
            data: [],
            backgroundColor: []
        }]
    },
    options: {
        animation: {
            duration: 3000
        },
        scales: {
            x:{
                grid: {
                    display: false
                }
            },
        }
    }
});

document.getElementById('monthSelect').addEventListener('change', function() {
    var month = this.value;
    var filteredData = monthlyData.filter(function(item) {
        return item.Month == month;
    });
    monthlyChart.data.labels = filteredData.map(function(item) {
        return item.Year;
    });
    monthlyChart.data.datasets[0].data = filteredData.map(function(item) {
        return item.Returns;
    });
    monthlyChart.data.datasets[0].backgroundColor = filteredData.map(function(item) {
        return item.Returns >= 0 ? 'green' : 'red';
    });
    monthlyChart.update();
});
document.getElementById('monthSelect').dispatchEvent(new Event('change'));

// Third Visualization: Bar Chart for Yearly Data
var yearlyCtx = document.getElementById('yearlyChart').getContext('2d');
var yearlyChart = new Chart(yearlyCtx, {
    type: 'bar',
    data: {
        labels: yearlyData.map(function(item) { return item.Year; }),
        datasets: [{
            label: 'Returns',
            data: yearlyData.map(function(item) { return parseFloat(item.Returns); }),
            backgroundColor: yearlyData.map(function(item) { return item.Direction == 'Positive' ? 'green' : 'red'; })
        }]
    },
    options: {
        animation: {
            duration: 3000
        },
        scales: {
            x:{
                grid: {
                    display: false
                }
            },
            y: {
                beginAtZero: true
            }
        }
    }
});

// Fouth Visualization: Pie Chart for Yearly Data
var monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
];
var monthlyCtx = document.getElementById('monthlyYearChart').getContext('2d');
var monthlyYearChart = new Chart(monthlyCtx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'Returns',
            data: [],
            backgroundColor: []
        }]
    },
    options: {
        animation: {
            duration: 3000
        },
        scales: {
            x: {
                grid: {
                    display: false
                }
            },
        }
    }
});

document.getElementById('yearSelect').addEventListener('change', function() {
    var year = this.value;
    var filteredData = data_yearly.filter(function(item) {
        return item.Year == year;
    });
    var labels = filteredData.map(function(item) {
        return monthNames[item.Month - 1]; // Assuming monthNames is defined elsewhere with month names
    });
    var returns = filteredData.map(function(item) {
        return item.Returns;
    });
    var backgroundColors = filteredData.map(function(item) {
        return item.Returns >= 0 ? 'green' : 'red';
    });
    monthlyYearChart.data.labels = labels;
    monthlyYearChart.data.datasets[0].data = returns;
    monthlyYearChart.data.datasets[0].backgroundColor = backgroundColors;
    monthlyYearChart.update();
});

// Trigger change event to display data for the default year
document.getElementById('yearSelect').dispatchEvent(new Event('change'));
