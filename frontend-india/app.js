// Configuration
const API_BASE_URL = 'http://localhost:8001';  // India tracker on port 8001
const REFRESH_INTERVAL = 60000; // Refresh every 60 seconds
const INDIA_CITIES = ['Bangalore', 'Bengaluru', 'Hyderabad', 'Pune', 'Mumbai', 'Delhi', 'Noida', 'Gurgaon', 'Gurugram', 'Chennai', 'Kolkata', 'Ahmedabad', 'Jaipur', 'Kochi', 'Chandigarh', 'Remote'];

// Global state
let allJobs = [];
let allCompanies = [];
let currentFilter = 'all';
let stats = {};
let scraperStatus = {};
let countdownInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadAllData();
    updateLastRefreshTime();
    
    // Auto-refresh every minute
    setInterval(async () => {
        await loadAllData();
        updateLastRefreshTime();
    }, REFRESH_INTERVAL);
    
    // Update countdown every second
    startCountdownTimer();
});

// Load all data from API
async function loadAllData() {
    try {
        await Promise.all([
            loadStats(),
            loadJobs(),
            loadCompanies(),
            loadScraperStatus()
        ]);
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Failed to load data. Make sure the API server is running on port 8000.');
    }
}

// Load scraper status
async function loadScraperStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/scraper-status`);
        scraperStatus = await response.json();
        updateScraperDisplay();
    } catch (error) {
        console.error('Error loading scraper status:', error);
    }
}

// Update scraper status display
function updateScraperDisplay() {
    const lastScrapeEl = document.getElementById('lastScrape');
    const nextScrapeEl = document.getElementById('nextScrape');
    
    if (scraperStatus.last_scrape_at) {
        const lastScrapeDate = new Date(scraperStatus.last_scrape_at);
        lastScrapeEl.textContent = formatDateFull(lastScrapeDate);
    } else {
        lastScrapeEl.textContent = 'No data yet';
    }
    
    updateCountdown();
}

// Update countdown timer
function updateCountdown() {
    const nextScrapeEl = document.getElementById('nextScrape');
    
    if (!scraperStatus.next_scrape_at) {
        nextScrapeEl.textContent = 'Calculating...';
        return;
    }
    
    const nextScrapeDate = new Date(scraperStatus.next_scrape_at);
    const now = new Date();
    const diff = nextScrapeDate - now;
    
    if (diff <= 0) {
        nextScrapeEl.textContent = 'Running now...';
        nextScrapeEl.classList.add('overdue');
        nextScrapeEl.classList.remove('countdown');
        return;
    }
    
    nextScrapeEl.classList.remove('overdue');
    nextScrapeEl.classList.add('countdown');
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    if (hours > 0) {
        nextScrapeEl.textContent = `${hours}h ${minutes}m ${seconds}s`;
    } else if (minutes > 0) {
        nextScrapeEl.textContent = `${minutes}m ${seconds}s`;
    } else {
        nextScrapeEl.textContent = `${seconds}s`;
    }
}

// Start countdown timer
function startCountdownTimer() {
    // Clear any existing interval
    if (countdownInterval) {
        clearInterval(countdownInterval);
    }
    
    // Update countdown every second
    countdownInterval = setInterval(() => {
        if (scraperStatus.next_scrape_at) {
            updateCountdown();
        }
    }, 1000);
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        stats = await response.json();
        
        document.getElementById('totalJobs').textContent = stats.active_jobs || 0;
        document.getElementById('totalCompanies').textContent = Object.keys(stats.jobs_by_company || {}).length;
        document.getElementById('alertsSent').textContent = stats.alerts_sent_today || 0;
        
        // Calculate new jobs today (jobs first seen today)
        const newToday = allJobs.filter(job => isToday(job.first_seen_at)).length;
        document.getElementById('newToday').textContent = newToday;
        
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load jobs from API
async function loadJobs() {
    try {
        const response = await fetch(`${API_BASE_URL}/jobs?limit=500`);
        const data = await response.json();
        
        // Store all jobs (filtering happens in renderJobs)
        allJobs = data.jobs.map(job => ({
            ...job,
            isNew: isToday(job.first_seen_at)
        }));
        
        console.log('Loaded jobs:', allJobs.length);
        renderJobs();
    } catch (error) {
        console.error('Error loading jobs:', error);
        document.getElementById('jobsContainer').innerHTML = '<div class="no-results">❌ Error loading jobs</div>';
    }
}

// Load companies
async function loadCompanies() {
    try {
        const response = await fetch(`${API_BASE_URL}/companies`);
        const data = await response.json();
        allCompanies = data.companies || [];
        renderCompanies();
    } catch (error) {
        console.error('Error loading companies:', error);
        document.getElementById('companiesGrid').innerHTML = '<div class="no-results">❌ Error loading companies</div>';
    }
}

// Check if job is an internship
function isInternship(job) {
    const internshipKeywords = ['intern', 'internship', 'summer 2026', 'co-op', 'coop'];
    const title = (job.title || '').toLowerCase();
    const tags = (job.tags || []).map(t => t.toLowerCase());
    
    return internshipKeywords.some(keyword => 
        title.includes(keyword) || tags.some(tag => tag.includes(keyword))
    );
}

// Check if location is in India
function isIndiaLocation(location) {
    if (!location || location === 'Remote') return true; // Assume Remote is OK
    
    // Check for Indian cities
    const hasIndiaCity = INDIA_CITIES.some(city => location.includes(city));
    
    // Check for India indicators
    const hasIndiaIndicator = location.includes('India') || 
                            location.includes('IND') ||
                            location.includes('IN');
    
    // Exclude international locations
    const internationalIndicators = ['USA', 'United States', 'UK', 'London', 'Singapore', 'Dubai', 'China', 'Japan', 'Australia', 'Canada'];
    const isInternational = internationalIndicators.some(loc => location.includes(loc));
    
    return (hasIndiaCity || hasIndiaIndicator) && !isInternational;
}

// Check if date is today
function isToday(dateString) {
    if (!dateString) return false;
    const date = new Date(dateString);
    const today = new Date();
    return date.toDateString() === today.toDateString();
}

// Render jobs
function renderJobs() {
    const container = document.getElementById('jobsContainer');
    let filteredJobs = [...allJobs];
    
    // Always filter for internships first
    filteredJobs = filteredJobs.filter(job => isInternship(job));
    
    // Apply category filter
    if (currentFilter !== 'all') {
        filteredJobs = filteredJobs.filter(job => job.category === currentFilter);
    }
    
    // Apply search filter
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
    if (searchTerm) {
        filteredJobs = filteredJobs.filter(job => 
            (job.company && job.company.toLowerCase().includes(searchTerm)) ||
            (job.title && job.title.toLowerCase().includes(searchTerm)) ||
            (job.location && job.location.toLowerCase().includes(searchTerm))
        );
    }
    
    // Apply India filter
    const indiaOnly = document.getElementById('indiaOnlyFilter').checked;
    if (indiaOnly) {
        filteredJobs = filteredJobs.filter(job => isIndiaLocation(job.location));
    }
    
    // Update count
    document.getElementById('jobCount').textContent = filteredJobs.length;
    
    // Render
    if (filteredJobs.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">😕</div>
                <h3>No Internships Found</h3>
                <p>Try adjusting your filters or search terms</p>
                ${searchTerm ? `<p class="search-hint">Searching for: "<strong>${searchTerm}</strong>"</p>` : ''}
            </div>
        `;
        return;
    }
    
    container.innerHTML = filteredJobs.map(job => `
        <div class="job-card ${job.isNew ? 'new-job' : ''}">
            <div class="job-header">
                <div class="job-title-section">
                    <div class="job-company">${escapeHtml(job.company)}</div>
                    <div class="job-title">${escapeHtml(job.title)}</div>
                </div>
            </div>
            
            <div class="job-meta">
                <div class="job-meta-item">
                    📍 ${escapeHtml(job.location || 'Location not specified')}
                </div>
                ${job.remote ? '<div class="job-meta-item">🏠 Remote</div>' : ''}
                <div class="job-meta-item">
                    ⏰ ${formatDate(job.first_seen_at)}
                </div>
            </div>
            
            ${job.tags && job.tags.length > 0 ? `
                <div class="job-tags">
                    ${job.category ? `<span class="job-tag category">${formatCategory(job.category)}</span>` : ''}
                    ${job.tags.map(tag => `<span class="job-tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            ` : ''}
            
            <div class="job-actions">
                <a href="${escapeHtml(job.url)}" target="_blank" rel="noopener noreferrer" class="apply-btn">
                    Apply Now →
                </a>
            </div>
        </div>
    `).join('');
}

// Render companies
function renderCompanies() {
    const container = document.getElementById('companiesGrid');
    
    if (allCompanies.length === 0) {
        container.innerHTML = '<div class="no-results">No companies with openings yet</div>';
        return;
    }
    
    container.innerHTML = allCompanies
        .slice(0, 20) // Show top 20 companies
        .map(company => `
            <div class="company-card" onclick="searchCompany('${escapeHtml(company.name)}')">
                <div class="company-name">${escapeHtml(company.name)}</div>
                <div class="company-count">${company.job_count} ${company.job_count === 1 ? 'position' : 'positions'}</div>
            </div>
        `).join('');
}

// Filter by category
function filterByCategory(category) {
    currentFilter = category;
    
    // Update active tab
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.dataset.category === category) {
            tab.classList.add('active');
        }
    });
    
    renderJobs();
}

// Filter jobs (called on search input)
function filterJobs() {
    renderJobs();
}

// Clear search
function clearSearch() {
    document.getElementById('searchInput').value = '';
    filterJobs();
}

// Search specific company
function searchCompany(companyName) {
    console.log('Searching for company:', companyName);
    document.getElementById('searchInput').value = companyName;
    currentFilter = 'all'; // Reset category filter
    
    // Update active tab to "All Categories"
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.dataset.category === 'all') {
            tab.classList.add('active');
        }
    });
    
    filterJobs();
    
    // Scroll to jobs section
    setTimeout(() => {
        const jobsSection = document.querySelector('.jobs-container');
        if (jobsSection) {
            jobsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 100);
}

// Refresh all data
async function refreshData() {
    const btn = document.querySelector('.refresh-btn');
    btn.textContent = '🔄 Refreshing...';
    btn.disabled = true;
    
    await loadAllData();
    updateLastRefreshTime();
    
    btn.textContent = '🔄 Refresh';
    btn.disabled = false;
    
    // Show success message
    showNotification('✅ Data refreshed successfully!');
}

// Update last refresh time
function updateLastRefreshTime() {
    const now = new Date();
    document.getElementById('lastUpdate').textContent = now.toLocaleTimeString();
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    
    return date.toLocaleDateString();
}

// Format date with time for scraper status
function formatDateFull(date) {
    if (!date) return 'Unknown';
    
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffMinutes = Math.floor(diffTime / (1000 * 60));
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes} ${diffMinutes === 1 ? 'minute' : 'minutes'} ago`;
    if (diffHours < 24) return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`;
    if (diffDays < 7) return `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ago`;
    
    return date.toLocaleString();
}

// Format category name
function formatCategory(category) {
    if (!category) return 'Other';
    return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show notification
function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #2ecc71;
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Show error
function showError(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #e74c3c;
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 5000);
}

// CSS for animations (injected)
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
`;
document.head.appendChild(style);
