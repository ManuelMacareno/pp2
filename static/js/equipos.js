// static/js/equipos.js
document.addEventListener('DOMContentLoaded', function() {
    const posiciones = ['Base', 'Escolta', 'Alero', 'Ala-pívot', 'Pívot'];
    let equipoActual = {
        titulares: Array(5).fill(null),
        suplentes: Array(5).fill(null)
    };
    let jugadoresCargados = [];

    // Inicializar búsqueda y filtros
    const searchInput = document.getElementById('searchPlayer');
    const positionFilter = document.getElementById('positionFilter');
    const searchResults = document.getElementById('searchResults');
    const saveTeamButton = document.getElementById('saveTeamButton');

    // Event listeners para búsqueda
    searchInput.addEventListener('input', filtrarJugadores);
    positionFilter.addEventListener('change', filtrarJugadores);

    // Cargar todos los jugadores al iniciar
    cargarTodosLosJugadores();

    // Función para verificar si el equipo está completo
    function equipoEstaCompleto() {
        const titularesCompletos = equipoActual.titulares.every(jugador => jugador !== null);
        const suplentesCompletos = equipoActual.suplentes.every(jugador => jugador !== null);
        return titularesCompletos && suplentesCompletos;
    }

    // Función para actualizar el estado del botón de guardar
    function actualizarBotonGuardar() {
        const estaCompleto = equipoEstaCompleto();
        if (saveTeamButton) {
            saveTeamButton.disabled = !estaCompleto;
            saveTeamButton.classList.toggle('btn-success', estaCompleto);
            saveTeamButton.classList.toggle('btn-secondary', !estaCompleto);
            
            if (!estaCompleto) {
                const jugadoresFaltantes = 10 - (
                    equipoActual.titulares.filter(Boolean).length + 
                    equipoActual.suplentes.filter(Boolean).length
                );
                saveTeamButton.title = `Faltan ${jugadoresFaltantes} jugadores para completar el equipo`;
            } else {
                saveTeamButton.title = 'Guardar equipo';
            }
        }
    }

    // Función para cargar todos los jugadores
    async function cargarTodosLosJugadores() {
        try {
            const promises = posiciones.map(pos => 
                fetch(`/api/jugadores_por_posicion/${pos}`)
                    .then(res => res.json())
            );
            const resultados = await Promise.all(promises);
            jugadoresCargados = resultados.flat();
            mostrarResultadosBusqueda(jugadoresCargados);
        } catch (error) {
            console.error('Error al cargar jugadores:', error);
        }
    }

    // Función para filtrar jugadores
    function filtrarJugadores() {
        const searchTerm = searchInput.value.toLowerCase();
        const positionTerm = positionFilter.value;

        const jugadoresFiltrados = jugadoresCargados.filter(jugador => {
            const matchName = jugador.nombre.toLowerCase().includes(searchTerm);
            const matchPosition = !positionTerm || jugador.posicion === positionTerm;
            return matchName && matchPosition;
        });
        mostrarResultadosBusqueda(jugadoresFiltrados);
    }

    // Función para mostrar los resultados de la búsqueda
    function mostrarResultadosBusqueda(jugadores) {
        searchResults.innerHTML = '';
        
        // Mostrar mensaje si no hay resultados
        if (jugadores.length === 0) {
            searchResults.innerHTML = '<div class="text-center text-muted">No se encontraron jugadores</div>';
            return;
        }

        jugadores.forEach(jugador => {
            const isSelected = estaJugadorSeleccionado(jugador.id);
            const card = document.createElement('div');
            card.className = `player-card ${isSelected ? 'selected' : ''} bg-dark text-white mb-2 p-3 rounded`;
            card.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="position-badge badge bg-primary">${jugador.posicion}</span>
                        <span class="fw-bold ms-2">${jugador.nombre}</span>
                    </div>
                    <div class="stats-container">
                        <span class="badge bg-info me-1">PPP: ${jugador.puntos_por_partido}</span>
                        <span class="badge bg-success me-1">RPP: ${jugador.rebotes_por_partido}</span>
                        <span class="badge bg-warning">APP: ${jugador.asistencias_por_partido}</span>
                    </div>
                </div>
                <div class="mt-2 text-muted">
                    <small>Equipo: ${jugador.equipo}</small>
                </div>
            `;

            if (!isSelected) {
                card.addEventListener('click', () => seleccionarJugador(jugador));
            }

            searchResults.appendChild(card);
        });
    }

    // Función para verificar si un jugador está seleccionado
    function estaJugadorSeleccionado(jugadorId) {
        return equipoActual.titulares.includes(jugadorId) || 
               equipoActual.suplentes.includes(jugadorId);
    }

    // Función para mostrar detalles del jugador
    async function mostrarDetallesJugador(jugadorId) {
        try {
            const response = await fetch(`/api/jugadores/${jugadorId}`);
            const jugador = await response.json();
            
            const modal = document.getElementById('jugadorModal');
            const detalles = document.getElementById('jugadorDetalles');
            
            detalles.innerHTML = `
                <div class="card bg-dark text-white">
                    <div class="card-body">
                        <h4 class="card-title text-primary">${jugador.nombre}</h4>
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Posición:</strong> ${jugador.posicion}</p>
                                <p><strong>Equipo:</strong> ${jugador.equipo}</p>
                                <p><strong>Edad:</strong> ${jugador.edad} años</p>
                                <p><strong>Altura:</strong> ${jugador.altura} m</p>
                                <p><strong>Universidad:</strong> ${jugador.universidad || 'N/A'}</p>
                                <p><strong>País:</strong> ${jugador.pais}</p>
                            </div>
                            <div class="col-md-6">
                                <h5 class="text-warning">Estadísticas</h5>
                                <p><strong>PPP:</strong> ${jugador.puntos_por_partido}</p>
                                <p><strong>RPP:</strong> ${jugador.rebotes_por_partido}</p>
                                <p><strong>APP:</strong> ${jugador.asistencias_por_partido}</p>
                                <p><strong>Partidos jugados:</strong> ${jugador.partidos_jugados}</p>
                                <p><strong>% Tiro efectivo:</strong> ${jugador.porcentaje_tiro_efectivo}%</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();
        } catch (error) {
            console.error('Error al cargar detalles del jugador:', error);
        }
    }

    // Función para crear la card de un jugador
    function crearCardJugador(jugador, tipo, index) {
        const div = document.createElement('div');
        div.className = 'player-card bg-dark text-white mb-2 p-3 rounded';
        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <span class="position-badge badge bg-primary">${jugador.posicion}</span>
                    <span class="fw-bold ms-2">${jugador.nombre}</span>
                </div>
                <div>
                    <button class="btn btn-link text-info me-2 view-details" 
                            data-jugador-id="${jugador.id}">
                        <i class="fas fa-info-circle"></i>
                    </button>
                    <button class="btn btn-sm btn-danger remove-player" 
                            data-tipo="${tipo}" 
                            data-index="${index}">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;

        // Event listener para ver detalles
        const viewDetailsBtn = div.querySelector('.view-details');
        viewDetailsBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            mostrarDetallesJugador(jugador.id);
        });

        // Event listener para remover jugador
        const removeBtn = div.querySelector('.remove-player');
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            removerJugador(tipo, index);
        });

        return div;
    }

    // Función para seleccionar un jugador
    function seleccionarJugador(jugador) {
        const posicionIndex = posiciones.indexOf(jugador.posicion);

        if (equipoActual.titulares[posicionIndex] === null) {
            equipoActual.titulares[posicionIndex] = jugador.id;
        } else if (equipoActual.suplentes[posicionIndex] === null) {
            equipoActual.suplentes[posicionIndex] = jugador.id;
        } else {
            alert('Ya hay dos jugadores seleccionados para esta posición');
            return;
        }

        actualizarVistaEquipo();
        filtrarJugadores();
        actualizarBotonGuardar();
    }

    // Función para remover un jugador del equipo
    function removerJugador(tipo, index) {
        if (tipo === 'titular') {
            equipoActual.titulares[index] = null;
        } else {
            equipoActual.suplentes[index] = null;
        }
        
        actualizarVistaEquipo();
        filtrarJugadores();
        actualizarBotonGuardar();
    }

    // Función para actualizar la vista del equipo
    function actualizarVistaEquipo() {
        const titularesContainer = document.getElementById('titularesContainer');
        const suplentesContainer = document.getElementById('suplentesContainer');

        titularesContainer.innerHTML = '';
        suplentesContainer.innerHTML = '';

        equipoActual.titulares.forEach((jugadorId, index) => {
            if (jugadorId) {
                const jugador = jugadoresCargados.find(j => j.id === jugadorId);
                titularesContainer.appendChild(crearCardJugador(jugador, 'titular', index));
            }
        });

        equipoActual.suplentes.forEach((jugadorId, index) => {
            if (jugadorId) {
                const jugador = jugadoresCargados.find(j => j.id === jugadorId);
                suplentesContainer.appendChild(crearCardJugador(jugador, 'suplente', index));
            }
        });
    }

    // Event listener para los jugadores en la página de mis equipos
    if (window.location.pathname === '/mis_equipos') {
        document.querySelectorAll('.list-group-item').forEach(item => {
            item.addEventListener('click', function() {
                const jugadorId = this.dataset.jugadorId;
                if (jugadorId) {
                    mostrarDetallesJugador(jugadorId);
                }
            });
        });
    }

    // Inicializar botón de guardar
    actualizarBotonGuardar();
});