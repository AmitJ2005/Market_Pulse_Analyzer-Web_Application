// Assuming dailyLabels and dailyData are arrays with corresponding indices
var filteredLabels = [];
var filteredData = [];

for (var i = 0; i < dailyData.length; i++) {
    if (dailyData[i] !== null && dailyData[i] !== undefined && dailyData[i] !== '') {
        filteredLabels.push(dailyLabels[i]);
        filteredData.push(dailyData[i]);
    }
}
var buttons = document.querySelectorAll('#timeRangeSelector .btn');
buttons.forEach(function(button) {
    button.addEventListener('click', function() {
        // Remove 'selected' class from all buttons
        buttons.forEach(function(btn) {
            btn.classList.remove('selected');
        });

        // Add 'selected' class to the clicked button
        this.classList.add('selected');
    });
});
// First Visualization: Line Chart
var dailyCtx = document.getElementById('dailyChart').getContext('2d');
var dailyChart = new Chart(dailyCtx, {
    type: 'line',
    data: {
        labels: filteredLabels, // Use filteredLabels here
        datasets: [{
            label: 'Data',
            data: filteredData, // Use filteredData here
            borderColor: 'blue',
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
                type: 'category',
                time: {
                    unit: 'day',
                    displayFormats: {
                        day: 'MMM D' // Display format for days
                    }
                },
                bounds: 'data',
                distribution: 'series',
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
        },
        plugins: {
            tooltip: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(context) {
                        var label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += '₹' + context.parsed.y.toFixed(1);
                        }
                        return label;
                    }
                }
            },
            legend: {
                display: false // Disable legend
            }
        }
    }
});

// Function to filter data for a specific date range
function filterDataForDateRange(startDate, endDate) {
    var newData = [];
    var newLabels = [];

    // Loop through the data to find points within the specified date range
    for (var i = 0; i < dailyLabels.length; i++) {
        var labelDate = new Date(dailyLabels[i]);
        if (isNaN(labelDate)) {
            console.log('Invalid date:', dailyLabels[i]);
        } else if (labelDate >= startDate && labelDate <= endDate && dailyData[i] !== null && dailyData[i] !== undefined && dailyData[i] !== '') {
            newLabels.push(dailyLabels[i]);
            newData.push(dailyData[i]);
        }
    }

    console.log('Filtered data:', newData);
    console.log('Filtered labels:', newLabels);

    return {
        newData: newData,
        newLabels: newLabels
    };
}

// Function to filter out dates with no data
function filterOutEmptyData(data, labels) {
    var newData = [];
    var newLabels = [];

    for (var i = 0; i < data.length; i++) {
        // Check for null, undefined, NaN, and 0
        if (data[i] !== null && data[i] !== undefined && !isNaN(data[i]) && data[i] !== 0) {
            newData.push(data[i]);
            newLabels.push(labels[i]);
        }
    }

    return {
        newData: newData,
        newLabels: newLabels
    };
}

// Add event listener for time range buttons
document.getElementById('timeRangeSelector').addEventListener('click', function(event) {
    if (event.target.nodeName === "BUTTON") {
        var selectedRange = event.target.getAttribute('data-value');
        var newData = [];
        var newLabels = [];

        // Depending on the selected range, filter the data accordingly
        switch(selectedRange) {
            case 'week':
                console.log('Filtering data for the last week...');
                // Filter data for the last week
                var endDateWeek = new Date();
                var startDateWeek = new Date();
                startDateWeek.setDate(startDateWeek.getDate() - 9);
                var filteredData = filterDataForDateRange(startDateWeek, endDateWeek);
                newData = filteredData.newData;
                newLabels = filteredData.newLabels.map(label => {
                    var date = new Date(label);
                    var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                    return date.getDate().toString() + ' ' + monthNames[date.getMonth()] ; // Format the label as a day
                });
                break;

            case 'month':
                console.log('Filtering data for the last month...');
                // Filter data for the last month
                var todayMonth = new Date();
                var lastMonth = new Date(todayMonth.getFullYear(), todayMonth.getMonth() - 1, todayMonth.getDate());
                var filteredData = filterDataForDateRange(lastMonth, todayMonth);
                newData = filteredData.newData;
                newLabels = filteredData.newLabels.map(label => {
                    var date = new Date(label);
                    var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                    return date.getDate().toString() + ' ' + monthNames[date.getMonth()] ;
                });
                break;

            case '6months':
                console.log('Filtering data for the last 6 months...');
                // Filter data for the last 6 months
                var today6Months = new Date();
                var last6Months = new Date(today6Months.getFullYear(), today6Months.getMonth() - 6, today6Months.getDate());
                var filteredData = filterDataForDateRange(last6Months, today6Months);
                newData = filteredData.newData;
                newLabels = filteredData.newLabels.map(label => {
                    var date = new Date(label);
                    var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                    return date.getDate() + ' ' + monthNames[date.getMonth()] ; // Format the label as DD MMM YYYY
                });
                break;

            // Add a case for 1 year
            case 'year':
                console.log('Filtering data for the last year...');
                // Filter data for the last year
                var todayYear = new Date();
                var lastYear = new Date(todayYear.getFullYear() - 1, todayYear.getMonth(), todayYear.getDate());
                var filteredData = filterDataForDateRange(lastYear, todayYear);
                newData = filteredData.newData;
                newLabels = filteredData.newLabels.map(label => {
                    var date = new Date(label);
                    var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
                    return monthNames[date.getMonth()] + ' ' + date.getFullYear(); // Format the label as MMM YYYY
                });
                break;

            // Add a case for 3 years
            case '3years':
                console.log('Filtering data for the last 3 years...');
                // Filter data for the last 3 years
                var today3Years = new Date();
                var last3Years = new Date(today3Years.getFullYear() - 3, today3Years.getMonth(), today3Years.getDate());
                var filteredData = filterDataForDateRange(last3Years, today3Years);
                newData = filteredData.newData;
                newLabels = filteredData.newLabels.map(label => {
                    var date = new Date(label);
                    return date.getFullYear().toString(); // Format the label as MMM YYYY
                });
                break;

            // Add a case for 5 years
            case '5years':
                console.log('Filtering data for the last 5 years...');
                // Filter data for the last 5 years
                var today5Years = new Date();
                var last5Years = new Date(today5Years.getFullYear() - 5, today5Years.getMonth(), today5Years.getDate());
                var filteredData = filterDataForDateRange(last5Years, today5Years);
                newData = filteredData.newData;
                newLabels = filteredData.newLabels.map(label => {
                    var date = new Date(label);
                    return date.getFullYear().toString(); // Format the label as MMM YYYY
                });
                break;

            case 'all':
                console.log('Displaying all data...');
                // Use the original data
                newData = dailyData;
                newLabels = dailyLabels.map(label => {
                    var date = new Date(label);
                    return date.getFullYear().toString(); // Format the label as a year
                });
                break;

            default:
                console.log('Invalid selection.');
                // Handle other cases as needed
                break;
        }

        // Filter out dates with no data
        var filteredData = filterOutEmptyData(newData, newLabels);
        newData = filteredData.newData;
        newLabels = filteredData.newLabels;

        // Update the chart with the new data and labels
        dailyChart.data.datasets[0].data = newData;
        dailyChart.data.labels = newLabels;
        dailyChart.update();
    }
});

// Trigger click event on the first button to display data for the default time range
document.getElementById('timeRangeSelector').querySelector('button').click();



// Second Visualization: Bar Chart for Monthly Data
var monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
var monthlyChart = new Chart(monthlyCtx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
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
        },
        plugins: {
            legend: {
                display: false // Remove the legend
            }
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
        },
        plugins: {
            legend: {
                display: false // Remove the legend
            }
        }
    }
});

// Fourth Visualization: Pie Chart for Yearly Data
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
        },
        plugins: {
            legend: {
                display: false // Remove the legend
            }
        }
    }
});

// Assuming `data_yearly` is your dataframe and it's an array of objects
var years = [...new Set(data_yearly.map(item => item.Year))]; // Get unique years

var yearSelect = document.getElementById('yearSelect');
years.forEach(year => {
    var option = document.createElement('option');
    option.value = year;
    option.text = year;
    yearSelect.appendChild(option);
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
