# Motor de Precios Dinámicos [Dynamic Pricing Engine](apps/core/engine.py)

## ¿Qué hace?
El `MotorDinamico` es un sistema diseñado para calcular y ajustar el precio de las entradas de un evento en tiempo real. 

En lugar de mantener un valor estático desde el inicio hasta el final de la venta, el motor toma el precio base del sector y lo multiplica por una serie de coeficientes variables. El precio final cambia entre el 100% y el 130% del valor original, basándose en tres factores calculados en el momento de la cotización:
1. La popularidad del artista (medida en reproducciones).
2. El tiempo (días faltantes para el evento).
3. La escasez (porcentaje de entradas disponibles en el sector).

---

## ¿Por qué lo hace?
El objetivo principal de esta implementacion es mejorar las ganancias por entrada sin perjudicar la ocupación de los eventos mediante la respuesta automática a la oferta y la demanda. Al cuantificar estas tres variables en tiempo real, el motor toma decisiones de precio fundamentadas en datos duros en lugar de estimaciones manuales de algun empleado gubernamental encargado de esta área.

La lógica detrás de cada factor responde a:

* Popularidad (El Valor Percibido): Estandariza la cantidad de reproducciones del artista frente a una muestra poblacional previamente confeccionada (esta muestra poblacional puede ser actualizada por medio de este "[Jupyter Notebook](persistencia_de_regla.ipynb)"). Si el artista es un fenómeno masivo, bajo los estandares de la "[regla de medir](micro_universo_artistas.csv)", el sistema asume que el público está dispuesto a pagar más por la popularidad del show.
* Tiempo (Incentivo de Compra Temprana): Premia a los usuarios que compran con anticipación manteniendo el precio base. A medida que la fecha del evento se acerca, el coeficiente aumenta aceleradamente (de forma cuadrática) penalizando la compra de último minuto.
* Escasez (Ley de Oferta y Demanda): A medida que un sector se llena y los lugares escasean, el valor de las entradas restantes sube. Esto asegura que los últimos tickets disponibles, que suelen ser los más buscado (poca oferta, mucha demanda), se vendan al máximo valor posible.

---

## Desglose Técnico de los Coeficientes

El algoritmo descompone el precio asignando un peso del 70% al valor fijo y un 30% a las variables dinámicas (10% a cada coeficiente).

* `coef_popularidad`: Aplica una transformación logarítmica y una función sigmoide para suavizar los extremos. Esto evita que un artista con billones de reproducciones rompa la escala de precios, manteniendo el multiplicador acotado de forma segura entre `1.0` y `2.0`. Para entender porque se tomó la decision de usar esta funcion vea el documento "" y puede ver el proceso de pensamiento en el documento interactivo [Proceso de confeccion del coeficiente](Basurero_de_ideas.ipynb).
* `coef_tiempo`: Calcula la proporción de días faltantes respecto a la ventana total de venta. Utiliza una curva cuadrática inversa para que el aumento de precio sea casi imperceptible al principio, pero escale rápidamente en los últimos días.
* `coef_escacez`: Consulta la base de datos para obtener la capacidad máxima y las entradas vendidas del sector. Al igual que con el tiempo, utiliza una curva cuadrática para que el precio se dispare solo cuando el porcentaje de disponibilidad es críticamente bajo.