import React from "react";
import { Snackbar } from "@mui/material";

function Toast({ message, isOpen, setIsOpen }) {
    const handleClose = () => {
        setIsOpen(false);
    };

    return (
        <Snackbar open={isOpen} autoHideDuration={3000} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            message={message} onClose={handleClose} />
    );
}

export default Toast;