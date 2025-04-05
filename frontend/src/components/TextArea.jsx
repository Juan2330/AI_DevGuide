import { h } from "preact";

const TextArea = ({ value, onChange }) => {
  return (
    <textarea
      className="w-full max-w-[950px] h-[162px] p-4 border-2 border-gray-700 bg-gray-800 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-base md:text-lg"
      placeholder="Describe tu proyecto aquí..."
      value={value}
      onInput={(e) => onChange(e.target.value)}
    />
  );
};

export default TextArea;
