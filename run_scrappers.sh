#!/bin/bash

SCRAPPER_DIR="scrappers"
COMMON_PRODUCT_FINDER="utils/common-products-filter/main.py"
ERROR_LOG="scrape_errors.log"
ERROR_OCCURRED=false

echo "⬇️  Iniciando ejecución de scrapers..."

for script in $(find "$SCRAPPER_DIR" -type f -name "*_scrapper.py"); do
    script_name=$(basename "$script")
    echo "→ Ejecutando $script_name..."

    start_time=$(date +%s)
    output=$(python "$script" 2>&1)
    exit_code=$?
    end_time=$(date +%s)
    duration=$((end_time - start_time))

    if [ $exit_code -ne 0 ]; then
        ERROR_OCCURRED=true
        echo "❌ Error en $script_name (duración: ${duration}s)"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Error en $script_name (duración: ${duration}s)" >> "$ERROR_LOG"
        echo "$output" >> "$ERROR_LOG"
        echo "----------------------------------------" >> "$ERROR_LOG"
    else
        echo "✅ $script_name ejecutado correctamente en ${duration}s."
    fi
done

if $ERROR_OCCURRED; then
    echo "⚠️  Errores detectados. Revisa $ERROR_LOG"
else
    [ -f "$ERROR_LOG" ] && rm "$ERROR_LOG"
    echo "✅ Todos los scrapers se ejecutaron correctamente. Sin errores."

    echo "🧠 Ejecutando filtrado de productos comunes..."
    start_time=$(date +%s)
    output=$(python "$COMMON_PRODUCT_FINDER" 2>&1)
    exit_code=$?
    end_time=$(date +%s)
    duration=$((end_time - start_time))

    if [ $exit_code -ne 0 ]; then
        echo "❌ Error al ejecutar el filtrado de productos comunes (duración: ${duration}s)"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Error en filtrado de productos comunes (duración: ${duration}s)" >> "$ERROR_LOG"
        echo "$output" >> "$ERROR_LOG"
    else
        echo "✅ Filtrado de productos comunes completado en ${duration}s."
    fi
fi
