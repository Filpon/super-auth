import React, { useEffect } from 'react';
import './styles/Snowflakes.scss';

/**
 * Functional component that represents flakes animation
 *
 * @returns TSX element representing animation of flakes
 */
export const Snowflakes: React.FC = () => {
  useEffect(() => {
    const snowflakes = document.querySelectorAll('.snowflake');

    snowflakes.forEach((snowflake) => {
      const element = snowflake as HTMLElement;
      element.style.left = Math.random() * 100 + 'vw';
      const fallDuration = Math.random() * 3 + 2;
      element.style.animationDuration = fallDuration + 's';
      const delay = Math.random() * 5;
      element.style.animationDelay = delay + 's';
    });
  }, []);

  return (
    <div className="snowflakes" aria-hidden="true">
      {Array.from({ length: 20 }).map((_, index) => (
        <div className="snowflake" key={index}>
          ❄
        </div>
      ))}
    </div>
  );
};
