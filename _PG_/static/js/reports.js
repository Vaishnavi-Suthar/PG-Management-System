// reports.js

document.addEventListener('DOMContentLoaded', function() {

    // Get chart data from HTML data attributes
    const reportContainer = document.getElementById('report-data');
    if (!reportContainer) return;

    const months = JSON.parse(reportContainer.dataset.months || "[]");
    const revenueData = JSON.parse(reportContainer.dataset.revenue || "[]");
    const occupiedRooms = parseInt(reportContainer.dataset.occupied || "0");
    const vacantRooms = parseInt(reportContainer.dataset.vacant || "0");
    const totalRooms = parseInt(reportContainer.dataset.total || "0");

    // --- Revenue Chart ---
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Monthly Revenue',
                    data: revenueData,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.3,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'Revenue Trend (Last 6 Months)' }
                }
            }
        });
    }

    // --- Occupancy Chart ---
    const occupancyCtx = document.getElementById('occupancyChart');
    if (occupancyCtx) {
        const maintenanceRooms = Math.max(0, totalRooms - occupiedRooms - vacantRooms);
        new Chart(occupancyCtx, {
            type: 'doughnut',
            data: {
                labels: ['Occupied', 'Vacant', 'Maintenance'],
                datasets: [{
                    data: [occupiedRooms, vacantRooms, maintenanceRooms],
                    backgroundColor: [
                        'rgb(54, 162, 235)',
                        'rgb(75, 192, 192)',
                        'rgb(255, 205, 86)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'Room Occupancy Status' }
                }
            }
        });
    }
});
