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
});