from django.shortcuts import render
import pandas as pd
from sodapy import Socrata
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import io
import base64
from django.http import HttpResponse

def index(request):
    # Fetch Socrata data
    client1 = Socrata("www.datos.gov.co", "1jFXKkxpQiKWOldM2HUTOw4TI")
    results = client1.get("rs3u-8r4q", limit=2000)
    results_df = pd.DataFrame.from_records(results)

    # Filter DataFrame to include only specified columns
    columns = ['entidad', 'gizscore', 'fallecidos', 'tramo', 'nombre', 'municipio', 'departamento']
    results_df = results_df[columns]

    # Convert DataFrame to JSON
    socrata_data_json = results_df.to_json(orient='records')

    return render(request, 'index.html', {'socrata_data': socrata_data_json})

def analisis(request):
    # Fetch data from rs3u-8r4q
    client2 = Socrata("www.datos.gov.co", "1jFXKkxpQiKWOldM2HUTOw4TI")
    results = client2.get("rs3u-8r4q", limit=2000)
    results_df = pd.DataFrame.from_records(results)

    # Filter DataFrame to include only specified columns
    columns = ['entidad', 'gizscore', 'fallecidos', 'tramo', 'nombre', 'municipio', 'departamento']
    results_df = results_df[columns]

    # Dictionary with tramo lengths
    road_distances = {
        "Bogotá - Villavicencio": 109.9,
        "Granada - Villavicencio": 100,
        "Villavicencio - Yopal": 252.9,
        "Duitama-Sogamoso": 19.7,
        "Tunja - Duitama": 55.7,
        "Bogotá - Tunja": 148.6,
        "Villavicencio-Puente Arimena": 47.4,
        "Bogotá - Barbosa": 433.9,
        "Puerto Araújo-Cimitarra": 29.47,
        "Bogotá - Villeta": 99.5,
        "Villeta-Honda": 66.1,
        "Bogotá - Mosquera": 22.5,
        "Mosquera - Facatativa - Los Andes": 175.1,
        "Mosquera - Funza": 3.3,
    }

    # Filter rows with tramo in road_distances and add tramo length
    results_df['tramo_length'] = results_df['tramo'].map(road_distances)
    filtered_df = results_df.dropna(subset=['tramo_length'])

    # Group by tramo to calculate total fallecidos and collect associated nombres
    grouped_data = (
        filtered_df.groupby('tramo')
        .agg(
            tramo_length=('tramo_length', 'first'),
            total_fallecidos=('fallecidos', lambda x: sum(map(int, x))),
            nombres=('nombre', lambda x: list(set(x)))
        )
        .reset_index()
    )

    # Convert grouped data to a list of dictionaries
    analisis_data = grouped_data.to_dict(orient='records')

    return render(request, 'analisis.html', {'analisis_data': analisis_data})

def tramo_detail(request, tramo_name):
    # Fetch data from rs3u-8r4q
    client2 = Socrata("www.datos.gov.co", "1jFXKkxpQiKWOldM2HUTOw4TI")
    results = client2.get("rs3u-8r4q", limit=2000)
    results_df = pd.DataFrame.from_records(results)

    # Filter DataFrame to include only specified columns
    columns = ['entidad', 'gizscore', 'fallecidos', 'tramo', 'nombre', 'municipio', 'departamento']
    results_df = results_df[columns]

    # Dictionary with tramo lengths
    road_distances = {
        "Bogotá - Villavicencio": 109.9,
        "Granada - Villavicencio": 100,
        "Villavicencio - Yopal": 252.9,
        "Duitama-Sogamoso": 19.7,
        "Tunja - Duitama": 55.7,
        "Bogotá - Tunja": 148.6,
        "Villavicencio-Puente Arimena": 47.4,
        "Bogotá - Barbosa": 433.9,
        "Puerto Araújo-Cimitarra": 29.47,
        "Bogotá - Villeta": 99.5,
        "Villeta-Honda": 66.1,
        "Bogotá - Mosquera": 22.5,
        "Mosquera - Facatativa - Los Andes": 175.1,
        "Mosquera - Funza": 3.3,
    }

    # Filter rows with tramo in road_distances and add tramo length
    results_df['tramo_length'] = results_df['tramo'].map(road_distances)
    filtered_df = results_df.dropna(subset=['tramo_length'])

    # Get data for the specific tramo
    tramo_data = filtered_df[filtered_df['tramo'] == tramo_name]
    if tramo_data.empty:
        return render(request, '404.html', status=404)

    # Aggregate data for the specific tramo
    tramo_length = tramo_data['tramo_length'].iloc[0]
    total_fallecidos = tramo_data['fallecidos'].astype(int).sum()
    density = total_fallecidos / tramo_length  # ρi = Total Fallecidos / Longitud del Tramo

    # Calculate the integral for the first half of the tramo using real data
    x1_half, x2_half = 0, tramo_length / 2  # Limits for the first half
    integral_half = density * (x2_half - x1_half)  # ∫[x1_half, x2_half] density dx

    tramo_info = {
        'tramo': tramo_name,
        'tramo_length': tramo_length,
        'half_length': tramo_length / 2,  # Pre-calculate half-length
        'total_fallecidos': total_fallecidos,
        'density': density,
        'integral_half': integral_half,  # Pass the pre-calculated integral value
        'nombres': list(tramo_data['nombre'].unique())
    }

    # Generate the line graph for the tramo
    x = [0, tramo_length]
    y = [density, density]  # Constant density across the tramo
    plt.figure(figsize=(8, 4))
    plt.plot(x, y, label=f"Densidad: {density:.2f} fallecidos/km", color='blue', linestyle='-', marker='o')
    plt.fill_between(x, y, color='blue', alpha=0.2)
    plt.title(f"Densidad de Fallecidos por Kilómetro - {tramo_name}", color='white')
    plt.xlabel("Distancia (km)", color='white')
    plt.ylabel("Densidad de Fallecidos", color='white')
    plt.legend()
    plt.grid(True, color='gray', linestyle='--', linewidth=0.5)
    plt.gca().set_facecolor('darkgray')
    plt.gca().tick_params(colors='white')
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', facecolor='darkgray')
    buffer.seek(0)
    graphic_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    tramo_info['graphic'] = graphic_base64

    # Generate the graph for the first half of the tramo (integral with adjusted limits)
    x_half = [0, tramo_length / 2]
    y_half = [density, density]
    plt.figure(figsize=(8, 4))
    plt.plot(x_half, y_half, label=f"Densidad: {density:.2f} fallecidos/km", color='purple', linestyle='-', marker='o')
    plt.fill_between(x_half, y_half, color='purple', alpha=0.2)
    plt.title(f"Integral Evaluada de 0 a {tramo_length / 2:.1f} km - {tramo_name}", color='white')
    plt.xlabel("Distancia (km)", color='white')
    plt.ylabel("Densidad de Fallecidos", color='white')
    plt.legend()
    plt.grid(True, color='gray', linestyle='--', linewidth=0.5)
    plt.gca().set_facecolor('darkgray')
    plt.gca().tick_params(colors='white')
    plt.tight_layout()
    buffer_half = io.BytesIO()
    plt.savefig(buffer_half, format='png', facecolor='darkgray')
    buffer_half.seek(0)
    graphic_half_base64 = base64.b64encode(buffer_half.getvalue()).decode('utf-8')
    buffer_half.close()

    tramo_info['graphic_half'] = graphic_half_base64

    # Generate the graph for quadratic modeling (fake data)
    quadratic_x = np.array([0, 1, 2, 3, 4, 5])  # Distances in km
    quadratic_y = np.array([2, 3, 5, 4, 2, 1])  # Fake accident densities

    # Fit a quadratic function to the data
    coefficients = np.polyfit(quadratic_x, quadratic_y, 2)
    quadratic_fit = np.poly1d(coefficients)

    # Calculate the integral of the quadratic function over the entire tramo
    x1, x2 = 0, 5  # Limits of the tramo
    integral_total = np.polyint(quadratic_fit)  # Get the indefinite integral
    area_under_curve = integral_total(x2) - integral_total(x1)  # Evaluate definite integral

    # Generate points for the fitted curve
    x_fit = np.linspace(0, 5, 100)
    y_fit = quadratic_fit(x_fit)

    # Plot the quadratic fit and the area under the curve
    plt.figure(figsize=(8, 4))
    plt.scatter(quadratic_x, quadratic_y, color='red', label='Datos de Accidentes')
    plt.plot(x_fit, y_fit, color='orange', label=f"Modelo Cuadrático: {coefficients[0]:.2f}x² + {coefficients[1]:.2f}x + {coefficients[2]:.2f}")
    plt.fill_between(x_fit, y_fit, color='orange', alpha=0.2, label=f"Área Bajo la Curva: {area_under_curve:.2f} accidentes")
    plt.title(f"Modelo Cuadrático de Densidad de Accidentes - {tramo_name}", color='white')
    plt.xlabel("Distancia (km)", color='white')
    plt.ylabel("Densidad de Accidentes", color='white')
    plt.legend()
    plt.grid(True, color='gray', linestyle='--', linewidth=0.5)
    plt.gca().set_facecolor('darkgray')
    plt.gca().tick_params(colors='white')
    plt.tight_layout()
    buffer_quadratic = io.BytesIO()
    plt.savefig(buffer_quadratic, format='png', facecolor='darkgray')
    buffer_quadratic.seek(0)
    graphic_quadratic_base64 = base64.b64encode(buffer_quadratic.getvalue()).decode('utf-8')
    buffer_quadratic.close()

    tramo_info['graphic_quadratic'] = graphic_quadratic_base64
    tramo_info['quadratic_coefficients'] = coefficients
    tramo_info['area_under_curve'] = area_under_curve

    return render(request, 'tramo_detail.html', {'tramo_info': tramo_info})