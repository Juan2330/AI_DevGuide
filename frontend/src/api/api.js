const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:3000/predict";

export const sendProjectDescription = async (descripcion) => {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ descripcion }),
    });

    if (!response.ok) {
      throw new Error("Error en la petición al backend");
    }

    return await response.json();
  } catch (error) {
    return { error: "No se pudo obtener una respuesta del servidor." };
  }
};