const searchForm = document.getElementById('searchForm');
const resultsDiv = document.getElementById('results');

searchForm.addEventListener('submit', async function(event) {
    event.preventDefault();
    const query = document.getElementById('query').value;
    const response = await fetch(`/search?query=${encodeURIComponent(query)}`);
    const results = await response.json();
    displayResults(results);
});

function displayResults(results) {
    resultsDiv.innerHTML = '';

    if (results.length === 0) {
        const noResultsMessage = document.createElement('p');
        noResultsMessage.textContent = 'No results found.';
        resultsDiv.appendChild(noResultsMessage);
    } else {
        results.forEach(function(result, index) {
            const resultDiv = document.createElement('div');
            resultDiv.classList.add('result');
        
            // Create paragraph for Document IDs
            const documentIdsParagraph = document.createElement('p');
            documentIdsParagraph.innerHTML = `<strong>Movie IDs:</strong> ${result.document_ids}`;
            resultDiv.appendChild(documentIdsParagraph);
        
            // Create paragraph for Movie Name
            const movieNameParagraph = document.createElement('p');
            movieNameParagraph.innerHTML = `<strong>Movie Name:</strong> ${result.movie_name}`;
            resultDiv.appendChild(movieNameParagraph);
        
            // Create a button to toggle subtitle visibility
            const subtitleButton = document.createElement('button');
            subtitleButton.textContent = 'Subtitles';
            resultDiv.appendChild(subtitleButton);
        
            // Create a paragraph for subtitles and hide it by default
            const subtitleParagraph = document.createElement('p');
            subtitleParagraph.innerHTML = `<strong>Subtitles:</strong> ${result.subtitle}`;
            subtitleParagraph.classList.add('subtitle'); // Add a class to the subtitle paragraph
            subtitleParagraph.classList.add('hidden'); // Initially hide the subtitle
            resultDiv.appendChild(subtitleParagraph);
        
            // Toggle subtitle visibility when the button is clicked
            subtitleButton.addEventListener('click', function() {
                subtitleParagraph.classList.toggle('hidden');
            });
        
            // Append the result div to the results container
            resultsDiv.appendChild(resultDiv);
       
        });
    }
}
