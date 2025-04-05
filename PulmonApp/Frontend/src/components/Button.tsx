import React from 'react';

type ButtonProps = {
  label: string;
  onClick: () => void;
  type?: 'button' | 'submit' | 'reset'; // ✅ Only allow valid types
  className?: string;
  disabled?: boolean;
};

const Button: React.FC<ButtonProps> = ({
  label,
  onClick,
  type = 'button',
  className = '',
  disabled = false,
}) => {
  return (
    <button
      type={type}
      onClick={onClick}
      className={`btn ${disabled ? 'btn-secondary' : 'btn-primary'} ${className}`}
      disabled={disabled}
    >
      {label}
    </button>
  );
};

export default Button;
