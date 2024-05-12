import React from 'react';

const AuthContext = React.createContext({
    isLoggedIn: false,
    email: "",
    hasPremium: false,
});

export default AuthContext;