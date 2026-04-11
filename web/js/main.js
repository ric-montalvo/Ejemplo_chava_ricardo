// Control de pantallas
function mostrarPantalla(id) {
    document.querySelectorAll('.pantalla').forEach(p => p.classList.remove('activa'));
    document.getElementById(id).classList.add('activa');
}

// Esperar a que el DOM cargue
document.addEventListener('DOMContentLoaded', () => {
    // Botón "Comenzar" (Cargar Imagen)
    const btnCargar = document.getElementById('btn-cargar');
    if (btnCargar) {
        btnCargar.addEventListener('click', () => {
            mostrarPantalla('pantalla-carga');
        });
    }

    // Botón "Ver Registros"
    const btnExpedientes = document.getElementById('btn-ver-expedientes');
    if (btnExpedientes) {
        btnExpedientes.addEventListener('click', () => {
            mostrarPantalla('pantalla-expedientes');
        });
    }

    const areaCarga = document.getElementById('area-carga');
    const inputFile = document.getElementById('input-imagen');
    const nombreInput = document.getElementById('nombre-paciente');
    const btnProcesar = document.getElementById('btn-procesar');
    const previewContainer = document.getElementById('preview-container');
    const vistaPrevia = document.getElementById('vista-previa');
    const btnRemover = document.getElementById('btn-remover');


    let imagenSeleccionada = null;

    function validarFormulario() {
        const nombreValido = nombreInput && nombreInput.value.trim() !== '';
        btnProcesar.disabled = !(nombreValido && imagenSeleccionada);
    }

    if (areaCarga) {
        areaCarga.addEventListener('click', () => {
            inputFile.click();
        });
    }

    if (inputFile) {
        inputFile.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const ext = file.name.split('.').pop().toLowerCase();
                if (!['jpg', 'jpeg', 'png'].includes(ext)) {
                    alert('Formato no válido. Use JPG, JPEG o PNG.');
                    return;
                }
                // Mostrar preview
                const reader = new FileReader();
                reader.onload = function(ev) {
                    vistaPrevia.src = ev.target.result;
                    previewContainer.style.display = 'block';
                    areaCarga.style.display = 'none';
                    imagenSeleccionada = file;
                    validarFormulario();
                };
                reader.readAsDataURL(file);
            }
        });
    }

    if (btnRemover) {
        btnRemover.addEventListener('click', () => {
            previewContainer.style.display = 'none';
            areaCarga.style.display = 'block';
            imagenSeleccionada = null;
            inputFile.value = '';
            validarFormulario();
        });
    }

    if (nombreInput) {
        nombreInput.addEventListener('input', validarFormulario);
    }

    // Evento del botón procesar (por ahora solo muestra alerta)
    if (btnProcesar) {
        btnProcesar.addEventListener('click', () => {
            if (!btnProcesar.disabled) {
                let procesando = false;
                let timeoutId = null;

                if (btnProcesar) {
                    btnProcesar.addEventListener('click', () => {
                        if (procesando) return;
                        const nombre = nombreInput.value.trim();
                        if (!nombre || !imagenSeleccionada) return;

                        procesando = true;
                        document.getElementById('overlay-procesando').style.display = 'flex';
                        document.getElementById('nombre-procesando').innerText = nombre;

                        // Simular procesamiento (3 segundos)
                        timeoutId = setTimeout(() => {
                            // Ocultar overlay
                            document.getElementById('overlay-procesando').style.display = 'none';
                            procesando = false;
                            // Redirigir a expedientes (aunque aún no haya datos reales)
                            mostrarPantalla('pantalla-expedientes');
                            // Limpiar campos
                            nombreInput.value = '';
                            imagenSeleccionada = null;
                            previewContainer.style.display = 'none';
                            areaCarga.style.display = 'block';
                            inputFile.value = '';
                            validarFormulario();
                        }, 3000);
                    });
                }

                // Cancelar procesamiento
                const btnCancelar = document.getElementById('btn-cancelar-procesamiento');
                if (btnCancelar) {
                    btnCancelar.addEventListener('click', () => {
                        if (timeoutId) {
                            clearTimeout(timeoutId);
                            timeoutId = null;
                        }
                        document.getElementById('overlay-procesando').style.display = 'none';
                        procesando = false;
                        alert('Procesamiento cancelado');
                    });
                }
            }
        });
    }

    // --- Pantalla de expedientes (mock) ---
    function cargarExpedientesMock() {
        const lista = document.getElementById('lista-expedientes');
        if (!lista) return;

        // Datos de ejemplo
        const expedientes = [
            { nombre: "Juan Pérez", fecha: "10 de abril de 2026, 21:38", piezas: 30 },
            { nombre: "María García", fecha: "9 de abril de 2026, 15:22", piezas: 28 },
            { nombre: "Carlos López", fecha: "8 de abril de 2026, 10:05", piezas: 32 }
        ];

        lista.innerHTML = expedientes.map(exp => `
            <div class="tarjeta-expediente" data-nombre="${exp.nombre}">
                <div class="info-expediente">
                    <strong>${exp.nombre}</strong>
                    <small>${exp.fecha} | ${exp.piezas} piezas segmentadas</small>
                </div>
                <button class="btn-ver-detalles">Ver Detalles</button>
            </div>
        `).join('');

        // Asignar eventos a los botones "Ver Detalles"
        document.querySelectorAll('.btn-ver-detalles').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const card = e.target.closest('.tarjeta-expediente');
                const nombre = card.dataset.nombre;
                alert(`Ver detalles de ${nombre} (próximamente)`);
                // Aquí después mostraremos la pantalla de detalles con métricas reales
            });
        });
    }

    // Llamar a la función cuando se muestre la pantalla de expedientes
    // Por ahora, cada vez que se navegue a ella, recargamos los datos.
    // Podemos sobreescribir la función mostrarPantalla para que al mostrar 'pantalla-expedientes' recargue.
    const originalMostrarPantalla = mostrarPantalla;
    window.mostrarPantalla = function(id) {
        originalMostrarPantalla(id);
        if (id === 'pantalla-expedientes') {
            cargarExpedientesMock();
        }
    };
});