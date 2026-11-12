# Guía para explicar la segunda entrega

Este archivo es una ayuda de estudio en español. La entrega académica es `project/project-model.ipynb`, en inglés.

## Qué has construido

Una comparación reproducible de métodos para prever las unidades vendidas por producto durante la próxima
semana. Mantienes Online Retail II y el problema del primer brief. La previsión informa una revisión de
compras: no calcula cantidades a pedir ni detecta roturas de stock.

El estudio se limita a 50 productos del Reino Unido. Se eligieron por sus ventas en las primeras 26 semanas
completas, antes del entrenamiento y de cualquier evaluación. Es una decisión de alcance para estudiar
productos establecidos con un tiempo de ejecución corto. No permite generalizar a productos nuevos.

## Qué datos utilizas

El Excel tiene 1.067.371 líneas. El script conserva el original y genera una auditoría de exclusiones:
duplicados exactos, abonos, cantidades/precios no positivos, códigos ajenos al patrón propuesto de productos
y semanas incompletas. Quedan 970.909 líneas. Los grandes pedidos positivos se conservan; pueden proceder
de mayoristas reales. Eliminar duplicados es una decisión discutible y queda declarada, no demostrada como
corrección universal. Un cero semanal significa ninguna venta registrada, no producto disponible.

Publicas agregados semanales sin clientes ni números de factura. El notebook carga esos datos pequeños;
el profesor no necesita tu Excel ni rutas del Mac.

## Cómo evitas que el modelo haga trampas

Entrenas con semanas anteriores, validas con las siguientes y reservas 14 semanas finales. Todos los
productos de una semana están en el mismo bloque. Nunca usas una cantidad de la semana que quieres prever.

Los parámetros del modelo no cambian durante un bloque de evaluación. Cada lunes sí puedes incorporar las
ventas reales de la semana que acaba de terminar. Eso es evaluación de un paso con origen móvil: no es una
previsión de 14 semanas realizada de una vez.

La selección de productos utiliza solo el periodo inicial. Encoders, escaladores y modelos se ajustan dentro
de los folds de entrenamiento. La comprobación de noviembre de 2011 se hace después de congelar los modelos,
y no se utiliza para cambiarlos.

## Modelos y resultados

- Regla actual: repetir las unidades de la semana anterior.
- Referencia ingenua: media del conjunto de entrenamiento.
- Competidor transparente: media de las cuatro semanas anteriores.
- Modelo sencillo: Ridge con predicciones truncadas a cero.
- Ensemble: histogram gradient boosting con pérdida de Poisson.

La validación selecciona boosting; una búsqueda temporal ajusta sus parámetros. Ridge se conserva como un
resultado negativo útil. El test final contiene 700 producto-semanas entre el 29/08/2011 y el 28/11/2011.

| Método | MAE, unidades | WAPE |
|---|---:|---:|
| Semana anterior | 208,48 | 71,81% |
| Boosting ajustado | 188,68 | 64,98% |
| Media de cuatro semanas | 177,69 | 61,20% |

El modelo reduce WAPE un 9,50% **relativo** frente a la semana anterior. No son 9,50 puntos porcentuales:
la diferencia absoluta es aproximadamente 6,82 puntos. La media de cuatro semanas obtiene el menor error.
La conclusión defendible es conservarla como primera candidata a un piloto, en vez de imponer ML.

## Qué significan las métricas

MAE es el error absoluto medio en unidades por producto-semana. WAPE suma errores absolutos y los divide
por las unidades reales totales. RMSE penaliza especialmente los fallos grandes. El sesgo firmado revela
si el método tiende a sobreestimar o subestimar. No confundas WAPE del 65% con una precisión del 35%.

El intervalo exploratorio del cambio relativo, de −3,08% a 18,82%, incluye cero. Solo hay 14 semanas y puede
haber dependencia entre semanas: no afirmes que hemos demostrado una mejora futura segura.

## Hipótesis y límites

H1: se observa concentración superior al 50%, con cuotas trimestrales del 78,6% al 81,7% para el 20% de
productos de mayor volumen. H2: los ratios de noviembre son 1,880 en 2010 y 1,652 en 2011, por encima de 1,10.
Es una comparación descriptiva de dos años, no una explicación causal. H3 supera el umbral del 5% frente
a la semana anterior, pero con incertidumbre y sin superar la media de cuatro semanas.

Los productos de menor volumen obtienen peor WAPE y no mejoran su referencia de la semana anterior.
Una media global no basta: hacen falta seguimiento por grupos y un método de respaldo.

No afirmes ahorro monetario, reducción real de roturas de stock ni beneficio actual. Faltan existencias,
costes y plazos de proveedores, y los datos son históricos. El siguiente bloque añade despliegue y monitoreo;
no los presentes como ya implementados.

## Qué guarda model.joblib

Un único pipeline de scikit-learn: construye variables desde una fila de históricos cerrados, transforma
las columnas y genera una predicción. Necesita `retail_features.py` y versiones compatibles. No recibe
facturas en bruto. El esquema indica las columnas y los productos admitidos. El modelo guardado se evaluó,
pero la recomendación del estudio es no automatizar compras con él.
