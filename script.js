document.addEventListener('DOMContentLoaded', function() {
    // Constants
    const categories = [
        "All Deals",  // New category added first
        "Computers and Tablets",
        "TVs and Home Theater",
        "Audio & Headphones",
        "Appliances",
        "Smart Home and Wifi",
        "Cell Phones",
        "Video Games"
    ];

    // DOM Elements
    const pageTitle = document.getElementById('page-title');
    const nav = document.getElementById('category-nav');
    const dealsContainer = document.getElementById('deals-container');
    const mobileToggle = document.querySelector('.mobile-menu-toggle');

    // State
    const urlParams = new URLSearchParams(window.location.search);
    let currentCategory = urlParams.get('category') || categories[0];

    const filterBtn = document.getElementById('filter-btn');
    const filterDropdown = document.getElementById('filter-dropdown');
    


    // Initialize
    
    updatePageTitle();
    createNavButtons();
    setupMobileMenu();
    setupFilters(); // Add this line
    loadDeals();
    setupSearch();

    // Functions
    function updatePageTitle() {
        if (currentCategory === 'All Deals'){
            pageTitle.textContent = `Best Buy ${currentCategory}`;
        }
        else {
            pageTitle.textContent = `Best Buy ${currentCategory} Deals`;
        }
        
    }

    function createNavButtons() {
        nav.innerHTML = '';
        
        categories.forEach(cat => {
            const button = document.createElement('button');
            button.textContent = cat;
            button.classList.toggle('active', cat === currentCategory);
            
            button.addEventListener('click', () => {
                currentCategory = cat;
                window.location.search = `?category=${encodeURIComponent(cat)}`;
            });
            
            nav.appendChild(button);
        });
    }

    function setupMobileMenu() {
        mobileToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            nav.classList.toggle('active');
        });

        document.addEventListener('click', () => {
            nav.classList.remove('active');
        });

        nav.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    async function loadDeals() {
        showLoading();
        
        try {
            if (currentCategory === "All Deals") {
                const allDeals = await loadAllDeals();
                // Ensure we're passing the deals array to displayDeals
                displayDeals(allDeals.deals || []);
                updateLastUpdated(allDeals.last_updated);
            } else {
                const filename = currentCategory.toLowerCase()
                    .replace(/\s+/g, '_')
                    .replace(/&/g, 'and');
                
                const response = await fetch(`${filename}.json`);
                if (!response.ok) throw new Error('Failed to load deals');
                
                const data = await response.json();
                displayDeals(data.deals || []);
                updateLastUpdated(data.last_updated);
            }
        } catch (error) {
            console.error('Error:', error);
            showError('Failed to load deals. Please try another category.');
        }
    }
    
    // Updated loadAllDeals function
    async function loadAllDeals() {
        try {
            // Get all category files except "All Deals"
            const categoryFiles = categories
                .filter(cat => cat !== "All Deals")
                .map(cat => 
                    cat.toLowerCase()
                       .replace(/\s+/g, '_')
                       .replace(/&/g, 'and') + '.json'
                );
            
            // Fetch all category files in parallel
            const responses = await Promise.all(
                categoryFiles.map(file => fetch(file).then(res => {
                    if (!res.ok) throw new Error(`Failed to load ${file}`);
                    return res.json();
                })
            ));
            
            // Combine all deals into one array
            const allDeals = {
                last_updated: new Date().toISOString(),
                deals: responses.flatMap(data => data.deals || [])
            };
            
            console.log("Combined all deals:", allDeals); // Debug log
            return allDeals;
            
        } catch (error) {
            console.error('Error loading all deals:', error);
            // Return empty structure if there's an error
            return {
                last_updated: new Date().toISOString(),
                deals: []
            };
        }
    }
    function setupFilters() {
        if (!filterBtn || !filterDropdown) return;
        
        // Toggle dropdown
        filterBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            filterDropdown.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            filterDropdown.classList.remove('active');
        });
        
        // Prevent dropdown from closing when clicking inside
        filterDropdown.addEventListener('click', (e) => {
            e.stopPropagation();
        });
        
        // Handle filter selection
        filterDropdown.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => {
                const sortMethod = btn.dataset.sort;
                sortDeals(sortMethod);
                filterDropdown.classList.remove('active');
                filterBtn.textContent = `Sort: ${btn.textContent} ▼`;
                filterBtn.classList.add('active');
            });
        });
    }
    
    // Enhanced sorting function using pre-calculated priority scores
    function sortDeals(sortMethod) {
        const container = document.getElementById('deals-container');
        if (!container) return;
        
        const dealCards = Array.from(container.querySelectorAll('.deal-card'));
        if (dealCards.length === 0) return;
        
        // Sort based on selected method
        dealCards.sort((a, b) => {
            try {
                const aData = JSON.parse(a.dataset.deal);
                const bData = JSON.parse(b.dataset.deal);
                
                // Handle each sort method specifically
                switch(sortMethod) {
                    case 'priority':
                        return (bData.priority_score || 0) - (aData.priority_score || 0);
                    
                    case 'savings':
                        // Sort by absolute savings amount (dollars saved)
                        return (bData.savings || 0) - (aData.savings || 0);
                    
                    case 'discount':
                        // Sort by discount percentage
                        return (bData.discount_percent || 0) - (aData.discount_percent || 0);
                    
                    case 'reviews':
                        return (bData.reviews || 0) - (aData.reviews || 0);
                    
                    case 'price-low':
                        return (aData.price || 0) - (bData.price || 0);
                    
                    case 'price-high':
                        return (bData.price || 0) - (aData.price || 0);
                    
                    default:
                        return 0;
                }
            } catch (e) {
                console.error('Error sorting deals:', e);
                return 0;
            }
        });
        
        // Re-append sorted deals
        dealCards.forEach(card => container.appendChild(card));
    }

    // Add these to your existing code

// Initialize search
    function setupSearch() {
        const searchInput = document.getElementById('search-input');
        const searchBtn = document.getElementById('search-btn');
        
        if (!searchInput || !searchBtn) return;
        
        // Search on button click
        searchBtn.addEventListener('click', () => {
            applySearch(searchInput.value.trim());
        });
        
        // Search on Enter key
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                applySearch(searchInput.value.trim());
            }
        });
    }

    // Search function
    function applySearch(query) {
        if (!query) {
            // If search is empty, show all deals
            const cards = document.querySelectorAll('.deal-card');
            cards.forEach(card => card.style.display = '');
            updateVisibleDealsCount();
            return;
        }
        
        const searchTerms = query.toLowerCase().split(' ');
        const cards = document.querySelectorAll('.deal-card');
        
        // Check for price-specific queries first
        const underMatch = query.match(/under\s*(\d+)/i);
        const rangeMatch = query.match(/(\d+)\s*-\s*(\d+)/i);
        let priceQuery = null;
        
        if (underMatch) {
            priceQuery = { type: 'under', value: parseFloat(underMatch[1]) };
        } else if (rangeMatch) {
            priceQuery = { 
                type: 'range', 
                min: parseFloat(rangeMatch[1]), 
                max: parseFloat(rangeMatch[2]) 
            };
        }
        
        cards.forEach(card => {
            try {
                const dealData = JSON.parse(card.dataset.deal);
                const title = card.querySelector('h2').textContent.toLowerCase();
                const category = (card.querySelector('.category')?.textContent || '').toLowerCase();
                const price = dealData.price;
                
                // Handle price matching
                let priceMatch = false;
                if (priceQuery) {
                    if (priceQuery.type === 'under') {
                        priceMatch = price <= priceQuery.value;
                    } else if (priceQuery.type === 'range') {
                        priceMatch = price >= priceQuery.min && price <= priceQuery.max;
                    }
                }
                
                // Check if matches search terms (excluding price terms if we have a price query)
                const textMatch = searchTerms.every(term => {
                    // Skip price-related terms if we have a price query
                    if (priceQuery && (term === 'under' || term.match(/^\d+$/))) {
                        return true;
                    }
                    return title.includes(term) || category.includes(term);
                });
                
                // Show card if it matches both text and price (if price query exists)
                const shouldShow = textMatch && (!priceQuery || priceMatch);
                card.style.display = shouldShow ? '' : 'none';
            } catch (e) {
                console.error('Error processing search:', e);
                card.style.display = 'none';
            }
        });
        
        updateVisibleDealsCount();
    }

    function updateVisibleDealsCount() {
        const countElement = document.querySelector('.deal-count');
        if (!countElement) return;
        
        const visibleCount = document.querySelectorAll('.deal-card:not([style*="display: none"])').length;
        const totalCount = document.querySelectorAll('.deal-card').length;
        
        countElement.textContent = `Showing ${visibleCount} of ${totalCount} deals`;
    }


    function updateLastUpdated(timestamp) {
        const updateElement = document.getElementById('last-updated');
        if (!updateElement) return;
        
        if (!timestamp) {
            updateElement.textContent = '';
            return;
        }
        
        const updateDate = new Date(timestamp);
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZoneName: 'short'
        };
        
        updateElement.textContent = `Last updated: ${updateDate.toLocaleString('en-US', options)}`;
    }

    function displayDeals(deals) {
        if (!dealsContainer) return;
        
        dealsContainer.innerHTML = '';
        
        if (!deals || !deals.length) {
            dealsContainer.innerHTML = '<div class="no-deals">No deals found</div>';
            return;
        }
        
        // Add a count display
        const countDisplay = document.createElement('div');
        countDisplay.className = 'deal-count';
        countDisplay.textContent = `Showing ${deals.length} deals`;
        dealsContainer.appendChild(countDisplay);
        
        // Display the deals
        deals.forEach(deal => {
            // Safely extract all values with fallbacks
            const dealData = {
                title: deal.title || 'Product title not available',
                price: Number(deal.price) || 0,
                savings: Number(deal.savings) || 0,
                discount_percent: Number(deal.discount_percent) || 0,
                reviews: typeof deal.reviews === 'string' 
                    ? parseInt(deal.reviews.match(/\d+/)?.[0]) || 0 
                    : deal.reviews || 0,
                image_url: deal.image_url || '/images/placeholder.jpg',
                category: deal.category || currentCategory,
                priority_score: Number(deal.priority_score) || 0
            };
            
            const card = document.createElement('div');
            card.className = 'deal-card';
            
            // Store all deal data on the card element
            card.dataset.deal = JSON.stringify(dealData);
            
            card.innerHTML = `
                <img src="${dealData.image_url}" alt="${dealData.title}" loading="lazy">
                <h2>${dealData.title}</h2>
                <div class="price-info">
                    <p class="price">$${formatPrice(dealData.price)}</p>
                    ${dealData.savings > 0 ? `
                    <p class="savings">
                        Save $${formatPrice(dealData.savings)} (${dealData.discount_percent.toFixed(1)}%)
                    </p>
                    ` : ''}
                    <p class="reviews">${dealData.reviews} ${dealData.reviews === 1 ? 'review' : 'reviews'}</p>
                    <p class="category">${dealData.category}</p>
                </div>
            `;
            
            card.addEventListener('click', () => {
                window.open(deal.product_url || 
                    `https://www.bestbuy.com/site/searchpage.jsp?st=${encodeURIComponent(dealData.title)}`, 
                    '_blank');
            });
            
            dealsContainer.appendChild(card);
        });
        
        updateVisibleDealsCount();
    }
    function showLoading() {
            dealsContainer.innerHTML = `
                <div class="loading">
                    <div class="loading-spinner"></div>
                </div>
            `;
        }

    function showError(message) {
            dealsContainer.innerHTML = `<div class="error">${message}</div>`;
        }

    function formatPrice(price) {
            return Number(price).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }
});