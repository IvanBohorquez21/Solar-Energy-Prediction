# src/processing.py

def calculate_solar_output(temp, clouds, p_nom, efficiency_user):
    """
    Calculates power output including user-defined efficiency/losses.
    """
    # 1. Estimated Irradiance
    est_irradiance = 1000 * (1 - (clouds/100) * 0.75)

    # 2. Temperature Factor
    t_factor = 1 - (0.0045 * (temp - 25)) if temp > 25 else 1.0

    # 3. Final Power Output 
    # Usamos la eficiencia del slider como un factor de ajuste (ej: 0.18)
    # Dividimos por 100 porque el slider da valores como 18.5
    eff_factor = efficiency_user / 100
    
    # La fórmula estándar se ajusta por la eficiencia real del sistema
    p_out = (p_nom * (est_irradiance / 1000) * t_factor) * (eff_factor / 0.20) 
    # (Dividimos por 0.20 como referencia de un panel estándar)

    return {
        "irradiance": round(est_irradiance, 2),
        "thermal_factor": round(t_factor, 3),
        "power_output": round(p_out, 2)
    }