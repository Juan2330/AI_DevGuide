import { h } from "preact";
import { useState, useCallback } from "preact/hooks";
import { motion } from "framer-motion";
import Button from "./components/Button";
import TextArea from "./components/TextArea";
import { sendProjectDescription } from "./api/api";

const decodeEntities = (str) => {
  if (!str) return str;
  const textarea = document.createElement('textarea');
  textarea.innerHTML = str;
  return textarea.value;
};

const CodeBlock = ({ code, language = '' }) => {
  const processCode = (code) => {
    if (!code) return code;
    const parts = code.split(/(\*\*.*?\*\*)/g);
    
    return parts.map((part, i) => {
      if (part.startsWith('//')) {
        return (
          <span key={i} className="text-purple-400 font-semibold">
            {part.replace(/\*\*/g, '')}
          </span>
        );
      } else {
        return (
          <span key={i} className="text-green-400">
            {part}
          </span>
        );
      }
    });
  };

  return (
    <pre className="bg-gray-900 p-3 rounded-md overflow-x-auto text-sm md:text-base">
      <code>{processCode(decodeEntities(code))}</code>
    </pre>
  );
};

const TechnologyDetail = ({ tech }) => {
  if (!tech) return null;

  return (
    <div className="space-y-3 p-4 bg-gray-800/50 rounded-lg border border-gray-700 text-base">
      <h3 className="text-lg md:text-xl font-semibold text-blue-300">{tech.nombre}</h3>
      <p className="text-gray-300">{tech.descripcion}</p>
      
      {tech.justificacion && (
        <div className="bg-gray-700/30 p-3 rounded">
          <h4 className="text-sm md:text-base font-semibold text-yellow-200 mb-1">Justificación técnica:</h4>
          <p className="text-gray-300">{tech.justificacion}</p>
        </div>
      )}
      
      {tech.uso && (
        <div className="bg-gray-700/30 p-3 rounded">
          <h4 className="text-sm md:text-base font-semibold text-green-200 mb-1">Uso en este proyecto:</h4>
          <p className="text-gray-300">{tech.uso}</p>
        </div>
      )}
      
      {tech.instalacion && (
        <div className="mt-3">
          <h4 className="text-sm md:text-base font-semibold text-purple-200 mb-2">Instalación:</h4>
          {typeof tech.instalacion === 'string' ? (
            <CodeBlock code={tech.instalacion} />
          ) : (
            Object.entries(tech.instalacion).map(([os, cmd]) => (
              cmd && (
                <div key={os} className="mb-3">
                  <span className="text-gray-400 text-xs md:text-sm font-medium capitalize">{os}:</span>
                  <CodeBlock code={cmd} />
                </div>
              )
            ))
          )}
        </div>
      )}
      
      {tech.caracteristicas?.length > 0 && (
        <div className="mt-3">
          <h4 className="text-sm md:text-base font-semibold text-blue-200 mb-1">Características clave:</h4>
          <ul className="list-disc list-inside ml-4 text-gray-300 space-y-1">
            {tech.caracteristicas.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

const App = () => {
  const [descripcion, setDescripcion] = useState("");
  const [respuesta, setRespuesta] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = useCallback(async () => {
    if (!descripcion.trim() || descripcion.trim().length < 20) {
      setError("Por favor ingresa una descripción detallada (mínimo 20 caracteres)");
      return;
    }

    setLoading(true);
    setError(null);
    setRespuesta(null);
    
    try {
      const resultado = await sendProjectDescription(descripcion);
      
      if (!resultado?.success) {
        setError(resultado?.message || "Error al generar recomendaciones");
      } else {
        setRespuesta(resultado);
      }
    } catch (err) {
      setError("Error al conectar con el servidor");
      console.error("Error:", err);
    } finally {
      setLoading(false);
    }
  }, [descripcion]);

  const renderReportSection = (title, content) => (
    content && (
      <div className="p-5 bg-gray-800 rounded-lg border border-gray-700 shadow">
        <h3 className="text-xl md:text-2xl font-semibold text-blue-400 mb-4">{title}</h3>
        {content}
      </div>
    )
  );

  const renderReport = () => {
    if (!respuesta?.report) return null;
    const { report } = respuesta;

    if (report.error) {
      return (
        <div className="p-4 bg-red-900/20 rounded-md border border-red-700">
          <h3 className="text-lg md:text-xl font-semibold text-red-400">Error en el informe</h3>
          <p className="text-red-300">{report.message}</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {renderReportSection(
          "📌 Introducción",
          <p className="text-gray-300">{report.introduccion}</p>
        )}

        {report.explicacion_tecnologias && renderReportSection(
          "🛠 Tecnologías Recomendadas",
          <div className="space-y-6">
            {report.explicacion_tecnologias.lenguaje && (
              <TechnologyDetail tech={report.explicacion_tecnologias.lenguaje} />
            )}
            
            {report.explicacion_tecnologias.framework && (
              <TechnologyDetail tech={report.explicacion_tecnologias.framework} />
            )}
            
            {report.explicacion_tecnologias.librerias?.length > 0 && (
              <div>
                <h4 className="text-lg md:text-xl font-semibold text-green-300 mb-3">Librerías principales</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {report.explicacion_tecnologias.librerias.map((lib, i) => (
                    <TechnologyDetail key={i} tech={lib} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {report.base_datos && renderReportSection(
          "💾 Base de Datos",
          <TechnologyDetail tech={report.base_datos} />
        )}

        {report.arquitectura && renderReportSection(
          "🏗 Arquitectura",
          <div className="space-y-4">
            {report.arquitectura.diagrama && (
              <div className="bg-gray-700/30 p-3 rounded">
                <p className="text-gray-300">{report.arquitectura.diagrama}</p>
              </div>
            )}
            {report.arquitectura.componentes?.length > 0 && (
              <div>
                <h4 className="text-sm md:text-base font-semibold text-yellow-200 mb-2">Componentes principales:</h4>
                <ul className="list-disc list-inside ml-4 text-gray-300">
                  {report.arquitectura.componentes.map((comp, i) => (
                    <li key={i}>{comp}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {report.instalacion && renderReportSection(
          "🔧 Instalación",
          <div className="space-y-4">
            {report.instalacion.requisitos?.length > 0 && (
              <div>
                <h4 className="text-sm md:text-base font-semibold text-blue-300 mb-2">Requisitos previos:</h4>
                <ul className="list-disc list-inside ml-4 text-gray-300">
                  {report.instalacion.requisitos.map((req, i) => (
                    <li key={i}>{req}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {report.instalacion.librerias && (
              <div>
                <h4 className="text-sm md:text-base font-semibold text-purple-300 mb-2">Instalación de dependencias:</h4>
                <div className="space-y-2">
                  <CodeBlock code={report.instalacion.librerias.comando} />
                  <CodeBlock code={report.instalacion.librerias.ejemplo} />
                </div>
              </div>
            )}
          </div>
        )}

        {report.recomendaciones?.length > 0 && renderReportSection(
          "💡 Recomendaciones",
          <ul className="list-disc list-inside ml-4 text-gray-300 space-y-2">
            {report.recomendaciones.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center p-4 md:p-8 text-base md:text-lg">
      <motion.div 
        className="flex items-center justify-center mb-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl md:text-4xl font-bold font-mono text-blue-400 flex items-center">
          AI 
          <img 
            src="/ai-devguide-logo.svg" 
            alt=""
            className="mx-2 w-8 h-8 md:w-12 md:h-12"
          />
          DevGuide
        </h1>
      </motion.div>

      <div className="w-full max-w-4xl">
        <div className="mb-6">
          <label className="block text-sm md:text-base font-medium text-gray-300 mb-2">
            Describe tu proyecto en detalle:
          </label>
          <TextArea
            value={descripcion}
            onChange={setDescripcion}
            placeholder="Ej: Sistema de gestión de inventario con control de ventas y reportes analíticos..."
          />
          <p className="text-xs md:text-sm text-gray-500 mt-1">
            Mínimo 20 caracteres. Sé específico sobre funcionalidades clave.
          </p>
        </div>
        
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-2 p-2 bg-red-900/20 rounded text-red-300 text-sm md:text-base"
          >
            {error}
          </motion.div>
        )}

        <div className="mt-4 flex justify-center">
          <Button
            onClick={handleSubmit}
            text={loading ? "Generando recomendación..." : "Generar Recomendación Técnica"}
            disabled={loading}
          />
        </div>
      </div>

      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-8 flex flex-col items-center"
        >
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500 mb-2"></div>
          <p className="text-gray-400">Analizando requisitos técnicos...</p>
        </motion.div>
      )}

      {respuesta && !loading && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-4xl mt-8 space-y-8"
        >
          {renderReport()}

          {respuesta.code_example?.content && (
            <div className="p-5 bg-gray-800 rounded-lg border border-gray-700 shadow">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl md:text-2xl font-semibold text-yellow-400">💻 Código de Ejemplo</h3>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(respuesta.code_example.content);
                    alert('Código copiado al portapapeles');
                  }}
                  className="text-sm md:text-base bg-gray-700 hover:bg-gray-600 text-white px-3 py-1 rounded"
                >
                  📋 Copiar
                </button>
              </div>
              <CodeBlock code={respuesta.code_example.content} />
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default App;