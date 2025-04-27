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
                const card = document.createElement('div');
                card.className = 'image-card';
                card.innerHTML = `
                    <img src="static/images/${imagePath}" alt="Similar image">
                    ${productInfo ? `
                        <div class="product-info">
                            <h4>${productInfo.ProductTitle}</h4>
                        </div>
                    ` : ''}
                `;
                results.appendChild(card);
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