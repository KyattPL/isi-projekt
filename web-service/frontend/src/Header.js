import React, { useContext } from 'react';
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import { Link } from 'react-router-dom';

import AuthContext from './AuthContext';

function Header() {
    const { isLoggedIn } = useContext(AuthContext);

    return (
        <AppBar position="sticky" sx={{ height: '60px' }}>
            <Toolbar>
                <Typography variant="h6" component={Link} sx={{ textDecoration: 'none' }} color='black' to="/" >
                    Clone.gg
                </Typography>
                <Container sx={{ flexGrow: 1 }} />
                {isLoggedIn && (
                    <Button color="inherit" component={Link} to="/premium">Premium</Button>
                )}
                <Button color="inherit" component={Link} to="/">Home</Button>
                <Button color="inherit" component={Link} to="/login">Log In</Button>
            </Toolbar>
        </AppBar>
    );
}

export default Header;