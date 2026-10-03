"""
Mi Profesor de Matemáticas Personal
Módulo de Teoría Pedagógica y Ejemplos Resueltos (Estilo Khan Academy)

Cada lección cuenta con:
1. Concepto intuitivo (sin tecnicismos intimidantes)
2. ¿Por qué funciona? (fundamento lógico)
3. Conexión con Ingeniería de Sistemas (aplicación real en computación)
4. Ejemplo modelo resuelto paso a paso
5. Errores comunes a evitar
6. Truco o consejo del profesor
"""

GUIA_TEORICA = {
    # ============================================================
    # NIVEL 1: SUMAS Y RESTAS
    # ============================================================
    '1.1': {
        'titulo': 'Sumas sencillas de una cifra',
        'subtitulo': 'La base de todo el cálculo numérico',
        'concepto': 'Sumar es juntar, reunir o avanzar en una línea recta. Si tienes 4 elementos y agregas 3 más, estás avanzando 3 pasos hacia adelante a partir del 4.',
        'por_que_funciona': 'La suma cumple la propiedad conmutativa: a + b es exactamente igual a b + a (4 + 3 = 3 + 4 = 7). Por eso, para sumar más rápido, siempre te conviene empezar por el número más grande y contar hacia adelante la cantidad del número menor.',
        'conexion_ingenieria': 'En computación, el procesador (CPU) hace exactamente esto a través de la ALU (Unidad Aritmético Lógica) usando compuertas lógicas (Half Adder y Full Adder). Toda la ejecución de software, bucles `for (int i = 0; i < n; i++)` y contadores de memoria nacen de esta operación básica.',
        'ejemplo': {
            'problema': 'Calcula: 7 + 5',
            'pasos': [
                'Paso 1: Identifica el número mayor. En este caso es el 7.',
                'Paso 2: Mentalmente o en papel, avanza 5 unidades: 8, 9, 10, 11, 12.',
                'Paso 3: También puedes descomponer el 5 como (3 + 2). Sumas 7 + 3 = 10 (llegas a la decena redonda), y luego sumas los 2 restantes: 10 + 2 = 12.'
            ],
            'resultado': '12'
        },
        'errores_comunes': [
            'Empezar a contar desde el número pequeño en lugar del grande (te toma más tiempo y puedes perder la cuenta).',
            'Contar el número de partida como el primer paso (si estás en 7 y sumas 1, vas al 8, no te quedas en 7).'
        ],
        'truco_profesor': 'Busca siempre el "amigo del 10": 7 necesita 3 para llegar a 10. Si sumas 7 + 5, quítale 3 al 5 para formar 10, y te quedan 2. Total: 12.'
    },
    '1.2': {
        'titulo': 'Restas sencillas de una cifra',
        'subtitulo': 'Quitar o medir la distancia entre dos cantidades',
        'concepto': 'Restar tiene dos significados igual de importantes: 1) Quitar una cantidad de otra, o 2) Medir cuánta distancia hay entre dos números (la diferencia). Si tienes 9 y restas 4, te estás preguntando cuántos pasos hay del 4 al 9.',
        'por_que_funciona': 'La resta es la operación inversa de la suma. Si 5 + 4 = 9, entonces obligatoriamente 9 - 4 = 5. Cuando te cueste restar, pregúntate: ¿cuánto le falta al número de abajo para alcanzar al de arriba?',
        'conexion_ingenieria': 'En programación, calcular la distancia entre dos índices de un arreglo (array), restar punteros de memoria o medir la latencia entre dos timestamps de red (tiempo_fin - tiempo_inicio) son restas directas en el código.',
        'ejemplo': {
            'problema': 'Calcula: 9 - 4',
            'pasos': [
                'Paso 1: Míralo como una distancia: ¿cuánto le falta a 4 para llegar a 9?',
                'Paso 2: Del 4 al 5 falta 1... al 6 faltan 2... al 9 faltan 5.',
                'Paso 3: Verificación inversa: 5 + 4 = 9. ¡Está perfecto!'
            ],
            'resultado': '5'
        },
        'errores_comunes': [
            'Restar al revés cuando el de arriba es menor (la resta NO es conmutativa: 9 - 4 no es lo mismo que 4 - 9).',
            'Confundir el signo menos (-) con un separador.'
        ],
        'truco_profesor': 'En vez de retroceder contando hacia atrás, piensa: "¿Cuánto le falta a 4 para ser 9?". Tu cerebro suma mucho más rápido de lo que resta.'
    },
    '1.3': {
        'titulo': 'Sumas con llevadas (acarreo)',
        'subtitulo': 'El sistema decimal y el desbordamiento de columna',
        'concepto': 'Nuestro sistema es de base 10 (decimal). Cada columna solo puede contener un solo dígito (del 0 al 9). Si en una columna la suma te da 10 o más, no cabe completa: dejas las unidades y "llevas" las decenas a la columna de la izquierda.',
        'por_que_funciona': 'Un número como 47 significa 4 decenas y 7 unidades. Si sumas 47 + 28, sumas las unidades: 7 + 8 = 15 unidades. 15 unidades equivalen a 1 decena y 5 unidades. Ese "1" viaja como decena a la siguiente columna.',
        'conexion_ingenieria': '¡Esto es exactamente el bit de acarreo (Carry Flag) en la arquitectura de computadoras! Cuando dos registros de 8 o 64 bits suman y superan el valor máximo, el procesador activa la bandera de Carry (`CF`). Es el mismo acarreo que aprendes en la escuela primaria.',
        'ejemplo': {
            'problema': 'Calcula: 48 + 37',
            'pasos': [
                'Paso 1: Alinea unidades con unidades y decenas con decenas.',
                'Paso 2: Suma las unidades: 8 + 7 = 15. Escribes el 5 abajo y te "llevas" 1 decena arriba.',
                'Paso 3: Suma las decenas incluyendo la llevada: 1 (que llevabas) + 4 + 3 = 8.',
                'Paso 4: Junta el resultado: 8 decenas y 5 unidades = 85.'
            ],
            'resultado': '85'
        },
        'errores_comunes': [
            'Olvidar sumar el número que llevas en la columna siguiente (el error más frecuente en todo el mundo).',
            'Escribir el 15 completo en la columna de las unidades.'
        ],
        'truco_profesor': 'Escribe siempre la llevada bien visible arriba de la columna de las decenas en un circulito para que tu ojo no la ignore.'
    },
    '1.4': {
        'titulo': 'Restas con préstamos',
        'subtitulo': 'Cuando la cifra de arriba es menor que la de abajo',
        'concepto': 'Si quieres restar 53 - 28, en las unidades tienes que hacer 3 - 8. Como a 3 no le puedes quitar 8 (en los números naturales), le "pides prestada" una decena al 5. La decena se convierte en 10 unidades, así que tu 3 ahora es 13.',
        'por_que_funciona': '53 es lo mismo que (40 + 13). No cambiaste el valor del número, solo lo reagrupaste. Ahora sí puedes hacer 13 - 8 = 5 en las unidades, y 4 - 2 = 2 en las decenas.',
        'conexion_ingenieria': 'En la ALU de un procesador se conoce como "Borrow Flag" (bandera de préstamo). Cuando se implementa aritmética de enteros de precisión múltiple (BigInt en lenguajes como Python, Java o JavaScript), el algoritmo simula exactamente este préstamo columna por columna.',
        'ejemplo': {
            'problema': 'Calcula: 62 - 27',
            'pasos': [
                'Paso 1: Mira las unidades: 2 - 7 no se puede directo.',
                'Paso 2: Pide prestada 1 decena al 6. El 6 se convierte en 5, y el 2 se convierte en 12.',
                'Paso 3: Ahora resta las unidades: 12 - 7 = 5.',
                'Paso 4: Resta las decenas restantes: 5 - 2 = 3.',
                'Paso 5: Resultado: 35. Comprueba sumando: 35 + 27 = 62.'
            ],
            'resultado': '35'
        },
        'errores_comunes': [
            'Restar al revés cuando no alcanza: ver 2 y 7 y hacer 7 - 2 = 5 sin pedir prestado.',
            'Pedir prestado pero olvidar tachar y restarle 1 al número de la izquierda.'
        ],
        'truco_profesor': 'Tacha inmediatamente el número al que le pediste prestado antes de hacer la resta de las unidades. Así es imposible que se te olvide.'
    },
    '1.5': {
        'titulo': 'Operaciones con números grandes',
        'subtitulo': 'Aplicando el orden columna por columna a cientos y miles',
        'concepto': 'Los números de 3 o 4 cifras siguen exactamente la misma regla: se resuelven de derecha a izquierda (unidades, decenas, centenas, unidades de mil). No importa cuán largo sea el número, solo haces una suma o resta de un dígito a la vez.',
        'por_que_funciona': 'El principio posicional: cada columna a la izquierda vale 10 veces más que la anterior. Resolver paso a paso divide un problema intimidante en 3 o 4 problemas pequeñitos.',
        'conexion_ingenieria': 'Este es el principio de "Divide and Conquer" (Divide y vencerás), uno de los paradigmas fundamentales en el diseño de algoritmos de sistemas.',
        'ejemplo': {
            'problema': 'Calcula: 384 + 259',
            'pasos': [
                'Paso 1: Unidades: 4 + 9 = 13. Escribes 3, llevas 1.',
                'Paso 2: Decenas: 1 (llevada) + 8 + 5 = 14. Escribes 4, llevas 1.',
                'Paso 3: Centenas: 1 (llevada) + 3 + 2 = 6.',
                'Paso 4: Resultado final: 643.'
            ],
            'resultado': '643'
        },
        'errores_comunes': [
            'Alinear mal los números si uno tiene más cifras que otro (siempre deben alinearse por la derecha, coincidiendo las unidades).'
        ],
        'truco_profesor': 'Escribe en columnas rectas y limpias. Muchos errores en números grandes son de caligrafía o desorden visual, no de matemáticas.'
    },
    '1.6': {
        'titulo': 'Cálculo mental rápido',
        'subtitulo': 'Estrategias de descomposición y redondeo',
        'concepto': 'El cálculo mental no consiste en memorizar todas las operaciones, sino en redondear y compensar. Por ejemplo, sumar 39 es lo mismo que sumar 40 y luego quitar 1.',
        'por_que_funciona': 'Transformas operaciones complicadas en números redondos terminados en cero, que son los más fáciles de procesar por el cerebro.',
        'conexion_ingenieria': 'Los compiladores de código optimizan operaciones complejas mediante técnicas llamadas "Strength Reduction" (reemplazar operaciones costosas por combinaciones equivalentes más rápidas). Tu mente hace lo mismo.',
        'ejemplo': {
            'problema': 'Calcula mentalmente: 56 + 29',
            'pasos': [
                'Paso 1: Piensa en 29 como (30 - 1).',
                'Paso 2: Suma 56 + 30 = 86 (muy fácil porque termina en cero).',
                'Paso 3: Quita el 1 que agregaste de más: 86 - 1 = 85.'
            ],
            'resultado': '85'
        },
        'errores_comunes': [
            'Intentar visualizar el algoritmo en papel dentro de tu cabeza columna por columna (eso cansa mucho la memoria de trabajo).'
        ],
        'truco_profesor': 'Busca siempre el múltiplo de 10 más cercano y luego ajusta la diferencia.'
    },
    '1.7': {
        'titulo': 'Problemas contextualizados de suma y resta',
        'subtitulo': 'Traduciendo situaciones del mundo real a lenguaje matemático',
        'concepto': 'Un problema matemático es una historia donde faltan datos. El objetivo es identificar qué te están preguntando, qué datos tienes y qué operación representa la acción.',
        'por_que_funciona': 'Las palabras clave te dan la pista: "ganar, juntar, aumentar, total" indican suma. "Perder, gastar, diferencia, cuántos más, cuántos sobran" indican resta.',
        'conexion_ingenieria': 'En Ingeniería de Software, esto se llama "Análisis de Requerimientos": traducir las necesidades de un cliente o usuario en lógica computable precisa.',
        'ejemplo': {
            'problema': 'Un servidor tenía 150 GB libres. Se instaló una base de datos de 45 GB y luego se liberaron 20 GB de archivos temporales. ¿Cuántos GB quedan?',
            'pasos': [
                'Paso 1: Identifica el inicio: 150 GB.',
                'Paso 2: Se ocupa espacio (resta): 150 - 45 = 105 GB.',
                'Paso 3: Se libera espacio (suma al espacio libre): 105 + 20 = 125 GB.',
                'Paso 4: Conclusión: Quedan 125 GB libres.'
            ],
            'resultado': '125'
        },
        'errores_comunes': [
            'Empezar a operar antes de leer el problema completo dos veces.'
        ],
        'truco_profesor': 'Subraya con lápiz los números y la pregunta principal antes de escribir cualquier operación.'
    },

    # ============================================================
    # NIVEL 2: MULTIPLICACIONES
    # ============================================================
    '2.1': {
        'titulo': 'Tablas de multiplicar del 1 al 5',
        'subtitulo': 'La suma abreviada en grupos iguales',
        'concepto': 'Multiplicar es sumar el mismo número varias veces. Si compras 4 paquetes con 3 galletas cada uno, tienes 3 + 3 + 3 + 3 = 12 galletas. En vez de escribir una suma larga, escribes 4 × 3 = 12.',
        'por_que_funciona': 'Es una cuadrícula: una matriz de 4 filas por 3 columnas tiene 12 celdas. No importa si cuentas filas o columnas: 4 × 3 es lo mismo que 3 × 4.',
        'conexion_ingenieria': 'Cálculo del tamaño de memoria: si tienes un arreglo de 5 elementos y cada uno ocupa 4 bytes, el arreglo ocupa 5 × 4 = 20 bytes en la memoria RAM.',
        'ejemplo': {
            'problema': 'Calcula: 4 × 3',
            'pasos': [
                'Paso 1: Visualízalo como 4 grupos de 3: (3 + 3) + (3 + 3).',
                'Paso 2: 3 + 3 = 6. Y 6 + 6 = 12.',
                'Paso 3: Resultado: 12.'
            ],
            'resultado': '12'
        },
        'errores_comunes': [
            'Confundir 4 × 3 con 4 + 3 (multiplicar no es sumar los dos números entre sí, es repetir uno tantas veces como dice el otro).'
        ],
        'truco_profesor': 'Para la tabla del 4: simplemente duplica dos veces. ¿4 × 6? El doble de 6 es 12, y el doble de 12 es 24.'
    },
    '2.2': {
        'titulo': 'Tablas del 6 al 9',
        'subtitulo': 'Dominando las multiplicaciones más temidas con patrones',
        'concepto': 'Las tablas del 6 al 9 asustan a muchos estudiantes, pero en realidad casi todas ya te las sabes por la conmutatividad (6 × 3 es la misma que 3 × 6). En realidad, solo hay unas 10 combinaciones nuevas que memorizar.',
        'por_que_funciona': 'Se pueden deducir usando la tabla del 5 y la del 10. Por ejemplo, multiplicar por 9 es multiplicar por 10 y restar el número una vez: 9 × 7 = (10 × 7) - 7 = 70 - 7 = 63.',
        'conexion_ingenieria': 'Las tablas de multiplicar se almacenan en hardware en una pequeña tabla de búsqueda (Lookup Table o LUT) para acelerar operaciones numéricas en chips DSP.',
        'ejemplo': {
            'problema': 'Calcula: 8 × 7',
            'pasos': [
                'Paso 1: Descompón el 8 como (5 + 3).',
                'Paso 2: (5 × 7) + (3 × 7) = 35 + 21.',
                'Paso 3: 35 + 21 = 56.',
                'Paso 4: Nemotecnia famosa: 5, 6, 7, 8 -> 56 = 7 × 8.'
            ],
            'resultado': '56'
        },
        'errores_comunes': [
            'Dudar entre 7 × 8 (56) y 6 × 9 (54).'
        ],
        'truco_profesor': 'Para la tabla del 9 con los dedos o por suma de cifras: los dos dígitos del resultado siempre suman 9 (ej. 9 × 4 = 36 -> 3 + 6 = 9).'
    },
    '2.3': {
        'titulo': 'Tablas del 10 al 12',
        'subtitulo': 'Multiplicar por potencias de 10 y docenas',
        'concepto': 'Multiplicar por 10 es simplemente desplazar las cifras una posición a la izquierda y agregar un cero. Multiplicar por 11 es sumar el número consigo mismo desplazado.',
        'por_que_funciona': 'Cada columna del sistema decimal vale 10 veces más. Multiplicar por 10 traslada las unidades a decenas: 7 unidades × 10 = 7 decenas (70).',
        'conexion_ingenieria': 'En binario, multiplicar por 2 es un desplazamiento de bits a la izquierda (`x << 1`). En decimal, multiplicar por 10 es desplazar un cero. ¡Es la misma operación a nivel de arquitectura!',
        'ejemplo': {
            'problema': 'Calcula: 12 × 6',
            'pasos': [
                'Paso 1: Descompón el 12 como 10 + 2.',
                'Paso 2: Multiplica por 10: 10 × 6 = 60.',
                'Paso 3: Multiplica por 2: 2 × 6 = 12.',
                'Paso 4: Suma ambos resultados: 60 + 12 = 72.'
            ],
            'resultado': '72'
        },
        'errores_comunes': [
            'Creer que multiplicar por 100 agrega un solo cero (agrega dos ceros: 10^2).'
        ],
        'truco_profesor': 'Para cualquier número por 11 de dos cifras: abre los dígitos y pon en el medio la suma de ambos (ej: 25 × 11 -> 2 _ 5 -> 2 + 5 = 7 -> 275).'
    },
    '2.4': {
        'titulo': 'Trucos y patrones de multiplicación',
        'subtitulo': 'Agilidad mental mediante propiedades algebraicas',
        'concepto': 'La propiedad distributiva: a × (b + c) = (a × b) + (a × c). Te permite romper multiplicaciones difíciles en dos operaciones muy fáciles.',
        'por_que_funciona': 'El área total de un rectángulo no cambia si lo divides con una línea en dos rectángulos más pequeños.',
        'conexion_ingenieria': 'Algoritmo de Karatsuba: la multiplicación rápida de números gigantes en criptografía (RSA, SSL/TLS) usa exactamente esta descomposición para reducir la complejidad temporal.',
        'ejemplo': {
            'problema': 'Calcula: 15 × 8',
            'pasos': [
                'Paso 1: Descompón 15 en 10 + 5.',
                'Paso 2: 10 × 8 = 80.',
                'Paso 3: 5 × 8 = 40.',
                'Paso 4: 80 + 40 = 120.'
            ],
            'resultado': '120'
        },
        'errores_comunes': [
            'Intentar calcular números de dos cifras sin descomponerlos mentalmente.'
        ],
        'truco_profesor': 'Para multiplicar por 5: multiplica por 10 (agrega un cero) y sácale la mitad (18 × 5 = mitad de 180 = 90).'
    },
    '2.5': {
        'titulo': 'Multiplicaciones de dos cifras',
        'subtitulo': 'Productos parciales alineados',
        'concepto': 'Para multiplicar números como 24 × 13, primero multiplicas 24 por las 3 unidades, luego 24 por la 1 decena (dejando un espacio o cero a la derecha), y finalmente sumas ambos productos parciales.',
        'por_que_funciona': '24 × 13 es literalmente 24 × (3 + 10) = (24 × 3) + (24 × 10) = 72 + 240 = 312.',
        'conexion_ingenieria': 'Representación de memoria en buffers de pantalla: calcular el offset de un píxel en una pantalla de resolución (X, Y) usa `offset = Y * ancho + X`.',
        'ejemplo': {
            'problema': 'Calcula: 24 × 13',
            'pasos': [
                'Paso 1: Multiplica por las unidades (3): 24 × 3 = 72.',
                'Paso 2: Multiplica por las decenas (1): 24 × 10 = 240 (escribes 24 desplazado un lugar).',
                'Paso 3: Suma los dos resultados parciales: 72 + 240 = 312.'
            ],
            'resultado': '312'
        },
        'errores_comunes': [
            'Olvidar dejar el espacio o poner el cero en la segunda fila (si no lo haces, estás multiplicando por 1 en vez de por 10).'
        ],
        'truco_profesor': 'Pon siempre un "0" explícito en el espacio de la segunda fila para no confundir la columna de alineación.'
    },
    '2.6': {
        'titulo': 'Multiplicaciones de varias cifras',
        'subtitulo': 'Escalando el método a cualquier tamaño numérico',
        'concepto': 'El mismo procedimiento de productos parciales se extiende a 3 o más cifras, desplazando una posición adicional por cada columna (decenas un espacio, centenas dos espacios).',
        'por_que_funciona': 'Cada posición representa una potencia de 10: unidades (1), decenas (10), centenas (100).',
        'conexion_ingenieria': 'Lógica de multiplicadores por hardware en procesadores modernos mediante árboles de Wallace y matrices de sumadores.',
        'ejemplo': {
            'problema': 'Calcula: 125 × 12',
            'pasos': [
                'Paso 1: 125 × 2 = 250.',
                'Paso 2: 125 × 10 = 1250.',
                'Paso 3: Suma: 250 + 1250 = 1500.'
            ],
            'resultado': '1500'
        },
        'errores_comunes': [
            'Confundir las llevadas de la primera fila con las llevadas de la segunda fila.'
        ],
        'truco_profesor': 'Borra o tacha las llevadas del primer dígito antes de empezar a multiplicar con el segundo dígito.'
    },
    '2.7': {
        'titulo': 'Problemas prácticos de multiplicación',
        'subtitulo': 'Identificando tasas, repeticiones y dimensiones',
        'concepto': 'Aprender a reconocer cuándo una situación de la vida real o técnica exige multiplicar: cuando hay cantidades por unidad (precio unitario, tasa de transferencia, memoria por proceso).',
        'por_que_funciona': 'Total = Tasa × Cantidad de unidades.',
        'conexion_ingenieria': 'Estimación de almacenamiento: si un sistema registra 50 transacciones por segundo y cada transacción pesa 2 KB, ¿cuántos KB por segundo ingresan? 50 × 2 = 100 KB/s.',
        'ejemplo': {
            'problema': 'Una página web carga 8 imágenes de 250 KB cada una. ¿Cuántos KB descarga en total?',
            'pasos': [
                'Paso 1: Identifica las cantidades: 8 imágenes × 250 KB.',
                'Paso 2: Descompón: 8 × 250 = 8 × (250) = 4 × 500 = 2 × 1000 = 2000 KB.',
                'Paso 3: Resultado: 2000 KB (aproximadamente 2 MB).'
            ],
            'resultado': '2000'
        },
        'errores_comunes': [
            'Sumar las cantidades en lugar de multiplicarlas.'
        ],
        'truco_profesor': 'Fíjate en palabras como "cada uno", "por hora", "por persona". Siempre indican multiplicación.'
    },

    # ============================================================
    # NIVEL 3: DIVISIONES
    # ============================================================
    '3.1': {
        'titulo': '¿Qué significa dividir?',
        'subtitulo': 'Repartir en partes iguales y contar grupos',
        'concepto': 'Dividir significa repartir una cantidad en partes iguales, o averiguar cuántas veces cabe un número dentro de otro. Si tienes 12 caramelos y los repartes entre 3 amigos, a cada uno le tocan 4.',
        'por_que_funciona': 'La división es la inversa exacta de la multiplicación. Decir 12 ÷ 3 = 4 es lo mismo que decir 3 × 4 = 12.',
        'conexion_ingenieria': 'En informática, la paginación de memoria divide la memoria virtual en bloques de tamaño fijo (páginas). Si tienes 4096 bytes y páginas de 512 bytes, tienes 4096 ÷ 512 = 8 páginas.',
        'ejemplo': {
            'problema': 'Calcula: 15 ÷ 3',
            'pasos': [
                'Paso 1: Pregúntate: ¿qué número multiplicado por 3 da 15?',
                'Paso 2: Repasa la tabla del 3: 3 × 1 = 3, 3 × 2 = 6... 3 × 5 = 15.',
                'Paso 3: Por lo tanto, 15 ÷ 3 = 5.'
            ],
            'resultado': '5'
        },
        'errores_comunes': [
            'Dividir entre cero (¡es una operación indefinida! En programación produce una excepción de `ZeroDivisionError` o `ArithmeticException`).'
        ],
        'truco_profesor': 'Nunca intentes "adivinar" la división: piensa siempre en la multiplicación inversa.'
    },
    '3.2': {
        'titulo': 'Divisiones exactas',
        'subtitulo': 'Cuando no sobra nada (residuo = 0)',
        'concepto': 'Una división es exacta cuando el dividendo es un múltiplo directo del divisor. El residuo es cero.',
        'por_que_funciona': 'El dividendo se descompone perfectamente en partes enteras.',
        'conexion_ingenieria': 'Verificar si un número es par en programación usando el operador módulo: `if (n % 2 == 0)`. Si el residuo es 0, es divisible exactamente.',
        'ejemplo': {
            'problema': 'Calcula: 42 ÷ 6',
            'pasos': [
                'Paso 1: ¿Cuántas veces cabe el 6 en el 42?',
                'Paso 2: Como 6 × 7 = 42, el cociente es 7.',
                'Paso 3: Residuo: 42 - 42 = 0.'
            ],
            'resultado': '7'
        },
        'errores_comunes': [
            'Confundir cociente (el resultado) con residuo (lo que sobra).'
        ],
        'truco_profesor': 'Comprueba siempre: Cociente × Divisor debe darte exactamente el Dividendo.'
    },
    '3.3': {
        'titulo': 'Divisiones con residuo',
        'subtitulo': 'Entendiendo el cociente y el resto (operador Módulo)',
        'concepto': 'Si tienes 17 galletas para repartir entre 5 personas, cada una recibe 3 galletas (15 en total) y sobran 2 galletas que no alcanzan para dar una más a todos. Ese sobrante es el residuo.',
        'por_que_funciona': 'Teorema de la división entera: Dividendo = (Divisor × Cociente) + Residuo, donde el residuo SIEMPRE debe ser menor que el divisor.',
        'conexion_ingenieria': '¡El operador `%` (módulo) en todos los lenguajes de programación (C++, Java, Python, C#)! Se usa para balanceo de carga en servidores (hashing), distribuir elementos en tablas hash, convertir segundos a minutos y segundos, etc.',
        'ejemplo': {
            'problema': 'Calcula: 23 ÷ 4 (indica cociente y residuo)',
            'pasos': [
                'Paso 1: ¿Cuántas veces cabe 4 en 23 sin pasarse? 4 × 5 = 20 (cabe 5 veces). Si ponemos 6 nos pasamos (24).',
                'Paso 2: El cociente es 5.',
                'Paso 3: Resta: 23 - 20 = 3. Ese es el residuo.',
                'Paso 4: Comprueba: (4 × 5) + 3 = 20 + 3 = 23.'
            ],
            'resultado': '5 (residuo 3)'
        },
        'errores_comunes': [
            'Dejar un residuo mayor o igual que el divisor (si te sobra 4 o más dividiendo entre 4, cabía una vez más).'
        ],
        'truco_profesor': 'El residuo NUNCA puede ser igual ni mayor que el número por el que divides.'
    },
    '3.4': {
        'titulo': 'Divisiones con números de varias cifras',
        'subtitulo': 'El algoritmo de la división larga paso a paso',
        'concepto': 'La división larga toma cifras del dividendo de izquierda a derecha. Estimas cuántas veces cabe el divisor en ese pedazo, multiplicas, restas y bajas la siguiente cifra.',
        'por_que_funciona': 'Vas dividiendo las centenas primero, lo que sobra lo conviertes en decenas, y lo que sobra en unidades.',
        'conexion_ingenieria': 'Algoritmo de división euclídea utilizado en criptografía para el cálculo del Máximo Común Divisor (MCD) y generación de claves asimétricas RSA.',
        'ejemplo': {
            'problema': 'Calcula: 156 ÷ 6',
            'pasos': [
                'Paso 1: ¿Cabe 6 en 1? No. Toma dos cifras: 15.',
                'Paso 2: ¿Cuántas veces cabe 6 en 15? Cabe 2 veces (6 × 2 = 12). Escribe 2 en el cociente.',
                'Paso 3: Resta: 15 - 12 = 3.',
                'Paso 4: Baja la siguiente cifra (6): tienes 36.',
                'Paso 5: ¿Cuántas veces cabe 6 en 36? Cabe 6 veces exactas (6 × 6 = 36). Escribe 6 en el cociente.',
                'Paso 6: Resultado final: 26 (residuo 0).'
            ],
            'resultado': '26'
        },
        'errores_comunes': [
            'Olvidar colocar un 0 en el cociente cuando bajas una cifra y no alcanza para dividir.'
        ],
        'truco_profesor': 'Regla de oro: cada vez que bajas una cifra, TIENES que poner un dígito en el cociente, aunque sea un cero.'
    },
    '3.5': {
        'titulo': 'División con decimales',
        'subtitulo': 'Continuando la división más allá del punto decimal',
        'concepto': 'Cuando una división no es exacta y se acaban las cifras enteras, agregamos una coma o punto decimal en el cociente y agregamos ceros al residuo para seguir repartiendo décimas, centésimas y milésimas.',
        'por_que_funciona': '1 unidad sobrante es igual a 10 décimas (0.1). Al agregar un cero al residuo, estamos cambiando de escala para repartir partes fraccionarias.',
        'conexion_ingenieria': 'Conversión de enteros a números de punto flotante (`float`, `double`) en software.',
        'ejemplo': {
            'problema': 'Calcula: 7 ÷ 2',
            'pasos': [
                'Paso 1: 7 ÷ 2 cabe 3 veces (3 × 2 = 6). Sobra 1.',
                'Paso 2: Ponemos punto decimal en el cociente (3.).',
                'Paso 3: Agregamos un 0 al residuo 1, convirtiéndolo en 10 décimas.',
                'Paso 4: 10 ÷ 2 = 5.',
                'Paso 5: Resultado: 3.5.'
            ],
            'resultado': '3.5'
        },
        'errores_comunes': [
            'Olvidar poner el punto decimal en el cociente al agregar el primer cero al residuo.'
        ],
        'truco_profesor': 'Apenas pongas un cero extra en el residuo, pon inmediatamente el punto en el resultado.'
    },
    '3.6': {
        'titulo': 'Problemas prácticos con divisiones',
        'subtitulo': 'Distribución, partición y razones en situaciones reales',
        'concepto': 'Reconocer situaciones donde se reparte, se calcula el promedio, o se determina la capacidad de recipientes o lotes.',
        'por_que_funciona': 'Cantidad por grupo = Total ÷ Número de grupos.',
        'conexion_ingenieria': 'Balanceo de carga en redes: distribuir N peticiones HTTP entre K servidores worker de forma equitativa.',
        'ejemplo': {
            'problema': 'Un disco duro tiene 240 GB para 4 máquinas virtuales con la misma capacidad. ¿Cuántos GB tiene cada una?',
            'pasos': [
                'Paso 1: Operación: 240 ÷ 4.',
                'Paso 2: Como 24 ÷ 4 = 6, entonces 240 ÷ 4 = 60.',
                'Paso 3: Cada máquina virtual tiene 60 GB.'
            ],
            'resultado': '60'
        },
        'errores_comunes': [
            'Invertir dividendo y divisor (hacer 4 ÷ 240 en lugar de 240 ÷ 4).'
        ],
        'truco_profesor': 'Pregúntate: ¿Qué cosa se está repartiendo? Eso que se reparte es el dividendo (va primero).'
    },

    # ============================================================
    # NIVEL 4: FRACCIONES, DECIMALES Y PORCENTAJES
    # ============================================================
    '4.1': {
        'titulo': '¿Qué son las fracciones?',
        'subtitulo': 'Numerador, denominador y partes de la unidad',
        'concepto': 'Una fracción a/b representa a partes tomadas de un total de b partes iguales en que se dividió una unidad. En 3/4, el denominador 4 dice en cuántas partes se cortó la pizza, y el numerador 3 dice cuántas rebanadas tomaste.',
        'por_que_funciona': 'Toda fracción es en realidad una división no resuelta: 3/4 es literalmente 3 ÷ 4 = 0.75.',
        'conexion_ingenieria': 'En interfaces gráficas y CSS, las proporciones relativas como `flex: 1` o unidades de grid (`1fr, 2fr`) son fracciones del espacio disponible.',
        'ejemplo': {
            'problema': '¿Qué fracción de una hora son 15 minutos?',
            'pasos': [
                'Paso 1: Una hora completa tiene 60 minutos (denominador = 60).',
                'Paso 2: Tomamos 15 minutos (numerador = 15). Fracción: 15/60.',
                'Paso 3: Simplificamos dividiendo arriba y abajo entre 15: 15÷15 = 1, 60÷15 = 4.',
                'Paso 4: Resultado: 1/4 de hora.'
            ],
            'resultado': '1/4'
        },
        'errores_comunes': [
            'Confundir numerador (arriba) con denominador (abajo).'
        ],
        'truco_profesor': 'D de Denominador = D de División (las partes en que se Divide).'
    },
    '4.2': {
        'titulo': 'Suma y resta de fracciones',
        'subtitulo': 'Mismo denominador vs denominador diferente (MCM)',
        'concepto': 'Solo puedes sumar o restar fracciones si las piezas son del mismo tamaño (mismo denominador). Si tienen distinto denominador, primero debes convertirlas a fracciones equivalentes con un denominador común.',
        'por_que_funciona': 'No puedes sumar 1 tercio con 1 cuarto directamente porque son rebanadas de distinto tamaño. Si cortas ambas en doceavos, 1/3 = 4/12 y 1/4 = 3/12. Ahora sí: 4/12 + 3/12 = 7/12.',
        'conexion_ingenieria': 'Alineación de memoria y padding: los compiladores alinean variables a múltiplos comunes de bytes (4 u 8 bytes) para que el procesador pueda leerlas eficientemente.',
        'ejemplo': {
            'problema': 'Calcula: 1/2 + 1/3',
            'pasos': [
                'Paso 1: Los denominadores son 2 y 3. El mínimo común múltiplo (MCM) es 6.',
                'Paso 2: Convierte 1/2 multiplicando por 3/3 = 3/6.',
                'Paso 3: Convierte 1/3 multiplicando por 2/2 = 2/6.',
                'Paso 4: Suma los numeradores: 3/6 + 2/6 = (3 + 2)/6 = 5/6.'
            ],
            'resultado': '5/6'
        },
        'errores_comunes': [
            'Sumar numeradores con numeradores y denominadores con denominadores (hacer 1/2 + 1/3 = 2/5 ¡ESTÁ TOTALMENTE MAL!).'
        ],
        'truco_profesor': 'Método mariposa o cruzado para 2 fracciones: (a×d + b×c) / (b×d).'
    },
    '4.3': {
        'titulo': 'Multiplicación y división de fracciones',
        'subtitulo': 'Directo en multiplicación, cruzado o inverso en división',
        'concepto': 'Multiplicar fracciones es la operación más fácil: numerador por numerador, y denominador por denominador: (a/b) × (c/d) = (a×c)/(b×d). Dividir es multiplicar por la fracción inversa: (a/b) ÷ (c/d) = (a/b) × (d/c).',
        'por_que_funciona': '1/2 × 1/3 significa "la mitad de un tercio", lo cual es un sexto (1/6). Dividir entre 1/2 es preguntar cuántas mitades caben, lo cual duplica la cantidad.',
        'conexion_ingenieria': 'Cálculo de probabilidades en machine learning y algoritmos probabilísticos (probabilidad conjunta $P(A \cap B) = P(A) \times P(B)$).',
        'ejemplo': {
            'problema': 'Calcula: (2/3) × (3/4)',
            'pasos': [
                'Paso 1: Multiplica numeradores: 2 × 3 = 6.',
                'Paso 2: Multiplica denominadores: 3 × 4 = 12.',
                'Paso 3: Simplifica 6/12 dividiendo entre 6: 1/2.'
            ],
            'resultado': '1/2'
        },
        'errores_comunes': [
            'Buscar común denominador para multiplicar (¡no se necesita común denominador para multiplicar ni dividir!).'
        ],
        'truco_profesor': 'Para dividir fracciones, invierte la segunda fracción de cabeza y multiplica normal: a/b ÷ c/d = a/b × d/c.'
    },
    '4.4': {
        'titulo': 'Fracciones y números decimales',
        'subtitulo': 'Dos formas distintas de escribir la misma cantidad',
        'concepto': 'Una fracción y un decimal son dos caras de la misma moneda. 1/2 es exactamente 0.5. Para convertir una fracción a decimal, simplemente divides el numerador entre el denominador.',
        'por_que_funciona': 'El punto decimal representa décimas (1/10), centésimas (1/100) y milésimas (1/1000).',
        'conexion_ingenieria': 'La trampa del punto flotante en informática: en binario, 0.1 no tiene representación finita (como 1/3 en decimal). Por eso en JavaScript `0.1 + 0.2 === 0.30000000000000004`. Entender fracciones te salva de bugs financieros.',
        'ejemplo': {
            'problema': 'Convierte 3/5 a decimal',
            'pasos': [
                'Paso 1: Divide 3 entre 5.',
                'Paso 2: 3 no cabe en 5, ponemos 0.',
                'Paso 3: Agregamos un cero al 3 para formar 30 décimas: 30 ÷ 5 = 6.',
                'Paso 4: Resultado: 0.6.'
            ],
            'resultado': '0.6'
        },
        'errores_comunes': [
            'Dividir 5 entre 3 en lugar de 3 entre 5.'
        ],
        'truco_profesor': 'Para fracciones con denominador 5: multiplica numerador y denominador por 2 para que quede en base 10 (3/5 = 6/10 = 0.6).'
    },
    '4.5': {
        'titulo': 'Porcentajes y aplicaciones',
        'subtitulo': 'Fracciones con denominador 100 y reglas de tres',
        'concepto': 'Porcentaje (%) significa literalmente "por cada cien". El 25% de algo es 25 de cada 100 partes, es decir, 25/100 o 0.25.',
        'por_que_funciona': 'Calcular el P% de N es multiplicar N × (P / 100).',
        'conexion_ingenieria': 'Métricas de sistemas: uso de CPU al 85%, disponibilidad del 99.9% (tres nueves de SLA), tasa de compresión de archivos.',
        'ejemplo': {
            'problema': 'Calcula el 20% de 150',
            'pasos': [
                'Paso 1: El 10% de cualquier número se calcula quitando un cero o corriendo el punto un lugar. El 10% de 150 es 15.',
                'Paso 2: Como el 20% es el doble del 10%, multiplicas: 15 × 2 = 30.',
                'Paso 3: Resultado: 30.'
            ],
            'resultado': '30'
        },
        'errores_comunes': [
            'Confundir 5% con 0.5 (el 5% es 0.05; 0.5 es el 50%).'
        ],
        'truco_profesor': 'Los porcentajes son reversibles: el 8% de 25 es exactamente lo mismo que el 25% de 8 (y el 25% de 8 es la cuarta parte de 8 = 2).'
    },

    # ============================================================
    # NIVEL 5: POTENCIAS Y RAÍCES
    # ============================================================
    '5.1': {
        'titulo': 'Potencias y exponentes',
        'subtitulo': 'Multiplicación repetida y crecimiento acelerado',
        'concepto': 'Una potencia $a^n$ indica que la base $a$ se multiplica por sí misma $n$ veces. En $2^3$, el 2 es la base y el 3 es el exponente: $2 \times 2 \times 2 = 8$.',
        'por_que_funciona': 'Así como la multiplicación abrevia la suma (3 + 3 + 3 + 3 = 4 × 3), la potencia abrevia la multiplicación (3 × 3 × 3 × 3 = 3^4).',
        'conexion_ingenieria': 'Toda la arquitectura de computación se basa en potencias de 2: 1 byte = $2^3$ bits (8), 1 KB = $2^{10}$ bytes (1024), 32 bits = $2^{32}$ direcciones (4 GB RAM).',
        'ejemplo': {
            'problema': 'Calcula: 2^5',
            'pasos': [
                'Paso 1: Escribe la multiplicación repetida: 2 × 2 × 2 × 2 × 2.',
                'Paso 2: 2 × 2 = 4.',
                'Paso 3: 4 × 2 = 8.',
                'Paso 4: 8 × 2 = 16.',
                'Paso 5: 16 × 2 = 32.'
            ],
            'resultado': '32'
        },
        'errores_comunes': [
            'Multiplicar la base por el exponente (pensar que 2^3 es 2 × 3 = 6 ¡ERROR! Es 2 × 2 × 2 = 8).'
        ],
        'truco_profesor': 'Cualquier número elevado a la 0 siempre vale 1 ($a^0 = 1$), y elevado a la 1 vale el mismo número ($a^1 = a$).'
    },
    '5.2': {
        'titulo': 'Cuadrados perfectos',
        'subtitulo': 'Números que forman cuadrados geométricos exactos',
        'concepto': 'Un cuadrado perfecto es el resultado de multiplicar un número entero por sí mismo ($1, 4, 9, 16, 25, 36, 49, 64, 81, 100...$). Representan el área de un cuadrado de lado entero.',
        'por_que_funciona': 'Un cuadrado de 5 de lado tiene un área de 5 × 5 = 25 celdas.',
        'conexion_ingenieria': 'Complejidad algorítmica $O(n^2)$: algoritmos con bucles anidados (como Bubble Sort) crecen cuadráticamente respecto al tamaño de los datos de entrada.',
        'ejemplo': {
            'problema': '¿Cuál es el cuadrado de 7?',
            'pasos': [
                'Paso 1: Eleva 7 al cuadrado: 7^2 = 7 × 7.',
                'Paso 2: 7 × 7 = 49.'
            ],
            'resultado': '49'
        },
        'errores_comunes': [
            'Confundir el cuadrado de un número con su doble (el doble de 7 es 14; el cuadrado de 7 es 49).'
        ],
        'truco_profesor': 'Aprenderte de memoria los cuadrados del 1 al 12 te ahorrará muchísimo tiempo en álgebra e ingeniería.'
    },
    '5.3': {
        'titulo': 'Raíces cuadradas',
        'subtitulo': 'La operación inversa de elevar al cuadrado',
        'concepto': 'La raíz cuadrada $\sqrt{N}$ busca el número que, al multiplicarse por sí mismo, da $N$. Si $6^2 = 36$, entonces $\sqrt{36} = 6$. Es como conocer el área de un cuadrado y buscar cuánto mide su lado.',
        'por_que_funciona': 'Es la función inversa de la potencia cuadrática para números no negativos.',
        'conexion_ingenieria': 'Cálculo de la distancia euclidiana en videojuegos, gráficos 3D y algoritmos de Machine Learning (como K-Nearest Neighbors): $d = \sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$.',
        'ejemplo': {
            'problema': 'Calcula: √64',
            'pasos': [
                'Paso 1: Pregúntate: ¿qué número multiplicado por sí mismo da 64?',
                'Paso 2: Probamos: 7 × 7 = 49 (falta)... 8 × 8 = 64 (¡exacto!).',
                'Paso 3: Por lo tanto, √64 = 8.'
            ],
            'resultado': '8'
        },
        'errores_comunes': [
            'Dividir entre 2 (pensar que √64 es 64 ÷ 2 = 32 ¡NO!).'
        ],
        'truco_profesor': 'La raíz cuadrada NO es la mitad de un número; es la base de un cuadrado.'
    },
    '5.4': {
        'titulo': 'Leyes de los exponentes',
        'subtitulo': 'Reglas para multiplicar, dividir y elevar potencias',
        'concepto': '1) Misma base multiplicando: se suman exponentes: $a^m \times a^n = a^{m+n}$. 2) Misma base dividiendo: se restan exponentes: $a^m / a^n = a^{m-n}$. 3) Potencia de potencia: se multiplican: $(a^m)^n = a^{m \times n}$.',
        'por_que_funciona': '$2^3 \times 2^2 = (2 \times 2 \times 2) \times (2 \times 2) = 2^5$. Es simplemente contar cuántas veces se repite el factor.',
        'conexion_ingenieria': 'Análisis asintótico en estructuras de datos: entender por qué un árbol binario balanceado de altura $h$ tiene $2^h$ nodos y su búsqueda toma $O(\log n)$ pasos.',
        'ejemplo': {
            'problema': 'Simplifica: (2^3) × (2^4)',
            'pasos': [
                'Paso 1: Tienen la misma base (2).',
                'Paso 2: Al multiplicarse, los exponentes se suman: 3 + 4 = 7.',
                'Paso 3: Queda 2^7 = 128.'
            ],
            'resultado': '128 (o 2^7)'
        },
        'errores_comunes': [
            'Multiplicar las bases (hacer 2^3 × 2^4 = 4^7 ¡GRAVE ERROR!). La base no cambia.'
        ],
        'truco_profesor': 'Si las bases se multiplican, los exponentes se suman. Si las bases se dividen, los exponentes se restan.'
    },
    '5.5': {
        'titulo': 'Logaritmos y Exponenciales',
        'subtitulo': 'La operación inversa de la exponenciación',
        'concepto': 'Un logaritmo responde a la pregunta: "¿A qué exponente debo elevar la base $b$ para obtener el número $x$?". Si $b^y = x$, entonces $\\log_b(x) = y$. Por ejemplo, $\\log_2(8) = 3$ porque $2^3 = 8$.',
        'por_que_funciona': 'El logaritmo "deshace" la potencia. Propiedades clave: $\\log(a \\cdot b) = \\log(a) + \\log(b)$ y $\\log(a^k) = k \\cdot \\log(a)$.',
        'conexion_ingenieria': 'La complejidad algorítmica fundamental en Ciencias de la Computación: Búsqueda Binaria $O(\\log_2 n)$, árboles binarios balanceados (AVL, Red-Black), y la escala de información en bits (Teoría de Shannon).',
        'ejemplo': {
            'problema': 'Calcula: \\log_2(64)',
            'pasos': [
                'Paso 1: Pregúntate: ¿2 elevado a qué potencia da 64?',
                'Paso 2: Cuenta potencias de 2: 2^1=2, 2^2=4, 2^3=8, 2^4=16, 2^5=32, 2^6=64.',
                'Paso 3: El exponente necesario es 6.',
                'Paso 4: Por lo tanto, \\log_2(64) = 6.'
            ],
            'resultado': '6'
        },
        'errores_comunes': [
            'Confundir logaritmo con división (pensar que log_2(64) es 64 ÷ 2 = 32).'
        ],
        'truco_profesor': 'Lee siempre log_b(x) como: "¿A cuánto elevo b para llegar a x?".'
    },

    # ============================================================
    # NIVEL 6: ÁLGEBRA BÁSICA
    # ============================================================
    '6.1': {
        'titulo': 'Números enteros: positivos y negativos',
        'subtitulo': 'La recta numérica y la ley de los signos',
        'concepto': 'Los números negativos representan deudas, temperaturas bajo cero o pasos hacia la izquierda en la recta numérica. La regla de signos: signos iguales dan positivo (+ × + = + y - × - = +); signos distintos dan negativo (+ × - = -).',
        'por_que_funciona': 'Restar un número negativo es quitar una deuda, lo cual equivale a tener más dinero (positivo): 5 - (-3) = 5 + 3 = 8.',
        'conexion_ingenieria': 'Representación en complemento a 2 en procesadores para manejar números con signo (`int8`, `int32`, `int64`).',
        'ejemplo': {
            'problema': 'Calcula: -7 + 12',
            'pasos': [
                'Paso 1: Míralo como: tienes una deuda de 7 dólares pero pagas con un billete de 12.',
                'Paso 2: Te sobra dinero: 12 - 7 = 5.',
                'Paso 3: Como el número positivo era mayor, el resultado es positivo: +5.'
            ],
            'resultado': '5'
        },
        'errores_comunes': [
            'Aplicar la ley de signos de la multiplicación a la suma (ej. pensar que en -3 - 4 "menos por menos da más"; ¡NO! Si debes 3 y debes 4, debes 7: -7).'
        ],
        'truco_profesor': 'Para sumar/restar con signos: piensa siempre en "dinero que tengo (+)" vs "deuda que debo (-)". Nunca falla.'
    },
    '6.2': {
        'titulo': 'Uso de letras en matemáticas (Variables)',
        'subtitulo': 'De los números fijos a las cajas que guardan valores',
        'concepto': 'Una letra en álgebra ($x, y, n$) es simplemente una etiqueta o caja que guarda un valor desconocido o variable. En $x + 3 = 10$, la letra $x$ es una incógnita cuyo valor hace verdadera la igualdad.',
        'por_que_funciona': 'Permite escribir fórmulas universales que funcionan para cualquier número, no solo para uno.',
        'conexion_ingenieria': '¡Las variables en programación! Cuando declaras `let x = 10;` o `int total = precio * cantidad;`, estás haciendo álgebra directa en código.',
        'ejemplo': {
            'problema': 'Si x = 4, ¿cuánto vale 3x + 2?',
            'pasos': [
                'Paso 1: 3x significa 3 multiplicado por x.',
                'Paso 2: Sustituye x por 4: 3(4) + 2.',
                'Paso 3: Primero la multiplicación: 3 × 4 = 12.',
                'Paso 4: Luego la suma: 12 + 2 = 14.'
            ],
            'resultado': '14'
        },
        'errores_comunes': [
            'Pensar que 3x cuando x=4 es el número 34 (no es juntar los dígitos, es una multiplicación: 3 × 4).'
        ],
        'truco_profesor': 'Siempre que veas un número pegado a una letra (como 5y), hay una multiplicación invisible entre ellos.'
    },
    '6.3': {
        'titulo': 'Expresiones algebraicas y términos semejantes',
        'subtitulo': 'Sumando manzanas con manzanas y peras con peras',
        'concepto': 'Solo puedes sumar o restar términos algebraicos que tengan exactamente la misma parte literal (mismas letras con mismos exponentes). $3x + 2x = 5x$, pero $3x + 2y$ no se puede juntar más.',
        'por_que_funciona': 'Es la propiedad distributiva al revés: $3x + 2x = (3 + 2)x = 5x$.',
        'conexion_ingenieria': 'Optimización de código en compiladores: simplificación de árboles de sintaxis abstracta (AST) para reducir instrucciones redundantes.',
        'ejemplo': {
            'problema': 'Simplifica: 4x + 7 - 2x + 3',
            'pasos': [
                'Paso 1: Agrupa los términos con x: 4x - 2x = 2x.',
                'Paso 2: Agrupa los números sueltos: 7 + 3 = 10.',
                'Paso 3: Junta todo: 2x + 10.'
            ],
            'resultado': '2x + 10'
        },
        'errores_comunes': [
            'Intentar sumar 2x + 10 = 12x (¡no puedes sumar una variable con un número independiente!).'
        ],
        'truco_profesor': 'Subraya con un color los términos con x y con otro color los números sueltos antes de operar.'
    },
    '6.4': {
        'titulo': 'Ecuaciones de primer grado',
        'subtitulo': 'La balanza en equilibrio y cómo encontrar la incógnita',
        'concepto': 'Una ecuación es una balanza en perfecto equilibrio. Lo que hay a la izquierda del signo "=" pesa exactamente lo mismo que lo de la derecha. Si sumas, restas, multiplicas o divides algo en un lado, debes hacer exactamente lo mismo en el otro para que la balanza no se desequilibre.',
        'por_que_funciona': 'El principio de operaciones inversas: para deshacer una suma, restas; para deshacer una multiplicación, divides.',
        'conexion_ingenieria': 'Resolución de dependencias y equilibrio de recursos en sistemas distribuidos.',
        'ejemplo': {
            'problema': 'Resuelve: 2x + 5 = 15',
            'pasos': [
                'Paso 1: El objetivo es dejar a la x sola en un lado.',
                'Paso 2: Quitamos el +5 restando 5 en ambos lados: 2x = 15 - 5 -> 2x = 10.',
                'Paso 3: Quitamos el 2 que multiplica a la x dividiendo entre 2 ambos lados: x = 10 / 2.',
                'Paso 4: Resultado: x = 5. Comprobamos: 2(5) + 5 = 10 + 5 = 15. ¡Exacto!'
            ],
            'resultado': 'x = 5'
        },
        'errores_comunes': [
            'Pasar un número al otro lado sin cambiarle el signo (si está sumando pasa restando).'
        ],
        'truco_profesor': 'Regla del "desvestir la x": primero quitas los números que están sumando o restando (lo que está más lejos), y al final quitas el número que está pegado multiplicando.'
    },
    '6.5': {
        'titulo': 'Despejes en fórmulas',
        'subtitulo': 'Aislando cualquier variable para reutilizarla',
        'concepto': 'Despejar es reorganizar una fórmula para que la variable que necesitas quede sola a la izquierda. Si tienes $Velocidad = Distancia / Tiempo$, puedes despejar $Distancia = Velocidad \times Tiempo$.',
        'por_que_funciona': 'Mismas reglas de la balanza de las ecuaciones aplicadas a letras en lugar de números.',
        'conexion_ingenieria': 'Transformación de modelos matemáticos y fórmulas en funciones computacionales: de $F = m \cdot a$ a `float aceleracion = fuerza / masa;`.',
        'ejemplo': {
            'problema': 'De la fórmula P = 2a + 2b, despeja la variable a',
            'pasos': [
                'Paso 1: Pasa el término +2b restando al otro lado: P - 2b = 2a.',
                'Paso 2: Pasa el 2 que multiplica a la variable a dividiendo a todo el lado izquierdo: (P - 2b) / 2 = a.',
                'Paso 3: Resultado: a = (P - 2b) / 2.'
            ],
            'resultado': 'a = (P - 2b) / 2'
        },
        'errores_comunes': [
            'Pasar dividiendo el 2 solo debajo de la P y no de todo el término.'
        ],
        'truco_profesor': 'Trata a las demás letras como si fueran números comunes y corrientes. Las reglas de movimiento son exactamente iguales.'
    },
    '6.6': {
        'titulo': 'Factorización básica: Factor Común',
        'subtitulo': 'El camino inverso de la multiplicación',
        'concepto': 'Factorizar significa transformar una suma en una multiplicación de factores. Si en $ax + ay$ la letra $a$ está en ambos términos, la sacas afuera de un paréntesis: $a(x + y)$.',
        'por_que_funciona': 'Es la propiedad distributiva leída de derecha a izquierda: $a(x + y) = ax + ay$.',
        'conexion_ingenieria': 'Compresión de datos y eliminación de código duplicado (factorización de código o refactoring: extraer una función común a la que se le pasan argumentos).',
        'ejemplo': {
            'problema': 'Factoriza: 6x + 9',
            'pasos': [
                'Paso 1: Busca el Máximo Común Divisor entre 6 y 9. Ambos se pueden dividir entre 3.',
                'Paso 2: Saca el 3 afuera del paréntesis: 3(...)',
                'Paso 3: Divide cada término entre 3: 6x / 3 = 2x, y 9 / 3 = 3.',
                'Paso 4: Escribe la expresión factorizada: 3(2x + 3).'
            ],
            'resultado': '3(2x + 3)'
        },
        'errores_comunes': [
            'Olvidar colocar el 1 cuando se factoriza un término completo (ej: $5x + 5 = 5(x + 1)$, no $5(x)$).'
        ],
        'truco_profesor': 'Comprueba siempre tu factorización multiplicando de vuelta con la distributiva. Si no te da exactamente la expresión original, revisa los signos.'
    },

    '6.7': {
        'titulo': 'Productos notables: Binomios al cuadrado y diferencias de cuadrados',
        'subtitulo': 'Fórmulas directas para expandir productos algebraicos',
        'concepto': 'Los productos notables son identidades algebraicas fijas: $(a+b)^2 = a^2 + 2ab + b^2$, $(a-b)^2 = a^2 - 2ab + b^2$, y la diferencia de cuadrados $(a+b)(a-b) = a^2 - b^2$.',
        'por_que_funciona': 'Surgen de la propiedad distributiva. Aprender el patrón de memoria te ahorra multiplicar término a término en cada paso de un problema largo.',
        'conexion_ingenieria': 'Optimización de algoritmos en compiladores y procesamiento de señales digitales (DSP), transformando operaciones pesadas en sumas y corrimientos.',
        'ejemplo': {
            'problema': 'Desarrolla: (x + 5)^2',
            'pasos': [
                'Paso 1: Identifica a = x y b = 5.',
                'Paso 2: Cuadrado del primero: x^2.',
                'Paso 3: Doble del primero por el segundo: 2 · x · 5 = 10x.',
                'Paso 4: Cuadrado del segundo: 5^2 = 25.',
                'Paso 5: Expresión desarrollada: x^2 + 10x + 25.'
            ],
            'resultado': 'x^2 + 10x + 25'
        },
        'errores_comunes': [
            'Olvidar el término central 2ab y escribir erróneamente (x+5)^2 = x^2 + 25.'
        ],
        'truco_profesor': 'Nemotecnia rítmica: "Primero al cuadrado, doble producto, segundo al cuadrado".'
    },
    '6.8': {
        'titulo': 'Ecuaciones cuadráticas (Segundo grado)',
        'subtitulo': 'Fórmula general y factorización',
        'concepto': 'Una ecuación cuadrática tiene la forma $ax^2 + bx + c = 0$. Sus soluciones vienen dadas por la fórmula general: $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$.',
        'por_que_funciona': 'El discriminante $\\Delta = b^2 - 4ac$ revela la cantidad y tipo de soluciones: $\\Delta > 0$ da 2 soluciones reales distintas, $\\Delta = 0$ da 1 solución real repetida, y $\\Delta < 0$ da soluciones complejas.',
        'conexion_ingenieria': 'Cálculo de trayectorias parabólicas en motores de física de videojuegos, tiempo de vuelo de proyectiles y diseño de antenas satelitales.',
        'ejemplo': {
            'problema': 'Resuelve: x^2 - 7x + 10 = 0',
            'pasos': [
                'Paso 1: Identifica coeficientes: a = 1, b = -7, c = 10.',
                'Paso 2: Factorización rápida: busca dos números que multiplicados den +10 y sumados den -7 (-5 y -2).',
                'Paso 3: Escribe como factores: (x - 5)(x - 2) = 0.',
                'Paso 4: Soluciones: x = 5 o x = 2.'
            ],
            'resultado': 'x = 2, x = 5'
        },
        'errores_comunes': [
            'Olvidar invertir los signos de los factores: si (x - 5) = 0, entonces x = +5.'
        ],
        'truco_profesor': 'Cuando el coeficiente principal es 1, busca dos números que multipliquen el término independiente y sumen el coeficiente central.'
    },
    '6.9': {
        'titulo': 'Sistemas Numéricos: Binario, Hexadecimal y Decimal',
        'subtitulo': 'El lenguaje nativo del hardware y la memoria',
        'concepto': 'El sistema binario (base 2) usa únicamente los dígitos 0 y 1. Cada posición representa una potencia de 2 ($1, 2, 4, 8, 16, 32, ...$). El sistema hexadecimal (base 16) usa dígitos del 0 al 9 y las letras A=10, B=11, C=12, D=13, E=14, F=15. Cada dígito hexadecimal comprime exactamente 4 bits (un nibble).',
        'por_que_funciona': 'Cualquier número en base $b$ equivale al polinomio $\\sum d_i \\cdot b^i$. Por ejemplo: $1101_2 = 1\\cdot 2^3 + 1\\cdot 2^2 + 0\\cdot 2^1 + 1\\cdot 2^0 = 8 + 4 + 0 + 1 = 13_{10}$.',
        'conexion_ingenieria': 'Esencial para todo Ingeniero de Sistemas: direcciones de memoria RAM (`0x7FFEE4B3`), códigos de color hexadecimal en frontend CSS (`#4F46E5`), máscaras de subred IPv4 y programación de bajo nivel a nivel de registros de CPU.',
        'ejemplo': {
            'problema': 'Convierte el número binario 1101 a decimal',
            'pasos': [
                'Paso 1: Escribe las potencias de 2 correspondientes de derecha a izquierda: 8, 4, 2, 1.',
                'Paso 2: Multiplica cada bit por su potencia: (1×8) + (1×4) + (0×2) + (1×1).',
                'Paso 3: Suma las contribuciones activas: 8 + 4 + 0 + 1 = 13.'
            ],
            'resultado': '13'
        },
        'errores_comunes': [
            'Olvidar que la primera posición a la derecha es 2^0 = 1 (no empezar en 2).'
        ],
        'truco_profesor': 'Memoriza la secuencia mágica: 128, 64, 32, 16, 8, 4, 2, 1. ¡Solo sumas las casillas que tienen un 1!'
    },

    # ============================================================
    # NIVEL 7: MATEMÁTICA PARA LA INGENIERÍA (SÍLABO OFICIAL 2026-2)
    # ============================================================
    '7.1': {
        'titulo': 'Sesión 1: Números Reales, Desigualdades y Valor Absoluto',
        'subtitulo': 'Conjuntos numéricos, intervalos en la recta y cotas de error',
        'concepto': 'Los números reales $\\mathbb{R}$ forman una recta continua. Las desigualdades ($<, \\le, >, \\ge$) definen intervalos como $[a, b]$ (cerrado, incluye extremos) o $(a, b)$ (abierto). El valor absoluto $|x|$ representa la distancia al cero: $|x| \\le k \\iff -k \\le x \\le k$.',
        'por_que_funciona': 'Al multiplicar o dividir una desigualdad por un número negativo, el sentido de la desigualdad se invierte: si $-2x < 6$, entonces $x > -3$.',
        'conexion_ingenieria': 'Validación de rangos de datos en formularios y APIs (evitar desbordamientos de enteros), ventanas de tiempo en protocolos de red y márgenes de tolerancia de latencia.',
        'ejemplo': {
            'problema': 'Resuelve la desigualdad: |x - 3| \\le 5',
            'pasos': [
                'Paso 1: Por la propiedad del valor absoluto: -5 \\le x - 3 \\le 5.',
                'Paso 2: Suma 3 a todos los miembros de la desigualdad: -5 + 3 \\le x \\le 5 + 3.',
                'Paso 3: Simplifica los extremos: -2 \\le x \\le 8.',
                'Paso 4: El conjunto solución es el intervalo cerrado [-2, 8].'
            ],
            'resultado': '[-2, 8]'
        },
        'errores_comunes': [
            'Olvidar invertir el signo de la desigualdad al multiplicar o dividir por un número negativo.'
        ],
        'truco_profesor': '|x - c| \\le r significa simplemente: todos los números cuya distancia al centro c es a lo sumo el radio r.'
    },
    '7.2': {
        'titulo': 'Sesión 2: Expresiones Racionales y Fracciones Algebraicas',
        'subtitulo': 'Simplificación, mínimo común múltiplo y restricciones de dominio',
        'concepto': 'Una expresión racional es una fracción de polinomios $\\frac{P(x)}{Q(x)}$ con la restricción obligatoria $Q(x) \\neq 0$. Para simplificarla, se factorizan numerador y denominador y se cancelan los factores comunes.',
        'por_que_funciona': 'Al igual que $\\frac{6}{8} = \\frac{2 \\cdot 3}{2 \\cdot 4} = \\frac{3}{4}$, en álgebra dividimos arriba y abajo entre el mismo factor no nulo.',
        'conexion_ingenieria': 'Funciones de transferencia en teoría de sistemas, análisis de algoritmos y diseño de filtros digitales en procesamiento de audio y vídeo.',
        'ejemplo': {
            'problema': 'Simplifica: \\frac{x^2 - 9}{x - 3} con x \\neq 3',
            'pasos': [
                'Paso 1: Factoriza el numerador por diferencia de cuadrados: x^2 - 9 = (x - 3)(x + 3).',
                'Paso 2: Escribe la fracción: \\frac{(x - 3)(x + 3)}{x - 3}.',
                'Paso 3: Cancela el factor común (x - 3).',
                'Paso 4: El resultado simplificado es x + 3.'
            ],
            'resultado': 'x + 3'
        },
        'errores_comunes': [
            'Intentar cancelar términos individuales que están sumando en vez de factores que multiplican a toda la expresión.'
        ],
        'truco_profesor': 'Solo se pueden tachar factores completos entre paréntesis, nunca números sueltos que estén sumando.'
    },
    '7.3': {
        'titulo': 'Sesión 3: Matrices y Operaciones Matriciales en Ingeniería',
        'subtitulo': 'Suma, producto por escalar y multiplicación de matrices',
        'concepto': 'Una matriz es una tabla rectangular de datos organizados en filas y columnas. Para sumar dos matrices deben tener el mismo tamaño. Para multiplicar $A_{m \\times k} \\times B_{k \\times n}$, el número de columnas de $A$ debe coincidir con el de filas de $B$. Cada elemento se calcula como el producto punto de una fila por una columna.',
        'por_que_funciona': 'La multiplicación de matrices representa la composición de transformaciones lineales en el espacio.',
        'conexion_ingenieria': 'Computación Gráfica 3D (rotar, escalar y mover personajes con matrices $4 \\times 4$), Deep Learning (multiplicación masiva de tensores en GPU/TPU) y grafos de redes representados por matrices de adyacencia.',
        'ejemplo': {
            'problema': 'Dadas A = [[1, 2], [3, 4]] y B = [[2, 0], [1, 3]], calcula el elemento C11 de C = A × B',
            'pasos': [
                'Paso 1: C11 es el producto de la Fila 1 de A por la Columna 1 de B.',
                'Paso 2: Fila 1 de A = [1, 2]. Columna 1 de B = [2, 1]^T.',
                'Paso 3: Multiplica y suma: (1 × 2) + (2 × 1) = 2 + 2 = 4.'
            ],
            'resultado': '4'
        },
        'errores_comunes': [
            'Creer que el producto de matrices es conmutativo: en general, A × B NO es igual a B × A.'
        ],
        'truco_profesor': 'Regla nemotécnica para multiplicar: "Fila horizontal de la izquierda por columna vertical de la derecha".'
    },
    '7.4': {
        'titulo': 'Sesión 4: Determinantes y Matriz Inversa',
        'subtitulo': 'Regla de Sarrus, cálculo de determinantes 2×2 y método de Gauss-Jordan',
        'concepto': 'El determinante $\\det(A)$ o $|A|$ es un escalar que indica si una matriz tiene inversa. Para una matriz $2 \\times 2$: $\\det(A) = ad - bc$. Si $\\det(A) \\neq 0$, la matriz es invertible (no singular) y existe $A^{-1}$ tal que $A \\cdot A^{-1} = I$.',
        'por_que_funciona': 'El determinante mide cuánto amplifica la matriz el área o volumen. Si el determinante es 0, la matriz "aplasta" el espacio y destruye información, por lo que no puede tener inversa.',
        'conexion_ingenieria': 'Criptografía (cifrado matricial de Hill), cálculo del Jacobiano en cinemática robótica y verificación de independencia de paquetes en transmisiones de red.',
        'ejemplo': {
            'problema': 'Calcula el determinante de la matriz A = [[4, 2], [1, 3]]',
            'pasos': [
                'Paso 1: Aplica la fórmula ad - bc: diagonal principal menos diagonal secundaria.',
                'Paso 2: Diagonal principal: 4 × 3 = 12.',
                'Paso 3: Diagonal secundaria: 2 × 1 = 2.',
                'Paso 4: Resta: 12 - 2 = 10.'
            ],
            'resultado': '10'
        },
        'errores_comunes': [
            'Confundir el signo al restar la diagonal secundaria (olvidar que siempre lleva un signo menos).'
        ],
        'truco_profesor': 'Si el determinante te da cero, la matriz no tiene inversa y el sistema de ecuaciones asociado no tendrá solución única.'
    },
    '7.5': {
        'titulo': 'Sesión 5: Sistemas de Ecuaciones Lineales y Regla de Cramer',
        'subtitulo': 'Resolución matricial de sistemas compatibles determinados',
        'concepto': 'Un sistema de ecuaciones $A \\cdot X = B$ se puede resolver mediante determinantes usando la Regla de Cramer: cada incógnita vale $x_i = \\frac{\\det(A_i)}{\\det(A)}$, donde $A_i$ resulta de sustituir la columna $i$ por el vector de términos independientes $B$.',
        'por_que_funciona': 'Es una consecuencia directa de la fórmula de la matriz inversa expresada término a término mediante adjuntos.',
        'conexion_ingenieria': 'Resolución de flujos de carga en redes eléctricas de computadores, planificación de balanceo de carga en clústeres de servidores y equilibrio de tráfico de paquetes.',
        'ejemplo': {
            'problema': 'Resuelve por Cramer para x: 2x + y = 7  y  x - y = 2',
            'pasos': [
                'Paso 1: Determinante del sistema Δ = (2)(-1) - (1)(1) = -2 - 1 = -3.',
                'Paso 2: Matriz para x: sustituye columna 1 por [7, 2]^T: Δx = (7)(-1) - (1)(2) = -7 - 2 = -9.',
                'Paso 3: Calcula x = Δx / Δ = -9 / -3 = 3.'
            ],
            'resultado': '3'
        },
        'errores_comunes': [
            'Dividir entre Δ cuando Δ = 0 (si Δ = 0, Cramer no se puede aplicar y el sistema es incompatible o indeterminado).'
        ],
        'truco_profesor': 'Siempre calcula primero el determinante del sistema Δ. Si da cero, detén Cramer inmediatamente.'
    },
    '7.6': {
        'titulo': 'Sesión 6: Funciones Reales y Modelos en Ingeniería',
        'subtitulo': 'Dominio, rango y modelos matemáticos de costos, ingresos y utilidades',
        'concepto': 'El dominio de una función $f(x)$ son todos los valores reales de $x$ para los que la función está matemáticamente definida. Restricciones clásicas: el denominador no puede ser 0 y la expresión dentro de una raíz cuadrada debe ser $\\ge 0$. En ingeniería modelamos costos $C(x) = C_{fijo} + C_{unitario} \\cdot x$ y utilidades $U(x) = I(x) - C(x)$.',
        'por_que_funciona': 'Las computadoras arrojan excepciones (`DivisionByZeroException`, `NaN`) exactamente cuando una entrada cae fuera del dominio matemático de la función.',
        'conexion_ingenieria': 'Modelado del costo de almacenamiento en la nube (AWS/Azure/GCP), cálculo de latencia en función del número de peticiones concurrentes y dimensionamiento de servidores.',
        'ejemplo': {
            'problema': 'Halla el dominio de la función f(x) = \\sqrt{x - 4}',
            'pasos': [
                'Paso 1: Lo que está dentro de la raíz cuadrada debe ser mayor o igual a cero: x - 4 \\ge 0.',
                'Paso 2: Despeja x pasando el 4 sumando: x \\ge 4.',
                'Paso 3: En notación de intervalo: [4, +\\infty).'
            ],
            'resultado': '[4, inf)'
        },
        'errores_comunes': [
            'Incluir valores que hacen cero el denominador en el dominio.'
        ],
        'truco_profesor': 'Pregúntate siempre dos cosas: "¿Hay alguna división entre algo con x?" y "¿Hay alguna raíz cuadrada?". Ellas son las únicas que restringen el dominio real.'
    },
    '7.7': {
        'titulo': 'Sesión 7: Composición de Funciones y Función Inversa',
        'subtitulo': 'Pipelines matemáticos (f o g)(x) y reversibilidad f^(-1)',
        'concepto': 'La composición $(f \\circ g)(x) = f(g(x))$ significa pasar la salida de la función $g$ como argumento de entrada de $f$. La función inversa $f^{-1}(x)$ revierte exactamente lo que hace $f$: si $f(a) = b$, entonces $f^{-1}(b) = a$.',
        'por_que_funciona': 'Cumplen la propiedad de identidad: $(f \\circ f^{-1})(x) = x$.',
        'conexion_ingenieria': 'Pipelines de datos en software (`Stream.map().filter()`, Unix pipes `ls | grep`), algoritmos de compresión y descompresión (Zip), y criptografía simétrica (cifrar y descifrar).',
        'ejemplo': {
            'problema': 'Si f(x) = 2x + 1 y g(x) = x^2, halla (f o g)(3)',
            'pasos': [
                'Paso 1: Evalúa primero la función interior g(3): g(3) = 3^2 = 9.',
                'Paso 2: Pasa ese resultado a la función exterior f: f(9).',
                'Paso 3: f(9) = 2(9) + 1 = 18 + 1 = 19.'
            ],
            'resultado': '19'
        },
        'errores_comunes': [
            'Confundir f(g(x)) con g(f(x)): el orden de composición sí altera el resultado.'
        ],
        'truco_profesor': 'Evalúa de adentro hacia afuera: primero calcula el valor de la función interna y luego aliméntalo a la externa.'
    },
    '7.8': {
        'titulo': 'Sesión 8/9: Funciones Seccionadas y Análisis Gráfico',
        'subtitulo': 'Funciones definidas por partes (tramos) y su visualización',
        'concepto': 'Una función seccionada (o a trozos) utiliza diferentes fórmulas según el subintervalo en el que se encuentre la variable $x$. Se grafica dibujando cada fórmula en su respectivo dominio, prestando atención a puntos cerrados (incluidos, $\\le, \\ge$) y abiertos (excluidos, $<, >$).',
        'por_que_funciona': 'Permite modelar sistemas que cambian drásticamente de comportamiento según un umbral crítico.',
        'conexion_ingenieria': '¡Las sentencias `if-else` y `switch` en programación! Ejemplo: tarificación de APIs por cuotas (hasta 10,000 requests gratis, luego $0.001 por llamada).',
        'ejemplo': {
            'problema': 'Sea f(x) = 2x si x < 3, y f(x) = x + 5 si x >= 3. Calcula f(4)',
            'pasos': [
                'Paso 1: Determina qué condición cumple x = 4.',
                'Paso 2: Como 4 >= 3, usamos el segundo tramo: f(x) = x + 5.',
                'Paso 3: Sustituye x = 4: f(4) = 4 + 5 = 9.'
            ],
            'resultado': '9'
        },
        'errores_comunes': [
            'Evaluar el valor en ambos tramos a la vez. Una función solo puede devolver un valor para cada x.'
        ],
        'truco_profesor': 'Trata cada tramo como una cláusula `if (x < umbral) return formula1; else return formula2;`.'
    },
    '7.9': {
        'titulo': 'Sesión 10: Examen Parcial de Ingeniería',
        'subtitulo': 'Evaluación integral de Álgebra Lineal, Matrices y Funciones',
        'concepto': 'El examen parcial consolida todos los conceptos fundamentales de la primera mitad del curso: operaciones matriciales, determinantes, sistemas de ecuaciones lineales por Cramer y análisis de funciones reales.',
        'por_que_funciona': 'Integra múltiples ramas de la matemática aplicada para comprobar que las herramientas se pueden combinar fluidamente en problemas de ingeniería.',
        'conexion_ingenieria': 'Resolución de problemas multidisciplinarios en desarrollo de software, modelado de sistemas de información y optimización.',
        'ejemplo': {
            'problema': 'Calcula det(A) si A = [[3, 1], [2, 4]]',
            'pasos': [
                'Paso 1: det(A) = ad - bc = (3)(4) - (1)(2).',
                'Paso 2: 12 - 2 = 10.'
            ],
            'resultado': '10'
        },
        'errores_comunes': [
            'Descuidar la verificación de signos en operaciones compuestas.'
        ],
        'truco_profesor': 'En el examen parcial, revisa siempre tus resultados sustituyendo las respuestas en las ecuaciones originales.'
    },
    '7.10': {
        'titulo': 'Sesión 11: Coordenadas Polares y Curvas Planas',
        'subtitulo': 'Representación por radio y ángulo (r, θ) vs coordenadas cartesianas (x, y)',
        'concepto': 'Un punto en coordenadas polares se define por su distancia al origen $r$ y su ángulo $\\theta$ respecto al eje polar. Fórmulas de conversión: de polar a cartesiano: $x = r \\cos\\theta$, $y = r \\sin\\theta$. De cartesiano a polar: $r = \\sqrt{x^2 + y^2}$, $\\theta = \\arctan(y/x)$.',
        'por_que_funciona': 'Surge de la trigonometría básica en el triángulo rectángulo formado por el vector posición.',
        'conexion_ingenieria': 'Sistemas de radar y sonar, navegación por satélite GPS, visión artificial en robots móviles y cinemática de motores giratorios.',
        'ejemplo': {
            'problema': 'Convierte el punto polar (r = 4, θ = 0°) a coordenadas cartesianas (x, y)',
            'pasos': [
                'Paso 1: x = r · cos(θ) = 4 · cos(0°) = 4 · 1 = 4.',
                'Paso 2: y = r · sin(θ) = 4 · sin(0°) = 4 · 0 = 0.',
                'Paso 3: El punto cartesiano es (4, 0).'
            ],
            'resultado': '(4, 0)'
        },
        'errores_comunes': [
            'Confundir radianes y grados al usar calculadoras o bibliotecas matemáticas en código (`Math.cos`).'
        ],
        'truco_profesor': 'Recuerda que en el eje X el ángulo es 0°. Si θ = 0°, x vale r y y vale 0.'
    },
    '7.11': {
        'titulo': 'Sesión 12: Límites de Funciones, Límites Laterales y Teoremas',
        'subtitulo': 'Comportamiento en la vecindad de un punto y existencia del límite',
        'concepto': 'El límite $\\lim_{x \\to a} f(x) = L$ describe el valor al que se aproxima $f(x)$ cuando $x$ se acerca infinitamente a $a$. El límite existe si y solo si los dos límites laterales coinciden: $\\lim_{x \\to a^-} f(x) = \\lim_{x \\to a^+} f(x) = L$.',
        'por_que_funciona': 'Permite estudiar el comportamiento asintótico sin tener que evaluar directamente en puntos donde la función no esté definida.',
        'conexion_ingenieria': 'Análisis asintótico de algoritmos (notación Big-O), comportamiento de latencias en colas de espera en servidores y estabilidad de sistemas en tiempo real.',
        'ejemplo': {
            'problema': 'Calcula: \\lim_{x \\to 3} (2x + 5)',
            'pasos': [
                'Paso 1: Como la función es polinómica (continua), sustituye directamente x = 3.',
                'Paso 2: 2(3) + 5 = 6 + 5 = 11.',
                'Paso 3: El límite es 11.'
            ],
            'resultado': '11'
        },
        'errores_comunes': [
            'Creer que el límite no existe solo porque f(a) tenga un hueco (el límite analiza las cercanías, no el punto exacto).'
        ],
        'truco_profesor': 'Empieza siempre intentando la sustitución directa. Si no da indeterminación (como 0/0), ¡ese número es tu respuesta!'
    },
    '7.12': {
        'titulo': 'Sesión 13: Cálculo Analítico de Límites e Indeterminaciones',
        'subtitulo': 'Superando la indeterminación 0/0 mediante factorización y racionalización',
        'concepto': 'Cuando la sustitución directa produce la forma indeterminada $\\frac{0}{0}$, significa que hay un factor $(x - a)$ oculto tanto en el numerador como en el denominador que produce el cero. Se resuelve factorizando y cancelando dicho factor, o multiplicando por la conjugada en expresiones con raíces.',
        'por_que_funciona': 'Al simplificar la fracción antes de tomar el límite, removemos la singularidad evitable.',
        'conexion_ingenieria': 'Cálculo de funciones de activación en Machine Learning (evitar overflow/underflow numérico en computación de punto flotante) y análisis de estabilidad de señales.',
        'ejemplo': {
            'problema': 'Calcula: \\lim_{x \\to 2} \\frac{x^2 - 4}{x - 2}',
            'pasos': [
                'Paso 1: Sustituye x = 2: (4 - 4)/(2 - 2) = 0/0 (indeterminación).',
                'Paso 2: Factoriza el numerador por diferencia de cuadrados: (x - 2)(x + 2).',
                'Paso 3: Cancela el factor (x - 2): queda (x + 2).',
                'Paso 4: Evalúa el límite en la expresión simplificada: 2 + 2 = 4.'
            ],
            'resultado': '4'
        },
        'errores_comunes': [
            'Concluir que 0/0 es igual a 0 o a 1. 0/0 es una forma indeterminada y requiere álgebra adicional.'
        ],
        'truco_profesor': 'Si x tiende a 2 y da 0/0, busca inmediatamente el factor (x - 2) arriba y abajo para cancelarlo.'
    },
    '7.13': {
        'titulo': 'Sesión 14: Continuidad de Funciones y Discontinuidades',
        'subtitulo': 'Las 3 condiciones de continuidad y clasificación de saltos',
        'concepto': 'Una función $f(x)$ es continua en $x = c$ si cumple 3 condiciones estrictas: 1) $f(c)$ existe, 2) $\\lim_{x \\to c} f(x)$ existe, y 3) $\\lim_{x \\to c} f(x) = f(c)$. Si falla alguna, hay una discontinuidad: evitable (un punto o hueco), de salto finito, o infinita (asíntota vertical).',
        'por_que_funciona': 'Intuitivamente, una función es continua si puedes trazar su gráfica completa sin levantar el lápiz del papel.',
        'conexion_ingenieria': 'Señales continuas analógicas vs señales digitales discretas, transiciones de estado en autómatas finitos y sistemas tolerantes a fallos.',
        'ejemplo': {
            'problema': '¿Es continua f(x) = 3x en x = 2?',
            'pasos': [
                'Paso 1: f(2) = 3(2) = 6 (existe).',
                'Paso 2: \\lim_{x \\to 2} (3x) = 6 (existe).',
                'Paso 3: El límite coincide con el valor de la función: 6 == 6.',
                'Paso 4: Por lo tanto, la función es continua en x = 2.'
            ],
            'resultado': 'Continua'
        },
        'errores_comunes': [
            'Verificar solo que el límite exista sin comprobar si coincide con el valor puntual f(c).'
        ],
        'truco_profesor': 'Todos los polinomios son continuos en todo su dominio. Las únicas sospechas de discontinuidad surgen en divisiones entre cero o en los cambios de tramo de funciones seccionadas.'
    },
    '7.14': {
        'titulo': 'Sesión 15: Derivadas, Reglas de Derivación y Optimización',
        'subtitulo': 'Tasa de cambio instantánea, regla de la potencia, cadena y máximos/mínimos',
        'concepto': 'La derivada $f\'(x)$ representa la pendiente de la recta tangente a la curva en un punto. Reglas clave: potencia $\\frac{d}{dx}[x^n] = n x^{n-1}$, producto $(uv)\' = u\'v + uv\'$, y regla de la cadena $[f(g(x))]\' = f\'(g(x)) \\cdot g\'(x)$. En optimización, los puntos críticos donde $f\'(x) = 0$ permiten encontrar costos mínimos o rendimientos máximos.',
        'por_que_funciona': 'En un punto máximo o mínimo de una curva suave, la recta tangente es completamente horizontal (pendiente = 0).',
        'conexion_ingenieria': 'El núcleo de la Inteligencia Artificial: Descenso de Gradiente (Gradient Descent) en redes neuronales, ajuste de pesos en Deep Learning y optimización del rendimiento en bases de datos.',
        'ejemplo': {
            'problema': 'Calcula la derivada de f(x) = 4x^3',
            'pasos': [
                'Paso 1: Aplica la regla de la potencia: baja el exponente 3 multiplicando al coeficiente 4.',
                'Paso 2: 4 × 3 = 12.',
                'Paso 3: Resta 1 al exponente: 3 - 1 = 2.',
                'Paso 4: La derivada es 12x^2.'
            ],
            'resultado': '12x^2'
        },
        'errores_comunes': [
            'Olvidar restar 1 al exponente tras multiplicarlo.'
        ],
        'truco_profesor': 'Canta el mantra: "Baja a multiplicar y descuenta uno al exponente".'
    },
    '7.15': {
        'titulo': 'Sesión 16: Examen Final de Matemática para la Ingeniería',
        'subtitulo': 'Evaluación integral de todo el curso',
        'concepto': 'El examen final evalúa la totalidad del contenido del curso: desde matrices y sistemas lineales hasta límites, continuidad y optimización mediante cálculo diferencial.',
        'por_que_funciona': 'Permite demostrar la integración de conocimientos analíticos aplicados a la resolución de problemas de ingeniería.',
        'conexion_ingenieria': 'Base indispensable para cursos avanzados: Cálculo Integral, Ecuaciones Diferenciales, Métodos Numéricos y Algoritmos Avanzados.',
        'ejemplo': {
            'problema': 'Halla el punto crítico donde la derivada de f(x) = x^2 - 6x se anula (f\'(x) = 0)',
            'pasos': [
                'Paso 1: Deriva f(x): f\'(x) = 2x - 6.',
                'Paso 2: Iguala a cero: 2x - 6 = 0.',
                'Paso 3: Despeja x: 2x = 6 -> x = 3.',
                'Paso 4: El punto crítico es x = 3 (mínimo de la parábola).'
            ],
            'resultado': '3'
        },
        'errores_comunes': [
            'Olvidar derivar antes de igualar a cero.'
        ],
        'truco_profesor': 'Para encontrar máximos y mínimos: 1) Deriva, 2) Iguala a cero, 3) Despeja x.'
    }
}


def obtener_teoria_leccion(leccion_id):
    """Devuelve la guía teórica completa para una lección específica."""
    return GUIA_TEORICA.get(leccion_id, {
        'titulo': f'Lección {leccion_id}',
        'subtitulo': 'Aprende los fundamentos paso a paso',
        'concepto': 'En esta lección reforzaremos los procedimientos matemáticos correspondientes con ejemplos paso a paso.',
        'por_que_funciona': 'Toda regla matemática tiene una base lógica y predecible.',
        'conexion_ingenieria': 'Este tipo de cálculo modela procesos computacionales directos en software.',
        'ejemplo': {
            'problema': 'Ejemplo práctico del tema',
            'pasos': ['Revisa la regla principal.', 'Aplica paso a paso.', 'Verifica el resultado.'],
            'resultado': 'Completado'
        },
        'errores_comunes': ['Apresurarse en el procedimiento.'],
        'truco_profesor': 'Trabaja con calma y comprueba cada paso.'
    })
