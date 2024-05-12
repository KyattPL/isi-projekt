import React, { useContext } from 'react';
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import { Link } from 'react-router-dom';
import Cookies from 'js-cookie';

import AuthContext from './AuthContext';

function Header() {
    const { isLoggedIn, hasPremium, email, setIsLoggedIn, setHasPremium, setEmail } = useContext(AuthContext);

    console.log("login:", isLoggedIn);
    console.log("hasPremium:", hasPremium);

    const handleSignOut = async () => {
        setEmail("");
        setHasPremium(false);
        setIsLoggedIn(false);
        Cookies.remove('isLoggedIn');
        Cookies.remove('hasPremium');
        Cookies.remove('email');
        await fetch(`http://localhost:8000/session/${email}`, {
            method: 'DELETE'
        });
    };

    return (
        <AppBar position="sticky" sx={{ height: '60px' }}>
            <Toolbar>
                <Typography variant="h6" component={Link} sx={{ textDecoration: 'none' }} color='black' to="/" >
                    Clone.gg
                </Typography>
                <Container sx={{ flexGrow: 1 }} />
                {(isLoggedIn && !hasPremium) ? (
                    <Button color="inherit" component={Link} to="/premium">Premium</Button>
                ) : <></>}
                <Button color="inherit" component={Link} to="/">Home</Button>
                {isLoggedIn ?
                    <Button color="inherit" onClick={handleSignOut}>Sign out</Button>
                    : <Button color="inherit" component={Link} to="/login">Log In</Button>
                }
            </Toolbar>
        </AppBar>
    );
}

export default Header;