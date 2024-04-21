// Wait for the DOM to be fully loaded before executing JavaScript
document.addEventListener('DOMContentLoaded', function () {
    // Get the search form and results container element
    const searchForm = document.getElementById('searchForm');
    const resultsDiv = document.getElementById('results');

    // Add submit event listener to the search form
    searchForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent form submission
        
        const queryInput = document.getElementById('query');
        const query = queryInput.value.trim(); // Get the search query
        
        // Perform AJAX request to search endpoint
        fetch(`/search?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(results => displayResults(results))
            .catch(error => console.error('Error:', error));
    });
    
    // Function to display search results
    function displayResults(results) {
        resultsDiv.innerHTML = ''; // Clear previous results
        
        if (results.length === 0) {
            const noResultsMessage = document.createElement('p');
            noResultsMessage.textContent = 'No results found.';
            resultsDiv.appendChild(noResultsMessage);
        } else {
            results.forEach(function (result) {
                const resultDiv = document.createElement('div');
                resultDiv.classList.add('result');

                // Create a clickable movie name
                const movieNameLink = document.createElement('a');
                movieNameLink.textContent = result.movie_name;
                movieNameLink.href = '#'; // Set href to '#' to prevent page reload
                movieNameLink.addEventListener('click', function (event) {
                    event.preventDefault(); // Prevent page reload
                    // Toggle subtitle visibility for this result
                    const subtitleParagraph = resultDiv.querySelector('.subtitle');
                    subtitleParagraph.classList.toggle('hidden');
                });
                resultDiv.appendChild(movieNameLink);

                // Create a paragraph for subtitles and hide it by default
                const subtitleParagraph = document.createElement('p');
                subtitleParagraph.innerHTML = `<strong>Subtitles:</strong> ${result.subtitle}`;
                subtitleParagraph.classList.add('subtitle'); // Add a class to the subtitle paragraph
                subtitleParagraph.classList.add('hidden'); // Initially hide the subtitle
                resultDiv.appendChild(subtitleParagraph);

                // Append the result div to the results container
                resultsDiv.appendChild(resultDiv);
            });
        }
    }
});
