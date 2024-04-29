const express = require('express');
const axios = require('axios');
const router = express.Router();
const {google} = require('googleapis');

const CLIENT_ID = '1004980276527-a99su492ckbo05dfji1i555dvt3v6jkc.apps.googleusercontent.com';
const CLIENT_SECRET = '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';
const REDIRECT_URI = '<http://localhost:3000/auth/google/callback>';

const oauth2Client = new google.auth.OAuth2(
  '1004980276527-a99su492ckbo05dfji1i555dvt3v6jkc.apps.googleusercontent.com',
  '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',
  '<http://localhost:3000/auth/google/callback>'
);

const scopes = [
  'https://www.googleapis.com/auth/drive.metadata.readonly'
];

// Generate a url that asks permissions for the Drive activity scope
const authorizationUrl = oauth2Client.generateAuthUrl({
  // 'online' (default) or 'offline' (gets refresh_token)
  access_type: 'offline',
  /** Pass in the scopes array defined above.
    * Alternatively, if only one scope is needed, you can pass a scope URL as a string */
  scope: scopes,
  // Enable incremental authorization. Recommended as a best practice.
  include_granted_scopes: true,
  prompt: 'select_account'
});

// Initiates the Google Login flow
router.get('/auth/google', (req, res) => {
  // const url = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=code&scope=profile email`;
  // const url = authorizationUrl;
  res.writeHead(301, { "Location": authorizationUrl });
  // res.redirect(url);
});

// Callback URL for handling the Google Login response
router.get('/auth/google/callback', async (req, res) => {
  const { code } = req.query;

  try {
    // Exchange authorization code for access token
    const { data } = await axios.post('<https://oauth2.googleapis.com/token>', {
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      code,
      redirect_uri: REDIRECT_URI,
      grant_type: 'authorization_code',
    });

    const { access_token, id_token } = data;

    // Use access_token or id_token to fetch user profile
    const { data: profile } = await axios.get('<https://www.googleapis.com/oauth2/v1/userinfo>', {
      headers: { Authorization: `Bearer ${access_token}` },
    });

    // Code to handle user authentication and retrieval using the profile data

    res.redirect('/');
  } catch (error) {
    console.error('Error:', error.response.data.error);
    res.redirect('/login');
  }
});

// Logout route
router.get('/logout', (req, res) => {
  // Code to handle user logout
  res.redirect('/login');
});

module.exports = router;