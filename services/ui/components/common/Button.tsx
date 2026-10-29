
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  children: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({ children, variant = 'primary', ...props }) => {
  const baseClasses = "px-4 py-2 rounded-md font-bold transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variantClasses = {
    primary: 'bg-sentinel-cyan text-sentinel-blue hover:bg-opacity-80',
    secondary: 'bg-sentinel-steel text-sentinel-light hover:bg-sentinel-silver',
    danger: 'bg-sentinel-red text-sentinel-light hover:bg-opacity-80',
  };

  return (
    <button className={`${baseClasses} ${variantClasses[variant]}`} {...props}>
      {children}
    </button>
  );
};

export default Button;
