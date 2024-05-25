// Variable to store the Typed.js instance
var typedInstance;
// Function to initialize the typing animation for the placeholder text
function initPlaceholderTyping() {
  var placeholderElement = document.getElementById('searchInput').getAttribute('placeholder');
  typedInstance = new Typed("#searchInput", {
    strings: ["Just Search... What U Want "," Reliance Industries. ", " Tata Consultancy Services. ", " HDFC Bank. ", " State Bank of India. ", " Bajaj Finance. ", " Hindustan Unilever.", " Berger Paints India. "], // Use the placeholder text as the string
    typeSpeed: 50,
    backSpeed: 45,
    loop: true,
    showCursor: false,
    backDelay: 800,
  });
}
// Call the function to initialize the typing animation
initPlaceholderTyping();

// Function to stop the typing animation
function stopTypingAnimation() {
  if (typedInstance) {
    typedInstance.destroy();
  }
}

// Function to handle input field focus
function handleInputFieldFocus() {
  // Stop the typing animation when the input field gains focus
  stopTypingAnimation();
}

// Attach event listener for input field focus
document.getElementById('searchInput').addEventListener('focus', handleInputFieldFocus);

// Function to handle input field blur
function handleInputFieldBlur() {
  // Reinitialize the typing animation when the input field loses focus
  initPlaceholderTyping();
}
// Attach event listener for input field blur
document.getElementById('searchInput').addEventListener('blur', handleInputFieldBlur);
var stocks = [];

// Function to load stock names from server
function loadStocks() {
  fetch('/stock_names.json')
    .then(response => response.json())
    .then(data => {
      stocks = Object.keys(data); // Store the loaded stock names in the array
    })
    .catch(error => console.error('Error loading stocks:', error));
}

// Function to submit selected stock to server
function submitSelectedStock(selectedStock) {
  var loader = document.getElementById('loader');
  loader.style.display = 'block'; // Display the loader

  fetch('/submit_selected_stock', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ selectedStock: selectedStock }), // Send selected stock as JSON
  })
    .then(response => response.json())
    .then(data => {
      console.log('Selected stock submitted successfully.');
      redirectToVisualizeData(); // Redirect to visualization page after successful submission
    })
    .catch(error => {
      console.error('Error submitting selected stock:', error);
    })
    .finally(() => {
      loader.style.display = 'none'; // Hide the loader after submission or error
    });
}

// Function to display stock suggestions based on user input
function displayStockSuggestions(searchTerm) {
  var suggestionList = document.getElementById('suggestionList');
  suggestionList.innerHTML = ''; // Clear previous suggestions
  // Filter stocks based on search term
  var filteredStocks = stocks.filter(function(stock) {
    // Check if the stock name or any part of it matches the search term
    return stock.toLowerCase().includes(searchTerm) ||
           stock.toLowerCase().includes(searchTerm + ' '); // Check for numbers appended after the stock name
  });
  // Create list items for filtered stocks and add click event listener
  filteredStocks.forEach(function(stock) {
    var listItem = document.createElement('li');
    listItem.textContent = stock;
    listItem.addEventListener('click', function() {
      var searchInput = document.getElementById('searchInput');
      searchInput.value = stock; // Set input value to selected stock
      stopTypingAnimation(); // Stop typing animation
      document.getElementById('searchInput').value = stock; // Set input value to selected stock
      submitSelectedStock(stock); // Submit selected stock to server
      suggestionList.classList.remove('show'); // Hide suggestion list
    });
    suggestionList.appendChild(listItem); // Add list item to suggestion list
  });
  // Show suggestion list if search term is not empty
  suggestionList.classList.toggle('show', searchTerm !== '');
}

// Function to handle cancel button click event
document.getElementById('cancelButton').addEventListener('click', function() {
  var searchInput = document.getElementById('searchInput');
  searchInput.value = ''; // Clear input value
  searchInput.focus(); // Keep focus after clearing
  document.getElementById('suggestionList').classList.remove('show'); // Hide suggestion list
});
// Function to handle input event in search input field
document.getElementById('searchInput').addEventListener('input', function() {
  var searchTerm = this.value.toLowerCase(); // Get input value and convert to lowercase
  displayStockSuggestions(searchTerm); // Display stock suggestions based on input value
});
// Function to expand search input field when focused
document.getElementById('searchInput').addEventListener('focus', function() {
  this.style.width = '350px'; // Expand input field width
});
// Function to collapse search input field when blurred if it's empty
document.getElementById('searchInput').addEventListener('blur', function() {
  if (this.value.trim() === '') {
    this.style.width = '250px'; // Collapse input field width
  }
});
// Function to redirect to visualization page
function redirectToVisualizeData() {
  window.location.replace('/visualize_data'); // Redirect to visualization page
}
// Load stocks when window is loaded
window.onload = loadStocks;


// Function to handle document click event
function handleDocumentClick(event) {
  var searchInput = document.getElementById('searchInput');
  var suggestionList = document.getElementById('suggestionList');

  // Check if the click was outside the search input and suggestion list
  if (!searchInput.contains(event.target) && !suggestionList.contains(event.target)) {
  suggestionList.classList.remove('show'); // Hide suggestion list
  searchInput.style.width = '250px'; // Collapse input field width
}
}

// Attach event listener for document click
document.addEventListener('click', handleDocumentClick);

function toggleMenu() {
  var menu = document.getElementById("menu");
  if (menu.style.display === "block") {
      menu.style.display = "none";
  } else {
      menu.style.display = "block";
  }
}

function openSupport() {
  window.open("https://www.google.com/search?q=johnny+sins&tbm=isch", "_blank");
}