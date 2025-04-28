// Wait for the DOM to be fully loaded before executing the code
document.addEventListener('DOMContentLoaded', function() {
    // Get references to DOM elements
    const uploadForm = document.getElementById('uploadForm');
    const imageInput = document.getElementById('imageInput');
    const results = document.getElementById('results');
    const errorMessage = document.getElementById('errorMessage');

    // Add event listener for form submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent default form submission

        // Validate that an image has been selected
        if (!imageInput.files[0]) {
            errorMessage.textContent = 'Please select an image';
            errorMessage.style.display = 'block';
            return;
        }

        // Create FormData object for file upload
        const formData = new FormData();
        formData.append('file', imageInput.files[0]);

        try {
            // Clear previous results
            results.innerHTML = '';

            // Send POST request to upload endpoint
            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            // Handle any errors from the server
            if (data.error) {
                throw new Error(data.error);
            }

            // Fetch product data from CSV file
            const fashionResponse = await fetch('/static/fashion.csv');
            const fashionText = await fashionResponse.text();
            const fashionData = parseCSV(fashionText);

            // Create a map for quick lookup of product data by image filename
            const productMap = new Map();
            fashionData.forEach(row => {
                productMap.set(row.Image, row);
            });

            // Display recommended images with their product information
            data.similar_images.slice(0,6).forEach(imagePath => {
                const productInfo = productMap.get(imagePath);

                // Create HTML for each recommended product
                let imagesHTML = `<div class = "col-md-3 mb-4">
                                     <div class="image-card">
                                        <img src="${productInfo.ImageURL}" alt="Similar image">
                                        <div class = "product-info">
                                          <h5 class="image-title">${productInfo.ProductTitle.toUpperCase()}</h5>
                                        </div>
                                   </div>
                                  </div>`;

                results.innerHTML += imagesHTML;
            });

        } catch (error) {
            // Display error message if something goes wrong
            errorMessage.textContent = error.message || 'An error occurred';
            errorMessage.style.display = 'block';
        }
    });
});

/**
 * Parse CSV text into an array of objects
 * @param {string} text - CSV text to parse
 * @returns {Array} Array of objects representing each row in the CSV
 */
function parseCSV(text) {
    const lines = text.split('\n');
    const headers = lines[0].split(',');
    return lines.slice(1).map(line => {
        const values = line.split(',');
        const obj = {};
        headers.forEach((header, index) => {
            obj[header] = values[index];
        });
        return obj;
    });
}