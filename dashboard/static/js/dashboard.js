/**
 * QuantConnect Backtest Dashboard - Main JavaScript
 * Interactive dashboard for visualizing backtest results
 */

(function() {
    'use strict';

    // Dashboard namespace
    window.BacktestDashboard = {
        // Configuration
        config: {
            apiBaseUrl: '/api',
            refreshInterval: 30000, // 30 seconds
            chartColors: {
                primary: '#007bff',
                success: '#28a745',
                warning: '#ffc107',
                danger: '#dc3545',
                info: '#17a2b8',
                light: '#f8f9fa',
                dark: '#343a40'
            }
        },

        // State management
        state: {
            currentProject: null,
            currentData: null,
            refreshTimer: null,
            isInitialized: false
        },

        // Initialize dashboard
        init: function() {
            console.log('📊 Initializing Backtest Dashboard...');
            this.setupEventListeners();
            this.loadInitialData();
            this.startAutoRefresh();
            this.state.isInitialized = true;
            console.log('✅ Dashboard initialized successfully');
        },

        // Setup event listeners
        setupEventListeners: function() {
            // Refresh button
            const refreshBtn = document.getElementById('refreshData');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', () => this.refreshData());
            }

            // Project selection
            document.addEventListener('click', (e) => {
                if (e.target.matches('[data-project]')) {
                    const project = e.target.getAttribute('data-project');
                    this.loadProject(project);
                }
            });

            // Chart interactions
            document.addEventListener('plotly_hover', this.handleChartHover.bind(this));
            document.addEventListener('plotly_unhover', this.handleChartUnhover.bind(this));

            // Window resize
            window.addEventListener('resize', this.debounce(() => {
                this.resizeCharts();
            }, 250));

            // Keyboard shortcuts
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey || e.metaKey) {
                    switch(e.key) {
                        case 'r':
                            e.preventDefault();
                            this.refreshData();
                            break;
                        case 'e':
                            e.preventDefault();
                            this.exportData();
                            break;
                    }
                }
            });
        },

        // Load initial data
        loadInitialData: function() {
            this.showLoading(true);
            this.apiCall('/projects')
                .then(data => {
                    this.updateProjectList(data);
                    this.loadDefaultProject();
                })
                .catch(error => {
                    console.error('Error loading initial data:', error);
                    this.showError('Failed to load project data');
                })
                .finally(() => {
                    this.showLoading(false);
                });
        },

        // Load default project
        loadDefaultProject: function() {
            const urlParams = new URLSearchParams(window.location.search);
            const project = urlParams.get('project');
            if (project) {
                this.loadProject(project);
            } else {
                // Load first available project
                const projectCards = document.querySelectorAll('[data-project]');
                if (projectCards.length > 0) {
                    const firstProject = projectCards[0].getAttribute('data-project');
                    this.loadProject(firstProject);
                }
            }
        },

        // Load specific project
        loadProject: function(projectName) {
            console.log(`📈 Loading project: ${projectName}`);
            this.showLoading(true);

            const dataUrl = `/project/${projectName}/data`;
            const metricsUrl = `/project/${projectName}/metrics`;

            console.log('🔗 API URLs:', { dataUrl, metricsUrl });
            console.log('🔗 Full URLs:', {
                data: `${this.config.apiBaseUrl}${dataUrl}`,
                metrics: `${this.config.apiBaseUrl}${metricsUrl}`
            });

            console.log('📡 Making API calls...');
            this.apiCall(dataUrl)
                .then(data => {
                    console.log('✅ Data API success:', data ? 'Data received' : 'No data');
                    return this.apiCall(metricsUrl).then(metrics => ({ data, metrics }));
                })
                .then(({ data, metrics }) => {
                    console.log('✅ Metrics API success:', metrics ? 'Metrics received' : 'No metrics');
                    this.state.currentProject = projectName;
                    this.state.currentData = data;
                    this.updateProjectData(data, metrics);
                    this.updateURL(`?project=${projectName}`);
                })
                .catch(error => {
                    console.error(`❌ Error loading project ${projectName}:`, error);
                    console.error('❌ Error type:', error.constructor.name);
                    console.error('❌ Error message:', error.message);
                    this.showError(`Failed to load ${projectName} data: ${error.message}`);
                })
                .finally(() => {
                    this.showLoading(false);
                });
        },

        // Update project data in UI
        updateProjectData: function(data, metrics) {
            this.updateMetricsCards(data);
            this.updateCharts(data);
            this.updateTradesTable(data.trades || []);
            this.updateStrategyParameters(data.summary.algorithmConfiguration.parameters);
        },

        // Update metrics cards
        updateMetricsCards: function(data) {
            const portfolioStats = data.summary.totalPerformance.portfolioStatistics;
            const tradeStats = data.summary.totalPerformance.tradeStatistics;

            // Update metrics cards if they exist
            const metricsCards = document.querySelectorAll('.metric-card');
            metricsCards.forEach(card => {
                const metric = card.getAttribute('data-metric');
                const value = this.getNestedValue(portfolioStats, metric) ||
                           this.getNestedValue(tradeStats, metric);
                if (value !== undefined) {
                    this.updateMetricCard(card, value, metric);
                }
            });
        },

        // Update individual metric card
        updateMetricCard: function(card, value, metric) {
            const valueElement = card.querySelector('.metric-value');
            const changeElement = card.querySelector('.metric-change');

            if (valueElement) {
                valueElement.textContent = this.formatMetricValue(value, metric);
            }

            if (changeElement && value !== 0) {
                changeElement.textContent = this.getMetricChangeText(value, metric);
                changeElement.className = `metric-change ${value >= 0 ? 'text-success' : 'text-danger'}`;
            }

            // Update card color based on performance
            this.updateCardColor(card, value, metric);
        },

        // Update charts
        updateCharts: function(data) {
            this.createEquityCurve(data.equity_curve, data.buy_hold_curve);
            this.createDrawdownChart(data.equity_curve);
            this.createMonthlyReturnsChart(data.equity_curve);
            this.createTradeAnalysisChart(data.trades || []);
        },

        // Create equity curve chart using TradingView Lightweight Charts
        createEquityCurve: function(equityData, buyHoldData) {
            console.log('🚀 Creating equity curve chart...', { equityData: equityData?.length, buyHoldData: buyHoldData?.length });
            console.log('📚 LightweightCharts available:', typeof LightweightCharts);
            console.log('📚 LightweightCharts.createChart available:', typeof LightweightCharts.createChart);

            const chartElement = document.getElementById('equityChart');
            if (!chartElement) {
                console.error('❌ CRITICAL: Chart element not found!');
                return;
            }

            if (!equityData || equityData.length === 0) {
                console.error('❌ No equity data:', equityData);
                chartElement.innerHTML = '<div class="alert alert-warning">No equity data available</div>';
                return;
            }

            console.log('✅ Chart element found, clearing...');
            // Force clear
            chartElement.innerHTML = '';

            try {
                console.log('📏 Creating chart with dimensions...');
                const width = chartElement.clientWidth || 800;
                const height = 400;

                console.log('📏 Dimensions:', { width, height, clientWidth: chartElement.clientWidth });

                // Create chart
                const chart = LightweightCharts.createChart(chartElement, {
                    width: width,
                    height: height,
                    layout: {
                        background: { type: 'solid', color: '#ffffff' },
                        textColor: '#333333',
                        fontSize: 12,
                        fontFamily: 'Inter, system-ui, sans-serif',
                    },
                    grid: {
                        vertLines: { color: 'rgba(197, 203, 206, 0.5)' },
                        horzLines: { color: 'rgba(197, 203, 206, 0.5)' },
                    },
                    crosshair: {
                        mode: LightweightCharts.CrosshairMode.Normal,
                    },
                    rightPriceScale: {
                        borderColor: 'rgba(197, 203, 206, 0.8)',
                        scaleMargins: {
                            top: 0.1,
                            bottom: 0.1,
                        },
                    },
                    timeScale: {
                        borderColor: 'rgba(197, 203, 206, 0.8)',
                        timeVisible: true,
                        secondsVisible: false,
                    },
                });

                console.log('✅ Chart object created:', chart.constructor.name);

                // Custom formatters for America/New_York timezone
                const priceFormatter = (price) => {
                    return new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: 'USD',
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }).format(price);
                };

                // Standard Practice: Use built-in localization for consistency
                chart.timeScale().applyOptions({
                    timeVisible: true,
                    secondsVisible: false,
                    rightOffset: 12,
                    barSpacing: 2,  // Reduced spacing to show more candles (was 8)
                    fixLeftEdge: false,
                    lockVisibleTimeRangeOnResize: true,
                    rightBarStaysOnScroll: true,
                    borderVisible: true,
                    axisLabelColor: '#333',
                    gridColor: 'rgba(197, 203, 206, 0.5)',
                });

                // Standard Practice: Apply consistent localization to both x-axis and tooltip
                chart.applyOptions({
                    localization: {
                        locale: 'en-US',
                        dateFormat: 'yyyy-MM-dd',
                        timeFormatter: function(businessDayOrTime) {
                            if (typeof businessDayOrTime === 'object') {
                                return `${businessDayOrTime.year}-${String(businessDayOrTime.month).padStart(2, '0')}-${String(businessDayOrTime.day).padStart(2, '0')}`;
                            }
                            // For time data, show in America/New_York timezone
                            const date = new Date(businessDayOrTime * 1000);
                            return date.toLocaleTimeString('en-US', {
                                timeZone: 'America/New_York',
                                hour: '2-digit',
                                minute: '2-digit',
                                hour12: false
                            });
                        }
                    }
                });

                // Prepare data with trading hours filter and candlestick format
                // Filter for NYSE trading hours only (9:30 AM - 4:00 PM EST = 14:30 - 21:00 UTC)
                const tradingHoursData = equityData.filter(point => {
                    const date = new Date(point[0] * 1000);
                    const hour = date.getUTCHours();
                    const minute = date.getUTCMinutes();
                    // Trading hours: 14:30 UTC (9:30 AM EST) to 21:00 UTC (4:00 PM EST)
                    const timeInMinutes = hour * 60 + minute;
                    return timeInMinutes >= (14 * 60 + 30) && timeInMinutes <= (21 * 60 + 0);
                });

                console.log('📊 Total data points:', equityData.length);
                console.log('⏰ Trading hours data points:', tradingHoursData.length);

                // Convert to TradingView candlestick format
                const candlestickData = tradingHoursData.map(point => ({
                    time: Math.floor(point[0]),
                    open: parseFloat(point[1]),
                    high: parseFloat(point[2]),
                    low: parseFloat(point[3]),
                    close: parseFloat(point[4])
                }));

                console.log('📊 Candlestick data prepared:', candlestickData.length, 'points');
                console.log('🕐 Sample OHLC:', candlestickData.slice(0, 3));

                // Create candlestick series for strategy
                const strategySeries = chart.addCandlestickSeries({
                    upColor: this.config.chartColors.success,
                    downColor: this.config.chartColors.danger,
                    borderUpColor: this.config.chartColors.success,
                    borderDownColor: this.config.chartColors.danger,
                    wickUpColor: this.config.chartColors.success,
                    wickDownColor: this.config.chartColors.danger,
                    title: 'Strategy',
                    priceLineVisible: true,
                    lastValueVisible: true,
                });

                strategySeries.setData(candlestickData);
                console.log('✅ Strategy candlestick data set');

                // Set the timezone after data is loaded
                setTimeout(() => {
                    try {
                        chart.timeScale().scrollToPosition(0);
                        chart.timeScale().fitContent();
                        console.log('✅ Chart fitted and timezone applied');
                    } catch (e) {
                        console.log('Note: fitContent call result:', e.message);
                    }
                }, 100);

                // Add legend with trading hours info
                this.addLightweightChartsLegend(chart, strategySeries, 'Strategy (Trading Hours)');

                // Add trading hours and data frequency indicator
                const tradingInfoIndicator = document.createElement('div');
                tradingInfoIndicator.className = 'trading-info-indicator badge bg-success';
                tradingInfoIndicator.style.cssText = 'position: absolute; top: 10px; right: 10px; z-index: 10; font-size: 11px;';
                tradingInfoIndicator.innerHTML = `<i class="fas fa-chart-candle me-1"></i>NYSE: 9:30 AM - 4:00 PM EST<br><small>1-min candles (${candlestickData.length} points)</small>`;
                chartElement.appendChild(tradingInfoIndicator);

                // Make responsive
                const resizeChart = () => {
                    if (chartElement.clientWidth > 0) {
                        chart.applyOptions({ width: chartElement.clientWidth });
                    }
                };
                window.addEventListener('resize', resizeChart);

                // Fit content
                setTimeout(() => {
                    chart.timeScale().fitContent();
                }, 200);

                console.log('🎉 Candlestick chart created successfully!');
                console.log('📈 Shows trading hours only: 9:30 AM - 4:00 PM EST');
                console.log('⏱️ Total data points:', equityData.length, '→ Trading hours:', tradingHoursData.length);
                console.log('📊 Candle frequency: 1-minute intervals (auto-sampled to fit screen)');
                console.log('💡 Tip: Zoom in to see individual 1-minute candles');

            } catch (error) {
                console.error('❌ CRITICAL ERROR:', error);
                console.error('Stack:', error.stack);
                chartElement.innerHTML = `<div class="alert alert-danger m-3"><strong>Error creating chart:</strong><br>${error.message}</div>`;
            }
        },

        // Add legend for Lightweight Charts
        addLightweightChartsLegend: function(chart, strategySeries, strategyName) {
            const container = document.getElementById('equityChart')?.parentElement;
            if (!container) return;

            // Remove existing legend
            const existingLegend = container.querySelector('.lw-legend');
            if (existingLegend) {
                existingLegend.remove();
            }

            // Create legend
            const legend = document.createElement('div');
            legend.className = 'lw-legend d-flex align-items-center gap-3 mt-2 p-2 bg-light rounded';
            legend.style.fontSize = '13px';
            legend.innerHTML = `
                <div class="d-flex align-items-center gap-2">
                    <div style="width: 3px; height: 20px; background: ${this.config.chartColors.primary};"></div>
                    <span class="fw-bold">Strategy</span>
                    <span class="text-success fw-bold" id="strategyValue">$0.00</span>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <div style="width: 3px; height: 20px; background: ${this.config.chartColors.warning}; border-left: 2px dashed ${this.config.chartColors.warning};"></div>
                    <span class="fw-bold">Buy & Hold</span>
                    <span class="text-info fw-bold" id="buyHoldValue">$0.00</span>
                </div>
            `;
            container.appendChild(legend);

            // Custom price formatter
            const priceFormatter = (price) => {
                return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD',
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }).format(price);
            };

            // Update legend on price change
            chart.subscribeCrosshairMove(param => {
                if (param.seriesPrices && param.seriesPrices.size > 0) {
                    const strategyPrice = param.seriesPrices.get(strategySeries);
                    if (strategyPrice) {
                        const valueEl = document.getElementById('strategyValue');
                        if (valueEl) {
                            valueEl.textContent = priceFormatter(strategyPrice);
                        }
                    }
                }
            });
        },

        // Create drawdown chart
        createDrawdownChart: function(equityData) {
            const chartElement = document.getElementById('drawdownChart');
            if (!chartElement || !equityData || equityData.length === 0) {
                if (chartElement) {
                    chartElement.innerHTML = '<div class="chart-error">No drawdown data available</div>';
                }
                return;
            }

            let peak = equityData[0][3];
            const drawdowns = equityData.map(point => {
                const value = point[3];
                peak = Math.max(peak, value);
                return ((value - peak) / peak) * 100;
            });

            const dates = equityData.map(point => new Date(point[0] * 1000));

            const trace = {
                x: dates,
                y: drawdowns,
                type: 'scatter',
                mode: 'lines',
                fill: 'tonexty',
                name: 'Drawdown',
                line: { color: this.config.chartColors.danger, width: 2 },
                fillcolor: 'rgba(220, 53, 69, 0.1)',
                hovertemplate: '<b>Date:</b> %{x}<br><b>Drawdown:</b> %{y:.2f}%<extra></extra>'
            };

            const layout = {
                title: '',
                xaxis: {
                    title: 'Date',
                    type: 'date',
                    showgrid: true,
                    gridcolor: 'rgba(0,0,0,0.1)'
                },
                yaxis: {
                    title: 'Drawdown (%)',
                    tickformat: '.2f',
                    showgrid: true,
                    gridcolor: 'rgba(0,0,0,0.1)'
                },
                showlegend: false,
                margin: { t: 20, r: 20, b: 40, l: 60 },
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)'
            };

            Plotly.newPlot('drawdownChart', [trace], layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d', 'autoScale2d']
            });
        },

        // Create monthly returns chart
        createMonthlyReturnsChart: function(equityData) {
            const chartElement = document.getElementById('monthlyReturnsChart');
            if (!chartElement || !equityData || equityData.length === 0) {
                if (chartElement) {
                    chartElement.innerHTML = '<div class="chart-error">No monthly returns data available</div>';
                }
                return;
            }

            // Calculate monthly returns
            const monthlyData = {};
            equityData.forEach(point => {
                const date = new Date(point[0] * 1000);
                const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
                monthlyData[monthKey] = point[3];
            });

            const months = Object.keys(monthlyData).sort();
            const returns = [];

            for (let i = 1; i < months.length; i++) {
                const prevValue = monthlyData[months[i-1]];
                const currValue = monthlyData[months[i]];
                const monthlyReturn = ((currValue - prevValue) / prevValue) * 100;
                returns.push(monthlyReturn);
            }

            const monthLabels = months.slice(1).map(month => {
                const [year, monthNum] = month.split('-');
                return `${year}-${monthNum}`;
            });

            const trace = {
                x: monthLabels,
                y: returns,
                type: 'bar',
                marker: {
                    color: returns.map(r => r >= 0 ? this.config.chartColors.success : this.config.chartColors.danger)
                },
                hovertemplate: '<b>Month:</b> %{x}<br><b>Return:</b> %{y:.2f}%<extra></extra>'
            };

            const layout = {
                title: '',
                xaxis: { title: 'Month' },
                yaxis: { title: 'Return (%)', tickformat: '.2f' },
                showlegend: false,
                margin: { t: 20, r: 20, b: 60, l: 60 },
                plot_bgcolor: 'rgba(0,0,0,0)',
                paper_bgcolor: 'rgba(0,0,0,0)'
            };

            Plotly.newPlot('monthlyReturnsChart', [trace], layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d', 'autoScale2d']
            });
        },

        // Create trade analysis chart
        createTradeAnalysisChart: function(tradesData) {
            const chartElement = document.getElementById('tradeAnalysisChart');
            if (!chartElement || !tradesData || tradesData.length === 0) {
                if (chartElement) {
                    chartElement.innerHTML = '<div class="chart-error">No trade data available</div>';
                }
                return;
            }

            // Process trades for chart
            const trades = this.processTradesForChart(tradesData);

            const trace = {
                x: trades.map(t => t.date),
                y: trades.map(t => t.pnl),
                mode: 'markers',
                type: 'scatter',
                marker: {
                    color: trades.map(t => t.pnl >= 0 ? this.config.chartColors.success : this.config.chartColors.danger),
                    size: 8,
                    opacity: 0.7
                },
                hovertemplate: '<b>Date:</b> %{x}<br><b>P&L:</b> $%{y:.2f}<extra></extra>'
            };

            const layout = {
                title: 'Trade P&L Distribution',
                xaxis: { title: 'Trade Date', type: 'date' },
                yaxis: { title: 'P&L ($)', tickformat: '$,.0f' },
                showlegend: false,
                margin: { t: 40, r: 20, b: 60, l: 60 }
            };

            Plotly.newPlot('tradeAnalysisChart', [trace], layout, { responsive: true });
        },

        // Process trades for chart display
        processTradesForChart: function(tradesData) {
            const trades = {};
            const processedTrades = [];

            tradesData.forEach(event => {
                if (event.status === 'filled') {
                    if (!trades[event.orderId]) {
                        trades[event.orderId] = {
                            date: new Date(event.time * 1000),
                            symbol: event.symbolValue,
                            type: event.direction,
                            quantity: Math.abs(event.fillQuantity),
                            price: event.fillPrice,
                            pnl: 0
                        };
                    } else {
                        const trade = trades[event.orderId];
                        if (trade.type === 'buy') {
                            trade.exitPrice = event.fillPrice;
                            trade.pnl = (trade.exitPrice - trade.price) * trade.quantity;
                        } else {
                            trade.exitPrice = event.fillPrice;
                            trade.pnl = (trade.price - trade.exitPrice) * trade.quantity;
                        }
                        processedTrades.push(trade);
                    }
                }
            });

            return processedTrades;
        },

        // Update trades table
        updateTradesTable: function(tradesData) {
            const tbody = document.getElementById('tradesTableBody');
            if (!tbody) return;

            tbody.innerHTML = '';

            if (!tradesData || tradesData.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No trade data available</td></tr>';
                return;
            }

            const trades = this.processTradesForChart(tradesData);

            trades.forEach(trade => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${trade.date.toLocaleDateString()}</td>
                    <td><span class="badge bg-secondary">${trade.symbol}</span></td>
                    <td><span class="badge ${trade.type === 'buy' ? 'bg-success' : 'bg-danger'}">${trade.type.toUpperCase()}</span></td>
                    <td>${trade.quantity.toLocaleString()}</td>
                    <td>$${trade.price.toFixed(2)}</td>
                    <td class="${trade.pnl >= 0 ? 'text-success' : 'text-danger'}">$${trade.pnl.toFixed(2)}</td>
                    <td>${this.calculateTradeDuration(trade)}</td>
                `;
                tbody.appendChild(row);
            });
        },

        // Update strategy parameters
        updateStrategyParameters: function(parameters) {
            const container = document.getElementById('strategyParameters');
            if (!container) return;

            container.innerHTML = '';
            Object.entries(parameters).forEach(([key, value]) => {
                const paramElement = document.createElement('div');
                paramElement.className = 'col-md-3 col-sm-6 mb-3';
                paramElement.innerHTML = `
                    <div class="d-flex justify-content-between p-2 bg-light rounded">
                        <span class="text-muted small">${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                        <span class="fw-bold">${value}</span>
                    </div>
                `;
                container.appendChild(paramElement);
            });
        },

        // Helper functions
        apiCall: function(endpoint) {
            return fetch(`${this.config.apiBaseUrl}${endpoint}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                });
        },

        formatMetricValue: function(value, metric) {
            if (metric.includes('Return') || metric.includes('Drawdown') || metric.includes('Rate') || metric.includes('Ratio')) {
                return new Intl.NumberFormat('en-US', {
                    style: 'percent',
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }).format(value);
            } else if (metric.includes('Value') || metric.includes('Equity') || metric.includes('PnL')) {
                return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD',
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }).format(value);
            } else {
                return new Intl.NumberFormat('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }).format(value);
            }
        },

        getMetricChangeText: function(value, metric) {
            if (value > 0) {
                return `▲ ${this.formatMetricValue(value, metric)}`;
            } else if (value < 0) {
                return `▼ ${this.formatMetricValue(Math.abs(value), metric)}`;
            } else {
                return '— 0.00%';
            }
        },

        updateCardColor: function(card, value, metric) {
            const isPositive = (metric.includes('Return') || metric.includes('Ratio')) ? value > 0 : value > 1;
            const cardClass = card.className;

            // Remove previous color classes
            card.className = cardClass.replace(/bg-(success|warning|danger|info|primary)/g, '');

            // Add appropriate color class
            if (isPositive) {
                card.classList.add('border-success');
            } else if (value < 0 || (metric.includes('Drawdown') && value > 0.1)) {
                card.classList.add('border-danger');
            }
        },

        getNestedValue: function(obj, path) {
            return path.split('.').reduce((current, key) => current && current[key], obj);
        },

        calculateTradeDuration: function(trade) {
            // This is a simplified calculation - in reality you'd track entry and exit times
            return 'N/A';
        },

        // UI utilities
        showLoading: function(show) {
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) {
                overlay.classList.toggle('d-none', !show);
            }
        },

        showError: function(message) {
            this.showToast(message, 'error');
        },

        showToast: function(message, type = 'info') {
            // Create toast element
            const toast = document.createElement('div');
            toast.className = `toast align-items-center text-white bg-${this.getToastType(type)} border-0`;
            toast.setAttribute('role', 'alert');
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            `;

            // Add to container
            const container = document.getElementById('toastContainer') || this.createToastContainer();
            container.appendChild(toast);

            // Show toast
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();

            // Remove after hiding
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        },

        getToastType: function(type) {
            const typeMap = {
                'error': 'danger',
                'success': 'success',
                'warning': 'warning',
                'info': 'info'
            };
            return typeMap[type] || 'info';
        },

        createToastContainer: function() {
            const container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
            return container;
        },

        // Chart utilities
        handleChartHover: function(event) {
            console.log('Chart hover:', event);
        },

        handleChartUnhover: function(event) {
            console.log('Chart unhover:', event);
        },

        resizeCharts: function() {
            const charts = document.querySelectorAll('.plotly-graph-div');
            charts.forEach(chart => {
                Plotly.Plots.resize(chart);
            });
        },

        // Refresh functionality
        refreshData: function() {
            if (this.state.currentProject) {
                this.loadProject(this.state.currentProject);
            } else {
                this.loadInitialData();
            }
        },

        startAutoRefresh: function() {
            if (this.state.refreshTimer) {
                clearInterval(this.state.refreshTimer);
            }
            this.state.refreshTimer = setInterval(() => {
                if (this.state.currentProject) {
                    this.refreshData();
                }
            }, this.config.refreshInterval);
        },

        stopAutoRefresh: function() {
            if (this.state.refreshTimer) {
                clearInterval(this.state.refreshTimer);
                this.state.refreshTimer = null;
            }
        },

        // URL management
        updateURL: function(params) {
            const newURL = window.location.pathname + params;
            window.history.pushState({}, '', newURL);
        },

        // Export functionality
        exportData: function() {
            if (!this.state.currentData) {
                this.showError('No data to export');
                return;
            }

            this.showToast('Preparing export...', 'info');

            // Create export data
            const exportData = {
                project: this.state.currentProject,
                timestamp: new Date().toISOString(),
                data: this.state.currentData
            };

            // Convert to JSON and download
            const dataStr = JSON.stringify(exportData, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);

            const link = document.createElement('a');
            link.href = url;
            link.download = `${this.state.currentProject}_backtest_${new Date().toISOString().split('T')[0]}.json`;
            link.click();

            URL.revokeObjectURL(url);
            this.showToast('Data exported successfully', 'success');
        },

        // Utility functions
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    };

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.BacktestDashboard.init();
        });
    } else {
        window.BacktestDashboard.init();
    }

})();
