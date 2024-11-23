// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Variable para la tabla de DataTables
    const tablaJugadores = {
        instancia: null
    };

    // Inicializar la tabla de jugadores solo si estamos en la pestaña de jugadores
    if (document.getElementById('jugadoresTable')) {
        initJugadoresTable();
    }

    // Inicializar la tabla de jugadores
    function initJugadoresTable() {
        tablaJugadores.instancia = $('#jugadoresTable').DataTable({
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.10.24/i18n/Spanish.json'
            },
            ajax: {
                url: '/api/jugadores',
                dataSrc: ''
            },
            columns: [
                { data: 'nombre' },
                { data: 'equipo' },
                { data: 'posicion' },
                { data: 'edad' },
                { data: 'altura' },
                { data: 'puntos_por_partido' },
                {
                    data: null,
                    render: function(data, type, row) {
                        return `<button class="btn btn-sm btn-info ver-detalles" data-id="${row.id}">Ver Detalles</button>`;
                    }
                }
            ]
        });
    }

    // Cargar detalles del jugador
    async function cargarDetallesJugador(id) {
        try {
            const response = await fetch(`/api/jugadores/${id}`);
            const jugador = await response.json();
            
            const detallesHTML = `
                <div class="table-responsive">
                    <table class="table">
                        <tr>
                            <th>Nombre:</th>
                            <td>${jugador.nombre}</td>
                        </tr>
                        <tr>
                            <th>Equipo:</th>
                            <td>${jugador.equipo}</td>
                        </tr>
                        <tr>
                            <th>Posición:</th>
                            <td>${jugador.posicion}</td>
                        </tr>
                        <tr>
                            <th>Edad:</th>
                            <td>${jugador.edad}</td>
                        </tr>
                        <tr>
                            <th>Altura:</th>
                            <td>${jugador.altura}</td>
                        </tr>
                        <tr>
                            <th>Universidad:</th>
                            <td>${jugador.universidad || '-'}</td>
                        </tr>
                        <tr>
                            <th>País:</th>
                            <td>${jugador.pais}</td>
                        </tr>
                        <tr>
                            <th>Partidos Jugados:</th>
                            <td>${jugador.partidos_jugados}</td>
                        </tr>
                        <tr>
                            <th>Puntos por Partido:</th>
                            <td>${jugador.puntos_por_partido}</td>
                        </tr>
                        <tr>
                            <th>Rebotes por Partido:</th>
                            <td>${jugador.rebotes_por_partido}</td>
                        </tr>
                        <tr>
                            <th>Asistencias por Partido:</th>
                            <td>${jugador.asistencias_por_partido}</td>
                        </tr>
                    </table>
                </div>
            `;
            
            document.getElementById('jugadorDetalles').innerHTML = detallesHTML;
            new bootstrap.Modal(document.getElementById('jugadorModal')).show();
        } catch (error) {
            console.error('Error al cargar detalles del jugador:', error);
            alert('Error al cargar los detalles del jugador');
        }
    }

    // Event Listeners - Solo agregar si estamos en la pestaña de jugadores
    const tablaJugadoresElement = document.getElementById('jugadoresTable');
    if (tablaJugadoresElement) {
        tablaJugadoresElement.addEventListener('click', function(e) {
            const botonDetalles = e.target.closest('.ver-detalles');
            if (botonDetalles) {
                const jugadorId = botonDetalles.dataset.id;
                cargarDetallesJugador(jugadorId);
            }
        });
    }

    // Manejar el cambio de pestañas
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function (event) {
            if (event.target.getAttribute('href') === '#jugadores') {
                // Reinicializar la tabla si es necesario
                if (tablaJugadores.instancia) {
                    tablaJugadores.instancia.ajax.reload();
                }
            }
        });
    });
});