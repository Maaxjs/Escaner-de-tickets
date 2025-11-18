/**
 * upload.js - Lógica para página de subida de tickets
 */

let currentImage = null;
let currentOCRData = null;

const uploadSection = document.getElementById('uploadSection');
const fileInput = document.getElementById('fileInput');
const loading = document.getElementById('loading');
const previewSection = document.getElementById('previewSection');
const imagePreview = document.getElementById('imagePreview');
const messageContainer = document.getElementById('message-container');
const itemsTableBody = document.getElementById('itemsTableBody');

const choiceOverlay = document.getElementById('choiceOverlay');
const chooseFileBtn = document.getElementById('chooseFileBtn');
const chooseCameraBtn = document.getElementById('chooseCameraBtn');
const cancelChoiceBtn = document.getElementById('cancelChoiceBtn');
const cameraInput = document.getElementById('cameraInput');

uploadSection.addEventListener('click', () => {
    choiceOverlay.style.display = 'flex';
});

chooseFileBtn.addEventListener('click', () => {
    choiceOverlay.style.display = 'none'; 
    fileInput.click(); 
});

// 3. Al hacer clic en el botón USAR CÁMARA
chooseCameraBtn.addEventListener('click', () => {
    choiceOverlay.style.display = 'none'; 
    cameraInput.click();
});

cancelChoiceBtn.addEventListener('click', () => {
    choiceOverlay.style.display = 'none';
});

choiceOverlay.addEventListener('click', (e) => {
    if (e.target === choiceOverlay) {
        choiceOverlay.style.display = 'none';
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

cameraInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

uploadSection.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadSection.classList.add('dragover');
});

uploadSection.addEventListener('dragleave', () => {
    uploadSection.classList.remove('dragover');
});

uploadSection.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadSection.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

function handleFile(file) {
    choiceOverlay.style.display = 'none';
    
    if (!file.type.startsWith('image/')) {
        showMessage('Por favor selecciona una imagen válida', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    // Show loading, hide upload area
    loading.style.display = 'block';
    uploadSection.style.display = 'none';
    previewSection.classList.remove('show');

    // Upload file and process with OCR
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        loading.style.display = 'none';
        
        if (data.success) {
            currentImage = data.image;
            currentOCRData = data.ocr_data || {};
            imagePreview.src = 'data:image/jpeg;base64,' + data.image;

            // Fill form with OCR data
            document.getElementById('nombreNegocio').value = currentOCRData.nombre_lugar || '';
            document.getElementById('precioTotal').value = currentOCRData.precio_total_compra || '';

            // Populate items table
            itemsTableBody.innerHTML = '';
            const items = currentOCRData.items || [];
            
            if (items.length > 0) {
                items.forEach((item, index) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><input type="text" value="${item.producto || ''}" data-field="producto" data-index="${index}"></td>
                        <td><input type="number" value="${item.cantidad || '1'}" data-field="cantidad" data-index="${index}" min="1" step="0.01"></td>
                        <td><input type="number" value="${item.precio_unitario || '0'}" data-field="precio_unitario" data-index="${index}" min="0" step="0.01"></td>
                        <td><input type="number" value="${item.precio_total || '0'}" data-field="precio_total" data-index="${index}" min="0" step="0.01"></td>
                    `;
                    itemsTableBody.appendChild(row);
                });
            } else {
                //Agregar una columna vacia si no hay items
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><input type="text" placeholder="Nombre del producto" data-field="producto" data-index="0"></td>
                    <td><input type="number" value="1" data-field="cantidad" data-index="0" min="1" step="0.01"></td>
                    <td><input type="number" value="0" data-field="precio_unitario" data-index="0" min="0" step="0.01"></td>
                    <td><input type="number" value="0" data-field="precio_total" data-index="0" min="0" step="0.01"></td>
                `;
                itemsTableBody.appendChild(row);
            }

            // Show preview section
            previewSection.classList.add('show');
        } else {
            showMessage('Error al procesar la imagen: ' + (data.error || 'Error desconocido'), 'error');
            uploadSection.style.display = 'block';
        }
    })
    .catch(error => {
        loading.style.display = 'none';
        uploadSection.style.display = 'block';
        showMessage('Error al procesar la imagen: ' + error.message, 'error');
        console.error('Error:', error);
    });
}

document.getElementById('cancelBtn').addEventListener('click', resetUpload);

document.getElementById('saveBtn').addEventListener('click', () => {
    const nombreUsuario = document.getElementById('nombreUsuario').value.trim();
    const nombreNegocio = document.getElementById('nombreNegocio').value.trim();
    const precioTotal = parseFloat(document.getElementById('precioTotal').value) || 0;

    if (!nombreUsuario) {
        showMessage('Por favor ingresa tu nombre', 'error');
        return;
    }
    
    if (!nombreNegocio) {
        showMessage('Por favor ingresa el nombre del negocio', 'error');
        return;
    }

    // Collect items from table
    const items = [];
    document.querySelectorAll('#itemsTableBody tr').forEach(row => {
        const producto = row.querySelector('[data-field="producto"]').value.trim();
        const cantidad = parseFloat(row.querySelector('[data-field="cantidad"]').value) || 1;
        const precio_unitario = parseFloat(row.querySelector('[data-field="precio_unitario"]').value) || 0;
        const precio_total = parseFloat(row.querySelector('[data-field="precio_total"]').value) || 0;

        if (producto) {
            items.push({
                producto,
                cantidad,
                precio_unitario,
                precio_total
            });
        }
    });

    if (items.length === 0) {
        showMessage('Por favor ingresa al menos un producto', 'error');
        return;
    }

    const dataToSend = {
        image: currentImage,
        nombre_negocio: nombreNegocio,
        items: items,
        precio_total_compra: precioTotal,
        nombre_usuario: nombreUsuario
    };

    const saveBtn = document.getElementById('saveBtn');
    saveBtn.disabled = true;
    saveBtn.textContent = 'Guardando...';

    fetch('/api/save-ticket', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    })
    .then(response => response.json())
    .then(resp => {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Guardar ticket';

        if (resp.success) {
            if (resp.id) {
                window.location.href = '/confirm/' + resp.id;
            } else {
                showMessage('¡Ticket guardado exitosamente!', 'success');
                setTimeout(resetUpload, 1500);
            }
        } else {
            showMessage('Error al guardar el ticket: ' + (resp.error || 'Error desconocido'), 'error');
        }
    })
    .catch(error => {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Guardar ticket';
        showMessage('Error al guardar el ticket: ' + error.message, 'error');
        console.error('Error:', error);
    });
});

function resetUpload() {
    currentImage = null;
    currentOCRData = null;
    fileInput.value = '';
    cameraInput.value = '';
    uploadSection.style.display = 'block';
    loading.style.display = 'none';
    previewSection.classList.remove('show');
    itemsTableBody.innerHTML = '';
}
