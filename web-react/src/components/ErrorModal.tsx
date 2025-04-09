import React from 'react';
import { Modal, Button } from 'react-bootstrap';

interface ErrorModalProps {
  show: boolean;
  handleClose: () => void;
  errorMessage: string;
}

export const ErrorModal: React.FC<ErrorModalProps> = ({
  show,
  handleClose,
  errorMessage,
}) => {
  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>Error</Modal.Title>
      </Modal.Header>
      <Modal.Body>{errorMessage}</Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ErrorModal;
