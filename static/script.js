var stocks = [];

function loadStocks() {
  fetch('/stock_names.json')
    .then(response => response.json())
    .then(data => {
      stocks = data;
    })
    .catch(error => console.error('Error loading stocks:', error));
}

function submitSelectedStock(selectedStock) {
  fetch('/submit_selected_stock', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ selectedStock: selectedStock }),
  })
    .then(response => response.json())
    .then(data => {
      console.log('Selected stock submitted successfully.');
    })
    .catch(error => console.error('Error submitting selected stock:', error));
}

function displayStockSuggestions(searchTerm) {
  var suggestionList = document.getElementById('suggestionList');
  suggestionList.innerHTML = '';

  var filteredStocks = stocks.filter(function(stock) {
    return stock.toLowerCase().includes(searchTerm);
  });

  filteredStocks.forEach(function(stock) {
    var listItem = document.createElement('li');
    listItem.textContent = stock;
    listItem.addEventListener('click', function() {
      document.getElementById('searchInput').value = stock;
      submitSelectedStock(stock);
      // suggestionList.innerHTML = '';

      // Close suggestion list after clicking
      suggestionList.classList.remove('show');
    });
    suggestionList.appendChild(listItem);
  });

  suggestionList.classList.toggle('show', searchTerm !== '');
}

document.getElementById('searchInput').addEventListener('input', function() {
  var searchTerm = this.value.toLowerCase();
  displayStockSuggestions(searchTerm);
});

document.getElementById('cancelButton').addEventListener('click', function() {
  var searchInput = document.getElementById('searchInput');
  searchInput.value = '';
  searchInput.focus();  // Keep focus after clearing
  document.getElementById('suggestionList').classList.remove('show');
});

document.getElementById('searchInput').addEventListener('focus', function() {
  // Expand the search bar when focused
  this.style.width = '350px';
});

document.getElementById('searchInput').addEventListener('blur', function() {
  // Collapse the search bar when blurred if it's empty
  if (this.value.trim() === '') {
    this.style.width = '250px';
  }
});

window.onload = loadStocks;
