import React from 'react';

interface AuthenticationMessageProps {
  message?: string;
}

/**
 * Functional component that represents authentication
 * @returns TSX element representing animation of flakes
 */
const AuthenticationMessage: React.FC<AuthenticationMessageProps> = ({
  message = 'Please log in to view this content.',
}) => {
  return <div>{message}</div>;
};

export default AuthenticationMessage;
