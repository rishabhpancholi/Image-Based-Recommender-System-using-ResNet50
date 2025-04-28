document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const imageInput = document.getElementById('imageInput');
    const results = document.getElementById('results');
    const errorMessage = document.getElementById('errorMessage');

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!imageInput.files[0]) {
            errorMessage.textContent = 'Please select an image';
            errorMessage.style.display = 'block';
            return;
        }

        const formData = new FormData();
        formData.append('file', imageInput.files[0]);

        try {
            results.innerHTML = '';

            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // Fetch fashion.csv data
            const fashionResponse = await fetch('/static/fashion.csv');
            const fashionText = await fashionResponse.text();
            const fashionData = parseCSV(fashionText);

            // Create a map of image filenames to product data
            const productMap = new Map();
            fashionData.forEach(row => {
                productMap.set(row.Image, row);
            });

            // Display results
            data.similar_images.slice(0,6).forEach(imagePath => {
                const productInfo = productMap.get(imagePath);

                let imagesHTML = `<div class = "col-md-3 mb-4">
                                     <div class="image-card">
                                        <img src="${productInfo.ImageURL}" alt="Similar image">
                                        <div class = "product-info">
                                          <h5 class="image-title">${productInfo.ProductTitle.toUpperCase()}</h5>
                                        </div>
                                   </div>
                                  </div>`;

                results.innerHTML+=imagesHTML;
            });

        } catch (error) {
            errorMessage.textContent = error.message || 'An error occurred';
            errorMessage.style.display = 'block';
        }
    });
});

// Helper function to parse CSV
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