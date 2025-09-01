// ========================================
// STATS MODULE - Learning Statistics & Progress
// ========================================

const StatsModule = {
    // Module state
    state: {
        isInitialized: false,
        stats: {
            total_words: 0,
            due_count: 0,
            overdue_count: 0,
            completed_reviews: 0,
            total_reviews: 0,
            average_quality: 0,
            streak_days: 0,
            last_review_date: null
        },
        upcomingReviews: [],
        dailyCounts: []
    },
    
    // Initialize the stats module
    init() {
        if (this.state.isInitialized) return;
        
        console.log('📊 Initializing Stats Module...');
        
        // Initialize event listeners
        this.initializeEventListeners();
        
        // Load stats data
        this.loadStatsData();
        
        this.state.isInitialized = true;
        console.log('✅ Stats Module initialized');
    },
    
    // Initialize event listeners
    initializeEventListeners() {
        // Global event delegation for stats actions
        DOM.on(document, 'click', (e) => this.handleGlobalClick(e));
    },
    
    // Load stats data from backend
    async loadStatsData() {
        try {
            console.log('📊 Loading stats data...');
            
            if (typeof API !== 'undefined') {
                // Load main stats
                const statsResponse = await API.get('/api/sr/stats');
                if (statsResponse) {
                    this.state.stats = {
                        total_words: statsResponse.total_words || 0,
                        due_count: statsResponse.due_count || 0,
                        overdue_count: statsResponse.overdue_count || 0,
                        completed_reviews: statsResponse.completed_reviews || 0,
                        total_reviews: statsResponse.total_reviews || 0,
                        average_quality: statsResponse.average_quality || 0,
                        streak_days: statsResponse.streak_days || 0,
                        last_review_date: statsResponse.last_review_date || null
                    };
                }
                
                // Load upcoming reviews
                const upcomingResponse = await API.get('/api/sr/daily-upcoming?days=7');
                if (upcomingResponse.daily_counts) {
                    this.state.dailyCounts = upcomingResponse.daily_counts;
                }
                
            } else {
                console.warn('⚠️ API module not available');
                // Use sample data for development
                this.loadSampleData();
            }
            
            this.renderStats();
            
        } catch (error) {
            console.error('❌ Failed to load stats data:', error);
            this.showError('Failed to load statistics');
        }
    },
    
    // Load sample data for development
    loadSampleData() {
        this.state.stats = {
            total_words: 25,
            due_count: 8,
            overdue_count: 2,
            completed_reviews: 45,
            total_reviews: 67,
            average_quality: 2.3,
            streak_days: 7,
            last_review_date: '2024-01-15'
        };
        
        this.state.dailyCounts = [
            { date: '2024-01-15', count: 5 },
            { date: '2024-01-16', count: 3 },
            { date: '2024-01-17', count: 7 },
            { date: '2024-01-18', count: 2 },
            { date: '2024-01-19', count: 4 },
            { date: '2024-01-20', count: 6 },
            { date: '2024-01-21', count: 1 }
        ];
    },
    
    // Render statistics
    renderStats() {
        this.renderOverviewCards();
        this.renderDetailedStats();
        this.renderUpcomingSchedule();
    },
    
    // Render overview cards
    renderOverviewCards() {
        const statsOverview = DOM.get('#statsOverview');
        if (!statsOverview) return;
        
        statsOverview.innerHTML = `
            <div class="overview-cards">
                <div class="overview-card">
                    <div class="overview-number">${this.state.stats.total_words}</div>
                    <div class="overview-label">Total Words</div>
                </div>
                <div class="overview-card">
                    <div class="overview-number">${this.state.stats.due_count}</div>
                    <div class="overview-label">Due Today</div>
                </div>
                <div class="overview-card">
                    <div class="overview-number">${this.state.stats.completed_reviews}</div>
                    <div class="overview-label">Reviews Done</div>
                </div>
                <div class="overview-card">
                    <div class="overview-number">${this.state.stats.streak_days}</div>
                    <div class="overview-label">Day Streak</div>
                </div>
            </div>
        `;
    },
    
    // Render detailed statistics
    renderDetailedStats() {
        const metricsGrid = DOM.get('#metricsGrid');
        if (!metricsGrid) return;
        
        metricsGrid.innerHTML = `
            <div class="metric-item">
                <div class="metric-value">${this.state.stats.average_quality.toFixed(1)}</div>
                <div class="metric-label">Avg Quality</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${this.state.stats.total_reviews}</div>
                <div class="metric-label">Total Reviews</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${this.state.stats.overdue_count}</div>
                <div class="metric-label">Overdue</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${this.calculateRetentionRate()}%</div>
                <div class="metric-label">Retention</div>
            </div>
        `;
    },
    
    // Render upcoming schedule
    renderUpcomingSchedule() {
        const statsDetails = DOM.get('.stats-details');
        if (!statsDetails) return;
        
        // Find the forecast grid section
        let forecastSection = statsDetails.querySelector('.forecast-grid');
        if (!forecastSection) {
            // Create forecast section if it doesn't exist
            const statsRow = statsDetails.querySelector('.stats-row');
            if (statsRow) {
                const forecastSectionContainer = DOM.create('div', { className: 'stats-section full-width' });
                forecastSectionContainer.innerHTML = `
                    <h3>📅 Upcoming Reviews (7 Days)</h3>
                    <div class="forecast-grid"></div>
                `;
                statsRow.appendChild(forecastSectionContainer);
                forecastSection = forecastSectionContainer.querySelector('.forecast-grid');
            }
        }
        
        if (forecastSection) {
            this.renderForecastGrid(forecastSection);
        }
    },
    
    // Render forecast grid
    renderForecastGrid(container) {
        if (!container) return;
        
        const today = new Date();
        const forecastHTML = this.state.dailyCounts.map((dayData, index) => {
            const date = new Date(dayData.date);
            const isToday = this.isSameDay(date, today);
            const isTomorrow = this.isSameDay(date, new Date(today.getTime() + 24 * 60 * 60 * 1000));
            
            let className = 'forecast-day';
            if (isToday) className += ' today';
            else if (isTomorrow) className += ' tomorrow';
            else className += ' future';
            
            return `
                <div class="${className}">
                    <div class="forecast-date">${this.formatDate(date)}</div>
                    <div class="forecast-count ${isToday ? 'today' : isTomorrow ? 'tomorrow' : 'future'}">
                        ${dayData.count}
                    </div>
                    <div class="forecast-label ${isToday ? 'today' : isTomorrow ? 'tomorrow' : 'future'}">
                        ${isToday ? 'Today' : isTomorrow ? 'Tomorrow' : this.getDayName(date)}
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = forecastHTML;
    },
    
    // Helper function to check if two dates are the same day
    isSameDay(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    },
    
    // Format date for display
    formatDate(date) {
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric' 
        });
    },
    
    // Get day name
    getDayName(date) {
        return date.toLocaleDateString('en-US', { weekday: 'short' });
    },
    
    // Calculate retention rate
    calculateRetentionRate() {
        if (this.state.stats.total_reviews === 0) return 0;
        
        const goodReviews = Math.floor(this.state.stats.average_quality * this.state.stats.total_reviews);
        const retentionRate = (goodReviews / this.state.stats.total_reviews) * 100;
        
        return Math.round(retentionRate);
    },
    
    // Handle global click events
    handleGlobalClick(e) {
        const action = e.target.dataset.action;
        
        if (!action) return;
        
        switch (action) {
            case 'refresh-stats':
                this.refreshStats();
                break;
            case 'export-stats':
                this.exportStats();
                break;
        }
    },
    
    // Refresh statistics
    async refreshStats() {
        console.log('🔄 Refreshing statistics...');
        await this.loadStatsData();
        this.showSuccess('Statistics updated!');
    },
    
    // Export statistics
    exportStats() {
        const statsData = {
            timestamp: new Date().toISOString(),
            stats: this.state.stats,
            upcomingReviews: this.state.dailyCounts
        };
        
        const dataStr = JSON.stringify(statsData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `learning-stats-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        this.showSuccess('Statistics exported successfully!');
    },
    
    // Show error message
    showError(message) {
        if (typeof AppUtils !== 'undefined' && AppUtils.showError) {
            AppUtils.showError(message, DOM.get('.stats-container'));
        } else {
            console.error('❌ Error:', message);
        }
    },
    
    // Show success message
    showSuccess(message) {
        if (typeof AppUtils !== 'undefined' && AppUtils.showSuccess) {
            AppUtils.showSuccess(message, DOM.get('.stats-container'));
        } else {
            console.log('✅ Success:', message);
        }
    },
    
    // Get current stats
    getStats() {
        return this.state.stats;
    },
    
    // Get upcoming reviews
    getUpcomingReviews() {
        return this.state.dailyCounts;
    },
    
    // Update stats (for external use)
    updateStats(newStats) {
        this.state.stats = { ...this.state.stats, ...newStats };
        this.renderStats();
    },
    
    // Add completed review
    addCompletedReview(quality) {
        this.state.stats.completed_reviews++;
        this.state.stats.total_reviews++;
        
        // Update average quality
        const totalQuality = this.state.stats.average_quality * (this.state.stats.total_reviews - 1);
        this.state.stats.average_quality = (totalQuality + quality) / this.state.stats.total_reviews;
        
        this.renderStats();
    }
};

// Export for use in other modules
window.StatsModule = StatsModule;
