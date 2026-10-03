/**
 * Mi Profesor de Matemáticas Personal
 * Aplicación principal - Frontend
 */

// ============================================================
// ESTADO GLOBAL
// ============================================================
const Estado = {
    perfil: null,
    leccionActual: null,
    ejercicioActual: null,
    timerInicio: null,
    timerSegundos: 0,
    intentosActuales: 0,
    pistasMostradas: 0,
    usaAyuda: false,
    historialOffset: 0,
    dificultadActual: 1,

    // Flujo Khan Academy (Teoría -> Práctica -> Examen)
    faseActual: 'teoria',
    teoriaData: null,
    ejerciciosPracticaResueltos: 0,
    examenPreguntas: [],
    examenPreguntaIdx: 0,
    examenRespuestas: [],

    // Diagnóstico
    diagPreguntas: [],
    diagPreguntaIdx: 0,
    diagResultados: [],
    diagTimerInicio: null,

    // Charts
    chartProgreso: null,
    chartEvolucion: null,
    chartNiveles: null,
};

const NOMBRES_NIVELES = {
    1: 'Sumas y restas',
    2: 'Multiplicaciones',
    3: 'Divisiones',
    4: 'Fracciones y decimales',
    5: 'Potencias y raíces',
    6: 'Álgebra',
    7: 'Matemáticas para Ingeniería',
};

const COLORES_NIVEL = [
    '#22c55e', '#3b82f6', '#8b5cf6', '#f59e0b',
    '#ef4444', '#06b6d4', '#f43f5e',
];

const TIPOS_ERROR = {
    'error_calculo': '🔢 Error de cálculo',
    'error_procedimiento': '📝 Error de procedimiento',
    'error_signo': '➕➖ Confusión de signos',
    'error_posicional': '📍 Error posicional',
    'error_formato': '✏️ Error de formato',
    'respuesta_azar': '🎲 Respuesta al azar',
};

// Renderizador KaTeX para tipografía matemática profesional
function renderMatematicas(elemento) {
    if (window.renderMathInElement && elemento) {
        try {
            window.renderMathInElement(elemento, {
                delimiters: [
                    {left: '$$', right: '$$', display: true},
                    {left: '$', right: '$', display: false},
                    {left: '\\(', right: '\\)', display: false},
                    {left: '\\[', right: '\\]', display: true}
                ],
                throwOnError: false
            });
        } catch (e) {
            console.warn('KaTeX render notice:', e);
        }
    }
}


// ============================================================
// INICIALIZACIÓN
// ============================================================
document.addEventListener('DOMContentLoaded', async () => {
    await cargarPerfil();

    const seccionGuardada = localStorage.getItem('ultimaSeccion');
    const evaluacionOmitida = localStorage.getItem('evaluacionOmitida') === 'true';

    // Si ya completó la evaluación, o ya decidió omitirla, o ya tiene ejercicios resueltos,
    // o ya estaba navegando en una sección previa:
    const yaInicio = Estado.perfil && (
        Estado.perfil.evaluacion_inicial_completada ||
        evaluacionOmitida ||
        (seccionGuardada && seccionGuardada !== 'diagnostico')
    );

    if (!yaInicio) {
        navegarA('diagnostico');
    } else {
        const destino = (seccionGuardada && seccionGuardada !== 'diagnostico') ? seccionGuardada : 'dashboard';
        navegarA(destino);
    }
});


// ============================================================
// NAVEGACIÓN
// ============================================================
function navegarA(seccion) {
    // Recordar la última sección para no perder el progreso al cerrar o recargar
    try {
        localStorage.setItem('ultimaSeccion', seccion);
    } catch (e) {
        // En caso de modo incógnito restrictivo
    }

    // Ocultar todas las secciones
    document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));

    // Desactivar todos los tabs
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));

    // Mostrar la sección
    const vista = document.getElementById(`view-${seccion}`);
    if (vista) {
        vista.classList.add('active');
    }

    // Activar el tab
    const tab = document.querySelector(`.nav-tab[data-tab="${seccion}"]`);
    if (tab) tab.classList.add('active');

    // Cargar datos según la sección
    switch (seccion) {
        case 'dashboard': cargarDashboard(); break;
        case 'lecciones': cargarLecciones(); break;
        case 'practicar': cargarLeccionesDisponibles(); break;
        case 'progreso': cargarProgreso(); break;
        case 'historial': cargarHistorial(); break;
        case 'logros': cargarLogros(); break;
        case 'ajustes': cargarAjustes(); break;
    }
}


// ============================================================
// API HELPERS
// ============================================================
async function api(url, options = {}) {
    const defaultOptions = {
        headers: { 'Content-Type': 'application/json' },
    };

    if (options.body && typeof options.body === 'object') {
        options.body = JSON.stringify(options.body);
    }

    const response = await fetch(url, { ...defaultOptions, ...options });
    return response.json();
}


// ============================================================
// PERFIL
// ============================================================
async function cargarPerfil() {
    try {
        Estado.perfil = await api('/api/perfil');
        actualizarHeader();
    } catch (e) {
        console.error('Error cargando perfil:', e);
    }
}

function actualizarHeader() {
    if (!Estado.perfil) return;
    document.getElementById('headerRacha').textContent = Estado.perfil.racha_actual || 0;
}


// ============================================================
// EVALUACIÓN DIAGNÓSTICA
// ============================================================
async function omitirDiagnostico() {
    try {
        localStorage.setItem('evaluacionOmitida', 'true');
        await api('/api/perfil', {
            method: 'PUT',
            body: { evaluacion_inicial_completada: 1 }
        });
        if (Estado.perfil) Estado.perfil.evaluacion_inicial_completada = true;
    } catch (e) {
        console.warn('Error guardando omisión de diagnóstico:', e);
    }
    navegarA('dashboard');
    mostrarToast('👋 ¡Bienvenido!', 'Explora tus lecciones y aprende a tu propio ritmo.');
}

async function iniciarDiagnostico() {
    document.getElementById('diagnosticoWelcome').classList.add('hidden');
    document.getElementById('diagnosticoArea').classList.remove('hidden');

    Estado.diagPreguntas = await api('/api/diagnostico/generar');
    Estado.diagPreguntaIdx = 0;
    Estado.diagResultados = [];

    document.getElementById('diagPreguntaTotal').textContent = Estado.diagPreguntas.length;
    mostrarPreguntaDiagnostico();
}

function mostrarPreguntaDiagnostico() {
    const pregunta = Estado.diagPreguntas[Estado.diagPreguntaIdx];
    document.getElementById('diagPreguntaActual').textContent = Estado.diagPreguntaIdx + 1;
    document.getElementById('diagNivel').textContent = `Nivel ${pregunta.nivel} - ${pregunta.tema}`;
    document.getElementById('diagOperacion').textContent = pregunta.operacion;
    document.getElementById('diagRespuesta').value = '';
    document.getElementById('diagRespuesta').focus();

    // Contador silencioso para diagnóstico
    Estado.diagTimerInicio = Date.now();

    const progreso = ((Estado.diagPreguntaIdx) / Estado.diagPreguntas.length) * 100;
    document.getElementById('diagProgressBar').style.width = `${progreso}%`;

    // Renderizado KaTeX si hay expresiones matemáticas
    renderMatematicas(document.getElementById('diagnosticoArea'));
}

async function verificarDiagnostico() {
    const respuesta = document.getElementById('diagRespuesta').value.trim();
    if (!respuesta) return;

    const pregunta = Estado.diagPreguntas[Estado.diagPreguntaIdx];
    const tiempoSegundos = Math.max(1, Math.round((Date.now() - (Estado.diagTimerInicio || Date.now())) / 1000));

    // Verificación local
    const esCorrecta = verificarLocal(respuesta, pregunta.respuesta_correcta);

    Estado.diagResultados.push({
        nivel: pregunta.nivel,
        tema: pregunta.tema,
        operacion: pregunta.operacion,
        respuesta_usuario: respuesta,
        respuesta_correcta: pregunta.respuesta_correcta,
        correcto: esCorrecta,
        desconocido: false,
        tiempo_segundos: tiempoSegundos,
    });

    avanzarDiagnostico();
}

function marcarTemaNoConocido() {
    const pregunta = Estado.diagPreguntas[Estado.diagPreguntaIdx];
    const tiempoSegundos = Math.max(1, Math.round((Date.now() - (Estado.diagTimerInicio || Date.now())) / 1000));

    Estado.diagResultados.push({
        nivel: pregunta.nivel,
        tema: pregunta.tema,
        operacion: pregunta.operacion,
        respuesta_usuario: 'No conozco este tema',
        respuesta_correcta: pregunta.respuesta_correcta,
        correcto: false,
        desconocido: true,
        tiempo_segundos: tiempoSegundos,
    });

    avanzarDiagnostico();
}

function saltarDiagnostico() {
    const pregunta = Estado.diagPreguntas[Estado.diagPreguntaIdx];
    const tiempoSegundos = Math.max(1, Math.round((Date.now() - (Estado.diagTimerInicio || Date.now())) / 1000));

    Estado.diagResultados.push({
        nivel: pregunta.nivel,
        tema: pregunta.tema,
        operacion: pregunta.operacion,
        respuesta_usuario: '',
        respuesta_correcta: pregunta.respuesta_correcta,
        correcto: false,
        desconocido: false,
        tiempo_segundos: tiempoSegundos,
    });

    avanzarDiagnostico();
}

async function avanzarDiagnostico() {
    Estado.diagPreguntaIdx++;

    if (Estado.diagPreguntaIdx >= Estado.diagPreguntas.length) {
        await finalizarDiagnostico();
    } else {
        mostrarPreguntaDiagnostico();
    }
}

async function finalizarDiagnostico() {
    document.getElementById('diagnosticoArea').classList.add('hidden');

    const analisis = await api('/api/diagnostico/evaluar', {
        method: 'POST',
        body: { resultados: Estado.diagResultados },
    });

    // Mostrar resultados
    const container = document.getElementById('diagnosticoResultados');
    container.classList.remove('hidden');

    let html = `
        <div class="diagnostic-welcome">
            <h1>¡Evaluación completada!</h1>
            <p>He analizado tus respuestas y preparé tu ruta de aprendizaje personalizada.</p>

            <div class="card mb-6" style="text-align: left;">
                <div class="card-title mb-4">📊 Resultados por nivel</div>
    `;

    for (const r of analisis.resultados) {
        const porcentaje = r.porcentaje.toFixed(0);
        const color = porcentaje >= 80 ? 'var(--color-success)' :
                      porcentaje >= 50 ? 'var(--color-warning)' : 'var(--color-error)';

        html += `
            <div style="margin-bottom: 16px;">
                <div class="flex items-center justify-between mb-2">
                    <span>${r.tema}</span>
                    <span style="color: ${color}; font-weight: 700;">${porcentaje}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-bar-fill" style="width: ${porcentaje}%; background: ${color};"></div>
                </div>
                <div class="text-muted" style="font-size: var(--text-sm); margin-top: 4px;">${r.recomendacion}</div>
            </div>
        `;
    }

    html += `
            </div>
            <div class="card mb-6" style="text-align: center;">
                <div style="font-size: var(--text-xl); margin-bottom: 8px;">
                    Comenzaremos en el <strong>Nivel ${analisis.nivel_recomendado}</strong>
                </div>
                <div class="text-muted">${NOMBRES_NIVELES[analisis.nivel_recomendado]}</div>
            </div>
            <button class="btn btn-success btn-lg" onclick="comenzarAprendizaje()">
                ¡Empezar a aprender! 🚀
            </button>
        </div>
    `;

    container.innerHTML = html;
}

async function comenzarAprendizaje() {
    await cargarPerfil();
    navegarA('dashboard');
}


const FRASES_MOTIVACIONALES = [
    "Aprender matemáticas no es una carrera de velocidad, es un camino paso a paso. ¡Aquí no hay prisa!",
    "Como futuro Ingeniero de Sistemas, cada concepto que aprendes hoy será una herramienta poderosa en tus algoritmos.",
    "Los errores son solo datos de depuración (debugging) para tu mente. Equivocarse es la forma natural de aprender.",
    "No necesitas tener un talento innato: con paciencia, curiosidad y práctica constante, las dominarás con soltura.",
    "Tu cerebro crea nuevas conexiones neuronales cada vez que piensas con calma en un problema. ¡Vamos con todo!",
    "Este es tu espacio seguro: sin calificaciones punitivas, sin presiones de tiempo y con explicaciones paso a paso.",
    "Cada pequeño ejercicio resuelto suma a tu confianza. Celebra cada acierto, por pequeño que parezca."
];

function actualizarFraseMotivacional() {
    const el = document.getElementById('welcomeMotivationalQuote');
    if (el) {
        const frase = FRASES_MOTIVACIONALES[Math.floor(Math.random() * FRASES_MOTIVACIONALES.length)];
        el.innerHTML = `✨ "${frase}"`;
    }
}

// ============================================================
// DASHBOARD
// ============================================================
async function cargarDashboard() {
    try {
        actualizarFraseMotivacional();

        const [stats, perfil, lecciones, repasosData] = await Promise.all([
            api('/api/estadisticas'),
            api('/api/perfil'),
            api('/api/lecciones'),
            api('/api/repasos/hoy').catch(() => ({ total: 0, repasos: [] })),
        ]);

        Estado.perfil = perfil;
        actualizarHeader();

        // Repetición Espaciada SM-2 Banner (Día 1, 3, 7, 21)
        const sm2Banner = document.getElementById('spacedRepetitionBanner');
        if (sm2Banner) {
            if (repasosData && repasosData.total > 0) {
                sm2Banner.classList.remove('hidden');
                sm2Banner.innerHTML = `
                    <div class="card" style="border: 2px solid var(--color-primary); background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(139, 92, 246, 0.08));">
                        <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
                            <div class="flex items-center gap-3">
                                <span style="font-size: 2rem;">🔔</span>
                                <div>
                                    <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: var(--color-primary-light);">
                                        Repaso Espaciado SM-2 conectado a tu Racha Diaria 🔥
                                    </h3>
                                    <p class="text-muted" style="margin: 0; font-size: var(--text-sm);">
                                        Tienes <strong>${repasosData.total} tema(s)</strong> listos para repasar hoy antes de tu nueva lección (fija conceptos en memoria permanente).
                                    </p>
                                </div>
                            </div>
                            <span class="badge badge-warning" style="font-size: 0.85rem; padding: 6px 12px;">⚡ Prioridad de hoy</span>
                        </div>
                        <div class="flex flex-col gap-2 mt-2">
                            ${repasosData.repasos.map(r => `
                                <div class="flex items-center justify-between p-3 rounded-lg" style="background: rgba(255,255,255,0.05); border: 1px solid var(--border-color); flex-wrap: wrap; gap: 8px;">
                                    <div class="flex items-center gap-3">
                                        <span class="badge badge-info">Lección ${r.leccion_id}</span>
                                        <div>
                                            <strong style="color: var(--text-bright);">${r.titulo}</strong>
                                            <div class="text-muted" style="font-size: var(--text-xs);">${r.descripcion || ''}</div>
                                        </div>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <button class="btn btn-sm btn-primary" onclick="iniciarPractica('${r.leccion_id}')">
                                            Repasar lección ✏️
                                        </button>
                                        <button class="btn btn-sm btn-outline" title="Marcar completado" onclick="marcarRepasoCompletado(${r.id}, '${r.leccion_id}')">
                                            ✓ Hecho
                                        </button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            } else {
                sm2Banner.classList.add('hidden');
                sm2Banner.innerHTML = '';
            }
        }

        // Stat cards
        document.getElementById('dashTotalEjercicios').textContent = stats.total_ejercicios;
        document.getElementById('dashPorcentaje').textContent = `${stats.porcentaje_aciertos}%`;
        document.getElementById('dashRacha').textContent = perfil.racha_actual || 0;
        document.getElementById('dashTiempo').textContent = `${stats.tiempo_total_minutos} min`;
        document.getElementById('headerAciertos').textContent = `${stats.porcentaje_aciertos}%`;
        document.getElementById('headerEjercicios').textContent = stats.total_ejercicios;

        // Recomendaciones
        const recsContainer = document.getElementById('dashRecomendaciones');
        const disponibles = lecciones.filter(l => l.estado === 'disponible' || (l.estado !== 'bloqueado' && l.porcentaje_dominio < 80));
        const recomendadas = disponibles.slice(0, 3);

        if (recomendadas.length === 0) {
            recsContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🎉</div>
                    <div class="empty-state-text">¡Haz tu evaluación inicial!</div>
                    <div class="empty-state-desc">Comienza practicando con las lecciones disponibles.</div>
                    <button class="btn btn-primary mt-4" onclick="navegarA('lecciones')">Ver lecciones</button>
                </div>
            `;
        } else {
            recsContainer.innerHTML = recomendadas.map(l => `
                <div class="lesson-card" onclick="iniciarPractica('${l.id}')">
                    <div class="lesson-card-header">
                        <span class="lesson-card-number">Lección ${l.id}</span>
                        <span class="badge ${l.porcentaje_dominio > 0 ? 'badge-warning' : 'badge-info'}">
                            ${l.porcentaje_dominio > 0 ? 'En progreso' : 'Nuevo'}
                        </span>
                    </div>
                    <div class="lesson-card-title">${l.titulo}</div>
                    <div class="lesson-card-desc">${l.descripcion}</div>
                    ${l.porcentaje_dominio > 0 ? `
                        <div class="lesson-card-progress">
                            <div class="lesson-card-percent">
                                <span>Dominio</span>
                                <span>${l.porcentaje_dominio.toFixed(0)}%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-bar-fill" style="width: ${l.porcentaje_dominio}%"></div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }

        // Chart: Progreso por nivel
        renderChartProgreso(stats);

        // Chart: Evolución
        renderChartEvolucion(stats);

    } catch (e) {
        console.error('Error cargando dashboard:', e);
    }
}

async function marcarRepasoCompletado(repasoId, leccionId) {
    try {
        await api(`/api/repasos/${repasoId}/completar`, {
            method: 'POST',
            body: { resultado: 100 }
        });
        mostrarToast('🎉', `¡Repaso de la Lección ${leccionId} completado! Siguiente intervalo SM-2 programado.`, 'achievement');
        cargarDashboard();
    } catch (e) {
        mostrarToast('❌', 'Error al completar el repaso', 'error');
    }
}

function renderChartProgreso(stats) {
    const ctx = document.getElementById('chartProgreso');
    if (!ctx) return;

    if (Estado.chartProgreso) Estado.chartProgreso.destroy();

    const niveles = [];
    const porcentajes = [];
    const colores = [];

    for (let i = 1; i <= 7; i++) {
        const nivelData = stats.por_nivel.find(n => n.nivel === i);
        niveles.push(`N${i}`);
        if (nivelData && nivelData.total > 0) {
            porcentajes.push(Math.round(nivelData.correctos / nivelData.total * 100));
        } else {
            porcentajes.push(0);
        }
        colores.push(COLORES_NIVEL[i - 1]);
    }

    Estado.chartProgreso = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: niveles,
            datasets: [{
                label: 'Aciertos %',
                data: porcentajes,
                backgroundColor: colores.map(c => c + '40'),
                borderColor: colores,
                borderWidth: 2,
                borderRadius: 8,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#8b8fa7', callback: v => v + '%' },
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#8b8fa7' },
                },
            },
        },
    });
}

function renderChartEvolucion(stats) {
    const ctx = document.getElementById('chartEvolucion');
    if (!ctx) return;

    if (Estado.chartEvolucion) Estado.chartEvolucion.destroy();

    const dias = stats.evolucion.map(e => {
        const d = new Date(e.dia);
        return `${d.getDate()}/${d.getMonth() + 1}`;
    });
    const totales = stats.evolucion.map(e => e.total);
    const correctos = stats.evolucion.map(e => e.correctos);

    Estado.chartEvolucion = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dias,
            datasets: [
                {
                    label: 'Total',
                    data: totales,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#6366f1',
                },
                {
                    label: 'Correctos',
                    data: correctos,
                    borderColor: '#22c55e',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#22c55e',
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#8b8fa7', usePointStyle: true },
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#8b8fa7' },
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#8b8fa7' },
                },
            },
        },
    });
}


let nivelFiltroActual = 'todos';

function filtrarNivel(nivel) {
    nivelFiltroActual = nivel;

    // Actualizar botones de filtro
    document.querySelectorAll('.level-filter-btn').forEach(btn => {
        const btnLevel = btn.getAttribute('data-level');
        if (btnLevel == nivel) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Mostrar u ocultar grupos de nivel
    document.querySelectorAll('.level-group').forEach(grupo => {
        const groupNivel = grupo.getAttribute('data-level');
        if (nivel === 'todos' || groupNivel == nivel) {
            grupo.style.display = 'block';
        } else {
            grupo.style.display = 'none';
        }
    });
}

// ============================================================
// LECCIONES
// ============================================================
async function cargarLecciones() {
    const lecciones = await api('/api/lecciones');

    const container = document.getElementById('leccionesContenido');
    let html = '';

    for (let nivel = 1; nivel <= 7; nivel++) {
        const leccionesNivel = lecciones.filter(l => l.nivel === nivel);
        const color = COLORES_NIVEL[nivel - 1];

        const totalDominio = leccionesNivel.reduce((sum, l) => sum + (l.porcentaje_dominio || 0), 0);
        const promedioDominio = leccionesNivel.length > 0 ? (totalDominio / leccionesNivel.length).toFixed(0) : 0;

        html += `
            <div class="level-group" data-level="${nivel}">
                <div class="level-header">
                    <div class="level-number" style="background: ${color}">${nivel}</div>
                    <div class="level-info">
                        <div class="level-title">${NOMBRES_NIVELES[nivel]}</div>
                        <div class="level-progress-text">Dominio promedio: ${promedioDominio}%</div>
                    </div>
                </div>
                <div class="level-lessons">
        `;

        for (const l of leccionesNivel) {
            const bloqueado = l.estado === 'bloqueado';
            const completado = l.porcentaje_dominio >= 80;
            const clases = `lesson-card ${bloqueado ? 'locked' : ''} ${completado ? 'completed' : ''}`;

            html += `
                <div class="${clases}" ${!bloqueado ? `onclick="iniciarPractica('${l.id}')"` : ''}>
                    <div class="lesson-card-header">
                        <span class="lesson-card-number">${l.id}</span>
                        <span class="lesson-card-status">
                            ${bloqueado ? '🔒' : completado ? '✅' : l.porcentaje_dominio > 0 ? '📝' : '🆕'}
                        </span>
                    </div>
                    <div class="lesson-card-title">${l.titulo}</div>
                    <div class="lesson-card-desc">${l.descripcion}</div>
                    ${!bloqueado ? `
                        <div class="lesson-card-progress">
                            <div class="lesson-card-percent">
                                <span>Dominio</span>
                                <span>${(l.porcentaje_dominio || 0).toFixed(0)}%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-bar-fill" style="width: ${l.porcentaje_dominio || 0}%; background: ${color}"></div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        html += '</div></div>';
    }

    container.innerHTML = html;
    filtrarNivel(nivelFiltroActual);
}


// ============================================================
// PRACTICAR
// ============================================================
async function cargarLeccionesDisponibles() {
    const lecciones = await api('/api/lecciones');
    const container = document.getElementById('leccionesDisponibles');

    const disponibles = lecciones.filter(l => l.estado !== 'bloqueado');

    if (disponibles.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📝</div>
                <div class="empty-state-text">Comienza con la evaluación diagnóstica</div>
            </div>
        `;
        return;
    }

    container.innerHTML = disponibles.map(l => {
        const color = COLORES_NIVEL[l.nivel - 1];
        return `
            <div class="lesson-card" onclick="iniciarPractica('${l.id}')">
                <div class="lesson-card-header">
                    <span class="lesson-card-number">
                        <span class="level-number" style="background: ${color}; width:28px; height:28px; font-size: var(--text-sm);">${l.nivel}</span>
                        Lección ${l.id}
                    </span>
                    <span class="badge ${l.porcentaje_dominio >= 80 ? 'badge-success' : l.porcentaje_dominio > 0 ? 'badge-warning' : 'badge-info'}">
                        ${l.porcentaje_dominio >= 80 ? 'Dominada' : l.porcentaje_dominio > 0 ? `${l.porcentaje_dominio.toFixed(0)}%` : 'Nueva'}
                    </span>
                </div>
                <div class="lesson-card-title">${l.titulo}</div>
                <div class="lesson-card-desc">${l.descripcion}</div>
            </div>
        `;
    }).join('');
}

async function iniciarPractica(leccionId) {
    navegarA('practicar');

    Estado.leccionActual = leccionId;
    Estado.dificultadActual = 1;
    Estado.intentosActuales = 0;
    Estado.pistasMostradas = 0;
    Estado.usaAyuda = false;
    Estado.ejerciciosPracticaResueltos = 0;
    Estado.ejercicioActual = null;

    document.getElementById('leccionSelector').classList.add('hidden');
    document.getElementById('temaActivoContainer').classList.remove('hidden');

    const leccion = await api(`/api/lecciones/${leccionId}`);
    document.getElementById('temaBadge').textContent = leccionId;
    document.getElementById('temaNombre').textContent = leccion.titulo;

    // Comenzar siempre por la Fase 1: Teoría (Aprender antes de resolver)
    await cambiarFaseTema('teoria');
}

async function cambiarFaseTema(fase) {
    Estado.faseActual = fase;

    // Actualizar botones de stepper
    ['Teoria', 'Practica', 'Examen'].forEach(f => {
        const btn = document.getElementById(`btnFase${f}`);
        if (btn) btn.classList.remove('active');
        const phaseDiv = document.getElementById(`fase${f}`);
        if (phaseDiv) phaseDiv.classList.add('hidden');
    });

    if (fase === 'teoria') {
        document.getElementById('btnFaseTeoria').classList.add('active');
        document.getElementById('faseTeoria').classList.remove('hidden');
        await cargarTeoriaLeccion(Estado.leccionActual);
    } else if (fase === 'practica') {
        document.getElementById('btnFasePractica').classList.add('active');
        document.getElementById('fasePractica').classList.remove('hidden');
        if (!Estado.ejercicioActual) {
            await generarNuevoEjercicio();
        } else {
            iniciarTimer();
        }
    } else if (fase === 'examen') {
        document.getElementById('btnFaseExamen').classList.add('active');
        document.getElementById('faseExamen').classList.remove('hidden');
        await iniciarExamen();
    }
}

async function cargarTeoriaLeccion(leccionId) {
    try {
        const data = await api(`/api/lecciones/${leccionId}/teoria`);
        const t = data.teoria;
        Estado.teoriaData = t;

        document.getElementById('teoriaTitulo').textContent = `${data.leccion_id}: ${t.titulo}`;
        document.getElementById('teoriaSubtitulo').textContent = t.subtitulo || '';
        document.getElementById('teoriaConcepto').textContent = t.concepto;
        document.getElementById('teoriaPorQue').textContent = t.por_que_funciona;
        document.getElementById('teoriaIngenieria').textContent = t.conexion_ingenieria;

        // Ejemplo modelo resuelto paso a paso
        if (t.ejemplo) {
            document.getElementById('teoriaEjemploProblema').textContent = t.ejemplo.problema;
            const pasosCont = document.getElementById('teoriaEjemploPasos');
            pasosCont.innerHTML = (t.ejemplo.pasos || []).map(paso => `
                <div class="example-step-item">
                    ${paso}
                </div>
            `).join('');
            document.getElementById('teoriaEjemploResultado').textContent = `✅ Resultado final comprobado: ${t.ejemplo.resultado}`;
        }

        // Errores comunes
        const erroresCont = document.getElementById('teoriaErrores');
        erroresCont.innerHTML = (t.errores_comunes || []).map(err => `
            <li>${err}</li>
        `).join('');

        // Truco del profesor
        document.getElementById('teoriaTruco').textContent = t.truco_profesor || 'Trabaja con calma y comprueba cada paso.';

        // Renderizado KaTeX
        renderMatematicas(document.getElementById('faseTeoria'));
    } catch (e) {
        console.error('Error cargando teoría:', e);
    }
}

async function generarNuevoEjercicio() {
    const ejercicio = await api('/api/ejercicio/generar', {
        method: 'POST',
        body: {
            leccion_id: Estado.leccionActual,
            dificultad: Estado.dificultadActual,
        },
    });

    Estado.ejercicioActual = ejercicio;
    Estado.intentosActuales = 0;
    Estado.pistasMostradas = 0;
    Estado.usaAyuda = false;

    // Mostrar ejercicio
    document.getElementById('ejOperacion').textContent = ejercicio.operacion;
    document.getElementById('ejDificultad').textContent = `Dificultad ${ejercicio.dificultad}`;
    document.getElementById('ejExplicacionPrevia').textContent = ejercicio.explicacion_previa || '';
    document.getElementById('ejExplicacionPrevia').classList.add('hidden');
    document.getElementById('ejRespuesta').value = '';
    document.getElementById('ejRespuesta').disabled = false;
    document.getElementById('ejFeedback').classList.add('hidden');
    document.getElementById('ejExplicacion').classList.add('hidden');
    document.getElementById('ejPostAcciones').classList.add('hidden');
    document.getElementById('ejAcciones').classList.remove('hidden');

    const btnPista = document.getElementById('btnPista');
    if (btnPista) {
        btnPista.disabled = false;
        btnPista.textContent = '💡 Pedir pista';
    }

    // Renderizado KaTeX
    renderMatematicas(document.getElementById('fasePractica'));

    document.getElementById('ejRespuesta').focus();

    // Contador silencioso (sin estrés de reloj en pantalla)
    iniciarTimer();
}

function volverASelector() {
    detenerTimer();
    document.getElementById('temaActivoContainer').classList.add('hidden');
    document.getElementById('leccionSelector').classList.remove('hidden');
    cargarLeccionesDisponibles();
}

// Contador Silencioso (Silent Timer)
function iniciarTimer() {
    Estado.timerInicio = Date.now();
    Estado.timerSegundos = 0;
}

function detenerTimer() {
    if (Estado.timerInicio) {
        Estado.timerSegundos = Math.max(1, Math.round((Date.now() - Estado.timerInicio) / 1000));
    }
}

function obtenerTiempoSilencioso() {
    if (Estado.timerInicio) {
        return Math.max(1, Math.round((Date.now() - Estado.timerInicio) / 1000));
    }
    return 1;
}

// Marcar "No sé" en práctica: revela respuesta correcta y explicación con empatía
async function marcarNoSePractica() {
    if (!Estado.ejercicioActual) return;
    Estado.usaAyuda = true;
    Estado.intentosActuales++;
    const tiempoSilencioso = obtenerTiempoSilencioso();
    detenerTimer();

    // Registrar intento en backend
    try {
        await api('/api/ejercicio/verificar', {
            method: 'POST',
            body: {
                leccion_id: Estado.leccionActual,
                respuesta_usuario: '(No sé)',
                respuesta_correcta: Estado.ejercicioActual.respuesta_correcta,
                operacion: Estado.ejercicioActual.operacion,
                tipo_ejercicio: Estado.ejercicioActual.tipo,
                tiempo_segundos: tiempoSilencioso,
                intentos: Estado.intentosActuales,
                uso_ayuda: 1,
                dificultad: Estado.ejercicioActual.dificultad,
            }
        });
    } catch (e) {
        console.warn('Registro silencioso:', e);
    }

    // Traer explicación paso a paso
    let explicacion = null;
    try {
        explicacion = await api('/api/ejercicio/explicacion', {
            method: 'POST',
            body: {
                leccion_id: Estado.leccionActual,
                operacion: Estado.ejercicioActual.operacion,
                respuesta_correcta: Estado.ejercicioActual.respuesta_correcta,
                respuesta_usuario: '(No sé)'
            }
        });
    } catch (e) {
        console.error(e);
    }

    const feedback = document.getElementById('ejFeedback');
    feedback.className = 'feedback feedback-friendly';
    feedback.style.background = 'rgba(99, 102, 241, 0.12)';
    feedback.style.border = '1px solid var(--color-primary)';
    feedback.innerHTML = `
        <div class="feedback-header" style="color: var(--color-primary-light);">
            <span>🌱</span> ¡No te preocupes por no saberlo! Así es como aprendemos
        </div>
        <div class="feedback-message" style="color: var(--color-text);">
            La respuesta correcta es: <strong class="badge badge-success" style="font-size: 1.15rem; padding: 4px 10px;">${Estado.ejercicioActual.respuesta_correcta}</strong>
        </div>
    `;
    feedback.classList.remove('hidden');

    const container = document.getElementById('ejExplicacion');
    container.classList.remove('hidden');

    let html = `
        <div class="card mt-4" style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--color-border);">
            <div class="card-title text-primary mb-3">📖 Explicación paso a paso de este ejercicio:</div>
            <div class="flex flex-col gap-2 mb-4">
    `;
    for (const paso of (explicacion?.pasos || [])) {
        html += `<div class="example-step-item">${paso}</div>`;
    }
    html += `
            </div>
            ${explicacion?.consejo ? `<div class="tip-box mb-3"><strong>💡 Consejo:</strong> ${explicacion.consejo}</div>` : ''}
            <div class="mt-2">
                <button class="btn btn-outline btn-sm" onclick="cambiarFaseTema('teoria')">
                    📖 Releer teoría completa
                </button>
            </div>
        </div>
    `;
    container.innerHTML = html;
    renderMatematicas(feedback);
    renderMatematicas(container);

    document.getElementById('ejAcciones').classList.add('hidden');
    document.getElementById('ejRespuesta').disabled = true;

    const postAcciones = document.getElementById('ejPostAcciones');
    postAcciones.innerHTML = `
        <button class="btn btn-primary btn-lg" onclick="generarNuevoEjercicio()">
            🔄 Practicar otro ejercicio similar
        </button>
        <button class="btn btn-outline btn-lg" onclick="cambiarFaseTema('teoria')">
            📖 Volver a la teoría
        </button>
    `;
    postAcciones.classList.remove('hidden');
}

async function mostrarAyudaCompleta() {
    return marcarNoSePractica();
}

// ============================================================
// FASE 3: EXAMEN DE DOMINIO (KHAN ACADEMY STYLE)
// ============================================================
async function iniciarExamen() {
    detenerTimer();
    Estado.examenPreguntas = [];
    Estado.examenPreguntaIdx = 0;
    Estado.examenRespuestas = [];

    document.getElementById('examAreaPregunta').classList.remove('hidden');
    document.getElementById('examResultados').classList.add('hidden');

    try {
        const data = await api(`/api/lecciones/${Estado.leccionActual}/examen/generar`, {
            method: 'POST'
        });
        Estado.examenPreguntas = data.preguntas || [];
        Estado.examenPreguntaIdx = 0;
        mostrarPreguntaExamen();
    } catch (e) {
        console.error('Error generando examen:', e);
    }
}

function mostrarPreguntaExamen() {
    if (Estado.examenPreguntaIdx >= Estado.examenPreguntas.length) {
        finalizarExamen();
        return;
    }

    const p = Estado.examenPreguntas[Estado.examenPreguntaIdx];
    const total = Estado.examenPreguntas.length;
    const actual = Estado.examenPreguntaIdx + 1;

    document.getElementById('examProgresoTexto').textContent = `Pregunta ${actual} de ${total}`;
    document.getElementById('examProgressBar').style.width = `${(actual / total) * 100}%`;
    document.getElementById('examDificultad').textContent = `Pregunta ${actual} · Dificultad ${p.dificultad}`;
    document.getElementById('examOperacion').textContent = p.operacion;
    document.getElementById('examRespuesta').value = '';
    renderMatematicas(document.getElementById('examAreaPregunta'));
    document.getElementById('examRespuesta').focus();

    // Contador silencioso para esta pregunta
    Estado.timerInicio = Date.now();
}

function marcarNoSeExamen() {
    responderPreguntaExamen(true);
}

async function responderPreguntaExamen(esNoSe = false) {
    let resp = document.getElementById('examRespuesta').value.trim();
    if (!resp && !esNoSe) {
        // En celular o PC, si confirman vacío, lo tomamos como "No sé" para que no queden bloqueados
        resp = '(No sé)';
    } else if (esNoSe) {
        resp = '(No sé)';
    }

    const p = Estado.examenPreguntas[Estado.examenPreguntaIdx];
    const tiempo = obtenerTiempoSilencioso();

    Estado.examenRespuestas.push({
        operacion: p.operacion,
        respuesta_correcta: p.respuesta_correcta,
        respuesta_usuario: resp,
        dificultad: p.dificultad,
        tiempo_segundos: tiempo,
    });

    Estado.examenPreguntaIdx++;
    mostrarPreguntaExamen();
}

async function finalizarExamen() {
    document.getElementById('examAreaPregunta').classList.add('hidden');
    const container = document.getElementById('examResultados');
    container.classList.remove('hidden');

    try {
        const resultado = await api(`/api/lecciones/${Estado.leccionActual}/examen/evaluar`, {
            method: 'POST',
            body: { respuestas: Estado.examenRespuestas }
        });

        const icon = document.getElementById('examIconoResultado');
        const title = document.getElementById('examTituloResultado');
        const msg = document.getElementById('examMensajeResultado');
        const det = document.getElementById('examDetallesRespuestas');

        if (resultado.aprobado) {
            icon.textContent = '🏆';
            title.textContent = `¡Felicitaciones! Acertaste ${resultado.correctas} de ${resultado.total} (${resultado.porcentaje}%)`;
            title.className = 'text-success mb-2';
            msg.textContent = '¡Has dominado esta lección! Se ha desbloqueado el siguiente tema del curso.';
            mostrarToast('🏆 ¡Lección Dominada!', `Has completado el examen con ${resultado.porcentaje}%`, 'achievement');
        } else {
            icon.textContent = '💪';
            title.textContent = `Puntaje: ${resultado.correctas} de ${resultado.total} (${resultado.porcentaje}%)`;
            title.className = 'text-warning mb-2';
            msg.textContent = 'Para dominar la lección necesitas al menos 75% (3 de 4). Revisa tus respuestas abajo y practica un poco más.';
        }

        // Mostrar detalles de respuestas
        let htmlDetalles = '<div class="font-bold mb-3">Revisión de tus preguntas:</div>';
        (resultado.detalles || []).forEach((d, idx) => {
            htmlDetalles += `
                <div class="mb-3 p-3" style="border-radius: var(--radius-md); background: ${d.es_correcto ? 'rgba(34, 197, 94, 0.08)' : 'rgba(239, 68, 68, 0.08)'}; border-left: 3px solid ${d.es_correcto ? '#22c55e' : '#ef4444'}">
                    <div><strong>${idx + 1}. ${d.operacion}</strong></div>
                    <div style="font-size: var(--text-sm)">Tu respuesta: <code>${d.respuesta_usuario}</code> ${d.es_correcto ? '✅ Correcto' : `❌ (Respuesta correcta: <strong>${d.respuesta_correcta}</strong>)`}</div>
                </div>
            `;
        });
        det.innerHTML = htmlDetalles;
        renderMatematicas(det);

        // Actualizar header y perfil
        await cargarPerfil();
    } catch (e) {
        console.error('Error evaluando examen:', e);
    }
}

// ============================================================
// VERIFICAR EJERCICIO DE PRÁCTICA
// ============================================================
async function verificarEjercicio() {
    const respuesta = document.getElementById('ejRespuesta').value.trim();
    if (!respuesta) {
        document.getElementById('ejRespuesta').focus();
        return;
    }

    Estado.intentosActuales++;
    const tiempoSilencioso = obtenerTiempoSilencioso();
    detenerTimer();

    const resultado = await api('/api/ejercicio/verificar', {
        method: 'POST',
        body: {
            leccion_id: Estado.leccionActual,
            respuesta_usuario: respuesta,
            respuesta_correcta: Estado.ejercicioActual.respuesta_correcta,
            operacion: Estado.ejercicioActual.operacion,
            tipo_ejercicio: Estado.ejercicioActual.tipo,
            tiempo_segundos: tiempoSilencioso,
            intentos: Estado.intentosActuales,
            uso_ayuda: Estado.usaAyuda,
            dificultad: Estado.ejercicioActual.dificultad,
        },
    });

    if (resultado.es_correcto) {
        Estado.ejerciciosPracticaResueltos++;
    }

    mostrarFeedback(resultado);

    // Mostrar logros nuevos
    if (resultado.logros_nuevos && resultado.logros_nuevos.length > 0) {
        for (const logroId of resultado.logros_nuevos) {
            const logros = await api('/api/logros');
            const logro = logros.find(l => l.id === logroId);
            if (logro) {
                mostrarToast(`${logro.icono} ${logro.titulo}`, logro.descripcion, 'achievement');
            }
        }
    }

    // Actualizar dominio
    document.getElementById('ejDominio').textContent = `${resultado.dominio_actual.toFixed(0)}%`;
    document.getElementById('ejDominioBar').style.width = `${resultado.dominio_actual}%`;
}

const TITULOS_CORRECTOS = [
    '🎉 ¡Excelente razonamiento!',
    '⭐ ¡Brillante! Lo resolviste con precisión.',
    '🚀 ¡Bien hecho! Tu lógica matemática está cada vez más sólida.',
    '👏 ¡Exacto! Un paso más cerca de dominar tu ingeniería.',
    '✨ ¡Impecable! Estás construyendo bases muy firmes.'
];

const TITULOS_ANIMO = [
    '🌱 ¡Buen intento! Vamos a revisar el detalle con calma',
    '🔍 ¡Casi lo tienes! Analicemos este paso juntos',
    '💡 No te preocupes: equivocarse es parte natural del aprendizaje',
    '🛠️ Depuración matemática: revisemos dónde se desvió el cálculo'
];

function mostrarFeedback(resultado) {
    const container = document.getElementById('ejFeedback');
    container.classList.remove('hidden');
    document.getElementById('ejAcciones').classList.add('hidden');
    document.getElementById('ejRespuesta').disabled = true;

    if (resultado.es_correcto) {
        const tituloAcierto = TITULOS_CORRECTOS[Math.floor(Math.random() * TITULOS_CORRECTOS.length)];
        container.innerHTML = `
            <div class="feedback feedback-correct">
                <div class="feedback-header">${tituloAcierto}</div>
                <div class="feedback-message">${resultado.mensaje}</div>
            </div>
        `;
        renderMatematicas(container);
        document.getElementById('ejPostAcciones').classList.remove('hidden');
        document.getElementById('btnReintentar').classList.add('hidden');

        // Incrementar dificultad gradualmente
        if (Estado.intentosActuales === 1 && Estado.dificultadActual < 3) {
            Estado.dificultadActual = Math.min(3, Estado.dificultadActual + 0.5);
            Estado.dificultadActual = Math.ceil(Estado.dificultadActual);
        }
    } else {
        const tituloAnimo = TITULOS_ANIMO[Math.floor(Math.random() * TITULOS_ANIMO.length)];
        const tipoErrorTexto = resultado.tipo_error ? (TIPOS_ERROR[resultado.tipo_error] || resultado.tipo_error) : '';

        container.innerHTML = `
            <div class="feedback feedback-incorrect">
                <div class="feedback-header">${tituloAnimo}</div>
                <div class="feedback-message">${resultado.mensaje}</div>
                ${tipoErrorTexto ? `
                    <div class="feedback-tip-box">
                        <strong>💡 Diagnóstico amigable:</strong> Posible ${tipoErrorTexto}. Respira hondo, revisa el método en los pasos y vuelve a intentarlo con tranquilidad.
                    </div>
                ` : ''}
            </div>
        `;
        renderMatematicas(container);

        // Mostrar explicación paso a paso
        if (resultado.explicacion) {
            mostrarExplicacionPasos(resultado.explicacion);
        }

        document.getElementById('ejPostAcciones').classList.remove('hidden');

        // Permitir reintentar (hasta 3 intentos)
        if (Estado.intentosActuales < 3) {
            document.getElementById('btnReintentar').classList.remove('hidden');
        } else {
            document.getElementById('btnReintentar').classList.add('hidden');
        }

        // Reducir dificultad si falla mucho
        if (Estado.intentosActuales >= 2 && Estado.dificultadActual > 1) {
            Estado.dificultadActual = Math.max(1, Estado.dificultadActual - 1);
        }
    }
}

function mostrarExplicacionPasos(explicacion) {
    const container = document.getElementById('ejExplicacion');
    container.classList.remove('hidden');

    let html = `
        <div class="explanation">
            <div class="explanation-title">📖 Explicación paso a paso</div>
    `;

    for (const paso of explicacion.pasos) {
        if (paso) {
            html += `<div class="explanation-step">${paso}</div>`;
        }
    }

    if (explicacion.consejo) {
        html += `<div class="explanation-tip">💡 ${explicacion.consejo}</div>`;
    }

    html += '</div>';
    container.innerHTML = html;
    renderMatematicas(container);
}

function intentarDeNuevo() {
    document.getElementById('ejFeedback').classList.add('hidden');
    document.getElementById('ejExplicacion').classList.add('hidden');
    document.getElementById('ejPostAcciones').classList.add('hidden');
    document.getElementById('ejAcciones').classList.remove('hidden');
    document.getElementById('ejRespuesta').disabled = false;
    document.getElementById('ejRespuesta').value = '';
    document.getElementById('ejRespuesta').focus();
    iniciarTimer();
}

async function siguienteEjercicio() {
    await generarNuevoEjercicio();
}


// ============================================================
// PISTAS Y EXPLICACIONES
// ============================================================
function mostrarPista() {
    if (!Estado.ejercicioActual || !Estado.ejercicioActual.pistas) return;

    Estado.usaAyuda = true;

    const pistas = Estado.ejercicioActual.pistas;
    if (Estado.pistasMostradas < pistas.length) {
        const pista = pistas[Estado.pistasMostradas];
        Estado.pistasMostradas++;

        const hint = document.getElementById('ejExplicacionPrevia');
        hint.textContent = `💡 ${pista}`;
        hint.classList.remove('hidden');

        if (Estado.pistasMostradas >= pistas.length) {
            document.getElementById('btnPista').disabled = true;
            document.getElementById('btnPista').textContent = '💡 Sin más pistas';
        }
    }
}

function mostrarExplicacion() {
    Estado.usaAyuda = true;
    const explicacion = Estado.ejercicioActual.explicacion_previa;
    if (explicacion) {
        const hint = document.getElementById('ejExplicacionPrevia');
        hint.textContent = `📖 ${explicacion}`;
        hint.classList.remove('hidden');
    }
}


// ============================================================
// PROGRESO
// ============================================================
async function cargarProgreso() {
    const stats = await api('/api/estadisticas');

    document.getElementById('progDominadas').textContent = stats.lecciones_dominadas;
    document.getElementById('progEnProgreso').textContent = stats.lecciones_en_progreso;
    document.getElementById('progPendientes').textContent = stats.lecciones_pendientes;

    // Chart niveles
    renderChartNiveles(stats);

    // Errores
    const erroresContainer = document.getElementById('progresoErrores');
    if (stats.errores_frecuentes.length === 0) {
        erroresContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">👍</div>
                <div class="empty-state-text">Sin errores registrados aún</div>
                <div class="empty-state-desc">A medida que practiques, aquí verás los tipos de errores más comunes.</div>
            </div>
        `;
    } else {
        erroresContainer.innerHTML = stats.errores_frecuentes.map(e => `
            <div class="flex items-center justify-between" style="padding: 12px 0; border-bottom: 1px solid var(--color-border);">
                <div>
                    <div class="font-bold">${TIPOS_ERROR[e.tipo_error] || e.tipo_error}</div>
                </div>
                <div class="badge badge-error">${e.frecuencia} veces</div>
            </div>
        `).join('');
    }
}

function renderChartNiveles(stats) {
    const ctx = document.getElementById('chartNiveles');
    if (!ctx) return;

    if (Estado.chartNiveles) Estado.chartNiveles.destroy();

    const labels = [];
    const correctos = [];
    const incorrectos = [];

    for (const n of stats.por_nivel) {
        labels.push(`Nivel ${n.nivel}`);
        correctos.push(n.correctos);
        incorrectos.push(n.total - n.correctos);
    }

    Estado.chartNiveles = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                {
                    label: 'Correctos',
                    data: correctos,
                    backgroundColor: 'rgba(34, 197, 94, 0.6)',
                    borderColor: '#22c55e',
                    borderWidth: 1,
                    borderRadius: 4,
                },
                {
                    label: 'Incorrectos',
                    data: incorrectos,
                    backgroundColor: 'rgba(239, 68, 68, 0.6)',
                    borderColor: '#ef4444',
                    borderWidth: 1,
                    borderRadius: 4,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#8b8fa7', usePointStyle: true },
                },
            },
            scales: {
                x: { stacked: true, grid: { display: false }, ticks: { color: '#8b8fa7' } },
                y: { stacked: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#8b8fa7' } },
            },
        },
    });
}


// ============================================================
// HISTORIAL
// ============================================================
async function cargarHistorial() {
    Estado.historialOffset = 0;
    const filtro = document.getElementById('historialFiltro').value;

    // Cargar opciones del filtro si están vacías
    const select = document.getElementById('historialFiltro');
    if (select.options.length <= 1) {
        const lecciones = await api('/api/lecciones');
        for (const l of lecciones) {
            const opt = document.createElement('option');
            opt.value = l.id;
            opt.textContent = `${l.id} - ${l.titulo}`;
            select.appendChild(opt);
        }
    }

    let url = `/api/historial?limite=30&offset=0`;
    if (filtro) url += `&leccion_id=${filtro}`;

    const historial = await api(url);
    renderHistorial(historial, false);
}

async function cargarMasHistorial() {
    Estado.historialOffset += 30;
    const filtro = document.getElementById('historialFiltro').value;

    let url = `/api/historial?limite=30&offset=${Estado.historialOffset}`;
    if (filtro) url += `&leccion_id=${filtro}`;

    const historial = await api(url);
    renderHistorial(historial, true);
}

function renderHistorial(historial, append) {
    const tbody = document.getElementById('historialBody');

    if (!append) tbody.innerHTML = '';

    if (historial.length === 0 && !append) {
        tbody.innerHTML = `
            <tr><td colspan="8" class="text-center text-muted" style="padding: 32px;">
                No hay ejercicios registrados aún. ¡Comienza a practicar!
            </td></tr>
        `;
        return;
    }

    for (const e of historial) {
        const fecha = new Date(e.fecha);
        const fechaStr = `${fecha.getDate()}/${fecha.getMonth() + 1} ${fecha.getHours()}:${fecha.getMinutes().toString().padStart(2, '0')}`;

        tbody.innerHTML += `
            <tr>
                <td>${fechaStr}</td>
                <td>${e.leccion_titulo || e.leccion_id}</td>
                <td class="text-mono">${truncar(e.operacion, 30)}</td>
                <td class="text-mono">${e.respuesta_usuario}</td>
                <td class="text-mono">${e.respuesta_correcta}</td>
                <td>${e.es_correcto ? '<span class="text-success">✅</span>' : '<span class="text-error">❌</span>'}</td>
                <td>${e.tiempo_segundos ? e.tiempo_segundos.toFixed(0) + 's' : '-'}</td>
                <td>${e.intentos}</td>
            </tr>
        `;
    }

    // Ocultar botón si no hay más
    document.getElementById('btnMasHistorial').classList.toggle('hidden', historial.length < 30);
}


// ============================================================
// LOGROS
// ============================================================
async function cargarLogros() {
    const logros = await api('/api/logros');
    const container = document.getElementById('logrosContenido');

    container.innerHTML = logros.map(l => {
        const desbloqueado = l.desbloqueado;
        const fecha = l.fecha_desbloqueo ? new Date(l.fecha_desbloqueo) : null;

        return `
            <div class="achievement ${desbloqueado ? 'unlocked' : 'locked'}">
                <div class="achievement-icon">${l.icono}</div>
                <div class="achievement-info">
                    <div class="achievement-title">${l.titulo}</div>
                    <div class="achievement-desc">${l.descripcion}</div>
                    ${fecha ? `<div class="achievement-date">Desbloqueado el ${fecha.getDate()}/${fecha.getMonth()+1}/${fecha.getFullYear()}</div>` : ''}
                </div>
            </div>
        `;
    }).join('');
}


// ============================================================
// AJUSTES
// ============================================================
function cargarAjustes() {
    if (!Estado.perfil) return;
    const objetivo = Estado.perfil.objetivo_diario_minutos || 15;

    document.querySelectorAll('[id^="obj"]').forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline');
    });

    const btnActivo = document.getElementById(`obj${objetivo}`);
    if (btnActivo) {
        btnActivo.classList.remove('btn-outline');
        btnActivo.classList.add('btn-primary');
    }
}

async function cambiarObjetivo(minutos) {
    await api('/api/perfil', {
        method: 'PUT',
        body: { objetivo_diario_minutos: minutos },
    });
    Estado.perfil.objetivo_diario_minutos = minutos;
    cargarAjustes();
    mostrarToast('⚙️', `Objetivo diario actualizado a ${minutos} minutos`);
}

async function exportarDatos() {
    const datos = await api('/api/exportar');
    const blob = new Blob([JSON.stringify(datos, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mi_profesor_backup_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    mostrarToast('💾', 'Datos exportados correctamente');
}

async function importarDatos(event) {
    const file = event.target.files[0];
    if (!file) return;

    const text = await file.text();
    const datos = JSON.parse(text);

    if (!confirm('⚠️ Esto reemplazará todos tus datos actuales. ¿Estás seguro?')) return;

    const resultado = await api('/api/importar', {
        method: 'POST',
        body: datos,
    });

    if (resultado.ok) {
        mostrarToast('✅', 'Datos importados correctamente');
        await cargarPerfil();
        navegarA('dashboard');
    } else {
        mostrarToast('❌', 'Error al importar: ' + resultado.error, 'error');
    }
}

async function reiniciarDiagnostico() {
    if (!confirm('¿Quieres repetir la evaluación diagnóstica?')) return;

    await api('/api/perfil', {
        method: 'PUT',
        body: { evaluacion_inicial_completada: 0 },
    });

    Estado.perfil.evaluacion_inicial_completada = 0;
    navegarA('diagnostico');
    document.getElementById('diagnosticoWelcome').classList.remove('hidden');
    document.getElementById('diagnosticoArea').classList.add('hidden');
    document.getElementById('diagnosticoResultados').classList.add('hidden');
}


// ============================================================
// UTILIDADES
// ============================================================
function verificarLocal(respuesta, correcta) {
    try {
        const r = parseFloat(respuesta.replace(',', '.'));
        const c = parseFloat(correcta.replace(',', '.'));

        if (isNaN(r) || isNaN(c)) {
            return respuesta.trim().toLowerCase() === correcta.trim().toLowerCase();
        }

        if (c === Math.floor(c)) {
            return Math.round(r) === Math.round(c);
        }

        return Math.abs(r - c) < 0.01;
    } catch {
        return respuesta.trim() === correcta.trim();
    }
}

function truncar(texto, maxLen) {
    if (!texto) return '';
    return texto.length > maxLen ? texto.substring(0, maxLen) + '...' : texto;
}

function mostrarToast(icono, mensaje, tipo = '') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${tipo === 'achievement' ? 'toast-achievement' : ''}`;
    toast.innerHTML = `
        <div class="toast-icon">${icono}</div>
        <div class="toast-content">
            <div class="toast-message">${mensaje}</div>
        </div>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(30px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
