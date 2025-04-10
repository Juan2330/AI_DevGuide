import { h } from "preact";
import { useState, useEffect } from "preact/hooks";
import { motion } from "framer-motion"; 

const Button = ({ onClick, text }) => {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg shadow-md transition-all text-base md:text-lg"
    >
      {text}
    </motion.button>
  );
};

export default Button;
