/**
 * Chart Module
 * Simple canvas-based charting for progress visualization
 */

class SimpleChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.data = [];
        this.labels = [];
    }

    setData(labels, data) {
        this.labels = labels;
        this.data = data;
    }

    draw() {
        if (!this.canvas || !this.ctx) return;

        const canvas = this.canvas;
        const ctx = this.ctx;

        // Set canvas size
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        // Clear canvas
        ctx.clearRect(0, 0, rect.width, rect.height);

        if (this.data.length === 0) {
            ctx.fillStyle = '#6B7280';
            ctx.font = '14px Inter, sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('No data available', rect.width / 2, rect.height / 2);
            return;
        }

        // Chart dimensions
        const padding = 40;
        const chartWidth = rect.width - padding * 2;
        const chartHeight = rect.height - padding * 2;

        // Find max value
        const maxValue = Math.max(...this.data, 1);

        // Draw axes
        ctx.strokeStyle = '#E5E7EB';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, rect.height - padding);
        ctx.lineTo(rect.width - padding, rect.height - padding);
        ctx.stroke();

        // Draw data points and line
        const pointSpacing = chartWidth / (this.data.length - 1 || 1);

        ctx.strokeStyle = '#4F46E5';
        ctx.fillStyle = '#4F46E5';
        ctx.lineWidth = 2;
        ctx.beginPath();

        this.data.forEach((value, index) => {
            const x = padding + (index * pointSpacing);
            const y = rect.height - padding - (value / maxValue * chartHeight);

            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }

            // Draw point
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, Math.PI * 2);
            ctx.fill();
            ctx.closePath();
        });

        ctx.stroke();

        // Draw labels
        ctx.fillStyle = '#6B7280';
        ctx.font = '12px Inter, sans-serif';
        ctx.textAlign = 'center';

        this.labels.forEach((label, index) => {
            if (index % Math.ceil(this.labels.length / 6) === 0) {
                const x = padding + (index * pointSpacing);
                ctx.fillText(label, x, rect.height - padding + 20);
            }
        });

        // Draw Y-axis labels
        ctx.textAlign = 'right';
        for (let i = 0; i <= 4; i++) {
            const value = Math.round((maxValue / 4) * i);
            const y = rect.height - padding - (i / 4 * chartHeight);
            ctx.fillText(value.toString(), padding - 10, y + 4);
        }
    }

    drawLineChart(labels, datasets) {
        this.labels = labels;

        if (!this.canvas || !this.ctx) return;

        const canvas = this.canvas;
        const ctx = this.ctx;

        // Set canvas size
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        // Clear canvas
        ctx.clearRect(0, 0, rect.width, rect.height);

        if (datasets.length === 0 || datasets[0].data.length === 0) {
            ctx.fillStyle = '#6B7280';
            ctx.font = '14px Inter, sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('No data available', rect.width / 2, rect.height / 2);
            return;
        }

        // Chart dimensions
        const padding = 50;
        const chartWidth = rect.width - padding * 2;
        const chartHeight = rect.height - padding * 2;

        // Find max value across all datasets
        let maxValue = 1;
        datasets.forEach(dataset => {
            const max = Math.max(...dataset.data);
            if (max > maxValue) maxValue = max;
        });

        // Draw axes
        ctx.strokeStyle = '#E5E7EB';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, rect.height - padding);
        ctx.lineTo(rect.width - padding, rect.height - padding);
        ctx.stroke();

        // Draw each dataset
        datasets.forEach((dataset, datasetIndex) => {
            const pointSpacing = chartWidth / (dataset.data.length - 1 || 1);

            ctx.strokeStyle = dataset.color || '#4F46E5';
            ctx.fillStyle = dataset.color || '#4F46E5';
            ctx.lineWidth = 2;
            ctx.beginPath();

            dataset.data.forEach((value, index) => {
                const x = padding + (index * pointSpacing);
                const y = rect.height - padding - (value / maxValue * chartHeight);

                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }

                // Draw point
                ctx.save();
                ctx.beginPath();
                ctx.arc(x, y, 4, 0, Math.PI * 2);
                ctx.fill();
                ctx.closePath();
                ctx.restore();
            });

            ctx.stroke();
        });

        // Draw labels
        ctx.fillStyle = '#6B7280';
        ctx.font = '11px Inter, sans-serif';
        ctx.textAlign = 'center';

        const labelInterval = Math.ceil(labels.length / 8);
        labels.forEach((label, index) => {
            if (index % labelInterval === 0 || index === labels.length - 1) {
                const pointSpacing = chartWidth / (labels.length - 1 || 1);
                const x = padding + (index * pointSpacing);
                ctx.save();
                ctx.translate(x, rect.height - padding + 15);
                ctx.rotate(-Math.PI / 6);
                ctx.fillText(label, 0, 0);
                ctx.restore();
            }
        });

        // Draw Y-axis labels
        ctx.textAlign = 'right';
        for (let i = 0; i <= 5; i++) {
            const value = Math.round((maxValue / 5) * i);
            const y = rect.height - padding - (i / 5 * chartHeight);
            ctx.fillText(value.toString(), padding - 10, y + 4);
        }

        // Draw legend
        if (datasets.length > 1) {
            let legendX = rect.width - padding - 100;
            let legendY = padding;

            datasets.forEach((dataset, index) => {
                ctx.fillStyle = dataset.color || '#4F46E5';
                ctx.fillRect(legendX, legendY + (index * 20), 15, 3);

                ctx.fillStyle = '#374151';
                ctx.font = '12px Inter, sans-serif';
                ctx.textAlign = 'left';
                ctx.fillText(dataset.label || `Dataset ${index + 1}`, legendX + 20, legendY + (index * 20) + 4);
            });
        }
    }
}
