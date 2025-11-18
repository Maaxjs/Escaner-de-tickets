/**
 * dashboard.js - Lógica para panel administrador
 */

function updateStats() {
    const rows = document.querySelectorAll('#ticketsTable tr');
    const totalTickets = rows.length;
    let totalMonto = 0;

    rows.forEach(row => {
        const montoCell = row.cells[5].textContent.trim();
        const monto = parseFloat(montoCell.replace('$', '').replace('-', '0'));
        if (!isNaN(monto)) {
            totalMonto += monto;
        }
    });

    document.getElementById('totalTickets').textContent = totalTickets;
    document.getElementById('totalMonto').textContent = '$' + totalMonto.toFixed(2);
}

function showImage(src) {
    document.getElementById('imageModal').classList.add('show');
    document.getElementById('modalImage').src = src;
}

function deleteTicket(id) {
    if (confirm('¿Estás seguro de que quieres eliminar este ticket?')) {
        fetch(`/api/delete-ticket/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`ticket-${id}`).remove();
                updateStats();
                showMessage('Ticket eliminado', 'success');
            } else {
                showMessage('Error al eliminar', 'error');
            }
        })
        .catch(error => {
            showMessage('Error al eliminar', 'error');
        });
    }
}

document.getElementById('exportBtn').addEventListener('click', () => {
    const email = prompt('Ingresa el email donde enviar el reporte:');
    if (email) {
        fetch('/api/export-monthly', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage('Reporte generado y guardado. Los tickets han sido eliminados.', 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showMessage(data.error || 'Error al generar reporte', 'error');
            }
        })
        .catch(error => {
            showMessage('Error al generar reporte', 'error');
        });
    }
});

// Click en el modal para cerrar
document.getElementById('imageModal').addEventListener('click', (e) => {
    if (e.target.id === 'imageModal') {
        closeImageModal();
    }
});

updateStats();
