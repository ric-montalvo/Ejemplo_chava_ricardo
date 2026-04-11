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
                alert(`Procesando imagen para ${nombreInput.value}...`);
                // Aquí después integraremos la llamada a Python
            }
        });
    }
});